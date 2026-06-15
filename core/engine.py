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
            entry = Decimal(str(pos["price"]))
            qty = Decimal(str(pos["quantity"]))
            stop = Decimal(str(pos["stop_loss"])) if pos["stop_loss"] is not None else None
            take = Decimal(str(pos["take_profit"])) if pos["take_profit"] is not None else None

            exit_price = reason = None
            if stop is not None and price <= stop:
                exit_price, reason = stop, "stop-loss"
            elif take is not None and price >= take:
                exit_price, reason = take, "take-profit"
            if exit_price is None:
                continue

            realized = (exit_price - entry) * qty
            sell = Order(book_id=ctx.book_id, account_id=pos["account_id"],
                         symbol=pos["symbol"], side="SELL", quantity=qty,
                         price=exit_price, notional=(exit_price * qty))
            self.broker.place(sell, ctx)                       # nets the paper position flat
            self.ledger.close_trade(pos["id"], exit_price, realized)
            log.info("[%s] EXIT %s (%s) @ %s pnl=%s", ctx.book_id, pos["symbol"],
                     reason, exit_price, realized)

    def run_cycle(self) -> None:
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

            for adapter in self.asset_adapters:
                if not (adapter.handles & ctx.allowed_assets):
                    continue  # this adapter's asset classes aren't permitted here

                gate = adapter.macro_gate()
                if gate < self.cfg.gate_min:
                    self.ledger.record_decision(ctx.book_id, None, gate, None, None,
                                                None, acted=False,
                                                reason="macro gate below floor")
                    log.info("[%s] gate %.0f < %.0f — holding cash",
                             ctx.book_id, gate, self.cfg.gate_min)
                             
                    if self.cfg.aggressive_liquidation:
                        log.info("[%s] AGGRESSIVE LIQUIDATION ENABLED. Liquidating open positions.", ctx.book_id)
                        open_positions = self.broker.positions(ctx)
                        for pos in open_positions:
                            order = Order(
                                book_id=ctx.book_id,
                                account_id=ctx.ibkr_account_id,
                                symbol=pos["symbol"],
                                side="SELL",
                                quantity=pos["quantity"],
                                price=pos.get("market_price", Decimal("0")),
                                notional=pos["quantity"] * pos.get("market_price", Decimal("0"))
                            )
                            fill = self.broker.place(order, ctx)
                            self.ledger.record_trade(
                                book_id=ctx.book_id, account_id=order.account_id, symbol=order.symbol,
                                side=order.side, quantity=order.quantity, price=order.price,
                                notional=order.notional, status=fill.get("status", "paper"),
                                stop_loss=order.stop_loss, take_profit=order.take_profit,
                                broker_ref=fill.get("broker_ref"),
                            )
                            log.info("[%s] LIQUIDATED %s qty=%s", ctx.book_id, order.symbol, order.quantity)
                    continue

                open_symbols = [p["symbol"] for p in open_positions]

                scan_universe = self.cfg.universe_for(adapter.handles)
                for c in adapter.scan(scan_universe)[: self.cfg.top_n]:
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

                    claude_score = self.auditor.audit(adapter.auditor_prompt(c))
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
def _demo() -> None:
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

if __name__ == "__main__":
    _demo()
