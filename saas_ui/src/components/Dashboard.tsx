import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, ShieldCheck, Zap, TrendingUp, DollarSign } from 'lucide-react';
import './Dashboard.css';

const mockData = [
  { name: 'Jan', value: 100000 },
  { name: 'Feb', value: 105000 },
  { name: 'Mar', value: 102000 },
  { name: 'Apr', value: 110000 },
  { name: 'May', value: 115000 },
  { name: 'Jun', value: 122500 },
];

const mockTrades = [
  { sym: 'AAPL', type: 'BUY', size: 15, price: 185.2, time: '10:45 AM', mlProb: '92.5%', trailingStop: '2.0 ATR' },
  { sym: 'NVDA', type: 'SELL', size: 10, price: 950.1, time: '11:15 AM', mlProb: '45.1%', trailingStop: '1.5 ATR' },
  { sym: 'TSLA', type: 'BUY', size: 50, price: 175.4, time: '1:30 PM', mlProb: '88.3%', trailingStop: '2.0 ATR' },
  { sym: 'GBPUSD=X', type: 'BUY', size: 10000, price: 1.25, time: '2:45 PM', mlProb: '95.8%', trailingStop: '15 pips' },
];

export default function Dashboard() {
  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar neu-flat">
        <div className="logo">
          <h2>NOVA <span className="text-primary">SAAS</span></h2>
        </div>
        <nav className="nav-links">
          <button className="btn-neu active"><Activity size={18}/> Overview</button>
          <button className="btn-neu"><Zap size={18}/> Engine Config</button>
          <button className="btn-neu"><ShieldCheck size={18}/> Guardrails</button>
          <button className="btn-neu"><DollarSign size={18}/> Tax Matrix</button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-bar neu-flat">
          <div className="status">
            <span className="dot pulse"></span>
            <span className="mono text-success">ENGINE ACTIVE</span>
          </div>
          <div className="user-profile">
            <div className="avatar neu-pressed">PH</div>
          </div>
        </header>

        <div className="grid-dashboard">
          
          {/* Portfolio Value */}
          <div className="card neu-flat col-span-2">
            <h3 className="text-muted">Total Portfolio Value</h3>
            <h1 className="mono">£122,500.00</h1>
            <p className="text-success mono">+£7,500 (6.5%)</p>
            <div className="chart-container" style={{ height: 200, marginTop: '20px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockData}>
                  <XAxis dataKey="name" stroke="#8b929a" tick={{fill: '#8b929a'}}/>
                  <Tooltip contentStyle={{backgroundColor: '#15171a', border: 'none', borderRadius: '8px', color: '#e7e5e4'}}/>
                  <Line type="monotone" dataKey="value" stroke="#ff6b35" strokeWidth={3} dot={{r: 4, fill: '#ff6b35', strokeWidth: 2, stroke: '#22252a'}} activeDot={{r: 6}}/>
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* The 50/50 Module */}
          <div className="card neu-flat">
            <h3 className="text-muted">The 50/50 System</h3>
            <div className="fifty-fifty-visual mt-md">
              <div className="split neu-pressed">
                <div className="bar compound" style={{width: '50%'}}></div>
                <div className="bar bank" style={{width: '50%'}}></div>
              </div>
              <div className="labels mt-sm flex-between mono text-sm">
                <span className="text-primary">£3,750 Cmpd</span>
                <span className="text-success">£3,750 Banked</span>
              </div>
            </div>
          </div>

          {/* Tax Optimizer */}
          <div className="card neu-flat">
            <h3 className="text-muted">UK CGT Allowance (GIA)</h3>
            <h2 className="mono mt-sm">£3,000 / £3,000</h2>
            <div className="progress neu-pressed mt-md">
              <div className="progress-fill" style={{width: '100%', background: 'var(--success)'}}></div>
            </div>
            <p className="mono text-muted text-sm mt-sm">Allowance fully utilized. Re-routing engine to ISA wrapper.</p>
          </div>

          {/* ML Engine Status */}
          <div className="card neu-flat">
            <h3 className="text-muted">AI Quant Engine</h3>
            <div className="flex-between mt-sm">
              <span className="mono">Model:</span>
              <span className="mono text-primary">Random Forest</span>
            </div>
            <div className="flex-between mt-sm">
              <span className="mono">Features:</span>
              <span className="mono text-primary">30+ Indicators</span>
            </div>
            <div className="flex-between mt-sm">
              <span className="mono">Horizon:</span>
              <span className="mono text-primary">5-Day Breakout</span>
            </div>
            <div className="flex-between mt-sm">
              <span className="mono">Global Prob:</span>
              <span className="mono text-success">85.4%</span>
            </div>
          </div>

          {/* Live Feed */}
          <div className="card neu-flat col-span-full">
            <h3 className="text-muted mb-md">Live Inference Feed</h3>
            <div className="feed-list">
              {mockTrades.map((t, i) => (
                <div key={i} className="feed-item neu-pressed">
                  <div className="feed-icon">
                    <TrendingUp size={16} className={t.type === 'BUY' ? 'text-primary' : 'text-danger'}/>
                  </div>
                  <div className="feed-details">
                    <span className="mono font-bold">{t.type} {t.sym}</span>
                    <span className="text-muted ml-md">{t.size} units @ £{t.price}</span>
                  </div>
                  <div className="feed-meta mono text-sm ml-auto mr-md" style={{ display: 'flex', gap: '15px' }}>
                    <span className="text-primary">ML: {t.mlProb}</span>
                    <span className="text-success">T-Stop: {t.trailingStop}</span>
                  </div>
                  <div className="feed-time text-muted mono text-sm">
                    {t.time}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
