import sys
import numpy as np
import datetime
import pytz

import matplotlib
matplotlib.use("TkAgg")  # Or "Qt5Agg" if you have PyQt installed
import matplotlib.pyplot as plt
from creds import BASE_URL

from datetime import datetime, time
from timedelta import Timedelta
from alpaca_trade_api import REST
from lumibot.strategies.strategy import Strategy
from finbert_utils import estimate_sentiment

class BaseNotionalStrategy(Strategy):
    """
    A helper base class to handle the fractionable check across all strategies.
    """
    def check_fractionable(self, symbol):
        current_module = sys.modules[__name__]
        creds = getattr(current_module, "ALPACA_CREDS")
        
        api = REST(key_id=creds["API_KEY"], secret_key=creds["API_SECRET"], base_url=BASE_URL)

        # Extract the underlying string symbol safely
        if hasattr(symbol, "symbol"):
            symbol_str = str(symbol.symbol)
        else:
            symbol_str = str(symbol)
        
        # CLEANUP ENGINE: Extract core pair name correctly without stacking suffixes
        if hasattr(self, "asset_type") and self.asset_type == "crypto":
            # If it has a slash, clean it up to verify it's just 'COIN/USD'
            base_coin = symbol_str.split("/")[0]
            symbol_str = f"{base_coin}/USD"
        elif "/" in symbol_str and ("USD" in symbol_str or "USDT" in symbol_str):
            # Fallback string guard
            base_coin = symbol_str.split("/")[0]
            symbol_str = f"{base_coin}/USD"
                
        try:
            asset = api.get_asset(symbol_str)
            return asset.fractionable
        except Exception as e:
            print(f"Skipping fractionable check for {symbol_str}: {e}")
            return False

    def log_message(self, message, *args, **kwargs):
        try:
            # Try using LumiBot's internal datetime tracking
            dt = self.get_datetime()
            if dt is not None:
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Fallback if get_datetime() is not yet initialized
                import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            # Ultimate fallback to standard library datetime
            import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("logs.log", "a") as file:
            file.write(f"[{timestamp}] {message}\n")

    def set_last_trade(self, last_trade=None):
        """Dynamically determines last_trade based on account holdings or history."""
        try:
            # If no position, check the last closed order to see if it was a sell
            # We limit to 1 to get the most recent transaction
            orders = self.get_orders()
            if orders:
                i = 0
                for order in orders:
                    self.log_message(order)
                    status = order.status if order else None
                    if status == 'filled' and i == 0:
                        i = i + 1
                        # Map the side to your tracker strings
                        last_trade = "sell" if order.side == "sell" else "buy"
                        self.log_message(f"Startup: No position. Last historical trade was '{last_trade}'.")
                        break
            else:
                # First time ever running the bot
                last_trade = None
                self.log_message("Startup: No history found. Starting fresh.")

        except Exception as e:
            self.log_message(f"Error determining initial state: {e}")
            last_trade = None
        
        return last_trade

    def log_order_status(self, order):
        order_status = order.status
        if order_status == "rejected":
            self.log_message(f"ORDER REJECTED, Reason: {order_status.failed_at} - {order_status.rejection_reason}")
        elif order_status == "filled":
            self.log_message(f"ORDER SUCCESS, Sold at {order_status.filled_avg_price}")
        else:
            self.log_message(f"ORDER: {order_status}")

    def should_algo_run(self, algo, position, last_price, order_type="limit"):
        # Use Lumibot's simulated backtest time instead of real-world time
        now_ny = algo.get_datetime().astimezone(pytz.timezone('America/New_York'))
        ny_time = now_ny.time()

        # --- Equity Market Open Blackout (9:20 – 9:40 AM NY) ---
        equity_blackout_start = datetime.time(9, 20)
        equity_blackout_end   = datetime.time(9, 40)
        is_blackout = equity_blackout_start <= ny_time <= equity_blackout_end

        # --- Crypto: use simulated UTC time ---
        now_utc = algo.get_datetime().astimezone(pytz.utc)
        minutes_past_hour = now_utc.minute

        if is_blackout:
            if position:
                if order_type == "limit":
                    sell_price = round(last_price * 0.9995, 8)
                    limit_sell = algo.create_order(
                        algo.symbol, quantity=position.quantity, side="sell",
                        type=order_type, limit_price=sell_price, time_in_force="gtc"
                    )
                    algo.submit_order(limit_sell)
                    algo.log_message(f"BLACKOUT SELL: Exited {algo.symbol} @ {sell_price:.6f}")
                else:
                    algo.sell_all()
                algo.max_price_since_buy = 0
                algo.last_trade = "sell"
                algo.log_message(f"BLACKOUT SELL: Exited {algo.symbol}")
            return False
        return True

