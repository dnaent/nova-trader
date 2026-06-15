from adapters.asset_equity import EquityAdapter
from adapters.asset_fx import FxAdapter
from run_paper import build_engine, DEFAULT_NAVS


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
