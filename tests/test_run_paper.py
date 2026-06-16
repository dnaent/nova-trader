from adapters.asset_equity import EquityAdapter
from adapters.asset_fx import FxAdapter
from adapters.broker_ibkr import IBKRAdapter
from run_paper import build_engine, DEFAULT_NAVS


class _Ctx:
    def __init__(self, acc): self.ibkr_account_id = acc


def test_broker_seed_positions_rehydrates_from_ledger():
    """A fresh broker seeded from the ledger's open trades reports those holdings,
    so the daily forward cron doesn't re-buy positions it already holds."""
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U": 1000})
    broker.connect()
    assert broker.positions(_Ctx("U")) == []                 # starts flat
    broker.seed_positions([{"id": 1, "account_id": "U", "symbol": "VWRL.L",
                            "side": "BUY", "quantity": 23, "price": 138.0}])
    pos = broker.positions(_Ctx("U"))
    assert len(pos) == 1 and pos[0]["symbol"] == "VWRL.L"     # holding visible after seed


def test_build_engine_offline():
    """Engine assembles with all 4 books + both adapters, no feed, no network."""
    engine, books, ledger, feed = build_engine(db_path=":memory:", use_feed=False)
    try:
        assert feed is None                          # --no-feed path
        ids = {b.book_id for b in books}
        assert {"ibkr_isa_equity", "ibkr_sipp_equity",
                "ibkr_gia_equity", "ibkr_forex_margin"} <= ids
        kinds = {type(a).__name__ for a in engine.asset_adapters}
        assert kinds == {"EquityAdapter", "FxAdapter", "AllocationAdapter"}
        # Paper stub gives every book a simulated NAV keyed by its account id.
        for b in books:
            assert engine.broker._navs[b.ibkr_account_id] == DEFAULT_NAVS.get(b.wrapper, 5000)
    finally:
        ledger.close()
