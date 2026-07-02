"""
Nova Engine — backtest/replay.py

Historical replay harness. Runs the REAL engine cycle-by-cycle over history so
the parent model's training dataset (the 32-marker snapshot + macro regime +
decision + outcome, per book) accumulates fast — months/years of trades in
minutes — instead of waiting on forward paper.

Point-in-time correctness (no lookahead) is the whole game: a `ReplayFeed` is
installed as the data_loader price feed and serves, for every symbol, ONLY the
bars up to the current as-of date. Because the engine reads all prices through
`get_daily_data` / `get_latest_price`, the scanner (32 markers), the macro gate,
correlation, and exit evaluation all become point-in-time automatically — no
engine changes.

Layer 3 uses NeutralAuditor by default (the live LLM is too slow for thousands
of cycles and historical news/fundamentals aren't available point-in-time).

Execution is the paper stub throughout — replay NEVER places a live order.

Usage:
    python -m backtest.replay --years 3
    python -m backtest.replay --start 2022-01-01 --end 2024-12-31 --step 1
"""
from __future__ import annotations

import argparse
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Optional

import pandas as pd

import layers.data_loader as dl
from core.context import Order, load_books
from core.engine import Engine, load_engine_config
from core.ledger import Ledger
from adapters.broker_ibkr import IBKRAdapter
from adapters.asset_equity import EquityAdapter
from adapters.asset_fx import FxAdapter
from adapters.asset_allocation import AllocationAdapter
from layers.analyst import NeutralAuditor
from backtest.validation import validate_from_ledger

log = logging.getLogger("nova.replay")

# Paper starting NAVs by wrapper (replay equity curve starts here, then compounds
# with realised PnL via broker.set_simulated_nav each cycle).
DEFAULT_NAVS = {"ISA": 4000, "SIPP": 13000, "GIA": 2000, "MARGIN": 5000}


# Long-history PROXY map: young UK-listed Acc funds (post-2019 inceptions) that
# post-date the validation window are backfilled PRE-inception with a scaled
# long-history proxy, so the historical replay can hold the full basket and produce
# a real, reproducible per-book verdict instead of a broken young-ticker curve.
# HONEST: recent years use the ACTUAL fund (direct); only the deep past — which
# physically has no data (the fund didn't exist) — is proxied. The LIVE config is
# unaffected; this is a validation-harness aid only.
HISTORICAL_PROXIES = {
    "SMGB.L": "SOXX",   # L&G US Semiconductors  -> iShares Semiconductor (2001)
    "REGB.L": "REMX",   # VanEck Rare Earth      -> VanEck Rare Earth/Strategic Metals (2010)
    "VPNG.L": "VNQ",    # Global X Data-Centre   -> Vanguard REIT (2004)
    "AIAG.L": "QQQ",    # L&G Artificial Intel.  -> Nasdaq-100 (1999)
    "INRA.L": "ICLN",   # iShares Clean Energy   -> iShares Global Clean Energy (2008)
    "ROBG.L": "QQQ",    # L&G ROBO Robotics      -> Nasdaq-100 (tech growth, 1999)
    "VWRP.L": "ACWI",   # Vanguard FTSE All-World-> MSCI ACWI (2008)
    "URNP.L": "URA",    # Sprott Uranium Miners  -> Global X Uranium (2010)
    "GCP.L":  "IGF",    # GCP Infrastructure     -> iShares Global Infrastructure (2007)
    "BRWM.L": "XME",    # BlackRock World Mining -> SPDR Metals & Mining (2006)
    "SGLN.L": "GLD",    # iShares Physical Gold  -> SPDR Gold (2004)
    "IGLG.L": "GLD",    # iShares Physical Gold  -> SPDR Gold (2004)
    "IUKD.L": "IDV",    # iShares UK Dividend    -> iShares Intl Dividend (2007; IUKD.L itself is 2005)
}


