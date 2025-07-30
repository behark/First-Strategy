"""
Indicators Module

Calculates technical indicators for trading signals.
"""
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Indicators:
    """
    Calculates and maintains technical indicators for trading signals.
    
    Attributes:
        period_rsi: Period for RSI calculation
        period_ema: Period for EMA calculation
    """
    
    def __init__(self, period_rsi: int = 2, period_ema: int = 8):
        """
        Initialize Indicators instance.
        
        Args:
            period_rsi: Period for RSI calculation (default: 2)
            period_ema: Period for EMA calculation (default: 8)
        """
        self.period_rsi = period_rsi
        self.period_ema = period_ema
        self.prices: List[float] = []
        self.gains: List[float] = []
        self.losses: List[float] = []
        self.ema_value: float = 0.0
        self.has_ema = False
        
    def update(self, price: float) -> None:
        """
        Update indicators with new price data.
        
        Args:
            price: Latest price
            
        Raises:
            ValueError: If price is invalid
        """
        if not isinstance(price, (int, float)) or np.isnan(price) or np.isinf(price):
            logger.warning(f"Invalid price value: {price}, skipping update")
            raise ValueError(f"Invalid price value: {price}")
        
        try:
            # Add price to buffer
            self.prices.append(price)
            
            # Calculate price change for RSI
            if len(self.prices) > 1:
                change = self.prices[-1] - self.prices[-2]
                self.gains.append(max(0, change))
                self.losses.append(max(0, -change))
            
            # Update EMA
            self._update_ema(price)
            
            # Trim buffers to required size
            max_period = max(self.period_rsi + 1, self.period_ema)
            if len(self.prices) > max_period:
                self.prices = self.prices[-max_period:]
            if len(self.gains) > self.period_rsi:
                self.gains = self.gains[-self.period_rsi:]
            if len(self.losses) > self.period_rsi:
                self.losses = self.losses[-self.period_rsi:]
                
        except (OverflowError, FloatingPointError) as e:
            logger.error(f"Calculation error: {e}, resetting buffers")
            self._reset_buffers()
            raise ValueError(f"Calculation error: {e}")
            
    def current_rsi(self) -> float:
        """
        Get current RSI value.
        
        Returns:
            float: Current RSI value (0-100)
            
        Raises:
            ValueError: If insufficient data for calculation
        """
        if len(self.gains) < self.period_rsi or len(self.losses) < self.period_rsi:
            raise ValueError(f"Insufficient data for RSI calculation, need {self.period_rsi} periods")
            
        avg_gain = sum(self.gains) / self.period_rsi
        avg_loss = sum(self.losses) / self.period_rsi
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def current_ema(self) -> float:
        """
        Get current EMA value.
        
        Returns:
            float: Current EMA value
            
        Raises:
            ValueError: If insufficient data for calculation
        """
        if not self.has_ema:
            raise ValueError(f"Insufficient data for EMA calculation, need {self.period_ema} periods")
            
        return self.ema_value
        
    def _update_ema(self, price: float) -> None:
        """
        Update EMA calculation with new price.
        
        Args:
            price: Latest price
        """
        # Simple moving average for initial EMA value
        if len(self.prices) == self.period_ema:
            self.ema_value = sum(self.prices) / self.period_ema
            self.has_ema = True
            return
            
        # EMA calculation
        if self.has_ema:
            multiplier = 2 / (self.period_ema + 1)
            self.ema_value = (price - self.ema_value) * multiplier + self.ema_value
            
    def _reset_buffers(self) -> None:
        """Reset all data buffers."""
        self.prices = []
        self.gains = []
        self.losses = []
        self.ema_value = 0.0
        self.has_ema = False
