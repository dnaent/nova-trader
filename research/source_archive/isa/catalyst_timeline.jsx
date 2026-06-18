import { useState } from "react";

const STOCKS = [
  // Tier 1
  { ticker: "IMPP", name: "Imperial Petroleum", tier: 1, allocation: 1200, current: 4.10, currency: "$",
    catalysts: [
      { q: "Q2", event: "Fleet expands to 24+ vessels", prob: 0.9 },
      { q: "Q2", event: "Hormuz freight rates sustain $100k+/day", prob: 0.7 },
      { q: "Q3", event: "Fleet hits 26 vessels target", prob: 0.85 },
      { q: "Q4", event: "Potential NAV re-rating to $8-11/share", prob: 0.5 },
    ],
    bear: 1.5, base: 2.5, bull: 4.0, quality: "Shipping", grade: "N/A - Tanker" },
  { ticker: "AET", name: "Afentra", tier: 1, allocation: 800, current: 77, currency: "p",
    catalysts: [
      { q: "Q2", event: "Etu Energias acquisition completes", prob: 0.85 },
      { q: "Q3", event: "Infill drilling programme commences", prob: 0.8 },
      { q: "Q4", event: "Block 3/24 FID targeted", prob: 0.6 },
    ],
    bear: 1.3, base: 2.0, bull: 3.0, quality: "Light-Med Sweet", grade: "30-33° API" },

  // Tier 2
  { ticker: "PXEN", name: "Prospex Energy", tier: 2, allocation: 700, current: 4.85, currency: "p",
    catalysts: [
      { q: "Q2", event: "El Romeral production optimisation", prob: 0.9 },
      { q: "Q2", event: "5-well drilling permits granted", prob: 0.6 },
      { q: "Q3", event: "Polish licence awards", prob: 0.5 },
      { q: "Q4", event: "El Romeral drilling campaign begins", prob: 0.5 },
    ],
    bear: 1.2, base: 2.5, bull: 5.0, quality: "EU Natural Gas", grade: "TTF-priced" },
  { ticker: "BOR", name: "Borders & Southern", tier: 2, allocation: 600, current: 10, currency: "p",
    catalysts: [
      { q: "Q2", event: "Partner discussions advance", prob: 0.7 },
      { q: "Q3", event: "Development partner announcement", prob: 0.35 },
      { q: "Q4", event: "Development planning if partner secured", prob: 0.3 },
    ],
    bear: 0.7, base: 2.0, bull: 8.0, quality: "Gas Condensate", grade: "~45°+ API Ultra-Light" },
  { ticker: "KOS", name: "Kosmos Energy", tier: 2, allocation: 800, current: 2.40, currency: "$",
    catalysts: [
      { q: "Q2", event: "GTA LNG cargoes ramp (32-36 target)", prob: 0.85 },
      { q: "Q2", event: "Jubilee production optimisation", prob: 0.8 },
      { q: "Q3", event: "Analyst upgrades on Hormuz repricing", prob: 0.7 },
      { q: "Q4", event: "FCF inflection from GTA revenues", prob: 0.65 },
    ],
    bear: 1.3, base: 2.5, bull: 3.5, quality: "Light Sweet", grade: "~37° API Premium" },
  { ticker: "RKH", name: "Rockhopper", tier: 2, allocation: 500, current: 75, currency: "p",
    catalysts: [
      { q: "Q2", event: "Sea Lion Phase 1 engineering advances", prob: 0.85 },
      { q: "Q3", event: "Development milestones from Navitas", prob: 0.7 },
      { q: "Q4", event: "First oil timeline confirmation", prob: 0.5 },
    ],
    bear: 1.0, base: 1.5, bull: 2.5, quality: "Medium Sweet", grade: "~28° API" },
  { ticker: "GKP", name: "Gulf Keystone", tier: 2, allocation: 400, current: 204, currency: "p",
    catalysts: [
      { q: "Q2", event: "Production restart post-conflict", prob: 0.6 },
      { q: "Q3", event: "International pricing agreement", prob: 0.4 },
      { q: "Q4", event: "Drilling restart if payments consistent", prob: 0.35 },
    ],
    bear: 0.5, base: 1.8, bull: 3.5, quality: "Medium Sour", grade: "~22° API Kurdistan" },
  { ticker: "EGY", name: "VAALCO Energy", tier: 2, allocation: 700, current: 6.25, currency: "$",
    catalysts: [
      { q: "Q2", event: "Gabon ET-14 drilling completes", prob: 0.85 },
      { q: "Q2", event: "Baobab FPSO returns (Côte d'Ivoire)", prob: 0.75 },
      { q: "Q3", event: "Kossipo FDP (102 MMBOE, 60% WI)", prob: 0.65 },
      { q: "Q4", event: "Production ramp from dual campaigns", prob: 0.6 },
    ],
    bear: 1.3, base: 2.0, bull: 3.0, quality: "Light Sweet", grade: "~31° API Gabonese" },
  { ticker: "AXL", name: "Arrow Exploration", tier: 2, allocation: 600, current: 16, currency: "p",
    catalysts: [
      { q: "Q2", event: "Icaco exploration well result (April)", prob: 0.7 },
      { q: "Q2", event: "M-12Hz horizontal well online", prob: 0.85 },
      { q: "Q3", event: "Production target 6,000+ bopd", prob: 0.7 },
      { q: "Q4", event: "Further development drilling", prob: 0.75 },
    ],
    bear: 1.2, base: 2.0, bull: 3.5, quality: "Light Sweet", grade: "~31° API Colombian" },
  { ticker: "FRO", name: "Frontline", tier: 2, allocation: 600, current: 33.78, currency: "$",
    catalysts: [
      { q: "Q2", event: "Q1 earnings at $107k/day VLCC rates", prob: 0.9 },
      { q: "Q2", event: "Newbuilding fleet deliveries begin", prob: 0.8 },
      { q: "Q3", event: "Sustained elevated freight rates", prob: 0.6 },
    ],
    bear: 0.8, base: 1.5, bull: 2.5, quality: "Shipping", grade: "N/A - 81 Vessels" },

  // Tier 3
  { ticker: "88E", name: "88 Energy", tier: 3, allocation: 200, current: 1.1, currency: "p",
    catalysts: [
      { q: "Q3", event: "Franklin Bluffs-1H drilling", prob: 0.7 },
      { q: "Q4", event: "Augusta-1 rig contract secured", prob: 0.6 },
    ],
    bear: 0.5, base: 1.5, bull: 5.0, quality: "Light Sweet", grade: "~32° API Alaska" },
  { ticker: "PANR", name: "Pantheon Resources", tier: 3, allocation: 300, current: 8, currency: "p",
    catalysts: [
      { q: "Q2", event: "Dubhe-1 flow test data analysis", prob: 0.8 },
      { q: "Q3", event: "Dubhe-1 testing resumes", prob: 0.6 },
      { q: "Q3", event: "Kodiak farm-out progress", prob: 0.5 },
    ],
    bear: 0.5, base: 1.8, bull: 5.0, quality: "Light Sweet + Gas", grade: "~32° API + 6.6Tcf" },
  { ticker: "SEPL", name: "Seplat Energy", tier: 3, allocation: 300, current: 456, currency: "p",
    catalysts: [
      { q: "Q2", event: "ANOH gas plant ramp continues", prob: 0.85 },
      { q: "Q3", event: "Yoho platform restart", prob: 0.7 },
      { q: "Q4", event: "Production approaching 155 kboepd", prob: 0.6 },
    ],
    bear: 1.1, base: 1.4, bull: 1.8, quality: "Premium Light Sweet", grade: "Bonny Light 32-36° API" },
  { ticker: "PTAL", name: "PetroTal", tier: 3, allocation: 250, current: 38, currency: "p",
    catalysts: [
      { q: "Q2", event: "Production exceeds 20,000 bopd", prob: 0.7 },
      { q: "Q3", event: "Continued dividend payments", prob: 0.8 },
    ],
    bear: 1.0, base: 1.5, bull: 2.5, quality: "Heavy Sweet", grade: "~19° API Peruvian" },
  { ticker: "AEX", name: "Aminex", tier: 3, allocation: 250, current: 2.3, currency: "p",
    catalysts: [
      { q: "Q3", event: "Ntorya pipeline completion (July target)", prob: 0.65 },
      { q: "Q3", event: "First gas revenue (Sept target)", prob: 0.55 },
      { q: "Q4", event: "Chikumbi-1 exploration well", prob: 0.5 },
    ],
    bear: 0.7, base: 2.0, bull: 4.0, quality: "Natural Gas", grade: "Tanzanian domestic" },
  { ticker: "ECO", name: "Eco (Atlantic)", tier: 3, allocation: 200, current: 12, currency: "p",
    catalysts: [
      { q: "Q2", event: "JHI acquisition completes", prob: 0.8 },
      { q: "Q3", event: "Namibia farmout progress", prob: 0.5 },
      { q: "Q4", event: "Guyana/Orinduik government approval", prob: 0.4 },
    ],
    bear: 0.6, base: 1.8, bull: 5.0, quality: "Light Sweet", grade: "Guyana ~33° API" },
  { ticker: "STAR", name: "Star Energy", tier: 3, allocation: 200, current: 13.5, currency: "p",
    catalysts: [
      { q: "Q2", event: "Singleton gas-to-wire commissioning", prob: 0.7 },
      { q: "Q3", event: "Stockbridge production reinstated", prob: 0.6 },
    ],
    bear: 1.0, base: 2.0, bull: 3.0, quality: "Light Sweet + Gas", grade: "~37° API UK Onshore" },
  { ticker: "JSE", name: "Jadestone Energy", tier: 3, allocation: 200, current: 28, currency: "p",
    catalysts: [
      { q: "Q2", event: "FY2025 results & guidance update", prob: 0.9 },
      { q: "Q3", event: "Malaysia/Vietnam development progress", prob: 0.7 },
    ],
    bear: 1.0, base: 1.7, bull: 2.5, quality: "Light-Medium", grade: "~30° API Asia-Pac" },
  { ticker: "CHAR", name: "Chariot Ltd", tier: 3, allocation: 200, current: 6.8, currency: "p",
    catalysts: [
      { q: "Q2", event: "Loukos onshore drilling results", prob: 0.7 },
      { q: "Q3", event: "Anchois rescaled FDP / new partner", prob: 0.35 },
    ],
    bear: 0.5, base: 2.0, bull: 5.0, quality: "Natural Gas", grade: "Moroccan offshore" },

  // Tier 4
  { ticker: "HBR", name: "Harbour Energy", tier: 4, allocation: 200, current: 300, currency: "p",
    catalysts: [
      { q: "Q2", event: "LLOG acquisition advances", prob: 0.8 },
      { q: "Q3", event: "Norway/UK gas production benefits", prob: 0.85 },
    ],
    bear: 1.0, base: 1.3, bull: 1.8, quality: "Diversified", grade: "Multi-grade global" },
  { ticker: "PBR", name: "Petrobras ADR", tier: 4, allocation: 200, current: 14.5, currency: "$",
    catalysts: [
      { q: "Q2", event: "Pre-salt output at elevated Brent", prob: 0.85 },
      { q: "Q3", event: "Dividend distributions", prob: 0.8 },
    ],
    bear: 1.0, base: 1.3, bull: 1.6, quality: "Light Sweet", grade: "Pre-salt ~28-30° API" },
  { ticker: "ENIM", name: "Eni", tier: 4, allocation: 100, current: 13.5, currency: "€",
    catalysts: [
      { q: "Q2", event: "EU gas repricing benefit", prob: 0.8 },
    ],
    bear: 1.0, base: 1.2, bull: 1.5, quality: "Diversified", grade: "Multi-grade" },
  { ticker: "APC", name: "ARKO Petroleum", tier: 4, allocation: 100, current: 18.74, currency: "$",
    catalysts: [
      { q: "Q2", event: "First quarterly results post-IPO", prob: 0.9 },
    ],
    bear: 0.9, base: 1.1, bull: 1.3, quality: "Distribution", grade: "Fuel distribution" },
];

