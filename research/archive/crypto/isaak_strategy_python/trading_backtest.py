import sys

# Force UTF-8 output so Lumibot's Unicode progress bar (█) doesn't crash
# on Windows terminals using cp1252 encoding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pytz
from lumibot.brokers import Alpaca
from lumibot.entities import Asset
from lumibot.backtesting import AlpacaBacktesting
from datetime import datetime
import strategies
from strategies import FrictionAwareMacdRsi
from creds import ALPACA_CREDS_ACCOUNT_3

timezone = pytz.timezone("Europe/London")

# CHANGE PARAMETERS HERE
FRICTION_AWARE_PARAMS = {
    "symbol": "SPY",
    "cash_at_risk": 0.60,
    "friction_buffer": 0.0005,
}


BENCHMARK = {
    "friction_aware": "SPY",
}

selected_creds = ALPACA_CREDS_ACCOUNT_3

# 2. Override the global ALPACA_CREDS variable inside the strategies module.
# This ensures classes like SentimentTrader pick up the correct keys during initialization.
strategies.ALPACA_CREDS = selected_creds

# 3. Initialize the broker with the targeted account credentials
broker = Alpaca(selected_creds)

algorithms = {
"friction_aware": FrictionAwareMacdRsi(
    name="Friction_Aware_Intraday", 
    broker=broker,
    parameters=FRICTION_AWARE_PARAMS
)
}

# CHANGE TIME PERIOD HERE
est = pytz.timezone("US/Eastern")
start_date = datetime(2023, 1, 1, 9, 30, 0, tzinfo=est)
end_date = datetime(2026, 6, 15, 16, 0, 0, tzinfo=est)
initial_cash = 1000

strategy = algorithms["friction_aware"]
strategy.backtest(
    AlpacaBacktesting, 
    start_date, 
    end_date,
    budget=initial_cash,
    parameters=FRICTION_AWARE_PARAMS,
    benchmark=BENCHMARK["friction_aware"],
    benchmark_asset=BENCHMARK["friction_aware"],
    config=selected_creds,
    timestep="minute",
    buy_trading_fee=0.0005,
    sell_trading_fee=0.0005
)