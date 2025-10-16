import pandas as pd
import numpy as np

def is_doji(row):
    """Check if candle is a doji (small body relative to range)"""
    body = abs(row['Close'] - row['Open'])
    rng = row['High'] - row['Low'] if (row['High'] - row['Low'])>0 else 1e-9
    return body / rng < 0.1

def bullish_engulfing(prev, curr):
    """Check for bullish engulfing pattern"""
    return (prev['Close'] < prev['Open']) and \
           (curr['Close'] > curr['Open']) and \
           (curr['Close'] > prev['Open']) and \
           (curr['Open'] < prev['Close'])

def bearish_engulfing(prev, curr):
    """Check for bearish engulfing pattern"""
    return (prev['Close'] > prev['Open']) and \
           (curr['Close'] < curr['Open']) and \
           (curr['Open'] > prev['Close']) and \
           (curr['Close'] < prev['Open'])

def hammer(row):
    """Check for hammer pattern"""
    body = abs(row['Close'] - row['Open'])
    lower_shadow = min(row['Open'], row['Close']) - row['Low']
    upper_shadow = row['High'] - max(row['Open'], row['Close'])
    return lower_shadow > 2 * body and upper_shadow < body

def shooting_star(row):
    """Check for shooting star pattern"""
    body = abs(row['Close'] - row['Open'])
    upper_shadow = row['High'] - max(row['Open'], row['Close'])
    lower_shadow = min(row['Open'], row['Close']) - row['Low']
    return upper_shadow > 2 * body and lower_shadow < body

def morning_star(prev2, prev1, curr):
    """Check for morning star pattern (3-candle pattern)"""
    return (prev2['Close'] < prev2['Open']) and \
           is_doji(prev1) and \
           (curr['Close'] > curr['Open']) and \
           (curr['Close'] > (prev2['Open'] + prev2['Close'])/2)

def detect_patterns(df: pd.DataFrame):
    """Check last 3 candles and return best matching pattern"""
    if df is None or df.shape[0] < 2:
        return None
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3] if df.shape[0] >= 3 else None

    if bullish_engulfing(prev, last):
        return "Bullish Engulfing"
    if bearish_engulfing(prev, last):
        return "Bearish Engulfing"
    if is_doji(last):
        return "Doji"
    if hammer(last):
        return "Hammer"
    if shooting_star(last):
        return "Shooting Star"
    if prev2 is not None and morning_star(prev2, prev, last):
        return "Morning Star"
    
    return None