const TIER_COLORS = { 1: "#16a34a", 2: "#0d9488", 3: "#f59e0b", 4: "#6b7280" };
const TIER_LABELS = { 1: "HIGHEST CONVICTION", 2: "STRONG CATALYST + HORMUZ", 3: "CATALYST-DEPENDENT", 4: "DEFENSIVE ANCHOR" };
const Q_COLORS = { "Q2": "#3b82f6", "Q3": "#8b5cf6", "Q4": "#ec4899" };

export default function CatalystDashboard() {
  const [view, setView] = useState("overview");
  const [scenario, setScenario] = useState("base");
  const [selected, setSelected] = useState(null);

  const totalAlloc = STOCKS.reduce((s, st) => s + st.allocation, 0);
  const multipliers = { bear: "bear", base: "base", bull: "bull" };

  const calcProfit = (stock, sc) => {
    const mult = stock[sc];
    const invested = stock.allocation;
    const returnVal = invested * mult;
    return { invested, returnVal, profit: returnVal - invested, pct: ((mult - 1) * 100) };
  };

  const totalProfit = STOCKS.reduce((s, st) => s + calcProfit(st, scenario).profit, 0);
  const totalReturn = totalAlloc + totalProfit;

  const scenarioLabels = {
    bear: { label: "BEAR", desc: "Ceasefire / oil drops to $60", color: "#ef4444" },
    base: { label: "BASE", desc: "Hormuz resolves Q3, oil settles $75-85", color: "#f59e0b" },
    bull: { label: "BULL", desc: "Prolonged crisis, oil stays $90-120+", color: "#16a34a" },
  };

  const allCatalysts = STOCKS.flatMap(st =>
    st.catalysts.map(c => ({ ...c, ticker: st.ticker, name: st.name, tier: st.tier }))
  ).sort((a, b) => {
    const qOrder = { "Q2": 0, "Q3": 1, "Q4": 2 };
    return qOrder[a.q] - qOrder[b.q];
  });

  return (
    <div style={{ background: "#0a0f1a", minHeight: "100vh", color: "#e2e8f0", fontFamily: "'JetBrains Mono', 'SF Mono', monospace" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
      `}</style>

      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)", borderBottom: "1px solid #1e3a5f", padding: "16px" }}>
        <div style={{ fontFamily: "Space Grotesk", fontWeight: 700, fontSize: 18, color: "#0d9488" }}>
          ENERGY CATALYST TIMELINE
        </div>
        <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
          £10,000 Theoretical Allocation • 23 Positions • Q2–Q4 2026
        </div>
      </div>

      {/* Scenario Selector */}
      <div style={{ display: "flex", gap: 6, padding: "12px 16px", background: "#0f172a" }}>
        {Object.entries(scenarioLabels).map(([key, val]) => (
          <button key={key} onClick={() => setScenario(key)}
            style={{
              flex: 1, padding: "10px 6px", border: scenario === key ? `2px solid ${val.color}` : "1px solid #1e293b",
              borderRadius: 8, background: scenario === key ? `${val.color}15` : "#0a0f1a",
              color: scenario === key ? val.color : "#64748b", cursor: "pointer", textAlign: "center",
              fontFamily: "JetBrains Mono", fontSize: 10, fontWeight: scenario === key ? 700 : 400
            }}>
            <div style={{ fontSize: 13, fontWeight: 700 }}>{val.label}</div>
            <div style={{ fontSize: 9, marginTop: 2, opacity: 0.8 }}>{val.desc}</div>
          </button>
        ))}
      </div>

      {/* Summary Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, padding: "8px 16px" }}>
        <div style={{ background: "#1e293b", borderRadius: 8, padding: 12, textAlign: "center" }}>
          <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: 1 }}>Invested</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: "#e2e8f0", fontFamily: "Space Grotesk" }}>£{totalAlloc.toLocaleString()}</div>
        </div>
        <div style={{ background: "#1e293b", borderRadius: 8, padding: 12, textAlign: "center" }}>
          <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: 1 }}>Return</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: totalReturn > totalAlloc ? "#16a34a" : "#ef4444", fontFamily: "Space Grotesk" }}>
            £{Math.round(totalReturn).toLocaleString()}
          </div>
        </div>
        <div style={{ background: "#1e293b", borderRadius: 8, padding: 12, textAlign: "center" }}>
          <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: 1 }}>P&L</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: totalProfit > 0 ? "#16a34a" : "#ef4444", fontFamily: "Space Grotesk" }}>
            {totalProfit > 0 ? "+" : ""}£{Math.round(totalProfit).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Nav Tabs */}
      <div style={{ display: "flex", gap: 0, padding: "8px 16px" }}>
        {[["overview", "Allocation"], ["timeline", "Timeline"], ["returns", "Returns"]].map(([k, l]) => (
          <button key={k} onClick={() => setView(k)}
            style={{
              flex: 1, padding: "8px", border: "none", borderBottom: view === k ? "2px solid #0d9488" : "2px solid transparent",
              background: "transparent", color: view === k ? "#0d9488" : "#64748b", cursor: "pointer",
              fontFamily: "JetBrains Mono", fontSize: 11, fontWeight: view === k ? 700 : 400
            }}>{l}</button>
        ))}
      </div>

      {/* Content */}
      <div style={{ padding: "8px 16px 100px" }}>

        {view === "overview" && (
          <div>
            {[1, 2, 3, 4].map(tier => (
              <div key={tier} style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: TIER_COLORS[tier], marginBottom: 6, letterSpacing: 1 }}>
                  TIER {tier} — {TIER_LABELS[tier]}
                </div>
                {STOCKS.filter(s => s.tier === tier).map(st => {
                  const p = calcProfit(st, scenario);
                  const pct = (st.allocation / totalAlloc * 100).toFixed(1);
                  return (
                    <div key={st.ticker} onClick={() => setSelected(selected === st.ticker ? null : st.ticker)}
                      style={{
                        background: "#1e293b", borderRadius: 8, padding: "10px 12px", marginBottom: 6, cursor: "pointer",
                        borderLeft: `3px solid ${TIER_COLORS[tier]}`, transition: "all 0.2s"
                      }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <span style={{ fontWeight: 700, fontSize: 13, color: "#f1f5f9" }}>{st.ticker}</span>
                          <span style={{ fontSize: 10, color: "#64748b", marginLeft: 8 }}>{st.name}</span>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9" }}>£{st.allocation}</div>
                          <div style={{ fontSize: 10, color: "#64748b" }}>{pct}%</div>
                        </div>
                      </div>
                      {/* Allocation bar */}
                      <div style={{ height: 4, background: "#0f172a", borderRadius: 2, marginTop: 6, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${pct * 2}%`, background: TIER_COLORS[tier], borderRadius: 2, maxWidth: "100%" }} />
                      </div>
                      {/* Return info */}
                      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 10 }}>
                        <span style={{ color: "#94a3b8" }}>{st.quality} • {st.grade}</span>
                        <span style={{ color: p.profit >= 0 ? "#16a34a" : "#ef4444", fontWeight: 700 }}>
                          {p.profit >= 0 ? "+" : ""}£{Math.round(p.profit)} ({p.pct > 0 ? "+" : ""}{p.pct.toFixed(0)}%)
                        </span>
                      </div>
                      {/* Expanded catalysts */}
                      {selected === st.ticker && (
                        <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #334155" }}>
                          <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 6 }}>UPCOMING CATALYSTS:</div>
                          {st.catalysts.map((c, i) => (
                            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, fontSize: 10 }}>
                              <span style={{ background: Q_COLORS[c.q], color: "#fff", padding: "1px 6px", borderRadius: 4, fontSize: 9, fontWeight: 700, minWidth: 28, textAlign: "center" }}>
                                {c.q}
                              </span>
                              <span style={{ flex: 1, color: "#cbd5e1" }}>{c.event}</span>
                              <span style={{ color: c.prob >= 0.7 ? "#16a34a" : c.prob >= 0.5 ? "#f59e0b" : "#ef4444", fontWeight: 700 }}>
                                {(c.prob * 100).toFixed(0)}%
                              </span>
                            </div>
                          ))}
                          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6, marginTop: 8 }}>
                            {["bear", "base", "bull"].map(sc => {
                              const r = calcProfit(st, sc);
                              return (
                                <div key={sc} style={{ background: "#0f172a", borderRadius: 6, padding: 6, textAlign: "center" }}>
                                  <div style={{ fontSize: 8, color: scenarioLabels[sc].color, fontWeight: 700 }}>{sc.toUpperCase()}</div>
                                  <div style={{ fontSize: 12, fontWeight: 700, color: r.profit >= 0 ? "#16a34a" : "#ef4444" }}>
                                    {r.pct > 0 ? "+" : ""}{r.pct.toFixed(0)}%
                                  </div>
                                  <div style={{ fontSize: 9, color: "#64748b" }}>£{Math.round(r.returnVal)}</div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        )}

        {view === "timeline" && (
          <div>
            {["Q2", "Q3", "Q4"].map(q => (
              <div key={q} style={{ marginBottom: 20 }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 8, marginBottom: 10,
                  padding: "8px 12px", background: `${Q_COLORS[q]}15`, borderRadius: 8, borderLeft: `3px solid ${Q_COLORS[q]}`
                }}>
                  <span style={{ fontSize: 16, fontWeight: 700, color: Q_COLORS[q], fontFamily: "Space Grotesk" }}>{q} 2026</span>
                  <span style={{ fontSize: 10, color: "#64748b" }}>
                    {q === "Q2" ? "Apr – Jun" : q === "Q3" ? "Jul – Sep" : "Oct – Dec"}
                  </span>
                  <span style={{ marginLeft: "auto", fontSize: 11, color: Q_COLORS[q], fontWeight: 700 }}>
                    {allCatalysts.filter(c => c.q === q).length} events
                  </span>
                </div>
                {allCatalysts.filter(c => c.q === q).map((c, i) => (
                  <div key={i} style={{
                    display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 6, padding: "8px 10px",
                    background: "#1e293b", borderRadius: 6, borderLeft: `2px solid ${TIER_COLORS[c.tier]}`
                  }}>
                    <div style={{ minWidth: 42 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: TIER_COLORS[c.tier] }}>{c.ticker}</div>
                      <div style={{
                        fontSize: 8, color: c.prob >= 0.7 ? "#16a34a" : c.prob >= 0.5 ? "#f59e0b" : "#ef4444",
                        fontWeight: 700, marginTop: 2
                      }}>
                        {(c.prob * 100).toFixed(0)}% prob
                      </div>
                    </div>
                    <div style={{ fontSize: 10, color: "#cbd5e1", lineHeight: 1.4 }}>{c.event}</div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}

        {view === "returns" && (
          <div>
            {/* Scenario summary */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16 }}>
              {Object.entries(scenarioLabels).map(([sc, info]) => {
                const tp = STOCKS.reduce((s, st) => s + calcProfit(st, sc).profit, 0);
                const tr = totalAlloc + tp;
                return (
                  <div key={sc} style={{
                    background: sc === scenario ? `${info.color}15` : "#1e293b", borderRadius: 8, padding: 12,
                    textAlign: "center", border: sc === scenario ? `2px solid ${info.color}` : "1px solid #334155",
                    cursor: "pointer"
                  }} onClick={() => setScenario(sc)}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: info.color }}>{info.label}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: tp >= 0 ? "#16a34a" : "#ef4444", fontFamily: "Space Grotesk", marginTop: 4 }}>
                      {tp >= 0 ? "+" : ""}£{Math.round(tp).toLocaleString()}
                    </div>
                    <div style={{ fontSize: 10, color: "#64748b", marginTop: 2 }}>
                      → £{Math.round(tr).toLocaleString()} ({((tp / totalAlloc) * 100).toFixed(0)}%)
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Individual returns sorted by profit */}
            <div style={{ fontSize: 10, color: "#64748b", marginBottom: 8, letterSpacing: 1 }}>
              RETURNS BY POSITION — {scenarioLabels[scenario].label} SCENARIO
            </div>
            {[...STOCKS].sort((a, b) => calcProfit(b, scenario).profit - calcProfit(a, scenario).profit).map(st => {
              const p = calcProfit(st, scenario);
              const barWidth = Math.min(Math.abs(p.pct), 400);
              return (
                <div key={st.ticker} style={{
                  display: "flex", alignItems: "center", gap: 8, marginBottom: 4, padding: "6px 10px",
                  background: "#1e293b", borderRadius: 6
                }}>
                  <div style={{ minWidth: 38, fontSize: 11, fontWeight: 700, color: TIER_COLORS[st.tier] }}>{st.ticker}</div>
                  <div style={{ flex: 1, position: "relative", height: 16 }}>
                    <div style={{
                      position: "absolute", left: p.pct >= 0 ? "50%" : `${50 - barWidth / 8}%`,
                      width: `${barWidth / 8}%`, height: "100%",
                      background: p.pct >= 0 ? "#16a34a40" : "#ef444440", borderRadius: 2,
                      ...(p.pct < 0 ? { right: "50%", left: "auto" } : {})
                    }} />
                    <div style={{
                      position: "absolute", left: "50%", top: 0, bottom: 0, width: 1, background: "#334155"
                    }} />
                  </div>
                  <div style={{ minWidth: 50, textAlign: "right", fontSize: 11, fontWeight: 700, color: p.pct >= 0 ? "#16a34a" : "#ef4444" }}>
                    {p.pct >= 0 ? "+" : ""}{p.pct.toFixed(0)}%
                  </div>
                  <div style={{ minWidth: 52, textAlign: "right", fontSize: 10, color: p.profit >= 0 ? "#16a34a" : "#ef4444" }}>
                    {p.profit >= 0 ? "+" : ""}£{Math.round(p.profit)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, background: "#0f172a", borderTop: "1px solid #1e293b", padding: "6px 16px" }}>
        <div style={{ fontSize: 8, color: "#475569", textAlign: "center" }}>
          ⚠️ THEORETICAL ONLY — Not financial advice. All investments carry risk including total loss of capital. Consult a qualified advisor.
        </div>
      </div>
    </div>
  );
}
