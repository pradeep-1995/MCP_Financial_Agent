# Financial AI Agent with LSTM, Candlestick Analysis & Telegram Integration

A comprehensive AI-powered financial analysis system that combines LSTM predictions, candlestick pattern recognition, sentiment analysis, and an adaptive self-learning (MCP) layer. Features real-time Telegram bot integration for instant market analysis.

## 🚀 Features

### Core Capabilities
- **Multi-Timeframe Analysis**: 1min, 15min, and 1hr candlestick data via yFinance
- **Candlestick Pattern Detection**: Bullish/Bearish Engulfing, Doji, Hammer, Shooting Star, Morning Star
- **Dual Forecasting Models**: ARIMA + LSTM neural networks
- **AI Sentiment Analysis**: Gemini API with TextBlob fallback
- **Adaptive MCP Layer**: Self-learning system that adjusts model weights based on accuracy
- **Telegram Bot**: Real-time analysis via simple commands
- **Web Dashboard**: Modern React UI for monitoring and analysis

## 📱 Quick Start - Telegram Bot

### 1. Set Webhook
```bash
# Your backend must be accessible via HTTPS
# Option A: Use ngrok for testing
ngrok http 8001

# Option B: Use your production URL
BACKEND_URL="<your-url>"
curl -F "url=${BACKEND_URL}/api/webhook" \
  https://api.telegram.org/
```

### 2. Use the Bot
Send to your bot: `TSLA` or `analyze AAPL`

Response includes:
- 📊 Candlestick pattern
- 💬 AI sentiment (Gemini)
- 🔮 ARIMA & LSTM forecasts
- ✅ BUY/SELL/HOLD recommendation
- 📈 Confidence level

## 🎯 Web Dashboard

Access at: `http://localhost:3000`

**Dashboard Page**: Monitor prediction accuracy, resolved vs pending predictions
**Analyze Page**: Analyze any ticker with comprehensive AI analysis

## 🤖 Training LSTM Models

Improve predictions by training models:
```bash
cd /app/backend
python scripts/train_lstm_for_ticker.py TSLA 1h
python scripts/train_lstm_for_ticker.py AAPL 15m
```

## 📊 API Usage

```bash
# Analyze ticker
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker":"TSLA"}'

# Get predictions
curl http://localhost:8001/api/predictions

# Get model stats
curl http://localhost:8001/api/model-stats/TSLA/1h
```

## 🧠 MCP Adaptive Learning

1. Every prediction is stored with timestamp
2. Background scheduler resolves predictions by comparing with actual prices
3. Mean Absolute Error (MAE) calculated for each model
4. Models with lower MAE get higher weights in decisions
5. System continuously improves accuracy over time

## ⚠️ Disclaimer

**NOT financial advice.** Educational purposes only. Always verify predictions independently and trade at your own risk.

## 🛠️ Tech Stack

Python • FastAPI • TensorFlow • React • Gemini API • yFinance • SQLite • MongoDB

---

**Built with Emergent AI Platform**