def _raw_history(symbol: str) -> pd.DataFrame:
    """Fetch a symbol's FULL history once (yfinance), normalised to naive dates.

    Must bypass get_daily_data (which routes through the feed) to avoid recursion.
    """
    import yfinance as yf
    from layers.data_loader import to_yf_symbol
    df = yf.Ticker(to_yf_symbol(symbol)).history(period="max")   # spot-FX -> "EURUSD=X"
    if df is None or df.empty:
        return pd.DataFrame()
    idx = pd.to_datetime(df.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    df = df.copy()
    df.index = idx.normalize()
    return df


def _default_loader(symbol: str) -> pd.DataFrame:
    """Proxy-aware history loader (the replay default).

    For a symbol in HISTORICAL_PROXIES: serve its REAL history where it exists and
    splice a SCALED long-history proxy onto the pre-inception past (continuous at the
    join, no price jump). Everything else loads raw. Pass ``loader=_raw_history`` to
    run_replay for a no-proxy (raw-ticker) run.
    """
    real = _raw_history(symbol)
    proxy_sym = HISTORICAL_PROXIES.get(symbol)
    if not proxy_sym:
        return real
    proxy = _raw_history(proxy_sym)
    if proxy is None or proxy.empty:
        return real
    if real is None or real.empty:
        log.info("[replay] %s: no real history -> using proxy %s in full", symbol, proxy_sym)
        return proxy
    join = real.index[0]
    before = proxy[proxy.index < join]
    if before.empty:
        return real
    try:
        ratio = float(real["Close"].iloc[0]) / float(before["Close"].iloc[-1])
    except (ZeroDivisionError, ValueError, TypeError):
        return real
    before = before.copy()
    for c in ("Open", "High", "Low", "Close"):
        if c in before.columns:
            before[c] = before[c] * ratio
    spliced = pd.concat([before, real])
    log.info("[replay] %s: proxy %s backfills pre-%s (%d rows) + real after (%d rows)",
             symbol, proxy_sym, join.date(), len(before), len(real))
    return spliced


class ReplayFeed:
    """data_loader price feed that serves point-in-time history.

    Lazily loads each symbol's full history once, then returns only the bars up
    to `as_of`. Returned frames are copies so the scanner's in-place indicator
    appends never corrupt the cache.
    """

    def __init__(self, loader: Optional[Callable[[str], pd.DataFrame]] = None):
        self._full: dict[str, pd.DataFrame] = {}
        self.as_of: Optional[pd.Timestamp] = None
        self._loader = loader or _default_loader

    def set_as_of(self, date) -> None:
        self.as_of = pd.Timestamp(date).normalize()

    def is_connected(self) -> bool:
        return self.as_of is not None

    def full_history(self, symbol: str) -> pd.DataFrame:
        if symbol not in self._full:
            self._full[symbol] = self._loader(symbol)
        return self._full[symbol]

    def get_daily_bars(self, symbol: str, lookback_days: int = 365) -> pd.DataFrame:
        df = self.full_history(symbol)
        if df is None or df.empty or self.as_of is None:
            return pd.DataFrame()
        sl = df[df.index <= self.as_of]
        if lookback_days:
            sl = sl.tail(lookback_days)
        return sl.copy()

    def get_price(self, symbol: str):
        sl = self.get_daily_bars(symbol, lookback_days=5)
        if sl.empty or "Close" not in sl.columns:
            return None
        return Decimal(str(sl["Close"].iloc[-1]))


def _force_close_all(engine: Engine, books, label: str = "end-of-replay") -> None:
    """Mark every still-open position to the final as-of price so all trades have
    an outcome (and the dataset has complete labels)."""
    for ctx in books:
        for pos in engine.ledger.open_trades(ctx.book_id):
            price = dl.get_latest_price(pos["symbol"])
            if price is None:
                continue
            entry = Decimal(str(pos["price"]))
            qty = Decimal(str(pos["quantity"]))
            side = pos.get("side", "BUY")
            if side == "SELL":                                 # short: PnL inverts, cover with BUY
                realized = (entry - price) * qty
                close_side = "BUY"
            else:
                realized = (price - entry) * qty
                close_side = "SELL"
            offset = Order(book_id=ctx.book_id, account_id=pos["account_id"],
                           symbol=pos["symbol"], side=close_side, quantity=qty,
                           price=price, notional=(price * qty))
            engine.broker.place(offset, ctx)
            engine.ledger.close_trade(pos["id"], price, realized)
            log.info("[%s] CLOSE %s %s (%s) @ %s pnl=%s", ctx.book_id, side,
                     pos["symbol"], label, price, realized)


def report(books, ledger) -> None:
    print("\n" + "=" * 70)
    print("PER-BOOK VALIDATION (historical replay dataset)")
    print("=" * 70)
    for ctx in books:
        res = validate_from_ledger(ctx, ledger, run_robustness=True, seed=42)
        print(res.summary())
        perf = ledger.performance_summary(ctx.book_id)
        print(f"  trades_closed={perf['trades_closed']} "
              f"realized_pnl={ledger.realized_pnl_total(ctx.book_id):.2f} "
              f"training_samples={len(ledger.training_samples(ctx.book_id))}")
        print("-" * 70)


def run_replay(start, end, *, db_path: str = "nova_replay.db", step_days: int = 1,
               exec_threshold: float = 50.0, gate_min: Optional[float] = None,
               auditor=None, adapters=None, books=None,
               loader: Optional[Callable[[str], pd.DataFrame]] = None,
               calendar_symbol: str = "SPY", do_report: bool = True) -> Ledger:
    """Replay the engine over [start, end]. Returns the (open) Ledger.

    `adapters` defaults to the live [EquityAdapter, FxAdapter]; inject custom
    adapters for testing. `books` defaults to portfolio.yaml; inject modified
    books for experiments (e.g. tuned sizing) without touching the manifest.
    `gate_min` overrides the macro-gate floor (else uses config). The caller owns
    the returned ledger and should close().
    """
    feed = ReplayFeed(loader=loader)
    dl.set_price_feed(feed)
    try:
        books = books if books is not None else load_books("portfolio.yaml")
        cfg = load_engine_config("config.yaml")
        cfg.exec_threshold = exec_threshold
        if gate_min is not None:
            cfg.gate_min = gate_min

        start_navs = {b.ibkr_account_id: DEFAULT_NAVS.get(b.wrapper, 5000) for b in books}
        broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs=dict(start_navs))
        broker.connect()
        ledger = Ledger(db_path)
        engine = Engine(books, adapters or [EquityAdapter(), FxAdapter(), AllocationAdapter()],
                        broker, auditor or NeutralAuditor(), ledger, cfg)

        # Trading calendar from the reference symbol's point-in-time index.
        feed.set_as_of(end)
        ref = feed.full_history(calendar_symbol)
        if ref is None or ref.empty:
            raise RuntimeError(f"no history for calendar symbol {calendar_symbol!r}")
        lo, hi = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
        calendar = [d for d in ref.index if lo <= d <= hi][::max(1, step_days)]
        log.info("Replaying %d trading steps from %s to %s (step=%d)",
                 len(calendar), lo.date(), hi.date(), step_days)

        for i, d in enumerate(calendar, 1):
            feed.set_as_of(d)
            # MARK-TO-MARKET equity curve: NAV = start + realised PnL + unrealised
            # P&L of open positions (priced at the as-of close). Realized-only NAV
            # is flat during holds and understates true drawdown — wrong especially
            # for buy-and-hold. This records the honest equity curve for validation.
            for b in books:
                nav = start_navs[b.ibkr_account_id] + ledger.realized_pnl_total(b.book_id)
                for pos in ledger.open_trades(b.book_id):
                    px = dl.get_latest_price(pos["symbol"])
                    if px is not None:
                        delta = float(px - Decimal(str(pos["price"]))) * float(pos["quantity"])
                        nav += -delta if pos.get("side") == "SELL" else delta   # short P&L inverts
                broker.set_simulated_nav(b.ibkr_account_id, nav)
            engine.run_cycle()
            if i % 25 == 0:
                log.info("  ...step %d/%d (%s)", i, len(calendar), d.date())

        _force_close_all(engine, books)
        if do_report:
            report(books, ledger)
        return ledger
    finally:
        dl.set_price_feed(None)


