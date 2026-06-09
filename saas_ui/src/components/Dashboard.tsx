import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { 
  Activity, 
  ShieldCheck, 
  Zap, 
  TrendingUp, 
  DollarSign, 
  Globe, 
  Info, 
  CheckCircle, 
  AlertTriangle,
  Sliders,
  Plus,
  Play
} from 'lucide-react';
import './Dashboard.css';

// --- Mock Data ---
const mockOverviewData = [
  { name: 'Jan', value: 76872 },
  { name: 'Feb', value: 85200 },
  { name: 'Mar', value: 92400 },
  { name: 'Apr', value: 99100 },
  { name: 'May', value: 112000 },
  { name: 'Jun', value: 122500 },
];

const mockTradesList = [
  { id: 1, date: '2026-06-09', book_id: 'ibkr_gia_equity', symbol: 'NVDA', side: 'BUY', qty: 15, price: 950.1, status: 'executed', isFxp: false },
  { id: 2, date: '2026-06-09', book_id: 'ibkr_sipp_equity', symbol: 'VWRL', side: 'BUY', qty: 50, price: 112.5, status: 'executed', isFxp: false },
  { id: 3, date: '2026-06-08', book_id: 'ibkr_isa_equity', symbol: 'SPY', side: 'BUY', qty: 20, price: 505.2, status: 'executed', isFxp: false },
  { id: 4, date: '2026-06-07', book_id: 'ibkr_gia_equity', symbol: 'FORD', side: 'SELL', qty: 120, price: 12.3, status: 'executed', isFxp: false },
  { id: 5, date: '2026-06-06', book_id: 'ibkr_fx_margin', symbol: 'GBPUSD=X', side: 'BUY', qty: 10000, price: 1.25, status: 'executed', isFxp: true },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'engine' | 'guardrails' | 'tax' | 'gpu' | 'forex'>('overview');
  
  // --- Global Toast State ---
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'info' | 'warning' } | null>(null);
  const triggerToast = (message: string, type: 'success' | 'info' | 'warning' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // --- Slide-to-Authorize Modal State ---
  const [authModal, setAuthModal] = useState<{
    isOpen: boolean;
    title: string;
    description: string;
    onAuthorize: () => void;
    diff?: { before: string; after: string }[];
  }>({
    isOpen: false,
    title: '',
    description: '',
    onAuthorize: () => {},
  });
  const [authSliderVal, setAuthSliderVal] = useState<number>(0);

  const closeAuthModal = () => {
    setAuthModal(prev => ({ ...prev, isOpen: false }));
    setAuthSliderVal(0);
  };

  const handleAuthSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setAuthSliderVal(val);
    if (val >= 100) {
      // Authorized!
      authModal.onAuthorize();
      closeAuthModal();
    }
  };

  // ==========================================
  // STATE 1: Overview Tab
  // ==========================================
  const [compoundPct, setCompoundPct] = useState<number>(50);
  const totalProfitYtd = 7500;
  const compoundedAmount = (totalProfitYtd * (compoundPct / 100)).toFixed(2);
  const bankedAmount = (totalProfitYtd * ((100 - compoundPct) / 100)).toFixed(2);

  // ==========================================
  // STATE 2: Engine Config Tab
  // ==========================================
  const [gateMin, setGateMin] = useState<number>(40);
  const [execThreshold, setExecThreshold] = useState<number>(75);
  const [topN, setTopN] = useState<number>(10);
  const [aggressiveLiq, setAggressiveLiq] = useState<boolean>(false);
  const [universe, setUniverse] = useState<string[]>(['SPY', 'NVDA', 'VWRL', 'FORD']);
  const [newSymbol, setNewSymbol] = useState<string>('');

  const handleAddSymbol = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanSym = newSymbol.trim().toUpperCase();
    if (cleanSym && !universe.includes(cleanSym)) {
      setUniverse([...universe, cleanSym]);
      setNewSymbol('');
      triggerToast(`Added ${cleanSym} to the scan universe`, 'info');
    }
  };

  const handleRemoveSymbol = (sym: string) => {
    setUniverse(universe.filter(s => s !== sym));
    triggerToast(`Removed ${sym} from scan universe`, 'info');
  };

  const handleSaveEngineConfig = () => {
    setAuthModal({
      isOpen: true,
      title: 'Authorize config.yaml Update',
      description: 'You are modifying the operational core variables of the trading cycle.',
      diff: [
        { before: 'gate_min: 40.0', after: `gate_min: ${gateMin}.0` },
        { before: 'exec_threshold: 75.0', after: `exec_threshold: ${execThreshold}.0` },
        { before: 'top_n: 10', after: `top_n: ${topN}` },
        { before: 'aggressive_liquidation: false', after: `aggressive_liquidation: ${aggressiveLiq}` },
      ],
      onAuthorize: () => {
        triggerToast('Engine Configuration (config.yaml) updated successfully!', 'success');
      }
    });
  };

  // ==========================================
  // STATE 3: Guardrails Tab
  // ==========================================
  const [maxDrawdown, setMaxDrawdown] = useState<number>(15.0);
  const [dailyLossCap, setDailyLossCap] = useState<number>(3.0);
  const [maxPositions, setMaxPositions] = useState<number>(10);
  const [sizerPolicy, setSizerPolicy] = useState<'atr' | 'nav'>('atr');
  const [riskCapitalPct, setRiskCapitalPct] = useState<number>(2.0);
  const [stopAtrMult, setStopAtrMult] = useState<number>(2.0);
  const [takeAtrMult, setTakeAtrMult] = useState<number>(4.0);
  const [maxCorrelation, setMaxCorrelation] = useState<number>(0.8);

  const handleSaveGuardrails = () => {
    setAuthModal({
      isOpen: true,
      title: 'Confirm Risk Guardrails Update',
      description: 'Modifying capital-at-risk limits and risk multipliers directly affects trade sizes and drawdown thresholds.',
      diff: [
        { before: 'max_drawdown_pct: 15.0', after: `max_drawdown_pct: ${maxDrawdown}.0` },
        { before: 'daily_loss_cap_pct: 3.0', after: `daily_loss_cap_pct: ${dailyLossCap}.0` },
        { before: 'sizing_type: "nav_pct"', after: `sizing_type: "${sizerPolicy}_sizing"` },
        { before: 'max_correlation: 0.8', after: `max_correlation: ${maxCorrelation}` }
      ],
      onAuthorize: () => {
        triggerToast('Risk Guardrails (portfolio.yaml) updated successfully!', 'success');
      }
    });
  };

  // ==========================================
  // STATE 4: Tax Matrix Tab
  // ==========================================
  const [selectedBook, setSelectedBook] = useState<'gia' | 'isa' | 'sipp'>('gia');
  const [isHigherRateTaxpayer, setIsHigherRateTaxpayer] = useState<boolean>(false);
  const currentGiaGains = 2850.00;
  const estimatedTax = isHigherRateTaxpayer ? currentGiaGains * 0.20 : currentGiaGains * 0.10;

  // ==========================================
  // STATE 5: GPU Optimizer Tab
  // ==========================================
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [mcPaths, setMcPaths] = useState<{ name: string; min: number; avg: number; max: number }[]>(
    Array.from({ length: 50 }, (_, i) => ({
      name: `Day ${i + 1}`,
      min: 100000 - i * 300,
      avg: 100000 + i * 200,
      max: 100000 + i * 800,
    }))
  );

  const triggerMonteCarloSimulation = () => {
    setIsSimulating(true);
    triggerToast('Starting GPU Monte Carlo bootstrap simulator...', 'info');
    setTimeout(() => {
      const seed = Math.random();
      const newPaths = Array.from({ length: 50 }, (_, i) => ({
        name: `Day ${i + 1}`,
        min: Math.round(100000 - i * (200 + seed * 300)),
        avg: Math.round(100000 + i * (100 + seed * 250)),
        max: Math.round(100000 + i * (600 + seed * 500)),
      }));
      setMcPaths(newPaths);
      setIsSimulating(false);
      triggerToast('Simulation completed. 10,000 paths shuffled.', 'success');
    }, 2000);
  };

  const handleSyncProposedParams = () => {
    setAuthModal({
      isOpen: true,
      title: 'Sync Proposed WFV Parameters',
      description: 'Apply Walk-Forward grid solutions directly to active configurations. This overwrites config.yaml settings.',
      diff: [
        { before: `gate_min: ${gateMin}.0`, after: 'gate_min: 45.0' },
        { before: `exec_threshold: ${execThreshold}.0`, after: 'exec_threshold: 80.0' }
      ],
      onAuthorize: () => {
        setGateMin(45);
        setExecThreshold(80);
        triggerToast('Synchronized optimal parameters and rebooted daemon!', 'success');
      }
    });
  };

  // ==========================================
  // STATE 6: Forex Hub Tab
  // ==========================================
  const [activeSubscriptionTier, setActiveSubscriptionTier] = useState<'basic' | 'pro' | 'enterprise'>('pro');
  const [forexEnabled, setForexEnabled] = useState<boolean>(true);

  return (
    <div className="dashboard-layout">
      {/* --- Sidebar Navigation --- */}
      <aside className="sidebar">
        <div className="logo">
          <h2>NOVA <span className="text-primary">SAAS</span></h2>
        </div>
        <nav className="nav-links">
          <button 
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            <Activity size={18}/> Overview
          </button>
          <button 
            className={activeTab === 'engine' ? 'active' : ''}
            onClick={() => setActiveTab('engine')}
          >
            <Zap size={18}/> Engine Config
          </button>
          <button 
            className={activeTab === 'guardrails' ? 'active' : ''}
            onClick={() => setActiveTab('guardrails')}
          >
            <ShieldCheck size={18}/> Guardrails
          </button>
          <button 
            className={activeTab === 'tax' ? 'active' : ''}
            onClick={() => setActiveTab('tax')}
          >
            <DollarSign size={18}/> Tax Matrix
          </button>
          <button 
            className={activeTab === 'gpu' ? 'active' : ''}
            onClick={() => setActiveTab('gpu')}
          >
            <Sliders size={18}/> GPU Optimizer
          </button>
          <button 
            className={activeTab === 'forex' ? 'active' : ''}
            onClick={() => setActiveTab('forex')}
          >
            <Globe size={18}/> Forex Bot Hub
          </button>
        </nav>
        <div className="sidebar-footer">
          <p>Nova Engine v2.0.8</p>
          <p>Local Time: 23:10</p>
        </div>
      </aside>

      {/* --- Main Contents Panel --- */}
      <main className="main-content">
        <header className="top-bar">
          <div className="status">
            <span className="dot pulse"></span>
            <span className="mono text-success">ENGINE ACTIVE</span>
          </div>
          <div className="flex-align-center gap-md">
            <span className="text-muted text-sm mono">Wrapper Priority: ISA</span>
            <div className="avatar">PH</div>
          </div>
        </header>

        {/* ==========================================
            TAB VIEW: Overview Dashboard
            ========================================== */}
        {activeTab === 'overview' && (
          <div className="grid-dashboard">
            {/* NAV Performance chart */}
            <div className="card col-span-2 glass-card">
              <div className="card-header-actions">
                <div>
                  <h3 className="text-muted">Total Portfolio Net Asset Value</h3>
                  <h1 className="mono mt-sm">£122,500.00</h1>
                </div>
                <div className="text-right">
                  <span className="text-success mono font-bold">+£7,500 (+6.5%)</span>
                  <p className="text-muted text-xs mono mt-sm">Peak: £125,200.00</p>
                </div>
              </div>
              
              <div className="chart-container mt-md" style={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockOverviewData}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.25}/>
                        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" stroke="#8b929a" tick={{fill: '#8b929a'}}/>
                    <YAxis stroke="#8b929a" tick={{fill: '#8b929a'}} domain={['dataMin - 5000', 'dataMax + 5000']}/>
                    <Tooltip contentStyle={{backgroundColor: '#15171a', border: 'none', borderRadius: '8px', color: '#e7e5e4'}}/>
                    <Area type="monotone" dataKey="value" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" dot={{r: 4, fill: '#ff6b35', strokeWidth: 2, stroke: '#22252a'}} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Compounding split slider */}
            <div className="card glass-card">
              <h3 className="text-muted flex-between">
                The 50/50 System
                <Info size={16} className="text-primary"/>
              </h3>
              <p className="text-muted text-sm mt-sm">Split allocation profit compound ratio dynamically.</p>
              
              <div className="split">
                <div className="bar compound" style={{ width: `${compoundPct}%` }}></div>
                <div className="bar bank" style={{ width: `${100 - compoundPct}%` }}></div>
              </div>

              <div className="flex-between mt-md mono text-sm font-bold">
                <span className="text-primary">£{compoundedAmount} Compounded</span>
                <span className="text-success">£{bankedAmount} Banked</span>
              </div>

              <div className="mt-lg">
                <label className="text-muted text-xs mono mb-md block">Compound Ratio: {compoundPct}%</label>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={compoundPct} 
                  onChange={(e) => setCompoundPct(parseInt(e.target.value))}
                  className="range-glass"
                />
              </div>
            </div>

            {/* Tax progress banner */}
            <div className="card glass-card col-span-2">
              <div className="flex-between">
                <div>
                  <h3 className="text-muted">UK Capital Gains Allowance (GIA)</h3>
                  <h2 className="mono mt-sm">£3,000 / £3,000 Utilised</h2>
                </div>
                <AlertTriangle size={32} className="text-primary"/>
              </div>
              <div className="progress mt-md">
                <div className="progress-fill" style={{ width: '100%', background: 'var(--primary)' }}></div>
              </div>
              <p className="text-xs text-muted mt-md mono">
                GIA Capital Gains wrapper limit is fully reached. The engine has halted new GIA buys and automatically re-routed asset scanner processes into the tax-free ISA wrapper.
              </p>
            </div>

            {/* ML Global metrics */}
            <div className="card glass-card">
              <h3 className="text-muted">Active Classifier Status</h3>
              <div className="flex-between mt-md">
                <span className="text-muted">Classifier model</span>
                <span className="mono text-primary font-bold">Random Forest</span>
              </div>
              <div className="flex-between mt-sm">
                <span className="text-muted">Technical Features</span>
                <span className="mono text-primary font-bold">30+ Indicators</span>
              </div>
              <div className="flex-between mt-sm">
                <span className="text-muted">Min blended score</span>
                <span className="mono text-success font-bold">85.4%</span>
              </div>
              <div className="flex-between mt-sm">
                <span className="text-muted">Active stops</span>
                <span className="mono text-success font-bold">Trailing ATR</span>
              </div>
            </div>

            {/* Live Feed component */}
            <div className="card col-span-full glass-card">
              <h3 className="text-muted mb-md">Live Inference Audit Stream</h3>
              <div className="feed-list">
                {mockTradesList.map((t) => (
                  <div key={t.id} className="feed-item glass-inset">
                    <div className="feed-icon">
                      <TrendingUp size={16} className={t.side === 'BUY' ? 'text-primary' : 'text-danger'}/>
                    </div>
                    <div className="feed-details flex-between">
                      <div>
                        <span className="mono font-bold text-primary mr-md">[{t.book_id.toUpperCase()}]</span>
                        <span className="mono font-bold">{t.side} {t.symbol}</span>
                        <span className="text-muted text-sm ml-md">{t.qty} shares @ £{t.price}</span>
                      </div>
                      <div className="mono text-sm gap-md flex-align-center">
                        <span className="badge-status executed">{t.status}</span>
                        <span className="text-muted">{t.date}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==========================================
            TAB VIEW: Engine Config Studio
            ========================================== */}
        {activeTab === 'engine' && (
          <div className="card glass-card">
            <h3 className="mb-lg">Engine Core Parameters Editor</h3>
            
            <div className="settings-grid">
              <div>
                <div className="settings-row">
                  <label className="mono font-bold text-muted text-sm flex-between">
                    <span>Macro Gate Minimum (gate_min)</span>
                    <span className="text-primary">{gateMin}.0</span>
                  </label>
                  <input 
                    type="range" 
                    min="10" 
                    max="90" 
                    value={gateMin} 
                    onChange={(e) => setGateMin(parseInt(e.target.value))}
                    className="range-glass"
                  />
                  <span className="text-xs text-muted">Below this sentiment index threshold, engine halts new acquisitions.</span>
                </div>

                <div className="settings-row mt-md">
                  <label className="mono font-bold text-muted text-sm flex-between">
                    <span>Execution Threshold (exec_threshold)</span>
                    <span className="text-primary">{execThreshold}.0</span>
                  </label>
                  <input 
                    type="range" 
                    min="50" 
                    max="95" 
                    value={execThreshold} 
                    onChange={(e) => setExecThreshold(parseInt(e.target.value))}
                    className="range-glass"
                  />
                  <span className="text-xs text-muted">Minimum blended rating (60% Quant + 40% LLM Auditor) required to execute order.</span>
                </div>

                <div className="settings-row mt-md">
                  <label className="mono font-bold text-muted text-sm">Top N Candidate Cap</label>
                  <input 
                    type="number" 
                    value={topN} 
                    onChange={(e) => setTopN(Math.max(1, parseInt(e.target.value) || 1))}
                    className="input-glass"
                  />
                  <span className="text-xs text-muted">Max number of top assets scored per wrapper book cycle.</span>
                </div>

                <div className="settings-row mt-lg">
                  <label className="switch-container">
                    <span className="switch-glass">
                      <input 
                        type="checkbox" 
                        checked={aggressiveLiq}
                        onChange={(e) => setAggressiveLiq(e.target.checked)}
                      />
                      <span className="slider-round"></span>
                    </span>
                    <span className="mono font-bold text-muted text-sm">Aggressive Liquidation Mode</span>
                  </label>
                  <span className="text-xs text-muted mt-sm">Immediately sell open assets if the Macro Gate falls below the minimum limit.</span>
                </div>
              </div>

              <div>
                <h4 className="text-muted mb-sm mono">Asset Universe Registry</h4>
                <p className="text-xs text-muted mb-md">Scan list evaluated by the Random Forest classifier every execution loop.</p>
                
                <form onSubmit={handleAddSymbol} className="flex-align-center gap-sm mb-md">
                  <input 
                    type="text" 
                    placeholder="Ticker Symbol (e.g. MSFT)" 
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value)}
                    className="input-glass"
                    style={{ flex: 1 }}
                  />
                  <button type="submit" className="btn-glass" style={{ padding: '12px' }}>
                    <Plus size={18}/>
                  </button>
                </form>

                <div className="universe-tag-container glass-inset">
                  {universe.map((sym) => (
                    <div key={sym} className="universe-tag">
                      <span>{sym}</span>
                      <button type="button" onClick={() => handleRemoveSymbol(sym)}>
                        &times;
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-xl flex-align-center gap-md">
              <button onClick={handleSaveEngineConfig} className="btn-primary">
                Save Engine Config
              </button>
              <button 
                onClick={() => {
                  setGateMin(40);
                  setExecThreshold(75);
                  setTopN(10);
                  setUniverse(['SPY', 'NVDA', 'VWRL', 'FORD']);
                  triggerToast('Reverted config state back to config.yaml baseline', 'info');
                }}
                className="btn-glass"
              >
                Reset Defaults
              </button>
            </div>
          </div>
        )}

        {/* ==========================================
            TAB VIEW: Risk Guardrails & Sizing
            ========================================== */}
        {activeTab === 'guardrails' && (
          <div className="card glass-card">
            <h3 className="mb-lg">System-Level Risk Limits</h3>

            <div className="settings-grid">
              <div>
                <h4 className="text-primary mb-md mono">Operational Safety Bounds</h4>
                
                <div className="settings-row">
                  <label className="mono font-bold text-muted text-sm flex-between">
                    <span>Max Drawdown Limit</span>
                    <span>{maxDrawdown}%</span>
                  </label>
                  <input 
                    type="range" 
                    min="5" 
                    max="30" 
                    step="0.5"
                    value={maxDrawdown} 
                    onChange={(e) => setMaxDrawdown(parseFloat(e.target.value))}
                    className="range-glass"
                  />
                  <span className="text-xs text-muted">Peak-to-trough wrapper valuation decline before buying halts.</span>
                </div>

                <div className="settings-row mt-md">
                  <label className="mono font-bold text-muted text-sm flex-between">
                    <span>Daily Loss Cap</span>
                    <span>{dailyLossCap}%</span>
                  </label>
                  <input 
                    type="range" 
                    min="1" 
                    max="10" 
                    step="0.1"
                    value={dailyLossCap} 
                    onChange={(e) => setDailyLossCap(parseFloat(e.target.value))}
                    className="range-glass"
                  />
                  <span className="text-xs text-muted">Daily loss index threshold to prevent intraday systemic cascading.</span>
                </div>

                <div className="settings-row mt-md">
                  <label className="mono font-bold text-muted text-sm">Max Concurrent Positions</label>
                  <input 
                    type="number" 
                    value={maxPositions} 
                    onChange={(e) => setMaxPositions(Math.max(1, parseInt(e.target.value) || 1))}
                    className="input-glass"
                  />
                </div>
              </div>

              <div>
                <h4 className="text-primary mb-md mono">Position Sizing Policy</h4>
                <div className="segmented-control mb-lg">
                  <button 
                    className={sizerPolicy === 'atr' ? 'active' : ''}
                    onClick={() => setSizerPolicy('atr')}
                  >
                    ATR Volatility
                  </button>
                  <button 
                    className={sizerPolicy === 'nav' ? 'active' : ''}
                    onClick={() => setSizerPolicy('nav')}
                  >
                    Flat NAV Pct
                  </button>
                </div>

                {sizerPolicy === 'atr' ? (
                  <div className="flex-between gap-md flex-wrap">
                    <div style={{ flex: '1 1 45%', marginBottom: '15px' }}>
                      <label className="text-xs text-muted mb-xs mono">Risk Capital per Trade</label>
                      <input 
                        type="number" 
                        step="0.1" 
                        value={riskCapitalPct} 
                        onChange={(e) => setRiskCapitalPct(parseFloat(e.target.value))}
                        className="input-glass"
                      />
                    </div>
                    <div style={{ flex: '1 1 45%', marginBottom: '15px' }}>
                      <label className="text-xs text-muted mb-xs mono">Stop ATR Multiplier</label>
                      <input 
                        type="number" 
                        step="0.1" 
                        value={stopAtrMult} 
                        onChange={(e) => setStopAtrMult(parseFloat(e.target.value))}
                        className="input-glass"
                      />
                    </div>
                    <div style={{ flex: '1 1 100%' }}>
                      <label className="text-xs text-muted mb-xs mono">Take Profit ATR Multiplier</label>
                      <input 
                        type="number" 
                        step="0.1" 
                        value={takeAtrMult} 
                        onChange={(e) => setTakeAtrMult(parseFloat(e.target.value))}
                        className="input-glass"
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="text-xs text-muted mb-xs mono">Max Sizing Per Position (NAV %)</label>
                    <input type="number" defaultValue="8.0" className="input-glass" />
                  </div>
                )}
              </div>
            </div>

            <div className="mt-lg">
              <h4 className="text-muted mb-sm mono">Pearson Correlation Coefficient Threshold</h4>
              <div className="settings-row">
                <label className="mono font-bold text-muted text-sm flex-between">
                  <span>Max Permitted Correlation Check</span>
                  <span>{maxCorrelation}</span>
                </label>
                <input 
                  type="range" 
                  min="0.3" 
                  max="0.95" 
                  step="0.05"
                  value={maxCorrelation} 
                  onChange={(e) => setMaxCorrelation(parseFloat(e.target.value))}
                  className="range-glass"
                />
                <span className="text-xs text-muted">Blocks buying highly correlated assets to diversify sectoral clustering.</span>
              </div>
              
              {/* Micro correlation Matrix */}
              <div className="correlation-matrix-card mt-md">
                <table className="correlation-table">
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>SPY</th>
                      <th>NVDA</th>
                      <th>VWRL</th>
                      <th>FORD</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="font-bold">SPY</td>
                      <td>1.00</td>
                      <td>0.45</td>
                      <td className="correlation-cell high-warning">0.82</td>
                      <td>0.31</td>
                    </tr>
                    <tr>
                      <td className="font-bold">NVDA</td>
                      <td>0.45</td>
                      <td>1.00</td>
                      <td>0.38</td>
                      <td>0.12</td>
                    </tr>
                    <tr>
                      <td className="font-bold">VWRL</td>
                      <td className="correlation-cell high-warning">0.82</td>
                      <td>0.38</td>
                      <td>1.00</td>
                      <td>0.28</td>
                    </tr>
                    <tr>
                      <td className="font-bold">FORD</td>
                      <td>0.31</td>
                      <td>0.12</td>
                      <td>0.28</td>
                      <td>1.00</td>
                    </tr>
                  </tbody>
                </table>
                <p className="text-xs text-danger mt-sm mono">*Highlighted entries exceed current threshold {maxCorrelation} constraint.</p>
              </div>
            </div>

            <div className="mt-xl">
              <button onClick={handleSaveGuardrails} className="btn-primary">
                Save Risk Limits
              </button>
            </div>
          </div>
        )}

        {/* ==========================================
            TAB VIEW: Wrapper Tax & Ledger Matrix
            ========================================== */}
        {activeTab === 'tax' && (
          <div className="card glass-card">
            <h3 className="mb-lg">Wrapper Tax Registry & SQLite Ledger</h3>

            <div className="segmented-control mb-lg" style={{ maxWidth: '400px' }}>
              <button className={selectedBook === 'gia' ? 'active' : ''} onClick={() => setSelectedBook('gia')}>GIA wrapper</button>
              <button className={selectedBook === 'isa' ? 'active' : ''} onClick={() => setSelectedBook('isa')}>ISA wrapper</button>
              <button className={selectedBook === 'sipp' ? 'active' : ''} onClick={() => setSelectedBook('sipp')}>SIPP wrapper</button>
            </div>

            {selectedBook === 'gia' ? (
              <div className="settings-grid mb-lg">
                <div className="card glass-inset">
                  <h4 className="text-muted mono">UK CGT Status Band</h4>
                  <p className="text-xs text-muted mb-md">GIA gains require active capital gains calculation and threshold monitoring.</p>
                  
                  <label className="switch-container mb-md">
                    <span className="switch-glass">
                      <input 
                        type="checkbox" 
                        checked={isHigherRateTaxpayer}
                        onChange={(e) => setIsHigherRateTaxpayer(e.target.checked)}
                      />
                      <span className="slider-round"></span>
                    </span>
                    <span className="mono font-bold text-muted text-sm">Higher Rate Taxpayer (20%)</span>
                  </label>
                  <p className="text-xs text-muted">Basic rate is 10% for assets. Toggle will adjust estimated CGT liability below.</p>
                </div>

                <div className="card glass-inset">
                  <h4 className="text-muted mono">Real-Time CGT Calculator</h4>
                  <div className="flex-between mt-sm">
                    <span className="text-muted text-sm">Realised gains</span>
                    <span className="mono font-bold text-primary">£{currentGiaGains.toFixed(2)}</span>
                  </div>
                  <div className="flex-between mt-sm">
                    <span className="text-muted text-sm">Tax rate</span>
                    <span className="mono font-bold">{isHigherRateTaxpayer ? '20%' : '10%'}</span>
                  </div>
                  <hr style={{ borderColor: 'rgba(255,255,255,0.05)', margin: '10px 0' }}/>
                  <div className="flex-between">
                    <span className="text-muted text-sm">Est. Liability</span>
                    <span className="mono font-bold text-danger">£{estimatedTax.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card glass-inset mb-lg">
                <h4 className="text-success mono">Compounding Tax-Free Wrapper</h4>
                <p className="text-xs text-muted mt-sm">
                  This wrapper ({selectedBook.toUpperCase()}) is completely exempt from Capital Gains Taxes. Standard UK allocation rules route speculative assets outside GIA.
                </p>
              </div>
            )}

            <h4 className="text-muted mb-sm mono">SQLite Trade Records</h4>
            <div className="ledger-table-container glass-inset">
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Book</th>
                    <th>Asset</th>
                    <th>Action</th>
                    <th>Qty</th>
                    <th>Fill Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {mockTradesList.map((t) => (
                    <tr key={t.id}>
                      <td className="mono">{t.date}</td>
                      <td>
                        <span className={`badge-wrapper ${t.book_id.includes('isa') ? 'isa' : t.book_id.includes('sipp') ? 'sipp' : 'gia'}`}>
                          {t.book_id.toUpperCase()}
                        </span>
                      </td>
                      <td className="mono font-bold">{t.symbol}</td>
                      <td className={t.side === 'BUY' ? 'text-primary' : 'text-danger'}>{t.side}</td>
                      <td className="mono">{t.qty}</td>
                      <td className="mono">£{t.price}</td>
                      <td>
                        <span className="badge-status executed">{t.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-lg flex-align-center gap-md">
              <button onClick={() => triggerToast('SQLite ledger CSV exported to desktop downloads', 'success')} className="btn-glass">
                Export Ledger CSV
              </button>
            </div>
          </div>
        )}

        {/* ==========================================
            TAB VIEW: Weekend GPU Optimizer
            ========================================== */}
        {activeTab === 'gpu' && (
          <div className="card glass-card">
            <h3 className="mb-md">Weekend Parameter Tuning & Stress Engine</h3>
            <p className="text-xs text-muted mb-lg">
              Runs Monte Carlo stress paths and Walk-Forward Validation algorithms on historical data. Apply improvements back to config.
            </p>

            <div className="settings-grid mb-lg">
              <div className="card glass-inset">
                <div className="flex-between">
                  <h4 className="text-muted mono">Monte Carlo Sim (10k paths)</h4>
                  <button 
                    disabled={isSimulating}
                    onClick={triggerMonteCarloSimulation} 
                    className="btn-primary" 
                    style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '8px' }}
                  >
                    <Play size={14}/> {isSimulating ? 'Simulating...' : 'Run Simulation'}
                  </button>
                </div>
                
                <div className="chart-container mt-md" style={{ height: 180 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mcPaths}>
                      <Tooltip contentStyle={{backgroundColor: '#15171a', border: 'none', color: '#e7e5e4'}}/>
                      <Line type="monotone" dataKey="min" stroke="var(--danger)" strokeWidth={1} dot={false} opacity={0.3}/>
                      <Line type="monotone" dataKey="avg" stroke="var(--info)" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="max" stroke="var(--success)" strokeWidth={1} dot={false} opacity={0.3}/>
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex-between text-xs mono text-muted mt-sm">
                  <span>95% Var: 14.2%</span>
                  <span>99% Worst-Case: 19.8%</span>
                </div>
              </div>

              <div className="card glass-inset">
                <h4 className="text-muted mono">Walk-Forward Proposed Parameters</h4>
                <p className="text-xs text-muted mb-md">Last validation run generated parameters optimized for local market regimes.</p>

                <div className="flex-between mt-sm text-sm">
                  <span className="text-muted">Baseline Sharpe</span>
                  <span className="mono">0.81</span>
                </div>
                <div className="flex-between mt-sm text-sm">
                  <span className="text-muted">Proposed Sharpe</span>
                  <span className="mono text-success font-bold">1.45</span>
                </div>

                <div className="diff-view mt-md">
                  <p className="text-muted text-xs mb-sm">Proposed `config.yaml` diff:</p>
                  <p className="text-danger">- gate_min: {gateMin}.0</p>
                  <p className="text-success">+ gate_min: 45.0</p>
                  <p className="text-danger">- exec_threshold: {execThreshold}.0</p>
                  <p className="text-success">+ exec_threshold: 80.0</p>
                </div>

                <button 
                  onClick={handleSyncProposedParams} 
                  className="btn-primary mt-lg"
                  style={{ width: '100%' }}
                >
                  Sync Proposed Parameters
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ==========================================
            TAB VIEW: Forex Hub
            ========================================== */}
        {activeTab === 'forex' && (
          <div className="card glass-card">
            <h3 className="mb-md">Forex Bot Integration & Tiers</h3>
            
            <div className="flex-between mb-lg card glass-inset" style={{ flexDirection: 'row', padding: '16px' }}>
              <div>
                <h4 className="mono">Forex Execution Strategy</h4>
                <p className="text-xs text-muted">Toggle forex algorithmic adapters inside the engine.</p>
              </div>
              <label className="switch-container">
                <span className="switch-glass">
                  <input 
                    type="checkbox" 
                    checked={forexEnabled}
                    onChange={(e) => {
                      setForexEnabled(e.target.checked);
                      triggerToast(e.target.checked ? 'Forex bot engine adapter activated' : 'Forex bot engine adapter suspended', 'warning');
                    }}
                  />
                  <span className="slider-round"></span>
                </span>
              </label>
            </div>

            <h4 className="text-muted mb-sm mono">Forex Market Matrix Scans</h4>
            <div className="grid-dashboard mb-lg">
              <div className="card glass-inset">
                <h4 className="mono">EUR/USD</h4>
                <div className="flex-between mt-sm">
                  <span className="text-muted text-xs">ML Direction (5d)</span>
                  <span className="text-success mono font-bold">UPWARDS (+0.45%)</span>
                </div>
                <div className="flex-between mt-sm">
                  <span className="text-muted text-xs">Spread / ATR</span>
                  <span className="mono text-xs">0.3 / 68 pips</span>
                </div>
                <span className="badge-status executed mt-md text-center">STRONG BUY</span>
              </div>

              <div className="card glass-inset">
                <h4 className="mono">GBP/USD</h4>
                <div className="flex-between mt-sm">
                  <span className="text-muted text-xs">ML Direction (5d)</span>
                  <span className="text-warning mono font-bold">NEUTRAL (+0.05%)</span>
                </div>
                <div className="flex-between mt-sm">
                  <span className="text-muted text-xs">Spread / ATR</span>
                  <span className="mono text-xs">0.4 / 84 pips</span>
                </div>
                <span className="badge-status paper mt-md text-center">HOLD</span>
              </div>

              <div className="card glass-inset">
                <h4 className="mono">USD/JPY</h4>
                <div className="flex-between mt-sm">
                  <span className="text-muted text-xs">ML Direction (5d)</span>
                  <span className="text-danger mono font-bold">DOWNWARDS (-0.85%)</span>
                </div>
                <div className="flex-between mt-sm">
                  <span className="text-muted text-xs">Spread / ATR</span>
                  <span className="mono text-xs">0.2 / 112 pips</span>
                </div>
                <span className="badge-status cancelled mt-md text-center">STRONG SELL</span>
              </div>
            </div>

            <h4 className="text-muted mb-sm mono">SAAS Subscription Tiers</h4>
            <div className="tier-grid">
              <div className={`tier-card glass-inset ${activeSubscriptionTier === 'basic' ? 'active-tier' : ''}`}>
                <h4 className="mono text-muted">Basic Tier</h4>
                <p className="text-xs text-muted">Manual trade notifications and recommendations.</p>
                <div className="tier-price mono font-bold">£50<span className="text-xs text-muted">/mo</span></div>
                <ul className="tier-features">
                  <li><CheckCircle size={12} className="text-success"/> EUR/USD, GBP/USD only</li>
                  <li><CheckCircle size={12} className="text-success"/> 10% Profit commission</li>
                </ul>
                <button 
                  disabled={activeSubscriptionTier === 'basic'}
                  onClick={() => {
                    setActiveSubscriptionTier('basic');
                    triggerToast('Downgraded plan to Basic Tier', 'info');
                  }} 
                  className="btn-glass mt-auto"
                >
                  {activeSubscriptionTier === 'basic' ? 'Active Plan' : 'Downgrade'}
                </button>
              </div>

              <div className={`tier-card glass-inset ${activeSubscriptionTier === 'pro' ? 'active-tier' : ''}`}>
                <h4 className="mono text-primary">Pro Tier</h4>
                <p className="text-xs text-muted">Fully automated execution and advanced risk indicators.</p>
                <div className="tier-price mono font-bold">£150<span className="text-xs text-muted">/mo</span></div>
                <ul className="tier-features">
                  <li><CheckCircle size={12} className="text-success"/> Full currency pairs catalog</li>
                  <li><CheckCircle size={12} className="text-success"/> 5% Profit commission</li>
                  <li><CheckCircle size={12} className="text-success"/> Trailing ATR stops</li>
                </ul>
                <button 
                  disabled={activeSubscriptionTier === 'pro'} 
                  onClick={() => {
                    setActiveSubscriptionTier('pro');
                    triggerToast('Downgraded to Pro Tier', 'info');
                  }}
                  className="btn-glass mt-auto"
                >
                  {activeSubscriptionTier === 'pro' ? 'Active Plan' : 'Select Pro'}
                </button>
              </div>

              <div className={`tier-card glass-inset ${activeSubscriptionTier === 'enterprise' ? 'active-tier' : ''}`}>
                <h4 className="mono text-success">Enterprise Tier</h4>
                <p className="text-xs text-muted">Custom algorithms and bespoke dedicated cloud container.</p>
                <div className="tier-price mono font-bold">£500<span className="text-xs text-muted">/mo</span></div>
                <ul className="tier-features">
                  <li><CheckCircle size={12} className="text-success"/> Custom backtest models</li>
                  <li><CheckCircle size={12} className="text-success"/> 2% Profit commission</li>
                  <li><CheckCircle size={12} className="text-success"/> Priority support</li>
                </ul>
                <button 
                  disabled={activeSubscriptionTier === 'enterprise'} 
                  onClick={() => {
                    setActiveSubscriptionTier('enterprise');
                    triggerToast('Upgraded plan to Enterprise Tier!', 'success');
                  }}
                  className="btn-primary mt-auto"
                >
                  {activeSubscriptionTier === 'enterprise' ? 'Active Plan' : 'Upgrade Now'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* --- Slider Confirmation / Authorization Modal --- */}
      {authModal.isOpen && (
        <div className="modal-overlay">
          <div className="modal-content glass-card">
            <h3 className="mono text-primary flex-align-center gap-sm">
              <ShieldCheck size={24}/> {authModal.title}
            </h3>
            <p className="text-muted text-sm">{authModal.description}</p>
            
            {authModal.diff && authModal.diff.length > 0 && (
              <div className="diff-view mt-sm">
                <p className="text-muted text-xs mb-xs">Diff Preview:</p>
                {authModal.diff.map((d, index) => (
                  <div key={index} style={{ marginBottom: '8px' }}>
                    <p className="text-danger" style={{ textDecoration: 'line-through' }}>{d.before}</p>
                    <p className="text-success">{d.after}</p>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-md">
              <label className="text-xs text-muted mono mb-sm block text-center">
                Slide to Authorize Changes ({authSliderVal}%)
              </label>
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={authSliderVal} 
                onChange={handleAuthSliderChange}
                className="range-glass"
                style={{ width: '100%', height: '14px', background: 'rgba(0, 0, 0, 0.5)' }}
              />
            </div>

            <div className="mt-md text-right">
              <button onClick={closeAuthModal} className="btn-glass" style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- Toast System --- */}
      {toast && (
        <div className="toast-container">
          <div className={`toast glass-card ${toast.type}`}>
            <CheckCircle size={16} className="text-success"/>
            <span className="mono">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
