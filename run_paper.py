"""
Nova Engine — run_paper.py

Paper-training runner for the LOCAL/PARENT model. Wires the live, read-only IBKR
data feed (yfinance fallback) + the Ollama auditor + both asset adapters + the
persistent SQLite ledger, runs a bounded number of engine cycles, and reports
each book's validation status as the training dataset accumulates.

HARD SAFETY: execution goes through the IBKR *paper stub* (connector="stub") — it
NEVER places live orders. The IBKR connection here is the read-only market-data
feed only. This is the "paper until validated" phase of the safety gate.

Usage (from the repo root):
    python run_paper.py                 # 1 cycle, validate, persistent ledger
    python run_paper.py --cycles 5      # a short burst
    python run_paper.py --no-feed       # yfinance only (skip IBKR feed)
    python run_paper.py --db :memory:   # throwaway run, nothing persisted
"""
from __future__ import annotations

import argparse
import logging

import layers.data_loader as dl
from core.context import load_books
from core.engine import Engine, load_engine_config
from core.ledger import Ledger
from adapters.broker_ibkr import IBKRAdapter
from adapters.asset_equity import EquityAdapter
from adapters.asset_fx import FxAdapter
from adapters.ibkr_feed import IBKRDataFeed
from layers.analyst import LLMAuditor
from backtest.validation import validate_from_ledger

log = logging.getLogger("nova.run_paper")

# Simulated paper NAVs by wrapper (the portfolio.yaml account IDs are placeholders
# until the real IBKR sub-accounts are linked; the paper stub uses these).
DEFAULT_NAVS = {"ISA": 4000, "SIPP": 13000, "GIA": 2000, "MARGIN": 5000}


def build_engine(db_path: str = "nova_ledger.db", *, use_feed: bool = True,
                 model_name: str = "qwen2.5:7b-instruct",
                 exec_threshold: float | None = None):
    """Assemble the paper-training engine. Returns (engine, books, ledger, feed)."""
    books = load_books("portfolio.yaml")
    cfg = load_engine_config("config.yaml")
    if exec_threshold is not None:
        # Paper-only override so the operator can deliberately exercise the full
        # open->close->outcome loop while experimenting. Never affects live.
        cfg.exec_threshold = exec_threshold

    feed = None
    if use_feed:
        feed = IBKRDataFeed()  # TWS paper @ 127.0.0.1:7497, readonly
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
    engine = Engine(books, [EquityAdapter(), FxAdapter()], broker, auditor, ledger, cfg)
    return engine, books, ledger, feed


def report_validation(books, ledger) -> None:
    """Print each book's validation verdict against its own profile."""
    print("\n" + "=" * 70)
    print("PER-BOOK VALIDATION (paper — robustness off for the burst)")
    print("=" * 70)
    for ctx in books:
        res = validate_from_ledger(ctx, ledger, run_robustness=False)
        print(res.summary())
        perf = ledger.performance_summary(ctx.book_id)
        print(f"  trades_recorded={perf['trades_recorded']} "
              f"closed={perf['trades_closed']} "
              f"training_samples={len(ledger.training_samples(ctx.book_id))}")
        print("-" * 70)


def run(cycles: int = 1, db_path: str = "nova_ledger.db", *,
        use_feed: bool = True, validate: bool = True,
        exec_threshold: float | None = None) -> None:
    engine, books, ledger, feed = build_engine(db_path, use_feed=use_feed,
                                               exec_threshold=exec_threshold)
    try:
        for i in range(1, cycles + 1):
            log.info("=== cycle %d/%d ===", i, cycles)
            engine.run_cycle()
        if validate:
            report_validation(books, ledger)
    finally:
        if feed is not None:
            feed.disconnect()
        ledger.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Nova paper-training runner (parent model).")
    p.add_argument("--cycles", type=int, default=1, help="number of engine cycles")
    p.add_argument("--db", default="nova_ledger.db", help="ledger path (':memory:' to discard)")
    p.add_argument("--no-feed", action="store_true", help="skip IBKR feed, use yfinance only")
    p.add_argument("--no-validate", action="store_true", help="skip the validation report")
    p.add_argument("--exec-threshold", type=float, default=None,
                   help="paper-only blended-score override (e.g. 55) to exercise trades")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(cycles=args.cycles, db_path=args.db, use_feed=not args.no_feed,
        validate=not args.no_validate, exec_threshold=args.exec_threshold)


if __name__ == "__main__":
    main()