def main() -> None:
    p = argparse.ArgumentParser(description="Nova historical replay harness (parent dataset).")
    p.add_argument("--start", default=None, help="YYYY-MM-DD (default: end - years)")
    p.add_argument("--end", default=None, help="YYYY-MM-DD (default: today)")
    p.add_argument("--years", type=float, default=3.0, help="window length if --start omitted")
    p.add_argument("--step", type=int, default=1, help="trading-day step (1 = every day)")
    p.add_argument("--db", default="nova_replay.db", help="ledger path for the dataset")
    p.add_argument("--exec-threshold", type=float, default=50.0, help="blended score to act")
    p.add_argument("--gate-min", type=float, default=None, help="macro-gate floor override")
    p.add_argument("--no-proxies", action="store_true",
                   help="disable long-history proxy backfill (raw tickers only; young "
                        "funds will be untradeable pre-inception)")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    end = pd.Timestamp(args.end) if args.end else pd.Timestamp(datetime.utcnow().date())
    start = pd.Timestamp(args.start) if args.start else end - timedelta(days=int(args.years * 365))
    ledger = run_replay(start, end, db_path=args.db, step_days=args.step,
                        exec_threshold=args.exec_threshold, gate_min=args.gate_min,
                        loader=(_raw_history if args.no_proxies else None))
    ledger.close()


if __name__ == "__main__":
    main()