class FrictionAwareMacdRsi(BaseNotionalStrategy):
    def initialize(self, symbol="SPY", cash_at_risk=0.60, friction_buffer=0.0005):
        """
        Initialize strategy variables.
        symbol: High-liquidity asset to trade.
        cash_at_risk: Portion of total portfolio value allocated to a trade (60%).
        friction_buffer: 0.05% per trade model for slippage, TAF, and SEC fees.
        """
        self.symbol = symbol
        # Strategy operates on a 5-minute timeframe interval
        self.sleeptime = "5M" 
        self.cash_at_risk = cash_at_risk
        self.friction_buffer = friction_buffer
        
        # Strategy configuration targets
        self.target_take_profit = 0.02  # 2.0%
        self.target_stop_loss = 0.012   # 1.2%
        
        # Timezone configuration
        self.est_tz = pytz.timezone("US/Eastern")

    def is_market_open(self):
        """
        Dynamically extracts the clock time from the current simulation 
        or live data iteration using Lumibot's native self.get_datetime()
        """
        # 1. Get the current strategy time (handles backtest simulation clock safely)
        current_dt = self.get_datetime()
        
        # 2. Convert to US/Eastern timezone 
        est_dt = current_dt.astimezone(self.est_tz)
        current_time = est_dt.time()
        
        # Define trade parameters
        start_time = time(9, 30)
        square_off_time = time(15, 50)
        end_time = time(16, 0)
        
        # 3. Evaluate conditional windows based on the simulation clock
        trade_window = start_time <= current_time < square_off_time
        square_off_window = square_off_time <= current_time < end_time
        
        return trade_window, square_off_window

    def position_sizing(self):
        """
        Dynamically calculates available settled cash and friction-adjusted quantity
        to avoid partial rejections and protect purchasing power.
        """
        try:
            portfolio_value = self.get_portfolio_value()
            cash = self.get_cash()
            last_price = self.get_last_price(self.symbol)
            
            if last_price <= 0:
                return 0, 0
                
            # Calculate total allocation budget based on target portfolio risk
            allocated_budget = portfolio_value * self.cash_at_risk
            
            # Ensure we never allocate more liquid cash than what is fully settled/available
            # Reserve an extra 1% cash buffer to guarantee margin safety and handle dynamic adjustments
            safe_cash_pool = min(allocated_budget, cash * 0.99)
            
            # Calculate maximum raw shares possible
            raw_quantity = safe_cash_pool / last_price
            
            # Account for the friction premium (entry slippage/fees) on the purchasing side
            quantity = int(np.floor(raw_quantity * (1 - self.friction_buffer)))
            
            return quantity, last_price
        except Exception as e:
            self.log_message(f"Error executing position sizing logic: {str(e)}", level="error")
            return 0, 0

    def get_indicators(self):
        """
        Fetches historical data and calculates technical indicators:
        - 200 EMA (Trend filter)
        - MACD (12, 26, 9)
        - RSI (14)
        """
        try:
            # Fetch sufficient bars to populate 200 EMA and technical warmups
            bars = self.get_historical_prices(self.symbol, 250, "minute")
            df = bars.df
            
            if df.empty or len(df) < 200:
                return None, None, None, None

            # 1. Exponential Moving Average
            df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
            
            # 2. MACD Calculation
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            
            # 3. RSI Calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10) # Avoid division by zero
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Retrieve the latest complete bar values
            last_row = df.iloc[-1]
            return last_row['ema_200'], last_row['macd'], last_row['macd_signal'], last_row['rsi']
        except Exception as e:
            self.log_message(f"Error calculating market indicators: {str(e)}", level="error")
            return None, None, None, None

    def on_trading_iteration(self):
        """Runs every 5 minutes during trading hours to evaluate signals and risk profiles."""
        trade_window, square_off_window = self.is_market_open()
        
        # 1. Hard Intraday Square-off Execution Window
        if square_off_window:
            position = self.get_position(self.symbol)
            if position is not None:
                self.log_message(f"Square-off window active (3:50 PM EST). Exiting all positions for {self.symbol}.")
                self.sell_all()
            return

        # Restrict entry logic to active market hours only
        if not trade_window:
            return

        # Check existing tracking state
        position = self.get_position(self.symbol)
        if position is not None:
            # Already in a trade; bracket orders automatically handle risk mitigation targets
            return

        # 2. Extract Data and Indicator Signatures
        ema_200, macd, macd_signal, rsi = self.get_indicators()
        if any(v is None for v in [ema_200, macd, macd_signal, rsi]):
            return

        quantity, last_price = self.position_sizing()
        if quantity <= 0:
            return

        # 3. Multi-Indicator Strategy Logic Execution
        # Long Entry Signatures
        long_condition = (
            last_price > ema_200 and       # Bullish structural bias
            macd > macd_signal and          # MACD Bullish Crossover
            rsi < 70                        # Prevent chasing overbought assets
        )

        # Short Entry Signatures
        short_condition = (
            last_price < ema_200 and      # Bearish structural bias
            macd < macd_signal and          # MACD Bearish Crossover
            rsi > 30                        # Prevent selling oversold bottoms
        )

        # 4. Friction-Adjusted Bracket Placement Engine
        try:
            if long_condition:
                # Friction-adjusted net entry price is higher due to upward buy slippage
                net_entry_price = last_price * (1 + self.friction_buffer)
                
                # Derive mathematical targets strictly matching risk specs relative to net cost
                take_profit_price = round(net_entry_price * (1 + self.target_take_profit), 2)
                stop_loss_price = round(net_entry_price * (1 - self.target_stop_loss), 2)
                
                self.log_message(f"Executing LONG Order: {quantity} units. Market Price: {last_price:.2f}, "
                         f"Friction-Adjusted Entry: {net_entry_price:.2f} -> TP: {take_profit_price}, SL: {stop_loss_price}")
                
                order = self.create_order(
                    asset=self.symbol,
                    quantity=quantity,
                    side="buy",
                    type="bracket",
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price
                )
                self.submit_order(order)

            elif short_condition:
                # Friction-adjusted net short entry price is lower due to selling slippage
                net_entry_price = last_price * (1 - self.friction_buffer)
                
                # Derive risk bracket specifications for shorting positions
                take_profit_price = round(net_entry_price * (1 - self.target_take_profit), 2)
                stop_loss_price = round(net_entry_price * (1 + self.target_stop_loss), 2)
                
                self.log_message(f"Executing SHORT Order: {quantity} units. Market Price: {last_price:.2f}, "
                         f"Friction-Adjusted Entry: {net_entry_price:.2f} -> TP: {take_profit_price}, SL: {stop_loss_price}")
                
                order = self.create_order(
                    asset=self.symbol,
                    quantity=quantity,
                    side="sell",
                    type="bracket",
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price
                )
                self.submit_order(order)
                
        except Exception as e:
            self.log_message(f"Failed to transmit execution structure to Alpaca: {str(e)}", level="error")
