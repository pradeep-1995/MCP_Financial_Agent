def format_short_report(ticker, pattern, sentiment_score, sentiment_reasons, quant_result, decision):
    """Format a concise trading report"""
    last_price = quant_result.get("last_price")
    
    s = f"📊 *{ticker} Analysis*\n\n"
    
    if last_price:
        s += f"💰 Current Price: ${last_price:.2f}\n\n"
    
    if pattern:
        s += f"🕯️ Pattern Detected: {pattern}\n"
    else:
        s += f"🕯️ Pattern: No significant pattern\n"
    
    s += f"💬 Sentiment Score: {sentiment_score:.3f}\n"
    
    s += f"\n🔮 Forecasts:\n"
    for tf, v in quant_result.get("tf", {}).items():
        arima_str = f"${v.get('arima_pred'):.2f}" if v.get('arima_pred') else "N/A"
        lstm_str = f"${v.get('lstm_pred'):.2f}" if v.get('lstm_pred') else "N/A"
        s += f"  • {tf}: ARIMA={arima_str}, LSTM={lstm_str}\n"
    
    s += f"\n✅ Recommendation: *{decision['action']}*\n"
    s += f"📈 Confidence: {decision['confidence']*100:.1f}%\n"
    s += f"🎯 Combined Signal: {decision['combined']:.4f}\n\n"
    
    s += "⚠️ _Note: This is not financial advice. DYOR & validate liquidity._\n"
    
    return s

def format_detailed_report(ticker, pattern, sentiment_score, sentiment_reasons, quant_result, decision):
    """Format a detailed trading report"""
    s = format_short_report(ticker, pattern, sentiment_score, sentiment_reasons, quant_result, decision)
    
    s += "\n📰 News Sentiment Details:\n"
    for idx, (text, score) in enumerate(sentiment_reasons[:3], 1):
        s += f"{idx}. {text[:80]}... (Score: {score:.2f})\n"
    
    return s
