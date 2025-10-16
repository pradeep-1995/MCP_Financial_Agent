from textblob import TextBlob
import google.generativeai as genai
from config import GEMINI_API_KEY
import yfinance as yf

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def fetch_news_headlines(ticker: str, limit=5):
    """Fetch recent news headlines for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:limit] if stock.news else []
        headlines = []
        for item in news:
            title = item.get('title', '')
            summary = item.get('summary', '')
            if title:
                headlines.append(f"{title}. {summary}" if summary else title)
        
        if not headlines:
            # Fallback stub
            headlines = [f"{ticker} shows market activity with recent trading patterns."]
        
        return headlines
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return [f"{ticker} market data available for analysis."]

def score_sentiment_textblob(texts):
    """Score sentiment using TextBlob"""
    if not texts:
        return 0.0, []
    
    scores = []
    reasons = []
    
    for t in texts:
        try:
            p = TextBlob(t).sentiment.polarity
            scores.append(p)
            reasons.append((t, p))
        except:
            continue
    
    agg = sum(scores)/len(scores) if scores else 0.0
    return agg, reasons

def score_sentiment_gemini(texts, ticker):
    """Score sentiment using Gemini AI"""
    if not GEMINI_API_KEY or not texts:
        return score_sentiment_textblob(texts)
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        combined_text = "\n".join(texts[:5])
        
        prompt = f"""Analyze the sentiment of these news headlines about {ticker}.
Provide a sentiment score between -1.0 (very negative) and 1.0 (very positive).
Return only the numerical score.

Headlines:
{combined_text}

Sentiment Score:"""
        
        response = model.generate_content(prompt)
        score_text = response.text.strip()
        
        # Extract number from response
        import re
        match = re.search(r'-?\d+\.?\d*', score_text)
        if match:
            score = float(match.group())
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
            return score, [("Gemini AI Analysis", score)]
    except Exception as e:
        print(f"Gemini sentiment error: {e}")
    
    return score_sentiment_textblob(texts)

def score_sentiment(texts, ticker=""):
    """Main sentiment scoring function"""
    if GEMINI_API_KEY:
        return score_sentiment_gemini(texts, ticker)
    else:
        return score_sentiment_textblob(texts)
