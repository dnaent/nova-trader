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

from core.context import AccountContext, AssetAdapter, BrokerAdapter, Candidate
from core.ledger import Ledger
from layers.analyst import Auditor

log = logging.getLogger("nova.engine")

@dataclass
class EngineConfig:
    gate_min: float = 40.0          # below this, hold cash (no new buys)
    exec_threshold: float = 75.0    # blended score required to act
    top_n: int = 10
    universe: list = field(default_factory=list)
    aggressive_liquidation: bool = False

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

    def run_cycle(self) -> None:
        for ctx in self.books:
            ctx.nav = self.broker.refresh_nav(ctx)
            log.info("[%s] %s nav=%s allowed=%s", ctx.book_id, ctx.wrapper,
                     ctx.nav, sorted(ctx.allowed_assets))

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

                for c in adapter.scan(self.cfg.universe)[: self.cfg.top_n]:
                    # HARD permission rule
                    if c.asset_class not in ctx.allowed_assets:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, None, None, acted=False,
                                                     reason=f"{c.asset_class} not permitted")
                        continue

                    claude_score = self.auditor.audit(adapter.auditor_prompt(c))
                    blended = 0.60 * c.quant_score + 0.40 * claude_score

                    if blended < self.cfg.exec_threshold:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, claude_score, blended,
                                                     acted=False, reason="below exec threshold")
                        continue

                    order = ctx.sizing.size(c, ctx, gate_score=gate)
                    if order.quantity <= 0:
                        self.ledger.record_decision(ctx.book_id, c.symbol, gate,
                                                     c.quant_score, claude_score, blended,
                                                     acted=False, reason="sized quantity <= 0")
                        continue

                    fill = self.broker.place(order, ctx)
                    self.ledger.record_trade(
                        book_id=ctx.book_id, account_id=order.account_id, symbol=order.symbol,
                        side=order.side, quantity=order.quantity, price=order.price,
                        notional=order.notional, status=fill.get("status", "paper"),
                        stop_loss=order.stop_loss, take_profit=order.take_profit,
                        broker_ref=fill.get("broker_ref"),
                    )
                    self.ledger.record_decision(ctx.book_id, c.symbol, gate, c.quant_score,
                                                claude_score, blended, acted=True,
                                                reason=f"executed ({fill.get('status')})")
                    log.info("[%s] ACT %s blended=%.1f qty=%s", ctx.book_id, c.symbol,
                             blended, order.quantity)

# =========================================================================== #
# Self-contained demo
# =========================================================================== #
def _demo() -> None:
    from core.context import AccountContext, NullTaxPolicy
    from tax.uk_cgt import UkCgtPolicy
    from core.risk import NavPctSizing
    from adapters.broker_ibkr import IBKRAdapter
    from adapters.asset_equity import EquityAdapter
    from layers.analyst import StubAuditor

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={
        "U_ISA": 4000, "U_SIPP": 13000, "U_GIA": 2000,
    })
    broker.connect()

    books = [
        AccountContext("ibkr_isa_equity", "ISA", "IBKR", "U_ISA",
                       {"EQUITY", "ETF"}, NullTaxPolicy(), NavPctSizing(max_per_position_pct=8)),
        AccountContext("ibkr_sipp_equity", "SIPP", "IBKR", "U_SIPP",
                       {"EQUITY", "ETF"}, NullTaxPolicy(), NavPctSizing(max_per_position_pct=6)),
        AccountContext("ibkr_gia_equity", "GIA", "IBKR", "U_GIA",
                       {"EQUITY", "ETF"}, UkCgtPolicy(higher_rate=False),
                       NavPctSizing(max_per_position_pct=8)),
    ]

    ledger = Ledger(":memory:")
    cfg = EngineConfig(universe=["SPY", "NVDA", "VWRL", "FORD"])
    Engine(books, [EquityAdapter()], broker, StubAuditor(), ledger, cfg).run_cycle()

    print("\n=== Performance summary (per book) ===")
    for b in books:
        print(ledger.performance_summary(b.book_id))
    print(ledger.performance_summary())  # ALL

if __name__ == "__main__":
    _demo()
