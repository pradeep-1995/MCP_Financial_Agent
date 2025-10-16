import yfinance as yf
import pandas as pd

def fetch_ohlcv(ticker: str, period="7d", intervals=("1m","15m","1h")) -> dict:
    """Fetch multi-timeframe OHLCV data via yfinance"""
    out = {}
    for interval in intervals:
        try:
            df = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
            # ensure DataFrame has columns
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Handle multi-level columns from yfinance
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                out[interval] = df[['Open','High','Low','Close','Volume']].dropna()
            else:
                out[interval] = pd.DataFrame()
        except Exception as e:
            print(f"Error fetching {ticker} {interval}: {e}")
            out[interval] = pd.DataFrame()
    return out
