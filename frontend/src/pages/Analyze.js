import { useState } from 'react';
import axios from 'axios';
import { Search, TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Analyze = () => {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!ticker) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/analyze`, { 
        ticker: ticker.toUpperCase() 
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error analyzing ticker');
    } finally {
      setLoading(false);
    }
  };

  const getActionStyle = (action) => {
    switch(action) {
      case 'BUY': return { background: 'rgba(34, 197, 94, 0.2)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)' };
      case 'SELL': return { background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.3)' };
      default: return { background: 'rgba(251, 191, 36, 0.2)', color: '#fbbf24', border: '1px solid rgba(251, 191, 36, 0.3)' };
    }
  };

  return (
    <div data-testid="analyze-page" style={{
      padding: '40px',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{
          fontSize: '36px',
          fontWeight: '700',
          marginBottom: '8px'
        }}>
          Analyze Ticker
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>
          Get AI-powered analysis with LSTM predictions, candlestick patterns, and sentiment
        </p>
      </div>

      {/* Search Box */}
      <div className="glass" style={{
        padding: '32px',
        marginBottom: '32px'
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ 
            position: 'relative', 
            flex: 1,
            display: 'flex',
            alignItems: 'center'
          }}>
            <Search 
              size={20} 
              style={{ 
                position: 'absolute', 
                left: '16px', 
                color: '#94a3b8' 
              }} 
            />
            <input
              data-testid="ticker-input"
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
              placeholder="Enter ticker symbol (e.g., TSLA, AAPL)"
              style={{
                width: '100%',
                padding: '16px 16px 16px 48px',
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid rgba(148, 163, 184, 0.2)',
                borderRadius: '12px',
                color: '#e2e8f0',
                fontSize: '16px',
                outline: 'none',
                transition: 'all 0.3s ease'
              }}
            />
          </div>
          <button
            data-testid="analyze-button"
            onClick={handleAnalyze}
            disabled={loading || !ticker}
            className="btn-primary"
            style={{
              padding: '16px 32px',
              fontSize: '16px',
              opacity: loading || !ticker ? 0.5 : 1,
              cursor: loading || !ticker ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div data-testid="error-message" style={{
          padding: '20px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          color: '#f87171',
          marginBottom: '32px'
        }}>
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div data-testid="analysis-results">
          {/* Decision Card */}
          <div className="glass" style={{
            padding: '32px',
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '20px' }}>
              {result.ticker} Analysis
            </h3>

            <div style={{
              display: 'inline-block',
              padding: '20px 40px',
              borderRadius: '12px',
              marginBottom: '20px',
              ...getActionStyle(result.decision.action)
            }}>
              <div style={{ fontSize: '14px', marginBottom: '8px', opacity: 0.8 }}>Recommendation</div>
              <div data-testid="recommendation" style={{ fontSize: '48px', fontWeight: '700' }}>
                {result.decision.action}
              </div>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              gap: '40px',
              marginTop: '24px'
            }}>
              <div>
                <div style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '8px' }}>Confidence</div>
                <div data-testid="confidence" style={{ fontSize: '24px', fontWeight: '600' }}>
                  {(result.decision.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '8px' }}>Combined Signal</div>
                <div data-testid="combined-signal" style={{ fontSize: '24px', fontWeight: '600' }}>
                  {result.decision.combined.toFixed(4)}
                </div>
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            {/* Price Info */}
            <div className="glass" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <DollarSign size={24} style={{ color: '#06b6d4' }} />
                <h4 style={{ fontSize: '18px', fontWeight: '600' }}>Price Info</h4>
              </div>
              <div data-testid="current-price" style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>
                ${result.quant_result.last_price?.toFixed(2) || 'N/A'}
              </div>
              <div style={{ color: '#94a3b8', fontSize: '14px' }}>Current Price</div>
            </div>

            {/* Pattern */}
            <div className="glass" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <Activity size={24} style={{ color: '#fbbf24' }} />
                <h4 style={{ fontSize: '18px', fontWeight: '600' }}>Pattern</h4>
              </div>
              <div data-testid="pattern" style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
                {result.pattern || 'No Pattern'}
              </div>
              <div style={{ color: '#94a3b8', fontSize: '14px' }}>Candlestick Pattern</div>
            </div>

            {/* Sentiment */}
            <div className="glass" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                {result.sentiment_score > 0 ? 
                  <TrendingUp size={24} style={{ color: '#4ade80' }} /> :
                  <TrendingDown size={24} style={{ color: '#f87171' }} />
                }
                <h4 style={{ fontSize: '18px', fontWeight: '600' }}>Sentiment</h4>
              </div>
              <div 
                data-testid="sentiment-score"
                style={{ 
                  fontSize: '32px', 
                  fontWeight: '700', 
                  marginBottom: '8px',
                  color: result.sentiment_score > 0 ? '#4ade80' : '#f87171'
                }}
              >
                {result.sentiment_score > 0 ? '+' : ''}{result.sentiment_score.toFixed(3)}
              </div>
              <div style={{ color: '#94a3b8', fontSize: '14px' }}>Market Sentiment</div>
            </div>
          </div>

          {/* Forecasts */}
          <div className="glass" style={{ padding: '24px', marginTop: '24px' }}>
            <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px' }}>Price Forecasts</h4>
            
            <div data-testid="forecasts" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px'
            }}>
              {Object.entries(result.quant_result.tf).map(([tf, data]) => (
                <div key={tf} style={{
                  padding: '16px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px solid rgba(148, 163, 184, 0.1)'
                }}>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '12px' }}>{tf.toUpperCase()}</div>
                  <div style={{ marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>ARIMA: </span>
                    <span style={{ fontSize: '16px', fontWeight: '600' }}>
                      {data.arima_pred ? `$${data.arima_pred.toFixed(2)}` : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>LSTM: </span>
                    <span style={{ fontSize: '16px', fontWeight: '600' }}>
                      {data.lstm_pred ? `$${data.lstm_pred.toFixed(2)}` : 'N/A'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analyze;