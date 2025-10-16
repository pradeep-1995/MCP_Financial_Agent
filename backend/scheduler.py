from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import yfinance as yf
from perf_db import get_unresolved_predictions, resolve_prediction

def check_and_resolve():
    """Background job to resolve predictions"""
    rows = get_unresolved_predictions()
    
    for r in rows:
        pred_id, ticker, timeframe, predicted_at_str, horizon = r
        predicted_at = datetime.fromisoformat(predicted_at_str)
        target_time = predicted_at + timedelta(minutes=horizon)
        
        if datetime.utcnow() >= target_time:
            # Fetch latest close price
            interval = "1m" if timeframe=="1m" else ("15m" if timeframe=="15m" else "1h")
            try:
                df = yf.download(ticker, period="1d", interval=interval, progress=False)
                if df is None or df.empty:
                    continue
                actual_price = float(df['Close'].iloc[-1])
                resolve_prediction(pred_id, actual_price)
            except Exception as e:
                print(f"Error resolving prediction {pred_id}: {e}")

def start_scheduler():
    """Start the background scheduler"""
    sched = BackgroundScheduler()
    sched.add_job(check_and_resolve, 'interval', seconds=60)
    sched.start()
    return sched
