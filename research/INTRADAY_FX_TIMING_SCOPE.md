# Scope — Intraday / Time-of-Day FX Timing

**Date:** 2026-06-19 · **Status:** SCOPE for review (nothing built) · **Origin:** operator idea — exploit time-of-day / day-of-week / session edges (e.g. an FX pair profitable in a specific intraday window on specific days).

## Goal
Let the engine **see and exploit temporal structure** in FX — session (Asia/London/NY/overlap), hour-of-day, day-of-week, and time-to-session-close — which the current daily-bar engine is completely blind to. FX is the right (and only) first target: it trades ~24h, session-liquidity and day-of-week effects are real and documented, and it's our one tactical trend book. Equities have fixed sessions and the ISA/SIPP books are buy-and-hold, so intraday is irrelevant there.

## Where the engine is today (grounding)
- **All data is DAILY.** `layers/data_loader.get_daily_data` (IBKR feed → yfinance fallback, 12h cache) and `get_technical_features` (the 32-marker matrix) operate on `barSizeSetting="1 day"` (`adapters/ibkr_feed.get_daily_bars`).
- **FX signal is daily.** `adapters/asset_fx.FxAdapter` computes EMA20/50 + ADX on daily bars; the gate reads daily DXY ADX.
- **Cadence is daily.** `Engine.run_cycle()` = one "day"; the cron fires once at 07:00. There is no intraday loop.
- **Replay/validation is daily.** `ReplayFeed` serves daily point-in-time bars; walk-forward + Monte-Carlo are daily.

So "profitable within a 2-hour window on Tuesdays" is currently **unrepresentable** — there is no time-of-day axis anywhere in the pipeline.

## ⚠️ Two hard constraints to decide around (flagged up front)
1. **Intraday history is SHORT — no GFC-scale stress test is possible.** yfinance intraday is capped (~730 days at 1h, ~60 days at 15m, ~7 days at 1m); IBKR gives more hourly history but still bounded (years, not decades). So intraday timing edges can only be validated on a **recent ~2-3-year window** — they cannot be put through the 2008/2020 stress tests that gave the daily books their credibility. Any intraday edge is therefore *less* battle-tested by construction.
2. **Intraday cadence is the engine's biggest assumption-break.** `run_cycle()` = one day. Real intraday trading needs the FX book evaluated many times per day (e.g. hourly during active sessions). That's a genuine architectural addition (an intraday loop), not a config tweak.

## Architecture changes required (by layer)
| Layer | Change |
|---|---|
| **Data** (`ibkr_feed.py`, `data_loader.py`) | Add `get_intraday_bars(symbol, bar_size="1 hour", lookback_days, use_rth=False)` (IBKR `reqHistoricalData` supports it; FX wants `useRTH=False` for 24h) + a yfinance intraday fallback + `get_intraday_data()` with its own cache. |
| **Temporal features** (`data_loader.py`) | Derive `hour`, `day_of_week`, `session` (Asia/London/NY/overlap, from UTC), `mins_to_session_close`, `is_friday_pm` from the intraday index; append to the marker snapshot so they flow into the scanner + Inference Context Bundle + **training records**. |
| **Signal** (`asset_fx.py`) | Compute the trend on intraday bars and/or **condition on session**; phase-gated (see plan) — start by *logging* temporal features, later *filter/learn* on them. |
| **Cadence** (`core/engine.py` + a new `run_paper_intraday.py`) | An FX-only intraday loop (hourly during active sessions) reusing the per-book logic; equities/allocation stay daily. |
| **Execution/exits** | Intraday fills + intraday stop/take on the finer bars (the paper stub already fills at price). |
| **Validation** (`backtest/`) | An intraday `ReplayFeed` (point-in-time hourly) + the FX account-level profile applied to the (shorter) intraday window. Honest caveat per constraint #1. |

## Recommended plan — evidence first, build later (3 phases)
This mirrors the lesson we already paid for once: **prove the edge in data before building expensive machinery around it** (the ML scanner had no edge — we don't want to assume an intraday edge either).

- **Phase 1 — OBSERVE (low risk, high learning).** Build the intraday data layer + temporal features and **log them into the FX training records — with execution still DAILY (unchanged).** The corpus starts accumulating `{session, hour, day_of_week, …}` alongside outcomes. No behaviour change, no new cadence, fully reversible. *Effort: small-medium.*
- **Phase 2 — ANALYZE.** Mine the accumulated corpus (temporal features vs R-multiples/PnL) to test whether real session/day edges exist for our pairs. Only proceed if the data shows a genuine, stable edge (not noise). *Effort: small (analysis).*
- **Phase 3 — ACT (only if Phase 2 confirms).** Add the intraday cadence (FX hourly loop) + session/time filters (or a learned timing model) + intraday backtest/validation on the recent window. The big build — justified by evidence, not hope. *Effort: large.*

## Open decisions for the operator
1. **Bar size** for Phase 1 — 1-hour (more history, less granular) vs 15-min (finer, ~60-day history). I'd start **1-hour** for history depth.
2. **Session reference timezone / definitions** — confirm Asia/London/NY/overlap boundaries (I'll default to standard FX session UTC windows).
3. **Pairs** — all 6 majors, or focus the intraday study on the most liquid (EURUSD, GBPUSD, USDJPY) first.
4. **Accept the constraint** that intraday edges can't be GFC-stress-tested (recent-window validation only) — i.e. a different, lower trust bar than the daily books.

## My recommendation
Do **Phase 1 now** (cheap, safe, reversible — just start *seeing* time), let it log temporal features into the live FX corpus for a few weeks alongside the daily accrual, then **Phase 2 decides** whether Phase 3 is worth it. This adds a powerful new feature axis to the model's context immediately, with zero risk to the validated daily books, and refuses to build intraday execution until the data earns it.
