
import React, { useEffect } from 'react';
import './LandingPage.css';
import { Link, useNavigate } from 'react-router-dom';
import { useColorScheme, IconButton } from '@mui/joy';
import { Moon, Sun } from 'lucide-react';

function ColorSchemeToggle() {
  const { mode, setMode } = useColorScheme();
  return (
    <IconButton
      onClick={() => setMode(mode === 'light' ? 'dark' : 'light')}
      variant="outlined"
      size="sm"
      sx={{ borderRadius: 'xl', ml: 2 }}
    >
      {mode === 'light' ? <Moon /> : <Sun />}
    </IconButton>
  );
}


export default function LandingPage() {
  const navigate = useNavigate();
  const { mode, systemMode } = useColorScheme();
  const currentMode = mode === 'system' ? systemMode : mode;
  const logoSrc = currentMode === 'dark' ? '/logo_dark.png' : '/logo_light.png';

  useEffect(() => {
    const script = document.createElement('script');
    script.src = '/legacy_script.js';
    script.async = true;
    document.body.appendChild(script);
    
    // Add event listeners to Launch Platform buttons since they are deeply nested
    const timer = setTimeout(() => {
      const buttons = document.querySelectorAll('.nav-cta');
      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          navigate('/login');
        });
      });
    }, 500);

    return () => {
      clearTimeout(timer);
      if (document.body.contains(script)) {
         document.body.removeChild(script);
      }
    };
  }, [navigate]);

  return (
    <div className="landing-page-wrapper">
      
    {/* Navigation */}
    <nav className="navbar">
        <div className="nav-container">
            <div className="nav-brand" style={{ gap: '10px' }}>
                <img src={logoSrc} alt="Nova Trading Logo" style={{ height: '28px', width: 'auto' }} />
                <span className="brand-text">Nova<span className="brand-accent">Trading</span></span>
            </div>
            <div className="nav-menu">
                <a href="#overview" className="nav-link">
                    <span className="nav-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="currentColor"/>
                        </svg>
                    </span>
                    Platform Overview
                </a>
                <a href="#infrastructure" className="nav-link">
                    <span className="nav-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2l3.09 6.26L22 9l-5 4.87 1.18 6.88L12 17.77l-6.18 2.98L7 14.87 2 9l6.91-1.74L12 2z" fill="currentColor"/>
                        </svg>
                    </span>
                    Trading Engine
                </a>
                <a href="#portfolios" className="nav-link">
                    <span className="nav-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" fill="currentColor"/>
                        </svg>
                    </span>
                    Asset Management
                </a>
                <a href="#technology" className="nav-link">
                    <span className="nav-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                        </svg>
                    </span>
                    Cloud Architecture
                </a>
                <a href="#performance" className="nav-link">
                    <span className="nav-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor"/>
                        </svg>
                    </span>
                    Analytics
                </a>
                <a href="docs/" className="nav-link">
                    <span className="nav-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2-7h-3V2h-2v2H8V2H6v2H3c-1.1 0-1.99.9-1.99 2L1 20c0 1.1.89 2 2 2h18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H3V9h18v11z" fill="currentColor"/>
                        </svg>
                    </span>
                    Capital Timeline
                </a>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center' }}>
                <button className="nav-cta">
                    <span className="cta-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42A6.92 6.92 0 0 1 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-1.99.85-3.77 2.17-5.41L6.17 5.17A8.932 8.932 0 0 0 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z" fill="currentColor"/>
                        </svg>
                    </span>
                    Launch Platform
                </button>
                <ColorSchemeToggle />
            </div>

        </div>
    </nav>

    {/* Hero Section */}
    <section className="hero">
        <div className="hero-container">
            <div className="hero-content">
                <h1 className="hero-title">
                    Institutional-Grade
                    <span className="gradient-text">Trading Platform</span>
                </h1>
                <p className="hero-subtitle">
                    Sophisticated multi-asset algorithmic trading with ML/AI integration,
                    professional risk management, and comprehensive tax optimization for UK investors.
                </p>
                <div className="hero-stats">
                    <div className="stat-item">
                        <div className="stat-value">£76,872</div>
                        <div className="stat-label">Total Portfolio Value</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-value">10+</div>
                        <div className="stat-label">Investment Strategies</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-value">9/10</div>
                        <div className="stat-label">Sophistication Rating</div>
                    </div>
                </div>
                <div className="hero-buttons">
                    <button className="btn-primary">Explore Platform</button>
                    <button className="btn-secondary">View Documentation</button>
                </div>
            </div>
            <div className="hero-visual">
                <div className="trading-dashboard">
                    <div className="dashboard-header">
                        <div className="status-indicator active"></div>
                        <span>Live Trading • Active</span>
                    </div>
                    <div className="dashboard-metrics">
                        <div className="metric">
                            <span className="metric-label">P&L Today</span>
                            <span className="metric-value positive">+£1,247</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Active Positions</span>
                            <span className="metric-value">23</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Success Rate</span>
                            <span className="metric-value">78.4%</span>
                        </div>
                    </div>
                    <div className="chart-placeholder">
                        <div className="chart-line"></div>
                        <div className="chart-bars">
                            <div className="bar" style={{ height: "60%" }}></div>
                            <div className="bar" style={{ height: "80%" }}></div>
                            <div className="bar" style={{ height: "45%" }}></div>
                            <div className="bar" style={{ height: "90%" }}></div>
                            <div className="bar" style={{ height: "70%" }}></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    {/* Overview Section */}
    <section id="overview" className="overview">
        <div className="container">
            <h2 className="section-title">Platform Overview</h2>
            <div className="overview-grid">
                <div className="overview-card">
                    <div className="card-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="currentColor"/>
                        </svg>
                    </div>
                    <h3>Algorithmic Trading</h3>
                    <p>Multi-agent AI framework powered by local edge-compute LLMs (Qwen 2.5) and FinBERT for deterministic, JSON-enforced market analysis.</p>
                    <div className="card-stats">
                        <span>5-Minute Intraday • Edge AI Compute • JSON Schema Enforced</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-label">Success Rate</span>
                            <span className="metric-value">78.4%</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Avg Trade</span>
                            <span className="metric-value">£247</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Daily Volume</span>
                            <span className="metric-value">£12.5K</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Latency</span>
                            <span className="metric-value">&lt; 100ms</span>
                        </div>
                    </div>
                </div>
                <div className="overview-card">
                    <div className="card-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                            <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" fill="currentColor"/>
                        </svg>
                    </div>
                    <h3>Multi-Asset Portfolios</h3>
                    <p>Diversified investment strategies across crypto, energy, commodities, and equities with sophisticated risk-adjusted allocation models.</p>
                    <div className="card-stats">
                        <span>100+ Positions • 7 Asset Classes • Tax Optimized</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-label">Total AUM</span>
                            <span className="metric-value">£76.9K</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Active Positions</span>
                            <span className="metric-value">127</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Portfolio Beta</span>
                            <span className="metric-value">0.85</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Correlation</span>
                            <span className="metric-value">0.34</span>
                        </div>
                    </div>
                </div>
                <div className="overview-card">
                    <div className="card-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                            <path d="M13 7h-2v4H7v2h4v4h2v-4h4v-2h-4V7zm-1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="currentColor"/>
                        </svg>
                    </div>
                    <h3>Geopolitical Intelligence</h3>
                    <p>Real-time catalyst monitoring for energy markets, critical minerals, and geopolitical events driving asymmetric opportunities.</p>
                    <div className="card-stats">
                        <span>Real-time Alerts • Event-driven • 37-68% Target Returns</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-label">Active Catalysts</span>
                            <span className="metric-value">23</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">News Sources</span>
                            <span className="metric-value">47</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Alert Accuracy</span>
                            <span className="metric-value">91.2%</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Response Time</span>
                            <span className="metric-value">&lt; 30s</span>
                        </div>
                    </div>
                </div>
                <div className="overview-card">
                    <div className="card-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" fill="currentColor"/>
                        </svg>
                    </div>
                    <h3>Risk Management</h3>
                    <p>Professional-grade risk controls with correlation analysis, dynamic position sizing, and maximum 19% portfolio downside protection.</p>
                    <div className="card-stats">
                        <span>3.7:1 Risk/Reward • ATR Stops • Correlation Matrix</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-label">Max Drawdown</span>
                            <span className="metric-value">-19%</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">VaR (95%)</span>
                            <span className="metric-value">£1.2K</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Sharpe Ratio</span>
                            <span className="metric-value">2.14</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Risk Score</span>
                            <span className="metric-value">7/10</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    {/* Trading Infrastructure Dashboard */}
    <section id="infrastructure" className="trading-infrastructure">
        <div className="container">
            <h2 className="section-title">Trading Infrastructure Dashboard</h2>
            <div className="infrastructure-grid">
                {/* Market Analysis */}
                <div className="infrastructure-card">
                    <div className="card-header">
                        <div className="card-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h3>Market Analysis Engine</h3>
                    </div>
                    <div className="infrastructure-metrics">
                        <div className="metric-row">
                            <span>Real-time Data Feeds</span>
                            <span className="metric-value-sm">47 Sources</span>
                        </div>
                        <div className="metric-row">
                            <span>Technical Indicators</span>
                            <span className="metric-value-sm">23 Active</span>
                        </div>
                        <div className="metric-row">
                            <span>Market Sentiment</span>
                            <span className="metric-value-sm positive">Bullish 64%</span>
                        </div>
                        <div className="metric-row">
                            <span>Volatility Index</span>
                            <span className="metric-value-sm">18.4</span>
                        </div>
                    </div>
                </div>

                {/* Position Calculator */}
                <div className="infrastructure-card">
                    <div className="card-header">
                        <div className="card-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h3>Position Calculator</h3>
                    </div>
                    <div className="infrastructure-metrics">
                        <div className="metric-row">
                            <span>Max Position Size</span>
                            <span className="metric-value-sm">£2,500</span>
                        </div>
                        <div className="metric-row">
                            <span>Risk Per Trade</span>
                            <span className="metric-value-sm">2%</span>
                        </div>
                        <div className="metric-row">
                            <span>ATR Stop Loss</span>
                            <span className="metric-value-sm">1.5x ATR</span>
                        </div>
                        <div className="metric-row">
                            <span>Kelly Criterion</span>
                            <span className="metric-value-sm">0.25</span>
                        </div>
                    </div>
                </div>

                {/* News Influence Tracker */}
                <div className="infrastructure-card">
                    <div className="card-header">
                        <div className="card-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M12 2l3.09 6.26L22 9l-5 4.87 1.18 6.88L12 17.77l-6.18 2.98L7 14.87 2 10l6.91-1.74L12 2z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h3>News Influence Tracker</h3>
                    </div>
                    <div className="infrastructure-metrics">
                        <div className="metric-row">
                            <span>Active News Events</span>
                            <span className="metric-value-sm">12</span>
                        </div>
                        <div className="metric-row">
                            <span>Sentiment Score</span>
                            <span className="metric-value-sm positive">+0.73</span>
                        </div>
                        <div className="metric-row">
                            <span>Impact Probability</span>
                            <span className="metric-value-sm">87%</span>
                        </div>
                        <div className="metric-row">
                            <span>Response Time</span>
                            <span className="metric-value-sm">&lt; 15s</span>
                        </div>
                    </div>
                </div>

                {/* Tax Optimization */}
                <div className="infrastructure-card">
                    <div className="card-header">
                        <div className="card-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h3>Tax Optimization Engine</h3>
                    </div>
                    <div className="infrastructure-metrics">
                        <div className="metric-row">
                            <span>CGT Allowance Used</span>
                            <span className="metric-value-sm">£2,400 / £6,000</span>
                        </div>
                        <div className="metric-row">
                            <span>ISA Allowance Used</span>
                            <span className="metric-value-sm">£11,500 / £20,000</span>
                        </div>
                        <div className="metric-row">
                            <span>SIPP Contribution</span>
                            <span className="metric-value-sm">£20,372</span>
                        </div>
                        <div className="metric-row">
                            <span>Tax Efficiency</span>
                            <span className="metric-value-sm positive">94.2%</span>
                        </div>
                    </div>
                </div>

                {/* Risk Calculator */}
                <div className="infrastructure-card">
                    <div className="card-header">
                        <div className="card-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M12 2l3.09 6.26L22 9l-5 4.87 1.18 6.88L12 17.77l-6.18 2.98L7 14.87 2 10l6.91-1.74L12 2z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h3>Risk Calculator</h3>
                    </div>
                    <div className="infrastructure-metrics">
                        <div className="metric-row">
                            <span>Portfolio VaR</span>
                            <span className="metric-value-sm danger">£1,247</span>
                        </div>
                        <div className="metric-row">
                            <span>Beta to Market</span>
                            <span className="metric-value-sm">0.85</span>
                        </div>
                        <div className="metric-row">
                            <span>Correlation Risk</span>
                            <span className="metric-value-sm">0.34</span>
                        </div>
                        <div className="metric-row">
                            <span>Stress Test</span>
                            <span className="metric-value-sm positive">Pass</span>
                        </div>
                    </div>
                </div>

                {/* Performance Analytics */}
                <div className="infrastructure-card">
                    <div className="card-header">
                        <div className="card-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2.5 12h-15V2h15v21z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h3>Performance Analytics</h3>
                    </div>
                    <div className="infrastructure-metrics">
                        <div className="metric-row">
                            <span>YTD Return</span>
                            <span className="metric-value-sm positive">+24.7%</span>
                        </div>
                        <div className="metric-row">
                            <span>Sharpe Ratio</span>
                            <span className="metric-value-sm">2.14</span>
                        </div>
                        <div className="metric-row">
                            <span>Max Drawdown</span>
                            <span className="metric-value-sm danger">-8.3%</span>
                        </div>
                        <div className="metric-row">
                            <span>Win Rate</span>
                            <span className="metric-value-sm positive">78.4%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    {/* Architecture Section */}
    <section id="architecture" className="architecture">
        <div className="container">
            <h2 className="section-title">System Architecture: Edge to Cloud</h2>
            <div className="architecture-diagram">
                <div className="arch-layer">
                    <h3>Phase 1: Edge Compute</h3>
                    <div className="arch-components">
                        <div className="arch-component">RTX 3080Ti Hardware</div>
                        <div className="arch-component">Local Python Engine</div>
                        <div className="arch-component">Ollama Inference</div>
                        <div className="arch-component">High-Frequency Loops</div>
                    </div>
                </div>
                <div className="arch-layer">
                    <h3>AI Multi-Agent Core</h3>
                    <div className="arch-components">
                        <div className="arch-component">Qwen 2.5 Coder</div>
                        <div className="arch-component">FinBERT Sentiment</div>
                        <div className="arch-component">JSON Schema Enforcement</div>
                        <div className="arch-component">Deterministic Auditor</div>
                    </div>
                </div>
                <div className="arch-layer">
                    <h3>SaaS Frontend UI</h3>
                    <div className="arch-components">
                        <div className="arch-component">React SPA</div>
                        <div className="arch-component">Vite Build Engine</div>
                        <div className="arch-component">MUI Joy Components</div>
                        <div className="arch-component">Bento Grid Layout</div>
                    </div>
                </div>
                <div className="arch-layer">
                    <h3>Phase 2: Cloud SaaS</h3>
                    <div className="arch-components">
                        <div className="arch-component">Cloud LLM Migration</div>
                        <div className="arch-component">Global User Auth</div>
                        <div className="arch-component">Multi-Tenant Database</div>
                        <div className="arch-component">Enterprise Scale API</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    {/* Portfolios Section */}
        <section id="portfolios" className="portfolios">
        <div className="container">
            <h2 className="section-title">5-Book Unified Architecture</h2>
            <div className="portfolios-grid">
                
                {/* Book 1: ISA */}
                <div className="portfolio-card" data-portfolio="isa">
                    <div className="portfolio-header">
                        <div className="portfolio-title-group">
                            <h3>ISA Book</h3>
                            <span className="portfolio-nickname">"The Tax-Free Compounder"</span>
                        </div>
                    </div>
                    <div className="portfolio-value">£11,500</div>
                    <div className="portfolio-description">Tax-free UK equity & ETF strategies utilizing the £20,000 annual allowance.</div>
                    <div className="portfolio-allocation">
                        <div className="allocation-bar">
                            <div className="allocation-fill" style={{ width: "15%" }}></div>
                        </div>
                        <span>15% Total Allocation</span>
                    </div>
                    <div className="portfolio-metrics" style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px' }}>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Strategy</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>Equity / ETF</span>
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '4px'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Tax Status</span>
                            <span style={{color: 'var(--success)', fontFamily: 'monospace', fontWeight: 'bold'}}>Tax-Free</span>
                        </div>
                    </div>
                </div>

                {/* Book 2: SIPP */}
                <div className="portfolio-card" data-portfolio="sipp">
                    <div className="portfolio-header">
                        <div className="portfolio-title-group">
                            <h3>SIPP Book</h3>
                            <span className="portfolio-nickname">"The Pension Fortress"</span>
                        </div>
                    </div>
                    <div className="portfolio-value">£20,372</div>
                    <div className="portfolio-description">Pension-optimized balanced allocation for 25-year compounding.</div>
                    <div className="portfolio-allocation">
                        <div className="allocation-bar">
                            <div className="allocation-fill" style={{ width: "27%" }}></div>
                        </div>
                        <span>27% Total Allocation</span>
                    </div>
                    <div className="portfolio-metrics" style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px' }}>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Strategy</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>Balanced Growth</span>
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '4px'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Time Horizon</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>25 Years</span>
                        </div>
                    </div>
                </div>

                {/* Book 3: GIA */}
                <div className="portfolio-card" data-portfolio="gia">
                    <div className="portfolio-header">
                        <div className="portfolio-title-group">
                            <h3>GIA Book</h3>
                            <span className="portfolio-nickname">"The Agile Growth Engine"</span>
                        </div>
                    </div>
                    <div className="portfolio-value">£27,000</div>
                    <div className="portfolio-description">Aggressive US growth strategy optimized for UK CGT thresholds.</div>
                    <div className="portfolio-allocation">
                        <div className="allocation-bar">
                            <div className="allocation-fill" style={{ width: "35%" }}></div>
                        </div>
                        <span>35% Total Allocation</span>
                    </div>
                    <div className="portfolio-metrics" style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px' }}>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Strategy</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>US Tech & Small Cap</span>
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '4px'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Tax Opt</span>
                            <span style={{color: 'var(--warning)', fontFamily: 'monospace', fontWeight: 'bold'}}>CGT Managed</span>
                        </div>
                    </div>
                </div>

                {/* Book 4: Forex */}
                <div className="portfolio-card" data-portfolio="forex">
                    <div className="portfolio-header">
                        <div className="portfolio-title-group">
                            <h3>Forex Book</h3>
                            <span className="portfolio-nickname">"The Volatility Capture"</span>
                        </div>
                    </div>
                    <div className="portfolio-value">£10,000</div>
                    <div className="portfolio-description">High-frequency intraday currency pair trading (G10/Majors).</div>
                    <div className="portfolio-allocation">
                        <div className="allocation-bar">
                            <div className="allocation-fill" style={{ width: "13%" }}></div>
                        </div>
                        <span>13% Total Allocation</span>
                    </div>
                    <div className="portfolio-metrics" style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px' }}>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Pairs</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>EUR/USD, GBP/USD</span>
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '4px'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Execution</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>5-Min Loops</span>
                        </div>
                    </div>
                </div>

                {/* Book 5: Crypto */}
                <div className="portfolio-card" data-portfolio="crypto">
                    <div className="portfolio-header">
                        <div className="portfolio-title-group">
                            <h3>Crypto Book</h3>
                            <span className="portfolio-nickname">"The Digital Frontier"</span>
                        </div>
                    </div>
                    <div className="portfolio-value">£7,628</div>
                    <div className="portfolio-description">DeFi integration, yield farming protocols, and blockchain exposure.</div>
                    <div className="portfolio-allocation">
                        <div className="allocation-bar">
                            <div className="allocation-fill" style={{ width: "10%" }}></div>
                        </div>
                        <span>10% Total Allocation</span>
                    </div>
                    <div className="portfolio-metrics" style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px' }}>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Focus</span>
                            <span style={{fontFamily: 'monospace', fontWeight: 'bold'}}>Web3 Infrastructure</span>
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: '4px'}}>
                            <span style={{color: 'var(--text-tertiary)'}}>Risk Profile</span>
                            <span style={{color: 'var(--danger)', fontFamily: 'monospace', fontWeight: 'bold'}}>High / Speculative</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </section>

    {/* Technology Section */}
    <section id="technology" className="technology">
        <div className="container">
            <h2 className="section-title">Technology Stack</h2>
            <div className="tech-categories">
                <div className="tech-category">
                    <h3>Local AI Models</h3>
                    <div className="tech-items">
                        <div className="tech-item">qwen2.5-coder:7b</div>
                        <div className="tech-item">FinBERT NLP</div>
                        <div className="tech-item">Ollama Server</div>
                        <div className="tech-item">Strict JSON Schemas</div>
                    </div>
                </div>
                <div className="tech-category">
                    <h3>Frontend SaaS</h3>
                    <div className="tech-items">
                        <div className="tech-item">React 18</div>
                        <div className="tech-item">Vite Dev Server</div>
                        <div className="tech-item">MUI Joy UI</div>
                        <div className="tech-item">React Router DOM</div>
                    </div>
                </div>
                <div className="tech-category">
                    <h3>Local Compute</h3>
                    <div className="tech-items">
                        <div className="tech-item">NVIDIA RTX 3080Ti</div>
                        <div className="tech-item">Python 3.12 Engine</div>
                        <div className="tech-item">Multi-threaded Core</div>
                        <div className="tech-item">Zero-latency Edge Processing</div>
                    </div>
                </div>
                <div className="tech-category">
                    <h3>Future Cloud Tier</h3>
                    <div className="tech-items">
                        <div className="tech-item">Hosted Cloud LLMs</div>
                        <div className="tech-item">SaaS Authentication</div>
                        <div className="tech-item">Horizontal Scaling</div>
                        <div className="tech-item">Subscription API</div>
                    </div>
                </div>
                <div className="tech-category">
                    <h3>Monitoring & Operations</h3>
                    <div className="tech-items">
                        <div className="tech-item">Cloud Monitoring</div>
                        <div className="tech-item">Cloud Logging</div>
                        <div className="tech-item">Error Reporting</div>
                        <div className="tech-item">Cloud Trace</div>
                    </div>
                </div>
                <div className="tech-category">
                    <h3>Trading Platforms</h3>
                    <div className="tech-items">
                        <div className="tech-item">MetaTrader Integration</div>
                        <div className="tech-item">Alpaca API</div>
                        <div className="tech-item">OANDA Platform</div>
                        <div className="tech-item">Trading212 Connector</div>
                    </div>
                </div>
            </div>
            <div className="tech-highlights">
                <div className="highlight-item">
                    <div className="highlight-number">&lt; 50ms</div>
                    <div className="highlight-label">Cloud Run Latency</div>
                </div>
                <div className="highlight-item">
                    <div className="highlight-number">99.95%</div>
                    <div className="highlight-label">GCP Uptime SLA</div>
                </div>
                <div className="highlight-item">
                    <div className="highlight-number">Auto-Scale</div>
                    <div className="highlight-label">Serverless Compute</div>
                </div>
                <div className="highlight-item">
                    <div className="highlight-number">Global</div>
                    <div className="highlight-label">Multi-Region Deploy</div>
                </div>
                <div className="highlight-item">
                    <div className="highlight-number">IAM</div>
                    <div className="highlight-label">Zero-Trust Security</div>
                </div>
                <div className="highlight-item">
                    <div className="highlight-number">BigQuery</div>
                    <div className="highlight-label">Petabyte Analytics</div>
                </div>
            </div>
        </div>
    </section>

    {/* Performance Section */}
    <section id="performance" className="performance">
        <div className="container">
            <h2 className="section-title">Performance Targets</h2>
            <div className="performance-grid">
                <div className="performance-card">
                    <h3>Oil Spike Strategy</h3>
                    <div className="performance-target">37-68%</div>
                    <div className="performance-description">Target returns on geopolitical events</div>
                    <div className="performance-timeline">Q2-Q4 2026 catalyst window</div>
                </div>
                <div className="performance-card">
                    <h3>Long-term Compounding</h3>
                    <div className="performance-target">15-25%</div>
                    <div className="performance-description">Annual returns across portfolios</div>
                    <div className="performance-timeline">25-year investment horizon</div>
                </div>
                <div className="performance-card">
                    <h3>Risk-Adjusted Returns</h3>
                    <div className="performance-target">3.7:1</div>
                    <div className="performance-description">Reward-to-risk ratio target</div>
                    <div className="performance-timeline">All strategies combined</div>
                </div>
                <div className="performance-card">
                    <h3>Maximum Drawdown</h3>
                    <div className="performance-target">19%</div>
                    <div className="performance-description">Portfolio downside protection</div>
                    <div className="performance-timeline">Stress-tested scenarios</div>
                </div>
            </div>
        </div>
    </section>

    {/* Footer */}
    <footer className="footer">
        <div className="container">
            <div className="footer-content">
                <div className="footer-brand" style={{ gap: '10px' }}>
                    <img src={logoSrc} alt="Nova Trading Logo" style={{ height: '24px', width: 'auto' }} />
                    <span className="brand-text">Nova<span className="brand-accent">Trading</span></span>
                </div>
                <div className="footer-links">
                    <a href="#documentation">Documentation</a>
                    <a href="#api">API Access</a>
                    <a href="#compliance">Compliance</a>
                    <a href="#support">Support</a>
                </div>
            </div>
            <div className="footer-disclaimer">
                <p>⚠️ This platform is for educational and demonstration purposes only. All investments carry risk including total loss of capital. Past performance does not guarantee future results. Consult a qualified financial advisor before making investment decisions.</p>
            </div>
        </div>
    </footer>

    <script src="script.js"></script>

    </div>
  );
}
