"""
Nova Engine — core/engine.py

The generic cycle loop. It is identical across every book and every asset class:
    macro gate -> deterministic scan -> Claude audit -> blend (60/40)
    -> permission check -> NAV sizing -> broker.place -> ledger

Run the self-contained demo from the repo root:
    python -m core.engine
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal

from core.context import AccountContext, AssetAdapter, BrokerAdapter, Candidate, Order
from core.ledger import Ledger
from layers.analyst import Auditor

log = logging.getLogger("nova.engine")

@dataclass
class EngineConfig:
    gate_min: float = 40.0          # below this, hold cash (no new buys)
    exec_threshold: float = 75.0    # blended score required to act
    top_n: int = 10
    # universe may be a flat list (applies to every adapter) OR a mapping of
    # asset_class -> [symbols] so each adapter scans only its own asset classes.
    universe: object = field(default_factory=list)
    aggressive_liquidation: bool = False
    allocation_basket: list = field(default_factory=list)  # SIPP path-A thematic basket

    def universe_for(self, handles: set) -> list:
        """Return the symbols an adapter should scan, given its `handles` set.

        Backward-compatible: a flat-list universe is returned to every adapter;
        a dict universe is filtered to the adapter's asset classes. Keeps any
        asset-class knowledge out of core — the adapter declares what it handles.
        """
        u = self.universe
        if isinstance(u, dict):
            symbols: list = []
            for asset_class in handles:
                symbols.extend(u.get(asset_class, []))
            return symbols
        return list(u or [])

def load_engine_config(path: str) -> EngineConfig:
    """Build an EngineConfig from config.yaml (yaml imported lazily)."""
    import yaml
    with open(path, "r", encoding="utf-8") as fh:
        d = yaml.safe_load(fh) or {}
    return EngineConfig(
        gate_min=d.get("gate_min", 40.0),
        exec_threshold=d.get("exec_threshold", 75.0),
        top_n=d.get("top_n", 10),
        universe=d.get("universe", []),
        aggressive_liquidation=d.get("aggressive_liquidation", False),
        allocation_basket=d.get("allocation_basket", []),
    )

class Engine:
    def __init__(self, books: list[AccountContext], asset_adapters: list[AssetAdapter],
                 broker: BrokerAdapter, auditor: Auditor, ledger: Ledger,
                 config: EngineConfig):
        self.books = books
        self.asset_adapters = asset_adapters
        self.broker = broker
        self.auditor = auditor
        self.ledger = ledger
        self.cfg = config
        self._cb_cooldown: dict[str, int] = {}   # book_id -> remaining circuit-breaker cooldown cycles
        self._cb_seen: dict[str, int] = {}       # book_id -> closed-trade count at the last trip (streak baseline)
        self._crash_state: dict[str, str] = {}   # book_id -> crash de-risk state ("armed"|"confirmed"|absent)
        self._crash_peak: dict[str, float] = {}  # book_id -> crash de-risk high-water mark (resets on re-entry)

    def _evaluate_exits(self, ctx: AccountContext) -> None:
        """Mark open positions to market and close any that hit stop / take-profit.

        Runs before new entries each cycle so existing risk is managed first. The
        position is filled at the stop/take LEVEL (standard backtest convention),
        giving clean R-multiples; close_trade() backfills realized PnL + R onto the
        linked training record. Daily-resolution for now — intrabar fills need tick
        data. Long-only paper; never executes live (paper stub).
        """
        from layers.data_loader import get_latest_price
        for pos in self.ledger.open_trades(ctx.book_id):
            price = get_latest_price(pos["symbol"])
            if price is None:
                continue
            side = pos.get("side", "BUY")
            # Trailing stop (FX trend-following): ratchet the stop toward price so
            # winners run and exit only on a trend reversal. Only positions sized
            # with a trailing_atr trail; equities (trailing_atr NULL) keep their
            # fixed stop unchanged.
            self._update_trailing_stop(pos, price, side)
            stop = Decimal(str(pos["stop_loss"])) if pos["stop_loss"] is not None else None
            take = Decimal(str(pos["take_profit"])) if pos["take_profit"] is not None else None

            exit_price = reason = None
            if side == "SELL":
                # Short: stop is ABOVE entry (loss), take-profit BELOW (gain).
                if stop is not None and price >= stop:
                    exit_price, reason = stop, "stop-loss"
                elif take is not None and price <= take:
                    exit_price, reason = take, "take-profit"
            else:
                if stop is not None and price <= stop:
                    exit_price, reason = stop, "stop-loss"
                elif take is not None and price >= take:
                    exit_price, reason = take, "take-profit"
            if exit_price is None:
                continue
            self._close_position(ctx, pos, exit_price, reason)

    def _circuit_broken(self, ctx: AccountContext) -> bool:
        """True if the book's consecutive-loss circuit breaker is tripped (pause new
        entries). Opt-in: guardrails.circuit_breaker_losses must be set (None for
        equities => never trips). State (cooldown) lives on the engine instance, so
        it persists across cycles within a run and resets on restart."""
        n = ctx.guardrails.circuit_breaker_losses
        if not n:
            return False
        remaining = self._cb_cooldown.get(ctx.book_id, 0)
        if remaining > 0:
            self._cb_cooldown[ctx.book_id] = remaining - 1
            log.info("[%s] Circuit breaker active (%d cycles left). Holding entries.",
                     ctx.book_id, remaining)
            return True
        # Count the trailing run of consecutive losses among trades closed AFTER the
        # last trip's baseline. Without the baseline the same old streak would re-trip
        # immediately after every cooldown (entries are paused, so no new winner can
        # break it) — freezing the book. Serving the cooldown IS the reset.
        closed = self.ledger._closed_pnls(ctx.book_id)
        baseline = self._cb_seen.get(ctx.book_id, 0)
        streak = 0
        for pnl in reversed(closed[baseline:]):
            if pnl < 0:
                streak += 1
            else:
                break
        if streak >= n:
            self._cb_cooldown[ctx.book_id] = ctx.guardrails.circuit_breaker_cooldown
            self._cb_seen[ctx.book_id] = len(closed)     # consume this streak; don't recount it
            log.warning("[%s] Circuit breaker TRIPPED (%d consecutive losses). "
                        "Pausing entries for %d cycles.", ctx.book_id, streak,
                        ctx.guardrails.circuit_breaker_cooldown)
            return True
        return False

    def _update_trailing_stop(self, pos: dict, price: Decimal, side: str) -> None:
        """Ratchet a trailing stop toward price (FX trend-following). No-op for
        positions without a trailing_atr (e.g. equities) — their fixed stop holds.
        Long: stop only rises (price - n*ATR). Short: stop only falls (price + n*ATR).
        Mutates pos['stop_loss'] in place and persists it."""
        trail = pos.get("trailing_atr")
        if trail is None:
            return
        from core.risk import calculate_atr
        atr = calculate_atr(pos["symbol"])
        if atr <= 0:
            return
        dist = Decimal(str(trail)) * atr
        cur = Decimal(str(pos["stop_loss"])) if pos["stop_loss"] is not None else None
        if side == "SELL":
            new_stop = price + dist
            if cur is None or new_stop < cur:
                pos["stop_loss"] = float(new_stop)
                self.ledger.update_stop(pos["id"], new_stop)
        else:
            new_stop = price - dist
            if cur is None or new_stop > cur:
                pos["stop_loss"] = float(new_stop)
                self.ledger.update_stop(pos["id"], new_stop)

    def _close_position(self, ctx: AccountContext, pos: dict, exit_price: Decimal,
                        reason: str) -> None:
        """Close one open position at exit_price: places the offsetting paper order
        + ledger close (which backfills realized PnL + R onto the training record).
        Shared by stop/take exits and regime de-risk liquidation. Direction-aware:
        a long (BUY) is closed by a SELL with PnL (exit-entry)*qty; a short (SELL)
        is closed by a BUY with PnL (entry-exit)*qty."""
        entry = Decimal(str(pos["price"]))
        qty = Decimal(str(pos["quantity"]))
        side = pos.get("side", "BUY")
        if side == "SELL":
            realized = (entry - exit_price) * qty
            close_side = "BUY"
        else:
            realized = (exit_price - entry) * qty
            close_side = "SELL"
        offset = Order(book_id=ctx.book_id, account_id=pos["account_id"],
                       symbol=pos["symbol"], side=close_side, quantity=qty,
                       price=exit_price, notional=(exit_price * qty))
        self.broker.place(offset, ctx)                         # nets the paper position flat
        self.ledger.close_trade(pos["id"], exit_price, realized)
        log.info("[%s] EXIT %s %s (%s) @ %s pnl=%s", ctx.book_id, side, pos["symbol"],
                 reason, exit_price, realized)

    def _liquidate_all(self, ctx: AccountContext, reason: str = "regime de-risk") -> None:
        """Close every open position at the current market price (regime de-risk).
        Unlike the old path, this fills at the real price and records realized PnL."""
        from layers.data_loader import get_latest_price
        for pos in self.ledger.open_trades(ctx.book_id):
            price = get_latest_price(pos["symbol"])
            if price is not None:
                self._close_position(ctx, pos, price, reason)

    def run_cycle(self) -> None:
        # Within one cycle the macro gate and scan are identical for every book
        # sharing an adapter + universe (e.g. the three equity books). Cache them
        # so the (expensive) gate fetch and per-symbol model fit run once, not
        # once per book. Candidates are read-only downstream, so sharing is safe.
        gate_cache: dict = {}
        scan_cache: dict = {}
        for ctx in self.books:
            ctx.nav = self.broker.refresh_nav(ctx)

            # 1. Update NAV history
            self.ledger.record_nav(ctx.book_id, ctx.nav)

            # 1b. Manage existing risk first: close positions that hit stop/take.
            self._evaluate_exits(ctx)

            log.info("[%s] %s nav=%s allowed=%s", ctx.book_id, ctx.wrapper,
                     ctx.nav, sorted(ctx.allowed_assets))

            # 2. Check Drawdown Limit
            peak_nav = self.ledger.get_peak_nav(ctx.book_id) or float(ctx.nav)
            if peak_nav > 0:
                drawdown = ((peak_nav - float(ctx.nav)) / peak_nav) * 100.0
                if drawdown >= ctx.guardrails.max_drawdown_pct:
                    log.warning("[%s] Max drawdown breached (%.1f%% >= %.1f%%). Pausing new buys.", 
                                ctx.book_id, drawdown, ctx.guardrails.max_drawdown_pct)
                    continue

            # 3. Check Daily Loss Cap
            daily_loss = self.ledger.get_daily_loss_pct(ctx.book_id, ctx.nav)
            if daily_loss >= ctx.guardrails.daily_loss_cap_pct:
                log.warning("[%s] Daily loss cap breached (%.1f%% >= %.1f%%). Pausing new buys.", 
                            ctx.book_id, daily_loss, ctx.guardrails.daily_loss_cap_pct)
                continue

            # 4. Check Max Concurrent Positions
            open_positions = self.broker.positions(ctx)
            if len(open_positions) >= ctx.guardrails.max_concurrent_positions:
                log.info("[%s] Max concurrent positions (%d) reached. Skipping scans.",
                         ctx.book_id, len(open_positions))
                continue

            # 5. Consecutive-loss circuit breaker (opt-in per book; off for equities).
            #    After N consecutive losing closed trades, pause NEW entries for a
            #    cooldown so a trend strategy doesn't keep re-entering a choppy regime.
            #    Existing positions still exit normally above.
            if self._circuit_broken(ctx):
                continue

            for adapter in self.asset_adapters:
                if not (adapter.handles & ctx.allowed_assets):
                    continue  # this adapter's asset classes aren't permitted here
                if getattr(adapter, "strategy", "tactical") != getattr(ctx, "strategy", "tactical"):
                    continue  # this book runs a different strategy family (e.g. allocation)

                if id(adapter) not in gate_cache:
                    gate_cache[id(adapter)] = adapter.macro_gate()
                gate = gate_cache[id(adapter)]
                book_gate_min = ctx.gate_min if ctx.gate_min is not None else self.cfg.gate_min
                derisk_floor = ctx.derisk_gate if ctx.derisk_gate is not None else book_gate_min

                # Crash de-risk circuit-breaker (opt-in: guardrails.crash_derisk_dd_pct).
                # The HMM macro gate LAGS a slow grind-down (e.g. Oct-2007 -> mid-2008
                # stayed above the floor while equity bled 15%+). This actively
                # liquidates to cash the moment the book's mark-to-market drawdown
                # breaches the threshold — capping the tail near that level — then
                # BLOCKS re-entry until the regime is CONFIRMED to have turned (gate
                # falls below the de-risk floor) AND recovered (gate back >= the entry
                # floor). Re-entry is regime-gated, NOT drawdown-gated: cash can't
                # recover NAV (a DD-based re-entry would deadlock), and re-entering on
                # the still-lagging-high gate would churn straight back into the grind.
                crash_dd = ctx.guardrails.crash_derisk_dd_pct
                if crash_dd is not None:
                    nav_f = float(ctx.nav)
                    state = self._crash_state.get(ctx.book_id)
                    # Crash high-water mark, tracked on the engine (NOT the ledger's
                    # all-time peak): it resets to the re-entry NAV on disarm so a
                    # post-crash re-entry — still below the pre-crash peak — isn't
                    # measured against that old peak and re-tripped immediately, and
                    # can ride the recovery.
                    peak = max(self._crash_peak.get(ctx.book_id, nav_f), nav_f)
                    self._crash_peak[ctx.book_id] = peak
                    if state is None:
                        dd = ((peak - nav_f) / peak) * 100.0 if peak > 0 else 0.0
                        if dd >= crash_dd:
                            self._liquidate_all(ctx, reason=f"crash de-risk (DD {dd:.1f}% >= {crash_dd:.1f}%)")
                            self._crash_state[ctx.book_id] = "armed"
                            log.warning("[%s] CRASH de-risk TRIPPED (DD %.1f%% >= %.1f%%). "
                                        "Cash until regime recovers.", ctx.book_id, dd, crash_dd)
                            continue
                    else:
                        if state == "armed" and gate < derisk_floor:
                            self._crash_state[ctx.book_id] = state = "confirmed"
                        if state == "confirmed" and gate >= book_gate_min:
                            self._crash_state[ctx.book_id] = None
                            self._crash_peak[ctx.book_id] = nav_f      # reset HWM at re-entry
                            log.info("[%s] CRASH de-risk CLEARED (gate %.0f >= %.0f). Re-entry enabled.",
                                     ctx.book_id, gate, book_gate_min)
                            # fall through: re-entry permitted this cycle
                        else:
                            if self.broker.positions(ctx):     # ensure flat while waiting
                                self._liquidate_all(ctx, reason="crash de-risk hold")
                            continue

                if gate < book_gate_min:
                    self.ledger.record_decision(ctx.book_id, None, gate, None, None,
                                                None, acted=False,
                                                reason="macro gate below floor")
                    log.info("[%s] gate %.0f < %.0f — holding cash (no new entries)",
                             ctx.book_id, gate, book_gate_min)
                    # Regime de-risk uses a separate (typically lower) exit floor
                    # (derisk_floor, computed above) so positions hold through minor
                    # dips and only liquidate on genuine deterioration — anti-whipsaw.
                    if (ctx.aggressive_liquidation or self.cfg.aggressive_liquidation) \
                            and gate < derisk_floor:
                        self._liquidate_all(ctx, reason="regime de-risk")
                    continue

                open_symbols = [p["symbol"] for p in open_positions]

                # Per-book watchlist (e.g. ISA=UK, GIA=US) overrides the shared
                # asset-class universe; falls back to config when the book has none.
                scan_universe = ctx.universe if getattr(ctx, "universe", None) \
                    else self.cfg.universe_for(adapter.handles)
                scan_key = (id(adapter), tuple(scan_universe))
                if scan_key not in scan_cache:
                    scan_cache[scan_key] = adapter.scan(scan_universe)
                for c in scan_cache[scan_key][: self.cfg.top_n]:
                    # HARD permission rule
                    if c.asset_class not in ctx.allowed_assets:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, None, None, acted=False,
                                                     reason=f"{c.asset_class} not permitted")
                        continue

                    # Correlation Guardrail
                    from core.risk import check_correlation
                    is_correlated, corr_reason = check_correlation(c.symbol, open_symbols, ctx.guardrails.max_correlation)
                    if is_correlated:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, None, None, acted=False,
                                                     reason=corr_reason)
                        log.info("[%s] Skip %s: %s", ctx.book_id, c.symbol, corr_reason)
                        continue

                    # Build the Inference Context Bundle only if the auditor uses
                    # it. Auditors that abstain (NeutralAuditor in replay) set
                    # uses_prompt=False, letting us skip the per-candidate
                    # news/financials network fetch — a large replay speedup with
                    # identical scores (constant abstention either way).
                    prompt = adapter.auditor_prompt(c) if getattr(self.auditor, "uses_prompt", True) else ""
                    claude_score = self.auditor.audit(prompt)
                    blended = 0.60 * c.quant_score + 0.40 * claude_score

                    # Full Inference Context Bundle now exists (macro regime + the
                    # 32-marker snapshot + all three scores). Log it as a parent
                    # training record at each decision branch below — both acted
                    # and not-acted are training signal (the parent->child bridge).
                    macro_ctx = getattr(adapter, "_last_gate_result", {}) or {}
                    markers = c.meta.get("markers", {})

                    def _log_training(acted: bool, reason: str, order=None, trade_id=None) -> None:
                        self.ledger.record_training_sample(
                            book_id=ctx.book_id, symbol=c.symbol, wrapper=ctx.wrapper,
                            asset_class=c.asset_class, macro=macro_ctx, markers=markers,
                            gate=gate, quant_score=c.quant_score, claude_score=claude_score,
                            blended=blended, acted=acted, reason=reason,
                            order=order, trade_id=trade_id)

                    if blended < self.cfg.exec_threshold:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, claude_score, blended,
                                                     acted=False, reason="below exec threshold")
                        _log_training(False, "below exec threshold")
                        continue

                    order = ctx.sizing.size(c, ctx, gate_score=gate)
                    if order.quantity <= 0:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, claude_score, blended,
                                                     acted=False, reason="sized quantity <= 0")
                        _log_training(False, "sized quantity <= 0", order=order)
                        continue

                    fill = self.broker.place(order, ctx)
                    trade_id = self.ledger.record_trade(
                        book_id=ctx.book_id, account_id=order.account_id, symbol=order.symbol,
                        side=order.side, quantity=order.quantity, price=order.price,
                        notional=order.notional, status=fill.get("status", "paper"),
                        stop_loss=order.stop_loss, take_profit=order.take_profit,
                        broker_ref=fill.get("broker_ref"),
                        trailing_atr=order.trailing_atr,
                    )
                    self.ledger.record_decision(ctx.book_id, c.symbol, gate, c.quant_score,
                                                claude_score, blended, acted=True,
                                                reason=f"executed ({fill.get('status')})")
                    _log_training(True, f"executed ({fill.get('status')})",
                                  order=order, trade_id=trade_id)
                    log.info("[%s] ACT %s blended=%.1f qty=%s", ctx.book_id, c.symbol,
                             blended, order.quantity)

# =========================================================================== #
# Self-contained demo
# =========================================================================== #
def _demo() -> None:  # pragma: no cover  (manual demonstration, not unit-tested)
    from core.context import load_books
    from adapters.broker_ibkr import IBKRAdapter
    from adapters.asset_equity import EquityAdapter
    from adapters.asset_fx import FxAdapter
    from layers.analyst import LLMAuditor

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Load the real manifest so the demo exercises every wired book (incl. FOREX)
    # and the structured, asset-class-aware universe from config.yaml.
    books = load_books("portfolio.yaml")
    # Paper NAVs keyed by the placeholder account IDs in portfolio.yaml.
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={
        "U_ISA_PLACEHOLDER": 4000, "U_SIPP_PLACEHOLDER": 13000,
        "U_GIA_PLACEHOLDER": 2000, "U_FX_PLACEHOLDER": 5000,
    })
    broker.connect()

    ledger = Ledger(":memory:")
    cfg = load_engine_config("config.yaml")
    # One engine, both asset adapters — the engine routes each book to the
    # adapter(s) whose `handles` intersect the book's allowed_assets.
    Engine(books, [EquityAdapter(), FxAdapter()], broker,
           LLMAuditor(backend="local"), ledger, cfg).run_cycle()

    print("\n=== Performance summary (per book) ===")
    for b in books:
        print(ledger.performance_summary(b.book_id))
    print(ledger.performance_summary())  # ALL

if __name__ == "__main__":  # pragma: no cover
    _demo()
