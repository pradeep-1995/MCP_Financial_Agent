from fastapi import FastAPI, APIRouter, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Import financial agent modules
from data_fetcher import fetch_ohlcv
from pattern_analyzer import detect_patterns
from sentiment_analyzer import fetch_news_headlines, score_sentiment
from arima_util import arima_one_step_forecast
from lstm_model import predict_lstm
from ensemble_agent import EnsembleAgent
from report_agent import format_short_report
from telegram_handler import send_msg
from perf_db import init_db, store_prediction, get_recent_predictions, get_model_stats
from scheduler import start_scheduler
from config import LSTM_MODEL_DIR


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize ensemble agent
ensemble = EnsembleAgent()


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class AnalysisRequest(BaseModel):
    ticker: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Financial AI Agent API - Ready"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Financial AI Agent Routes

@api_router.post("/analyze")
async def analyze_ticker(request: AnalysisRequest):
    """Analyze a ticker and return comprehensive report"""
    ticker = request.ticker.upper()
    
    try:
        # Fetch data
        dfs = fetch_ohlcv(ticker, period="2d", intervals=("1m","15m","1h"))
        
        # Detect pattern on 1h
        pattern = None
        if "1h" in dfs and not dfs["1h"].empty:
            pattern = detect_patterns(dfs["1h"])
        
        # Sentiment
        headlines = fetch_news_headlines(ticker, limit=5)
        sent_score, sent_reasons = score_sentiment(headlines, ticker)
        
        # Quant: ARIMA + LSTM per timeframe
        quant_result = {"last_price": None, "tf": {}}
        
        for tf, df in dfs.items():
            if df.empty:
                quant_result["tf"][tf] = {
                    "arima_pred": None, "arima_ret": None, 
                    "lstm_pred": None, "lstm_ret": None
                }
                continue
            
            try:
                last = float(df['Close'].iloc[-1])
                quant_result["last_price"] = last
            except Exception:
                last = None
            
            # ARIMA
            arima_pred = arima_one_step_forecast(df['Close']) if len(df['Close'])>10 else None
            arima_ret = (arima_pred - last)/last if arima_pred and last else None
            
            # LSTM
            model_path = os.path.join(LSTM_MODEL_DIR, f"{ticker}_{tf}_lstm.h5")
            lstm_preds = predict_lstm(model_path, df['Close'].astype(float).tolist(), window=32, steps=1) if os.path.exists(model_path) else []
            lstm_pred = lstm_preds[0] if lstm_preds else None
            lstm_ret = (lstm_pred - last)/last if lstm_pred and last else None

            quant_result["tf"][tf] = {
                "arima_pred": arima_pred, "arima_ret": arima_ret, 
                "lstm_pred": lstm_pred, "lstm_ret": lstm_ret
            }
            
            # Store predictions for MCP
            if arima_pred:
                store_prediction(ticker, tf, "arima", datetime.utcnow().isoformat(), 
                               60 if tf=="1h" else (15 if tf=="15m" else 1), arima_pred)
            if lstm_pred:
                store_prediction(ticker, tf, "lstm", datetime.utcnow().isoformat(), 
                               60 if tf=="1h" else (15 if tf=="15m" else 1), lstm_pred)
        
        # Combine
        decision = ensemble.combine(ticker, quant_result, sent_score)
        
        return {
            "ticker": ticker,
            "pattern": pattern,
            "sentiment_score": sent_score,
            "quant_result": quant_result,
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        return {"error": str(e)}, 500

@api_router.get("/predictions")
async def get_predictions():
    """Get recent predictions"""
    try:
        preds = get_recent_predictions(limit=20)
        return {
            "predictions": [
                {
                    "ticker": p[0], "timeframe": p[1], "model": p[2],
                    "predicted_at": p[3], "predicted_price": p[4],
                    "actual_price": p[5], "error": p[6], "resolved": p[7]
                }
                for p in preds
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        return {"error": str(e)}, 500

@api_router.get("/model-stats/{ticker}/{timeframe}")
async def get_ticker_stats(ticker: str, timeframe: str):
    """Get model performance stats for a ticker"""
    try:
        stats = get_model_stats(ticker.upper(), timeframe)
        return {"ticker": ticker, "timeframe": timeframe, "stats": stats}
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {"error": str(e)}, 500

@api_router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    data = await request.json()
    
    # Get message from update
    message = data.get("message") or data.get("edited_message")
    if not message:
        return {"ok": True}
    
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    
    if not text:
        send_msg(chat_id, "Please send a ticker symbol to analyze (e.g., TSLA, AAPL)")
        return {"ok": True}
    
    # Extract ticker from message
    parts = text.upper().split()
    ticker = None
    
    for p in reversed(parts):
        if p.isalpha() and len(p) <= 5:
            ticker = p
            break
    
    if not ticker:
        send_msg(chat_id, "Please send a valid ticker symbol (e.g., `analyze TSLA` or just `TSLA`)")
        return {"ok": True}
    
    # Send processing message
    send_msg(chat_id, f"\ud83d\udd0d Analyzing {ticker}... Please wait.")
    
    try:
        # Fetch data
        dfs = fetch_ohlcv(ticker, period="2d", intervals=("1m","15m","1h"))
        
        # Detect pattern
        pattern = None
        if "1h" in dfs and not dfs["1h"].empty:
            pattern = detect_patterns(dfs["1h"])
        
        # Sentiment
        headlines = fetch_news_headlines(ticker, limit=5)
        sent_score, sent_reasons = score_sentiment(headlines, ticker)
        
        # Quant analysis
        quant_result = {"last_price": None, "tf": {}}
        
        for tf, df in dfs.items():
            if df.empty:
                quant_result["tf"][tf] = {
                    "arima_pred": None, "arima_ret": None,
                    "lstm_pred": None, "lstm_ret": None
                }
                continue
            
            try:
                last = float(df['Close'].iloc[-1])
                quant_result["last_price"] = last
            except Exception:
                last = None
            
            # ARIMA
            arima_pred = arima_one_step_forecast(df['Close']) if len(df['Close'])>10 else None
            arima_ret = (arima_pred - last)/last if arima_pred and last else None
            
            # LSTM
            model_path = os.path.join(LSTM_MODEL_DIR, f"{ticker}_{tf}_lstm.h5")
            lstm_preds = predict_lstm(model_path, df['Close'].astype(float).tolist(), window=32, steps=1) if os.path.exists(model_path) else []
            lstm_pred = lstm_preds[0] if lstm_preds else None
            lstm_ret = (lstm_pred - last)/last if lstm_pred and last else None

            quant_result["tf"][tf] = {
                "arima_pred": arima_pred, "arima_ret": arima_ret,
                "lstm_pred": lstm_pred, "lstm_ret": lstm_ret
            }
            
            # Store predictions
            if arima_pred:
                store_prediction(ticker, tf, "arima", datetime.utcnow().isoformat(),
                               60 if tf=="1h" else (15 if tf=="15m" else 1), arima_pred)
            if lstm_pred:
                store_prediction(ticker, tf, "lstm", datetime.utcnow().isoformat(),
                               60 if tf=="1h" else (15 if tf=="15m" else 1), lstm_pred)
        
        # Make decision
        decision = ensemble.combine(ticker, quant_result, sent_score)
        
        # Format report
        report_text = format_short_report(ticker, pattern, sent_score, sent_reasons, quant_result, decision)
        send_msg(chat_id, report_text)
        
    except Exception as e:
        logger.error(f"Error processing {ticker}: {e}")
        send_msg(chat_id, f"\u274c Error analyzing {ticker}: {str(e)}")
    
    return {"ok": True}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    """Initialize database and scheduler on startup"""
    init_db()
    start_scheduler()
    logger.info("Financial AI Agent started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()