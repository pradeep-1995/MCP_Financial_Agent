import { Link, useLocation } from 'react-router-dom';
import { TrendingUp, BarChart3 } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  return (
    <nav data-testid="navigation" style={{
      padding: '20px 40px',
      background: 'rgba(15, 23, 42, 0.8)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          textDecoration: 'none',
          color: '#e2e8f0'
        }}>
          <TrendingUp size={32} style={{ color: '#06b6d4' }} />
          <h1 data-testid="app-title" style={{
            fontSize: '24px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Financial AI Agent
          </h1>
        </Link>

        <div style={{ display: 'flex', gap: '20px' }}>
          <Link
            data-testid="nav-dashboard"
            to="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: '10px',
              textDecoration: 'none',
              color: '#e2e8f0',
              background: location.pathname === '/' 
                ? 'rgba(6, 182, 212, 0.1)' 
                : 'transparent',
              border: location.pathname === '/' 
                ? '1px solid rgba(6, 182, 212, 0.3)' 
                : '1px solid transparent',
              transition: 'all 0.3s ease'
            }}
          >
            <BarChart3 size={18} />
            Dashboard
          </Link>

          <Link
            data-testid="nav-analyze"
            to="/analyze"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: '10px',
              textDecoration: 'none',
              color: '#e2e8f0',
              background: location.pathname === '/analyze' 
                ? 'rgba(6, 182, 212, 0.1)' 
                : 'transparent',
              border: location.pathname === '/analyze' 
                ? '1px solid rgba(6, 182, 212, 0.3)' 
                : '1px solid transparent',
              transition: 'all 0.3s ease'
            }}
          >
            <TrendingUp size={18} />
            Analyze
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;