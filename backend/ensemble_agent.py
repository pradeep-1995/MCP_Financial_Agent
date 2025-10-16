from adaptive_layer import AdaptiveLayer
import numpy as np

class EnsembleAgent:
    """Ensemble agent that combines multiple signals with adaptive weights"""
    
    def __init__(self):
        self.adaptive = AdaptiveLayer()
        self.base = {"indicators": 0.35, "numeric": 0.45, "sentiment": 0.2}

    def combine(self, ticker, quant_result, sentiment_score):
        """Combine all signals to make a trading decision"""
        timeframe = "1h"  # Decision based on 1h by default
        
        # Compute numeric score from arima & lstm using adaptive weights
        model_weights = self.adaptive.compute_model_weights(ticker, timeframe)
        numeric_vals = []
        wts = []
        
        tf = quant_result.get("tf", {})
        t1 = tf.get("1h", {})
        
        if t1.get("arima_ret") is not None:
            numeric_vals.append(t1.get("arima_ret"))
            wts.append(model_weights.get("arima", 0.5))
        
        if t1.get("lstm_ret") is not None:
            numeric_vals.append(t1.get("lstm_ret"))
            wts.append(model_weights.get("lstm", 0.5))
        
        numeric_score = sum(v*w for v,w in zip(numeric_vals, wts))/sum(wts) if numeric_vals else 0.0

        # Indicator score based on arima trend
        indicator_score = 0.0
        if t1.get("arima_ret"):
            indicator_score = t1["arima_ret"]
        
        # Sentiment score already normalized to [-1, 1]
        s_score = sentiment_score

        # Combine using base weights
        combined = (self.base["indicators"]*indicator_score +
                    self.base["numeric"]*numeric_score +
                    self.base["sentiment"]*s_score)

        conf = min(1.0, max(0.0, abs(combined)))  # Confidence
        
        # Make decision
        if combined > 0.02 and conf > 0.3:
            action = "BUY"
        elif combined < -0.02 and conf > 0.3:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            "action": action, 
            "confidence": conf, 
            "combined": combined,
            "numeric_score": numeric_score,
            "indicator_score": indicator_score,
            "sentiment_score": s_score
        }
