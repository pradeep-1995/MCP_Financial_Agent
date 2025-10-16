import sqlite3
from datetime import datetime
import os
from config import PERF_DB_PATH

def init_db():
    """Initialize MCP performance database"""
    os.makedirs(os.path.dirname(PERF_DB_PATH) if os.path.dirname(PERF_DB_PATH) else '.', exist_ok=True)
    con = sqlite3.connect(PERF_DB_PATH)
    cur = con.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        timeframe TEXT,
        model TEXT,
        predicted_at TEXT,
        horizon_minutes INTEGER,
        predicted_price REAL,
        actual_price REAL,
        error REAL,
        resolved INTEGER DEFAULT 0
    )""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        timeframe TEXT,
        model TEXT,
        mean_abs_error REAL,
        count INTEGER,
        last_updated TEXT
    )""")
    
    con.commit()
    con.close()

def store_prediction(ticker, timeframe, model, predicted_at, horizon_minutes, predicted_price):
    """Store a prediction in the database"""
    con = sqlite3.connect(PERF_DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT INTO predictions (ticker, timeframe, model, predicted_at, horizon_minutes, predicted_price)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (ticker, timeframe, model, predicted_at, horizon_minutes, predicted_price))
    con.commit()
    con.close()

def resolve_prediction(pred_id, actual_price):
    """Resolve a prediction by comparing with actual price"""
    con = sqlite3.connect(PERF_DB_PATH)
    cur = con.cursor()
    
    cur.execute("SELECT predicted_price, ticker, timeframe, model FROM predictions WHERE id=?", (pred_id,))
    row = cur.fetchone()
    if not row:
        con.close()
        return
    
    predicted_price, ticker, timeframe, model = row
    error = abs(actual_price - predicted_price)
    
    cur.execute("UPDATE predictions SET actual_price=?, error=?, resolved=1 WHERE id=?", 
                (actual_price, error, pred_id))
    
    cur.execute("SELECT mean_abs_error, count FROM model_stats WHERE ticker=? AND timeframe=? AND model=?", 
                (ticker, timeframe, model))
    r = cur.fetchone()
    
    if r:
        mean_abs_error, count = r
        new_count = count + 1
        new_mean = (mean_abs_error * count + error)/new_count
        cur.execute("UPDATE model_stats SET mean_abs_error=?, count=?, last_updated=? WHERE ticker=? AND timeframe=? AND model=?",
                    (new_mean, new_count, datetime.utcnow().isoformat(), ticker, timeframe, model))
    else:
        cur.execute("INSERT INTO model_stats (ticker, timeframe, model, mean_abs_error, count, last_updated) VALUES (?,?,?,?,?,?)",
                    (ticker, timeframe, model, error, 1, datetime.utcnow().isoformat()))
    
    con.commit()
    con.close()

def get_model_stats(ticker, timeframe):
    """Get model statistics for a ticker and timeframe"""
    con = sqlite3.connect(PERF_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT model, mean_abs_error, count FROM model_stats WHERE ticker=? AND timeframe=?", 
                (ticker, timeframe))
    rows = cur.fetchall()
    con.close()
    return [{"model": r[0], "mae": r[1], "count": r[2]} for r in rows]

def get_unresolved_predictions():
    """Get all unresolved predictions"""
    con = sqlite3.connect(PERF_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id, ticker, timeframe, predicted_at, horizon_minutes FROM predictions WHERE resolved=0")
    rows = cur.fetchall()
    con.close()
    return rows

def get_recent_predictions(limit=20):
    """Get recent predictions for dashboard"""
    con = sqlite3.connect(PERF_DB_PATH)
    cur = con.cursor()
    cur.execute("""
    SELECT ticker, timeframe, model, predicted_at, predicted_price, actual_price, error, resolved
    FROM predictions 
    ORDER BY id DESC 
    LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    con.close()
    return rows
