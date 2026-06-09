"""
Nova Engine — adapters/broker_ibkr.py

IBKR broker adapter. Phase 1 ships a SIMULATED paper stub so the full engine
cycle runs end-to-end with no live connection. Two real paths are stubbed with
TODOs for later phases:

  * connector="claude_connector"  -> IBKR's official Claude connector (launched
    2 Jun 2026). Approval-gated: place() should STAGE an instruction the operator
    approves in IBKR's "AI Instructions" tab, never execute silently.
  * connector="gateway"           -> local IB Gateway via ib_async (port 4002
    paper / 7496 live). Only for genuinely autonomous execution — out of scope
    for the first build.

HARD RULE: never execute live unless mode == 'live' AND a real connector is
configured. The stub refuses to pretend.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from core.context import AccountContext, Order

log = logging.getLogger("nova.broker.ibkr")


class IBKRAdapter:
    def __init__(self, mode: str = "paper", connector: str = "stub",
                 simulated_navs: Optional[dict] = None):
        if mode not in ("paper", "live"):
            raise ValueError("mode must be 'paper' or 'live'")
        if mode == "live" and connector == "stub":
            raise RuntimeError("Refusing live mode with the simulation stub. "
                               "Configure 'claude_connector' or 'gateway' first.")
        self.mode = mode
        self.connector = connector
        # account_id -> simulated NAV (Decimal). Used only by the stub.
        self._navs = {k: Decimal(str(v)) for k, v in (simulated_navs or {}).items()}
        self._positions: list[dict] = []   # in-memory paper book
        self._connected = connector == "stub"

    # ----- connection ----------------------------------------------------- #
    def connect(self) -> bool:
        if self.connector == "stub":
            self._connected = True
            log.info("IBKR stub: simulated connection (no network).")
            return True
        # TODO[gateway]: ib_async connectAsync(host, 4002/7496, clientId)
        # TODO[claude_connector]: handled via Claude connector marketplace, not here
        raise NotImplementedError(f"connector '{self.connector}' not implemented yet")

    def is_connected(self) -> bool:
        return self._connected

    # ----- account / positions ------------------------------------------- #
    def refresh_nav(self, ctx: AccountContext) -> Decimal:
        if self.connector == "stub":
            nav = self._navs.get(ctx.ibkr_account_id, Decimal("0"))
            ctx.nav = nav
            return nav
        # TODO: gateway -> ib.accountSummary(); connector -> portfolio query
        raise NotImplementedError

    def positions(self, ctx: AccountContext) -> list[dict]:
        if self.connector == "stub":
            return [p for p in self._positions if p["account_id"] == ctx.ibkr_account_id]
        raise NotImplementedError

    # ----- execution ------------------------------------------------------ #
    def place(self, order: Order, ctx: AccountContext) -> dict:
        """
        Paper stub: 'fills' instantly and records to the in-memory book.
        Live paths must respect the approval gate (see module docstring).
        """
        if self.connector == "stub":
            fill = {
                "status": "paper",
                "symbol": order.symbol,
                "side": order.side,
                "quantity": str(order.quantity),
                "price": str(order.price),
                "account_id": order.account_id,
                "broker_ref": f"PAPER-{len(self._positions) + 1}",
            }
            self._positions.append(fill)
            log.info("PAPER fill: %s %s x%s @ %s -> %s",
                     order.side, order.symbol, order.quantity, order.price, order.account_id)
            return fill

        if self.connector == "claude_connector":
            # TODO: stage instruction in IBKR 'AI Instructions' tab for operator sign-off.
            # Return status 'staged' — DO NOT mark as filled here.
            raise NotImplementedError("claude_connector staging not implemented yet")

        if self.connector == "gateway":
            # TODO: ib.placeOrder(Stock(...), MarketOrder(... account=ctx.ibkr_account_id))
            raise NotImplementedError("ib_async gateway execution not implemented yet")

        raise ValueError(f"unknown connector '{self.connector}'")
