import { useState } from "react";

const S = [
  {t:"AET",n:"Afentra",tier:1,rank:1,a:1400,cur:72,cy:"p",sl:58,bear:1.3,base:2.0,bull:3.0,hz:"V.STRONG",sp:"MED-HIGH",cq:"Light-Med Sweet",api:"28-32°",bp:"-$2 to -$4",impl:"~$90-98",
   cats:[{q:"Q2",e:"Etu acquisition + Rule 2.7 bid expected",p:.65},{q:"Q3",e:"Infill drilling programme commences",p:.8},{q:"Q4",e:"Block 3/24 FID targeted",p:.6}],act:"STRONG BUY",risk:"Bid may not materialise"},
  {t:"IMPP",n:"Imperial Petroleum",tier:1,rank:2,a:1200,cur:4.10,cy:"$",sl:2.80,bear:1.5,base:2.5,bull:4.0,hz:"EXTREME",sp:"HIGH",cq:"Shipping - Rate Driven",api:"N/A",bp:"N/A",impl:"$107k/day",
   cats:[{q:"Q2",e:"Fleet expands 24+ vessels + Q1 peak earnings",p:.9},{q:"Q3",e:"Fleet hits 26 vessels target",p:.85},{q:"Q4",e:"NAV re-rating to $8-11/share",p:.5}],act:"STRONG BUY",risk:"Dilutive offerings"},
  {t:"KOS",n:"Kosmos Energy",tier:2,rank:3,a:700,cur:2.40,cy:"$",sl:1.60,bear:1.3,base:2.5,bull:3.5,hz:"V.STRONG",sp:"MED-HIGH",cq:"Premium Light Sweet",api:"~37°",bp:"Flat to +$2",impl:"~$94-102",
   cats:[{q:"Q2",e:"GTA LNG cargoes ramp (32-36 yr target)",p:.85},{q:"Q2",e:"Jubilee production optimisation",p:.8},{q:"Q3",e:"Analyst upgrades on Hormuz repricing",p:.7},{q:"Q4",e:"FCF inflection from GTA",p:.65}],act:"BUY",risk:"Debt leverage"},
  {t:"EGY",n:"VAALCO Energy",tier:2,rank:4,a:600,cur:6.25,cy:"$",sl:4.50,bear:1.3,base:2.0,bull:3.0,hz:"EXTREME",sp:"MED-HIGH",cq:"Light Sweet African",api:"~31°",bp:"Flat",impl:"~$94-100",
   cats:[{q:"Q2",e:"Gabon ET-14 completes + Baobab FPSO",p:.8},{q:"Q3",e:"Kossipo FDP (102 MMBOE, 60% WI)",p:.65},{q:"Q4",e:"Dual campaign production ramp",p:.6}],act:"BUY",risk:"FPSO delays"},
  {t:"JSE",n:"Jadestone Energy",tier:2,rank:5,a:500,cur:28,cy:"p",sl:20,bear:1.0,base:1.7,bull:2.5,hz:"STRONG",sp:"MED-HIGH",cq:"Condensate/Light ASIA PREM",api:"38-47°",bp:"+$3 to +$10",impl:"~$97-115",
   cats:[{q:"Q2",e:"Vietnam FDP approval + PM323 drilling",p:.65},{q:"Q3",e:"RBL refinancing + production growth",p:.7}],act:"STRONG BUY",risk:"Hedging caps upside"},
  {t:"GKP",n:"Gulf Keystone",tier:2,rank:6,a:400,cur:204,cy:"p",sl:165,bear:0.5,base:1.8,bull:3.5,hz:"EXTREME BINARY",sp:"MED-HIGH",cq:"Light Sweet CEYHAN PREM",api:"~35°",bp:"-$10→$90+ intl",impl:"~$74→$124",
   cats:[{q:"Q2",e:"Div Apr 27 + AIM 100 + restart?",p:.6},{q:"Q3",e:"International pricing review",p:.4},{q:"Q4",e:"Drilling restart if payments",p:.35}],act:"HOLD",risk:"Iran conflict adjacent"},
  {t:"FRO",n:"Frontline",tier:2,rank:7,a:500,cur:33.78,cy:"$",sl:25,bear:0.8,base:1.5,bull:2.5,hz:"EXTREME",sp:"MED-HIGH",cq:"Shipping - 81 VLCCs",api:"N/A",bp:"N/A",impl:"$107k/day VLCC",
   cats:[{q:"Q2",e:"Q1 earnings at $107k/day rates",p:.9},{q:"Q2",e:"Newbuilding fleet deliveries",p:.8},{q:"Q3",e:"Sustained elevated freight",p:.6}],act:"BUY",risk:"Cyclical rate collapse"},
  {t:"AXL",n:"Arrow Exploration",tier:2,rank:8,a:500,cur:16,cy:"p",sl:12,bear:1.2,base:2.0,bull:3.5,hz:"STRONG",sp:"MED-HIGH",cq:"Light Sweet Colombian",api:"~31°",bp:"Brent-linked",impl:"~$90-94",
   cats:[{q:"Q2",e:"Icaco exploration (Apr) + M-12Hz",p:.7},{q:"Q3",e:"Production 6,000+ bopd",p:.7},{q:"Q4",e:"Further dev drilling",p:.75}],act:"BUY",risk:"Colombia political"},
  {t:"PXEN",n:"Prospex Energy",tier:2,rank:9,a:400,cur:4.85,cy:"p",sl:3.0,bear:1.2,base:2.5,bull:5.0,hz:"V.STRONG",sp:"MED-HIGH",cq:"EU Gas - TTF Premium",api:"Gas",bp:"TTF",impl:"~€52/MWh",
   cats:[{q:"Q2",e:"El Romeral optimisation + permits?",p:.6},{q:"Q3",e:"Polish licence awards",p:.5},{q:"Q4",e:"El Romeral drilling begins",p:.5}],act:"BUY",risk:"Spanish permitting"},
  {t:"SEPL",n:"Seplat Energy",tier:2,rank:10,a:400,cur:456,cy:"p",sl:350,bear:1.1,base:1.4,bull:1.8,hz:"V.STRONG",sp:"MED",cq:"WORLD'S MOST PREMIUM",api:"~35°",bp:"+$2 to +$5",impl:"~$96-104",
   cats:[{q:"Q2",e:"ANOH gas ramp + MPNU integration",p:.85},{q:"Q3",e:"Yoho platform restart",p:.7},{q:"Q4",e:"Approaching 155 kboepd",p:.6}],act:"BUY",risk:"Nigeria security"},
  {t:"BOR",n:"Borders & Southern",tier:2,rank:11,a:300,cur:10,cy:"p",sl:5,bear:0.7,base:2.0,bull:8.0,hz:"V.STRONG",sp:"MED-HIGH",cq:"ULTRA-LIGHT CONDENSATE",api:"46-49°",bp:"+$5-10",impl:"~$99-115",
   cats:[{q:"Q2",e:"Partner discussions",p:.7},{q:"Q3",e:"Dev partner announcement?",p:.35}],act:"SPEC BUY",risk:"Cash runway / binary"},
  {t:"RKH",n:"Rockhopper",tier:2,rank:12,a:300,cur:75,cy:"p",sl:55,bear:1.0,base:1.5,bull:2.5,hz:"V.STRONG",sp:"MED-HIGH",cq:"Light Sweet Atlantic",api:"~32°",bp:"-$1 to flat",impl:"~$93",
   cats:[{q:"Q2",e:"Sea Lion Phase 1 engineering",p:.85},{q:"Q3",e:"Navitas milestones",p:.7}],act:"HOLD",risk:"Argentina geo risk"},
  {t:"ENQ",n:"EnQuest",tier:2,rank:13,a:300,cur:13,cy:"p",sl:9,bear:1.0,base:1.8,bull:2.5,hz:"STRONG",sp:"MED-HIGH",cq:"Med Sour + ASIA PREMIUM",api:"30-40°",bp:"Brent+Asia",impl:"~$94-110",
   cats:[{q:"Q2",e:"Magnus infill drilling + Seligi gas",p:.7},{q:"Q3",e:"Vietnam Block 12W growth",p:.65},{q:"Q4",e:"Serica merger potential",p:.5}],act:"BUY",risk:"UK windfall tax 78%"},
  {t:"HBR",n:"Harbour Energy",tier:2,rank:14,a:300,cur:300,cy:"p",sl:240,bear:1.0,base:1.4,bull:1.8,hz:"STRONG",sp:"MED",cq:"MEDIUM SOUR $124/bbl",api:"Mixed",bp:"+$11.30 RECORD",impl:"~$124/bbl!",
   cats:[{q:"Q2",e:"LLOG acquisition + Sverdrup premium",p:.8},{q:"Q3",e:"Norway/UK gas benefits",p:.85}],act:"BUY ↑",risk:"Debt from acquisitions"},
  {t:"PTAL",n:"PetroTal",tier:3,rank:15,a:200,cur:38,cy:"p",sl:28,bear:1.0,base:1.5,bull:2.5,hz:"STRONG",sp:"MED",cq:"Light Sweet Peruvian",api:"~35-37°",bp:"-$5 to -$15",impl:"~$79-89",
   cats:[{q:"Q2",e:"Production >20,000 bopd",p:.7},{q:"Q3",e:"Dividend payments",p:.8}],act:"HOLD",risk:"Peru social unrest"},
  {t:"SQZ",n:"Serica Energy",tier:3,rank:16,a:150,cur:130,cy:"p",sl:100,bear:1.0,base:1.5,bull:2.0,hz:"STRONG",sp:"MED",cq:"UK Gas - 5% of UK supply",api:"~38°",bp:"NBP-linked",impl:"~$94+",
   cats:[{q:"Q2",e:"EnQuest merger talks advance",p:.5},{q:"Q3",e:"Production optimisation",p:.7}],act:"BUY",risk:"UK windfall tax"},
  {t:"ECO",n:"Eco (Atlantic)",tier:3,rank:17,a:150,cur:12,cy:"p",sl:7,bear:0.6,base:1.8,bull:5.0,hz:"STRONG",sp:"MED",cq:"Multi-basin Atlantic",api:"~33°",bp:"N/A",impl:"Farm-out driven",
   cats:[{q:"Q2",e:"JHI acquisition completes",p:.8},{q:"Q3",e:"Namibia farmout progress",p:.5}],act:"HOLD",risk:"Pre-revenue explorer"},
  {t:"STAR",n:"Star Energy",tier:3,rank:18,a:150,cur:13.5,cy:"p",sl:9,bear:1.0,base:2.0,bull:3.0,hz:"STRONG",sp:"MED",cq:"UK Onshore Light Sweet",api:"~35-40°",bp:"Brent-linked",impl:"~$92",
   cats:[{q:"Q2",e:"Singleton gas-to-wire Q2",p:.7},{q:"Q3",e:"Stockbridge restart",p:.6}],act:"HOLD",risk:"Production below guidance"},
  {t:"EQNR",n:"Equinor",tier:3,rank:19,a:200,cur:25,cy:"$",sl:20,bear:1.0,base:1.3,bull:1.6,hz:"V.STRONG",sp:"LOW-MED",cq:"Sverdrup OPERATOR $124",api:"~28°",bp:"+$11.30",impl:"~$124",
   cats:[{q:"Q2",e:"Sverdrup premium revenues + EU gas",p:.85},{q:"Q3",e:"Phase 3 Sverdrup",p:.7}],act:"BUY",risk:"Norwegian tax"},
  {t:"ITH",n:"Ithaca Energy",tier:3,rank:20,a:100,cur:130,cy:"p",sl:100,bear:1.0,base:1.3,bull:1.7,hz:"STRONG",sp:"LOW-MED",cq:"Brent Basket Hedged",api:"~35-38°",bp:"Brent",impl:"~$94",
   cats:[{q:"Q2",e:"Cambo field progress",p:.6},{q:"Q3",e:"Production maintenance",p:.8}],act:"HOLD-Income",risk:"Hedging limits upside"},
  {t:"AEX",n:"Aminex",tier:3,rank:21,a:100,cur:2.3,cy:"p",sl:1.5,bear:0.7,base:2.0,bull:4.0,hz:"MOD",sp:"MED",cq:"Tanzanian Gas",api:"Gas",bp:"Domestic",impl:"~$3-5/MMBtu",
   cats:[{q:"Q3",e:"Pipeline completion Jul + first gas Sept",p:.55}],act:"REDUCE",risk:"Tanzania govt delays"},
  {t:"88E",n:"88 Energy",tier:3,rank:22,a:100,cur:1.1,cy:"p",sl:0.5,bear:0.5,base:1.5,bull:5.0,hz:"STRONG",sp:"MED",cq:"Alaska Light Sweet",api:"~32°",bp:"ANS",impl:"~$92",
   cats:[{q:"Q3",e:"Franklin Bluffs-1H drilling",p:.7}],act:"SPEC",risk:"Serial disappointment"},
  {t:"PANR",n:"Pantheon",tier:3,rank:23,a:100,cur:8,cy:"p",sl:4,bear:0.5,base:1.8,bull:5.0,hz:"STRONG",sp:"MED",cq:"Alaska Light Sweet + Gas",api:"~32°",bp:"ANS",impl:"~$92",
   cats:[{q:"Q2",e:"Dubhe-1 data analysis",p:.8},{q:"Q3",e:"Dubhe-1 retest + Kodiak farmout",p:.5}],act:"HOLD",risk:"Flow rates disappointing"},
  {t:"CHAR",n:"Chariot Ltd",tier:3,rank:24,a:100,cur:6.8,cy:"p",sl:3.5,bear:0.5,base:2.0,bull:5.0,hz:"STRONG",sp:"MED",cq:"Moroccan Gas",api:"Gas",bp:"TTF",impl:"~€52/MWh",
   cats:[{q:"Q2",e:"Loukos onshore drilling results",p:.7},{q:"Q3",e:"Anchois rescaled FDP",p:.35}],act:"SPEC",risk:"Cash constraints"},
  {t:"PBR",n:"Petrobras ADR",tier:4,rank:25,a:150,cur:14.50,cy:"$",sl:11,bear:1.0,base:1.3,bull:1.6,hz:"STRONG",sp:"LOW-MED",cq:"Pre-salt Atlantic",api:"~28-29°",bp:"-$2 to flat",impl:"~$92-94",
   cats:[{q:"Q2",e:"Dividend + Buzios Phase 7",p:.85}],act:"HOLD",risk:"Political interference"},
  {t:"ENIM",n:"Eni",tier:4,rank:26,a:50,cur:13.50,cy:"€",sl:11,bear:1.0,base:1.2,bull:1.5,hz:"MOD",sp:"LOW",cq:"Diversified Major",api:"Mixed",bp:"Various",impl:"Various",
   cats:[{q:"Q2",e:"EU gas repricing",p:.8}],act:"HOLD",risk:"Size limits upside"},
  {t:"APC",n:"ARKO Petroleum",tier:4,rank:27,a:50,cur:18.74,cy:"$",sl:16,bear:0.9,base:1.1,bull:1.3,hz:"MINIMAL",sp:"LOW",cq:"Fuel Distribution",api:"N/A",bp:"N/A",impl:"Fee-based",
   cats:[{q:"Q2",e:"First quarterly post-IPO",p:.9}],act:"HOLD",risk:"Consumer spending"},
];

