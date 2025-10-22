import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, TrendingDown, Database } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(fetchPredictions, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await axios.get(`${API}/predictions`);
      setPredictions(response.data.predictions || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      setLoading(false);
    }
  };

  const getStatusStyle = (resolved) => {
    return resolved ? 'status-buy' : 'status-hold';
  };

  return (
    <div data-testid="dashboard" style={{
      padding: '40px',
      maxWidth: '1400px',
      margin: '0 auto'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{
          fontSize: '36px',
          fontWeight: '700',
          marginBottom: '8px'
        }}>
          Performance Dashboard
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>
          Monitor MCP adaptive learning and prediction accuracy
        </p>
      </div>

      {/* Stats Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '40px'
      }}>
        <div className="glass glass-hover" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Activity size={24} style={{ color: '#06b6d4' }} />
            <h3 style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>Total Predictions</h3>
          </div>
          <p data-testid="total-predictions" style={{ fontSize: '32px', fontWeight: '700' }}>
            {predictions.length}
          </p>
        </div>

        <div className="glass glass-hover" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <TrendingUp size={24} style={{ color: '#4ade80' }} />
            <h3 style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>Resolved</h3>
          </div>
          <p data-testid="resolved-count" style={{ fontSize: '32px', fontWeight: '700', color: '#4ade80' }}>
            {predictions.filter(p => p.resolved).length}
          </p>
        </div>

        <div className="glass glass-hover" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <TrendingDown size={24} style={{ color: '#fbbf24' }} />
            <h3 style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>Pending</h3>
          </div>
          <p data-testid="pending-count" style={{ fontSize: '32px', fontWeight: '700', color: '#fbbf24' }}>
            {predictions.filter(p => !p.resolved).length}
          </p>
        </div>

        <div className="glass glass-hover" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Database size={24} style={{ color: '#3b82f6' }} />
            <h3 style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>Avg Error</h3>
          </div>
          <p data-testid="avg-error" style={{ fontSize: '32px', fontWeight: '700', color: '#3b82f6' }}>
            {(() => {
              const resolved = predictions.filter(p => p.resolved && p.error);
              if (resolved.length === 0) return '0.00';
              const avg = resolved.reduce((sum, p) => sum + p.error, 0) / resolved.length;
              return avg.toFixed(2);
            })()}
          </p>
        </div>
      </div>

      {/* Predictions Table */}
      <div className="glass" style={{ padding: '24px', overflow: 'hidden' }}>
        <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px' }}>
          Recent Predictions
        </h3>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="pulse" style={{ color: '#94a3b8' }}>Loading predictions...</div>
          </div>
        ) : predictions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
            No predictions yet. Try analyzing a ticker!
          </div>
        ) : (
          <div data-testid="predictions-table" style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.2)' }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8', fontWeight: '500' }}>Ticker</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8', fontWeight: '500' }}>Model</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8', fontWeight: '500' }}>Timeframe</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Predicted</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Actual</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8', fontWeight: '500' }}>Error</th>
                  <th style={{ padding: '12px', textAlign: 'center', color: '#94a3b8', fontWeight: '500' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred, idx) => (
                  <tr 
                    key={idx}
                    data-testid={`prediction-row-${idx}`}
                    style={{ 
                      borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
                      transition: 'background 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(148, 163, 184, 0.05)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '16px', fontWeight: '600' }}>{pred.ticker}</td>
                    <td style={{ padding: '16px', color: '#94a3b8' }}>{pred.model}</td>
                    <td style={{ padding: '16px', color: '#94a3b8' }}>{pred.timeframe}</td>
                    <td style={{ padding: '16px', textAlign: 'right' }}>${pred.predicted_price?.toFixed(2) || 'N/A'}</td>
                    <td style={{ padding: '16px', textAlign: 'right' }}>
                      {pred.actual_price ? `$${pred.actual_price.toFixed(2)}` : '-'}
                    </td>
                    <td style={{ padding: '16px', textAlign: 'right', color: pred.error ? '#f87171' : '#94a3b8' }}>
                      {pred.error ? `$${pred.error.toFixed(2)}` : '-'}
                    </td>
                    <td style={{ padding: '16px', textAlign: 'center' }}>
                      <span className={getStatusStyle(pred.resolved)}>
                        {pred.resolved ? 'Resolved' : 'Pending'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;