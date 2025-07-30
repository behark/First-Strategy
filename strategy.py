import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

class TradingStrategy:
    """
    Trading strategy implementation that analyzes market data and generates trading signals.
    """
    
    def __init__(self, symbols: List[str], lookback_period: int = 20, 
                 rsi_threshold_low: int = 30, rsi_threshold_high: int = 70):
        """
        Initialize the trading strategy with configuration parameters.
        
        Args:
            symbols: List of trading symbols to monitor
            lookback_period: Period for calculating indicators
            rsi_threshold_low: RSI threshold for oversold condition
            rsi_threshold_high: RSI threshold for overbought condition
        """
        self.symbols = symbols
        self.lookback_period = lookback_period
        self.rsi_threshold_low = rsi_threshold_low
        self.rsi_threshold_high = rsi_threshold_high
        self.historical_data = {}
        
    def update_data(self, symbol: str, new_data: pd.DataFrame) -> None:
        """
        Update the historical data for a symbol.
        
        Args:
            symbol: The trading symbol
            new_data: New market data to append
        """
        if symbol not in self.historical_data:
            self.historical_data[symbol] = new_data
        else:
            self.historical_data[symbol] = pd.concat([self.historical_data[symbol], new_data])
            # Keep only the most recent data points based on lookback_period
            self.historical_data[symbol] = self.historical_data[symbol].tail(self.lookback_period * 3)
    
    def calculate_rsi(self, prices: np.ndarray) -> float:
        """
        Calculate the Relative Strength Index (RSI) for a price series.
        
        Args:
            prices: Array of price data
            
        Returns:
            RSI value
        """
        # Calculate price changes
        price_diff = np.diff(prices)
        
        # Separate gains and losses
        gains = np.clip(price_diff, 0, None)
        losses = -np.clip(price_diff, None, 0)
        
        # Calculate average gains and losses over the lookback period
        avg_gain = np.mean(gains[-self.lookback_period:]) if len(gains) > 0 else 0
        avg_loss = np.mean(losses[-self.lookback_period:]) if len(losses) > 0 else 0
        
        # Calculate RSI
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_sma(self, prices: np.ndarray, period: int) -> float:
        """
        Calculate Simple Moving Average.
        
        Args:
            prices: Array of price data
            period: Period for SMA calculation
            
        Returns:
            SMA value
        """
        if len(prices) < period:
            return np.nan
        return np.mean(prices[-period:])
    
    def generate_signals(self) -> Dict[str, str]:
        """
        Generate trading signals for all tracked symbols.
        
        Returns:
            Dictionary of symbols and their corresponding signals ('BUY', 'SELL', or 'HOLD')
        """
        signals = {}
        
        for symbol, data in self.historical_data.items():
            if len(data) < self.lookback_period:
                signals[symbol] = "HOLD"  # Not enough data
                continue
                
            prices = data['close'].values
            
            # Calculate indicators
            rsi = self.calculate_rsi(prices)
            sma_short = self.calculate_sma(prices, self.lookback_period // 2)
            sma_long = self.calculate_sma(prices, self.lookback_period)
            
            # Generate signal based on RSI and moving averages
            if rsi < self.rsi_threshold_low and sma_short > sma_long:
                signals[symbol] = "BUY"  # Oversold condition and positive momentum
            elif rsi > self.rsi_threshold_high or sma_short < sma_long:
                signals[symbol] = "SELL"  # Overbought condition or negative momentum
            else:
                signals[symbol] = "HOLD"
        
        return signals
    
    def get_position_size(self, symbol: str, account_balance: float, 
                         risk_per_trade: float = 0.02) -> Optional[float]:
        """
        Calculate the position size based on risk management parameters.
        
        Args:
            symbol: Trading symbol
            account_balance: Current account balance
            risk_per_trade: Percentage of account to risk per trade
            
        Returns:
            Recommended position size or None if not enough data
        """
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < self.lookback_period:
            return None
            
        data = self.historical_data[symbol]
        current_price = data['close'].iloc[-1]
        
        # Calculate volatility (standard deviation of returns)
        returns = data['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Adjust position size based on volatility
        risk_amount = account_balance * risk_per_trade
        position_size = risk_amount / (current_price * volatility * 10)
        
        return position_size