const TC={1:"#16a34a",2:"#0d9488",3:"#f59e0b",4:"#6b7280"};
const TL={1:"HIGHEST CONVICTION",2:"STRONG CATALYST+HORMUZ",3:"CATALYST-DEPENDENT",4:"DEFENSIVE"};
const QC={"Q2":"#3b82f6","Q3":"#8b5cf6","Q4":"#ec4899"};
const SL={bear:{l:"BEAR",d:"Ceasefire / $60 oil",c:"#ef4444"},base:{l:"BASE",d:"Resolves Q3 / $75-85",c:"#f59e0b"},bull:{l:"BULL",d:"Prolonged / $90-120+",c:"#16a34a"}};

export default function D(){
  const[v,setV]=useState("alloc");
  const[sc,setSc]=useState("base");
  const[sel,setSel]=useState(null);
  const tot=S.reduce((s,x)=>s+x.a,0);
  const cp=(s,c)=>{const m=s[c],r=s.a*m;return{inv:s.a,ret:r,pnl:r-s.a,pct:(m-1)*100}};
  const tp=S.reduce((s,x)=>s+cp(x,sc).pnl,0);
  const tr=tot+tp;

  const allCats=S.flatMap(s=>s.cats.map(c=>({...c,t:s.t,n:s.n,tier:s.tier}))).sort((a,b)=>{
    const o={"Q2":0,"Q3":1,"Q4":2};return o[a.q]-o[b.q];
  });

  return(
    <div style={{background:"#0a0f1a",minHeight:"100vh",color:"#e2e8f0",fontFamily:"'JetBrains Mono','SF Mono',monospace"}}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');*{box-sizing:border-box;margin:0;padding:0}::-webkit-scrollbar{width:4px}::-webkit-scrollbar-thumb{background:#334155;border-radius:4px}`}</style>

      <div style={{background:"linear-gradient(135deg,#0f172a,#1e293b)",borderBottom:"1px solid #1e3a5f",padding:"14px 16px"}}>
        <div style={{fontFamily:"Space Grotesk",fontWeight:700,fontSize:17,color:"#0d9488"}}>DNA ENERGY CATALYST ENGINE</div>
        <div style={{fontSize:10,color:"#64748b",marginTop:3}}>27 Positions • £10,000 • Full Crude Quality + Hormuz Analysis</div>
      </div>

      <div style={{display:"flex",gap:6,padding:"10px 16px",background:"#0f172a"}}>
        {Object.entries(SL).map(([k,v])=>(
          <button key={k} onClick={()=>setSc(k)} style={{flex:1,padding:"8px 4px",border:sc===k?`2px solid ${v.c}`:"1px solid #1e293b",borderRadius:8,background:sc===k?`${v.c}15`:"#0a0f1a",color:sc===k?v.c:"#64748b",cursor:"pointer",fontFamily:"JetBrains Mono",fontSize:10,textAlign:"center"}}>
            <div style={{fontSize:12,fontWeight:700}}>{v.l}</div>
            <div style={{fontSize:8,marginTop:1,opacity:.8}}>{v.d}</div>
          </button>
        ))}
      </div>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8,padding:"8px 16px"}}>
        <div style={{background:"#1e293b",borderRadius:8,padding:10,textAlign:"center"}}>
          <div style={{fontSize:8,color:"#64748b",textTransform:"uppercase",letterSpacing:1}}>Deployed</div>
          <div style={{fontSize:16,fontWeight:700,color:"#e2e8f0",fontFamily:"Space Grotesk"}}>£{tot.toLocaleString()}</div>
        </div>
        <div style={{background:"#1e293b",borderRadius:8,padding:10,textAlign:"center"}}>
          <div style={{fontSize:8,color:"#64748b",textTransform:"uppercase",letterSpacing:1}}>Return</div>
          <div style={{fontSize:16,fontWeight:700,color:tr>tot?"#16a34a":"#ef4444",fontFamily:"Space Grotesk"}}>£{Math.round(tr).toLocaleString()}</div>
        </div>
        <div style={{background:"#1e293b",borderRadius:8,padding:10,textAlign:"center"}}>
          <div style={{fontSize:8,color:"#64748b",textTransform:"uppercase",letterSpacing:1}}>P&L</div>
          <div style={{fontSize:16,fontWeight:700,color:tp>0?"#16a34a":"#ef4444",fontFamily:"Space Grotesk"}}>{tp>0?"+":""}£{Math.round(tp).toLocaleString()}</div>
          <div style={{fontSize:9,color:tp>0?"#16a34a":"#ef4444"}}>({((tp/tot)*100).toFixed(0)}%)</div>
        </div>
      </div>

      <div style={{display:"flex",gap:0,padding:"6px 16px"}}>
        {[["alloc","Allocation"],["crude","Crude Quality"],["timeline","Timeline"],["returns","Returns"]].map(([k,l])=>(
          <button key={k} onClick={()=>setV(k)} style={{flex:1,padding:"7px",border:"none",borderBottom:v===k?"2px solid #0d9488":"2px solid transparent",background:"transparent",color:v===k?"#0d9488":"#64748b",cursor:"pointer",fontFamily:"JetBrains Mono",fontSize:10,fontWeight:v===k?700:400}}>{l}</button>
        ))}
      </div>

      <div style={{padding:"6px 16px 90px",overflowY:"auto"}}>

        {v==="alloc"&&<div>
          {[1,2,3,4].map(tier=><div key={tier} style={{marginBottom:14}}>
            <div style={{fontSize:9,fontWeight:700,color:TC[tier],marginBottom:5,letterSpacing:1}}>TIER {tier} — {TL[tier]}</div>
            {S.filter(s=>s.tier===tier).map(s=>{const p=cp(s,sc);const pct=(s.a/tot*100).toFixed(1);
              return(<div key={s.t} onClick={()=>setSel(sel===s.t?null:s.t)} style={{background:"#1e293b",borderRadius:8,padding:"8px 10px",marginBottom:5,cursor:"pointer",borderLeft:`3px solid ${TC[tier]}`}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                  <div><span style={{fontWeight:700,fontSize:12,color:"#f1f5f9"}}>{s.t}</span><span style={{fontSize:9,color:"#64748b",marginLeft:6}}>{s.n}</span></div>
                  <div style={{textAlign:"right"}}><div style={{fontSize:11,fontWeight:700}}>£{s.a}</div><div style={{fontSize:9,color:"#64748b"}}>{pct}%</div></div>
                </div>
                <div style={{height:3,background:"#0f172a",borderRadius:2,marginTop:4,overflow:"hidden"}}><div style={{height:"100%",width:`${Math.min(pct*2.5,100)}%`,background:TC[tier],borderRadius:2}}/></div>
                <div style={{display:"flex",justifyContent:"space-between",marginTop:4,fontSize:9}}>
                  <span style={{color:"#94a3b8"}}>{s.cq} • {s.api} • {s.impl}</span>
                  <span style={{color:p.pnl>=0?"#16a34a":"#ef4444",fontWeight:700}}>{p.pnl>=0?"+":""}£{Math.round(p.pnl)} ({p.pct>0?"+":""}{p.pct.toFixed(0)}%)</span>
                </div>
                {sel===s.t&&<div style={{marginTop:6,paddingTop:6,borderTop:"1px solid #334155"}}>
                  <div style={{display:"flex",gap:4,flexWrap:"wrap",marginBottom:6}}>
                    <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:"#94a3b8"}}>Hz: <b style={{color:s.hz.includes("EXTREME")?"#ef4444":"#16a34a"}}>{s.hz}</b></span>
                    <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:"#94a3b8"}}>Squeeze: <b style={{color:"#f59e0b"}}>{s.sp}</b></span>
                    <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:"#94a3b8"}}>Brent: <b style={{color:"#0d9488"}}>{s.bp}</b></span>
                    <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:"#94a3b8"}}>Action: <b style={{color:"#f1f5f9"}}>{s.act}</b></span>
                  </div>
                  <div style={{fontSize:9,color:"#94a3b8",marginBottom:4}}>CATALYSTS:</div>
                  {s.cats.map((c,i)=><div key={i} style={{display:"flex",alignItems:"center",gap:6,marginBottom:3,fontSize:9}}>
                    <span style={{background:QC[c.q],color:"#fff",padding:"1px 5px",borderRadius:3,fontSize:8,fontWeight:700,minWidth:24,textAlign:"center"}}>{c.q}</span>
                    <span style={{flex:1,color:"#cbd5e1"}}>{c.e}</span>
                    <span style={{color:c.p>=.7?"#16a34a":c.p>=.5?"#f59e0b":"#ef4444",fontWeight:700}}>{(c.p*100).toFixed(0)}%</span>
                  </div>)}
                  <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:4,marginTop:6}}>
                    {["bear","base","bull"].map(c=>{const r=cp(s,c);return(
                      <div key={c} style={{background:"#0f172a",borderRadius:5,padding:4,textAlign:"center"}}>
                        <div style={{fontSize:7,color:SL[c].c,fontWeight:700}}>{c.toUpperCase()}</div>
                        <div style={{fontSize:11,fontWeight:700,color:r.pnl>=0?"#16a34a":"#ef4444"}}>{r.pct>0?"+":""}{r.pct.toFixed(0)}%</div>
                        <div style={{fontSize:8,color:"#64748b"}}>£{Math.round(r.ret)}</div>
                      </div>
                    )})}
                  </div>
                  <div style={{fontSize:8,color:"#ef4444",marginTop:4}}>⚠️ Risk: {s.risk}</div>
                </div>}
              </div>)})}
          </div>)}
        </div>}

        {v==="crude"&&<div>
          <div style={{fontSize:9,color:"#64748b",marginBottom:8}}>SORTED BY CURRENT IMPLIED $/BBL — HIGHEST VALUE FIRST</div>
          {[...S].filter(s=>s.impl!=="Fee-based"&&s.impl!=="Farm-out driven").sort((a,b)=>{
            const av=parseFloat(a.impl.replace(/[^0-9.]/g,''))||0;const bv=parseFloat(b.impl.replace(/[^0-9.]/g,''))||0;return bv-av;
          }).map(s=><div key={s.t} style={{background:"#1e293b",borderRadius:8,padding:"8px 10px",marginBottom:5,borderLeft:`3px solid ${TC[s.tier]}`}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
              <div><span style={{fontWeight:700,fontSize:12,color:"#f1f5f9"}}>{s.t}</span><span style={{fontSize:9,color:"#64748b",marginLeft:6}}>{s.n}</span></div>
              <div style={{fontSize:11,fontWeight:700,color:"#16a34a"}}>{s.impl}</div>
            </div>
            <div style={{display:"flex",gap:6,marginTop:4,flexWrap:"wrap"}}>
              <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:"#f59e0b"}}>{s.cq}</span>
              <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:"#94a3b8"}}>API: {s.api}</span>
              <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:s.bp.includes("+")?"#16a34a":"#94a3b8"}}>Brent: {s.bp}</span>
              <span style={{fontSize:8,background:"#0f172a",padding:"2px 6px",borderRadius:4,color:s.hz.includes("EXTREME")?"#ef4444":"#0d9488"}}>Hz: {s.hz}</span>
            </div>
          </div>)}
        </div>}

        {v==="timeline"&&<div>
          {["Q2","Q3","Q4"].map(q=><div key={q} style={{marginBottom:16}}>
            <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8,padding:"6px 10px",background:`${QC[q]}15`,borderRadius:8,borderLeft:`3px solid ${QC[q]}`}}>
              <span style={{fontSize:14,fontWeight:700,color:QC[q],fontFamily:"Space Grotesk"}}>{q} 2026</span>
              <span style={{fontSize:9,color:"#64748b"}}>{q==="Q2"?"Apr–Jun":q==="Q3"?"Jul–Sep":"Oct–Dec"}</span>
              <span style={{marginLeft:"auto",fontSize:10,color:QC[q],fontWeight:700}}>{allCats.filter(c=>c.q===q).length} events</span>
            </div>
            {allCats.filter(c=>c.q===q).map((c,i)=><div key={i} style={{display:"flex",alignItems:"flex-start",gap:8,marginBottom:4,padding:"6px 8px",background:"#1e293b",borderRadius:6,borderLeft:`2px solid ${TC[c.tier]}`}}>
              <div style={{minWidth:36}}><div style={{fontSize:10,fontWeight:700,color:TC[c.tier]}}>{c.t}</div><div style={{fontSize:7,color:c.p>=.7?"#16a34a":c.p>=.5?"#f59e0b":"#ef4444",fontWeight:700}}>{(c.p*100).toFixed(0)}%</div></div>
              <div style={{fontSize:9,color:"#cbd5e1",lineHeight:1.3}}>{c.e}</div>
            </div>)}
          </div>)}
        </div>}

        {v==="returns"&&<div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:6,marginBottom:14}}>
            {Object.entries(SL).map(([k,info])=>{const t=S.reduce((s,x)=>s+cp(x,k).pnl,0);const r=tot+t;return(
              <div key={k} onClick={()=>setSc(k)} style={{background:sc===k?`${info.c}15`:"#1e293b",borderRadius:8,padding:10,textAlign:"center",border:sc===k?`2px solid ${info.c}`:"1px solid #334155",cursor:"pointer"}}>
                <div style={{fontSize:10,fontWeight:700,color:info.c}}>{info.l}</div>
                <div style={{fontSize:18,fontWeight:700,color:t>=0?"#16a34a":"#ef4444",fontFamily:"Space Grotesk",marginTop:3}}>{t>=0?"+":""}£{Math.round(t).toLocaleString()}</div>
                <div style={{fontSize:9,color:"#64748b",marginTop:1}}>→ £{Math.round(r).toLocaleString()} ({((t/tot)*100).toFixed(0)}%)</div>
              </div>
            )})}
          </div>
          <div style={{fontSize:9,color:"#64748b",marginBottom:6,letterSpacing:1}}>RETURNS — {SL[sc].l} SCENARIO</div>
          {[...S].sort((a,b)=>cp(b,sc).pnl-cp(a,sc).pnl).map(s=>{const p=cp(s,sc);return(
            <div key={s.t} style={{display:"flex",alignItems:"center",gap:6,marginBottom:3,padding:"5px 8px",background:"#1e293b",borderRadius:5}}>
              <div style={{minWidth:36,fontSize:10,fontWeight:700,color:TC[s.tier]}}>{s.t}</div>
              <div style={{flex:1,height:12,position:"relative",background:"#0f172a",borderRadius:2,overflow:"hidden"}}>
                <div style={{position:"absolute",left:p.pct>=0?"50%":"auto",right:p.pct<0?"50%":"auto",width:`${Math.min(Math.abs(p.pct)/10,50)}%`,height:"100%",background:p.pct>=0?"#16a34a50":"#ef444450",borderRadius:2}}/>
                <div style={{position:"absolute",left:"50%",top:0,bottom:0,width:1,background:"#334155"}}/>
              </div>
              <div style={{minWidth:44,textAlign:"right",fontSize:10,fontWeight:700,color:p.pct>=0?"#16a34a":"#ef4444"}}>{p.pct>=0?"+":""}{p.pct.toFixed(0)}%</div>
              <div style={{minWidth:48,textAlign:"right",fontSize:9,color:p.pnl>=0?"#16a34a":"#ef4444"}}>{p.pnl>=0?"+":""}£{Math.round(p.pnl)}</div>
            </div>
          )})}
        </div>}
      </div>

      <div style={{position:"fixed",bottom:0,left:0,right:0,background:"#0f172a",borderTop:"1px solid #1e293b",padding:"5px 16px"}}>
        <div style={{fontSize:7,color:"#475569",textAlign:"center"}}>⚠️ THEORETICAL — Not financial advice. All investments carry risk including total loss. Consult a qualified advisor.</div>
      </div>
    </div>
  );
}
