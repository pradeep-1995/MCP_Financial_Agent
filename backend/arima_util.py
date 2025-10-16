from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

def arima_one_step_forecast(series, order=(2,1,2)):
    """Perform ARIMA forecast for one step ahead"""
    try:
        model = ARIMA(series.astype(float).dropna(), order=order)
        res = model.fit()
        fc = res.forecast(steps=1)
        return float(fc.iloc[0] if isinstance(fc, pd.Series) else fc[0])
    except Exception as e:
        print(f"ARIMA forecast error: {e}")
        return None
