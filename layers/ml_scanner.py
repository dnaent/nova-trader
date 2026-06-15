import numpy as np
from sklearn.ensemble import RandomForestClassifier
from layers.data_loader import get_technical_features
from core.context import Candidate

class MLScanner:
    """
    Advanced Intelligence Scanner (Phase 8).
    Uses a Random Forest Classifier trained on the 30+ indicator matrix
    to predict the probability of a positive breakout.
    """
    def __init__(self, asset_class: str, prediction_horizon: int = 5):
        self.asset_class = asset_class
        self.prediction_horizon = prediction_horizon
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

    def scan(self, universe: list[str]) -> list[Candidate]:
        candidates = []
        for symbol in universe:
            df = get_technical_features(symbol, lookback_days=500)
            if df.empty or len(df) < 100:
                continue

            df = df.copy()  # own the frame before adding Target (avoids SettingWithCopyWarning)
            # Create Target: 1 if the price in `prediction_horizon` days is higher than today, else 0
            df['Target'] = (df['Close'].shift(-self.prediction_horizon) > df['Close']).astype(int)
            
            # Drop the final rows where target is NaN
            train_df = df.dropna()
            
            if len(train_df) < 50:
                continue
                
            # Features are all TA columns (drop OHLCV and Target)
            exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'Target']
            features = [c for c in train_df.columns if c not in exclude_cols]
            
            if not features:
                continue
                
            X_train = train_df[features].values
            y_train = train_df['Target'].values
            
            # Train the lightweight model
            self.model.fit(X_train, y_train)
            
            # Predict today
            today_features = df.iloc[-1][features].values.reshape(1, -1)
            # Ensure no NaNs in today's features
            if np.isnan(today_features).any():
                continue
                
            prob_breakout = self.model.predict_proba(today_features)[0][1]

            # quant_score is 0-100 probability
            quant_score = float(prob_breakout * 100)
            price = df.iloc[-1]['Close']

            # Snapshot of the full marker matrix (all indicators the scanner saw)
            # so the SAME 32 markers flow downstream into the Inference Context
            # Bundle (Layer 3) and the parent model's training records — not just
            # into this scanner. Keys are the pandas-ta column names.
            markers = {f: round(float(v), 6)
                       for f, v in zip(features, today_features.flatten())}

            c = Candidate(
                symbol=symbol,
                asset_class=self.asset_class,
                quant_score=quant_score,
                price=price,
                meta={"ml_prob": f"{quant_score:.1f}%", "markers": markers}
            )
            candidates.append(c)
            
        # Sort by ML probability descending
        candidates.sort(key=lambda x: x.quant_score, reverse=True)
        return candidates
