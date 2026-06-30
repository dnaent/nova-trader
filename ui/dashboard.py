"""
Nova Engine — ui/dashboard.py

Local terminal dashboard using 'rich'.
Run with: python -m ui.dashboard
"""
import time
import sqlite3
from datetime import datetime, timezone
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console

from core.ledger import Ledger
from core.context import load_books
from core.engine import load_engine_config

def generate_dashboard() -> Layout:
    ledger = Ledger()
    # Read books for context
    try:
        books = load_books("portfolio.yaml")
    except Exception:
        books = []

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="portfolio", size=15),
        Layout(name="activity")
    )
    
    # 1. Header
    try:
        latest_decision = ledger.conn.execute("SELECT gate FROM decisions ORDER BY ts DESC LIMIT 1").fetchone()
        gate_score = f"{latest_decision['gate']:.1f}" if latest_decision and latest_decision['gate'] else "N/A"
    except Exception:
        gate_score = "N/A"
        
    header = Panel(f"Nova Engine Dashboard | Local Time: {datetime.now().strftime('%H:%M:%S')} | Macro Gate: {gate_score}", style="bold cyan")
    layout["header"].update(header)
    
    # 2. Portfolio Summary Table
    table = Table(title="Live Portfolio Guardrails & Summary", expand=True)
    table.add_column("Book ID")
    table.add_column("NAV")
    table.add_column("Peak NAV")
    table.add_column("Drawdown %")
    table.add_column("Daily Loss %")
    table.add_column("Total Realized PnL")
    
    for book in books:
        peak = ledger.get_peak_nav(book.book_id) or 0.0
        latest_nav_row = ledger.conn.execute("SELECT nav FROM nav_history WHERE book_id=? ORDER BY ts DESC LIMIT 1", (book.book_id,)).fetchone()
        nav = latest_nav_row["nav"] if latest_nav_row else 0.0
        
        drawdown = 0.0
        if peak > 0:
            drawdown = ((peak - float(nav)) / peak) * 100.0
            
        daily_loss = ledger.get_daily_loss_pct(book.book_id, nav)
        
        perf = ledger.performance_summary(book.book_id)
        pnl = perf.get("total_realized_pnl", 0.0)
        
        table.add_row(
            book.book_id,
            f"£{nav:,.2f}",
            f"£{peak:,.2f}",
            f"{drawdown:.2f}%",
            f"{daily_loss:.2f}%",
            f"£{pnl:,.2f}"
        )
        
    if not books:
        table.add_row("No books found", "", "", "", "", "")
        
    layout["portfolio"].update(table)
    
    # 3. Activity Table
    act_table = Table(title="Recent Engine Decisions (Layer 1-3)", expand=True)
    act_table.add_column("Time")
    act_table.add_column("Book")
    act_table.add_column("Symbol")
    act_table.add_column("Gate")
    act_table.add_column("Quant Score")
    act_table.add_column("Auditor Score")
    act_table.add_column("Blended")
    act_table.add_column("Action")
    act_table.add_column("Reason")
    
    try:
        decisions = ledger.conn.execute("SELECT * FROM decisions ORDER BY ts DESC LIMIT 10").fetchall()
        for d in decisions:
            ts = d["ts"].split("T")[1][:8] if "T" in d["ts"] else d["ts"]
            act_table.add_row(
                ts,
                d["book_id"],
                d["symbol"] or "-",
                f"{d['gate']:.1f}" if d['gate'] else "-",
                f"{d['quant_score']:.1f}" if d['quant_score'] else "-",
                f"{d['claude_score']:.1f}" if d['claude_score'] else "-",
                f"{d['blended']:.1f}" if d['blended'] else "-",
                "EXECUTE" if d['acted'] else "SKIP",
                d["reason"] or ""
            )
    except Exception:
        act_table.add_row("Error loading decisions", "", "", "", "", "", "", "", "")
        
    layout["activity"].update(act_table)
    
    return layout

def main():
    console = Console()
    console.clear()
    with Live(generate_dashboard(), refresh_per_second=1, screen=True) as live:
        try:
            while True:
                time.sleep(2)
                live.update(generate_dashboard())
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
