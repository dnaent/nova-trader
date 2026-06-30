"""
Nova Engine — run_intraday.py

Continuous 5-minute loop for intraday strategies (FX, Crypto, ISA Intraday sleeve).
Wires the IntradayAdapter, FrictionSizing, and the LLMAuditor.
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timedelta

import layers.data_loader as dl
from core.context import load_books
from core.engine import Engine, load_engine_config
from core.ledger import Ledger
from adapters.broker_ibkr import IBKRAdapter
from adapters.asset_intraday import HybridIntradayAdapter
from adapters.ibkr_feed import IBKRDataFeed
from layers.analyst import LLMAuditor

log = logging.getLogger("nova.run_intraday")

DEFAULT_NAVS = {"ISA": 4000, "SIPP": 13000, "GIA": 2000, "MARGIN": 5000}

def build_engine(db_path: str = "nova_ledger.db", *, use_feed: bool = True,
                 model_name: str = "qwen2.5:7b-instruct",
                 exec_threshold: float | None = None):
    # Only load books configured for intraday
    all_books = load_books("portfolio.yaml")
    books = [b for b in all_books if b.strategy == "intraday"]
    
    cfg = load_engine_config("config.yaml")
    if exec_threshold is not None:
        cfg.exec_threshold = exec_threshold

    feed = None
    if use_feed:
        import os
        port = int(os.environ.get("NOVA_IBKR_PORT", "7497"))
        # Distinct clientId from run_paper's feed (17) so both can hold IBKR
        # connections concurrently (IBKR rejects duplicate clientIds).
        feed = IBKRDataFeed(port=port, client_id=18)
        if feed.connect():
            dl.set_price_feed(feed)
            log.info("Live IBKR data feed engaged (read-only).")
        else:
            log.info("IBKR feed unavailable — using yfinance fallback.")

    simulated_navs = {b.ibkr_account_id: DEFAULT_NAVS.get(b.wrapper, 5000) for b in books}
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs=simulated_navs)
    broker.connect()

    auditor = LLMAuditor(backend="local", model_name=model_name)
    ledger = Ledger(db_path)
    broker.seed_positions(ledger.open_trades())

    # HYBRID intraday adapters — one instance PER asset class so each carries its own
    # trend-REGIME gate (cached per adapter id by the engine): FX gates on the US-Dollar
    # index, Crypto on Bitcoin (the complex leader), equity intraday on the macro gate.
    # Each merges the daily trend skeleton with intraday momentum confluence and degrades
    # to the daily skeleton when intraday data is unavailable (replay).
    adapters = [
        HybridIntradayAdapter(asset_class="FX", handles={"FX"},
                              regime_symbol="DX-Y.NYB", friction_buffer=0.0001),
        HybridIntradayAdapter(asset_class="CRYPTO", handles={"CRYPTO"},
                              regime_symbol="BTC-USD", friction_buffer=0.001),
        HybridIntradayAdapter(asset_class="EQUITY", handles={"EQUITY", "ETF"},
                              regime_symbol=None, friction_buffer=0.0005),
    ]
    engine = Engine(books, adapters, broker, auditor, ledger, cfg)
    return engine, books, ledger, feed

def sleep_until_next_5m_mark():
    now = datetime.now()
    # Calculate minutes to next 5-minute mark
    next_min = ((now.minute // 5) + 1) * 5
    next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_min)
    sleep_seconds = (next_time - now).total_seconds()
    log.info(f"Sleeping for {sleep_seconds:.1f} seconds until {next_time.strftime('%H:%M:%S')}...")
    time.sleep(sleep_seconds)

def run(cycles: int | None = None, db_path: str = "nova_ledger.db", *,
        use_feed: bool = True, exec_threshold: float | None = None) -> None:
    engine, books, ledger, feed = build_engine(db_path, use_feed=use_feed, exec_threshold=exec_threshold)
    
    if not books:
        log.warning("No intraday books found in portfolio.yaml. Exiting.")
        return

    log.info(f"Loaded {len(books)} intraday books: {[b.book_id for b in books]}")
    
    try:
        i = 1
        while True:
            log.info("=== Intraday Cycle %d ===", i)
            engine.run_cycle()
            
            if cycles is not None and i >= cycles:
                break
                
            sleep_until_next_5m_mark()
            i += 1
            
    except KeyboardInterrupt:
        log.info("Intraday runner stopped by user.")
    finally:
        if feed is not None:
            feed.disconnect()
        ledger.close()

def main() -> None:
    p = argparse.ArgumentParser(description="Nova intraday paper-training runner.")
    p.add_argument("--cycles", type=int, default=None, help="limit number of engine cycles (default: run forever)")
    p.add_argument("--db", default="nova_ledger.db", help="ledger path")
    p.add_argument("--no-feed", action="store_true", help="skip IBKR feed, use yfinance only")
    p.add_argument("--exec-threshold", type=float, default=None,
                   help="paper-only blended-score override to exercise trades")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(cycles=args.cycles, db_path=args.db, use_feed=not args.no_feed, exec_threshold=args.exec_threshold)

if __name__ == "__main__":
    main()
