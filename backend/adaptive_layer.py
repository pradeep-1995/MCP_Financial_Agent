import numpy as np
from perf_db import get_model_stats

class AdaptiveLayer:
    """Adaptive MCP layer for self-learning and weight adjustment"""
    
    def __init__(self):
        # Base weights for ensemble
        self.base = {"indicators": 0.35, "numeric": 0.45, "sentiment": 0.2}

    def compute_model_weights(self, ticker, timeframe):
        """Compute adaptive weights based on model performance"""
        stats = get_model_stats(ticker, timeframe)
        
        if not stats:
            return {"arima": 0.5, "lstm": 0.5}
        
        inv = []
        models = []
        
        for s in stats:
            mae = s["mae"] if s["mae"] and s["mae"]>0 else 1e-6
            inv.append(1.0/mae)
            models.append(s["model"])
        
        inv = np.array(inv)
        w = inv / inv.sum()
        
        return dict(zip(models, w.tolist()))

    def adjust_weights_for_ensemble(self, ticker, timeframe):
        """Adjust ensemble weights based on performance"""
        return self.compute_model_weights(ticker, timeframe)
