import pandas as pd
import ta

class TechnicalAnalyzer:
    def __init__(self):
        # Using a fixed queue for rolling prices to compute indicators on the fly
        self.prices = []
        self.max_window = 250 # Sufficient to compute 200 EMA

    def add_price(self, price: float):
        self.prices.append(price)
        if len(self.prices) > self.max_window:
            self.prices.pop(0)

    def compute_indicators(self) -> dict:
        if len(self.prices) < 26: 
            return {
                "rsi": None, "macd": None, "ema": None, 
                "signal": "WAITING...", "reason": f"Gathering data ({len(self.prices)}/26)",
                "latest_price": self.prices[-1] if self.prices else 0
            }
            
        df = pd.DataFrame(self.prices, columns=['close'])
        
        # Calculate RSI (Window 14)
        rsi_series = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        rsi = rsi_series.iloc[-1]
        
        # Calculate MACD
        macd_indicator = ta.trend.MACD(close=df['close'])
        macd = macd_indicator.macd().iloc[-1]
        macd_signal = macd_indicator.macd_signal().iloc[-1]
        
        # Calculate EMA (up to 200 based on window)
        ema = ta.trend.EMAIndicator(close=df['close'], window=min(200, len(self.prices) - 1)).ema_indicator().iloc[-1]

        # Signal Logic Synthesis
        signal_action = "HOLD"
        reason = "Neutral Trends"
        
        # Primitive technical rules for demonstration 
        if rsi < 30 and macd > macd_signal:
            signal_action = "BUY"
            reason = "RSI Oversold & MACD Crossover"
        elif rsi > 70 and macd < macd_signal:
            signal_action = "SELL"
            reason = "RSI Overbought & MACD Crossunder"
            
        return {
            "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
            "macd": round(macd, 2) if not pd.isna(macd) else None,
            "ema": round(ema, 2) if not pd.isna(ema) else None,
            "signal": signal_action,
            "reason": reason,
            "latest_price": round(self.prices[-1], 2)
        }
