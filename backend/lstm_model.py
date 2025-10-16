import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

def build_lstm(input_shape=(32,1), hidden=64, dropout=0.1):
    """Build LSTM model architecture"""
    model = Sequential()
    model.add(LSTM(hidden, input_shape=input_shape))
    model.add(Dropout(dropout))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

def create_windows(arr, window=32):
    """Create sliding windows for time series"""
    X, y = [], []
    for i in range(len(arr)-window):
        X.append(arr[i:i+window])
        y.append(arr[i+window])
    return np.array(X), np.array(y)

def train_lstm(close_series, model_path, window=32, epochs=50, batch_size=64):
    """Train LSTM model on close price series"""
    arr = close_series.astype(float).dropna().values.reshape(-1,1)
    scaler = MinMaxScaler()
    arr_s = scaler.fit_transform(arr).flatten()
    
    X, y = create_windows(arr_s, window)
    if X.size == 0:
        raise ValueError("Not enough data to train")
    
    X = X.reshape((X.shape[0], X.shape[1], 1))
    model = build_lstm((window,1))
    
    es = EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True)
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1, callbacks=[es], verbose=1)
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    np.save(model_path + ".scaler_mean.npy", scaler.mean_)
    np.save(model_path + ".scaler_scale.npy", scaler.scale_)
    
    return model_path

def predict_lstm(model_path, recent_closes, window=32, steps=1):
    """Make predictions using trained LSTM model"""
    if not os.path.exists(model_path):
        return []
    
    try:
        mean = np.load(model_path + ".scaler_mean.npy")
        scale = np.load(model_path + ".scaler_scale.npy")
        scaler = MinMaxScaler()
        scaler.mean_ = mean
        scaler.scale_ = scale
        
        model = load_model(model_path)
        arr = np.array(recent_closes[-window:]).reshape(-1,1)
        arr_s = scaler.transform(arr).flatten()
        
        x = arr_s.reshape((1, window, 1))
        preds = []
        x_curr = x.copy()
        
        for _ in range(steps):
            p = model.predict(x_curr, verbose=0)[0,0]
            preds.append(p)
            x_roll = np.roll(x_curr.flatten(), -1)
            x_roll[-1] = p
            x_curr = x_roll.reshape((1,window,1))
        
        preds = np.array(preds).reshape(-1,1)
        preds_ori = scaler.inverse_transform(preds).flatten().tolist()
        
        return preds_ori
    except Exception as e:
        print(f"LSTM prediction error: {e}")
        return []
