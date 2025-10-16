import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from lstm_model import train_lstm
from config import LSTM_MODEL_DIR

def train(ticker, tf="1h", period="2y", window=32):
    """Train LSTM model for a specific ticker and timeframe"""
    print(f"Training LSTM for {ticker} on {tf} timeframe...")
    
    df = yf.download(ticker, period=period, interval=tf, progress=False)
    
    if df.empty:
        print(f"No data available for {ticker}")
        return
    
    model_path = os.path.join(LSTM_MODEL_DIR, f"{ticker}_{tf}_lstm.h5")
    
    try:
        train_lstm(df['Close'], model_path, window=window, epochs=30)
        print(f"✅ Model saved to {model_path}")
    except Exception as e:
        print(f"❌ Training failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_lstm_for_ticker.py TICKER [TIMEFRAME]")
        print("Example: python train_lstm_for_ticker.py TSLA 1h")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    timeframe = sys.argv[2] if len(sys.argv) > 2 else "1h"
    
    train(ticker, timeframe)
