"""
Risk Manager Module

Calculates risk parameters for trading signals.
"""
from typing import Tuple
import logging
from src.signal_engine import Direction

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Calculates risk parameters for trading signals.
    
    Attributes:
        profit_pct: Take profit percentage
        stop_pct: Stop loss percentage
        tick_size: Minimum price movement
    """
    
    def __init__(self, profit_pct: float = 0.004, stop_pct: float = 0.004, tick_size: float = 0.0001):
        """
        Initialize RiskManager instance.
        
        Args:
            profit_pct: Take profit percentage (default: 0.004 = 0.4%)
            stop_pct: Stop loss percentage (default: 0.004 = 0.4%)
            tick_size: Minimum price movement (default: 0.0001)
        """
        self.profit_pct = profit_pct
        self.stop_pct = stop_pct
        self.tick_size = tick_size
        
    def compute_targets(self, entry_price: float, direction: Direction) -> Tuple[float, float]:
        """
        Compute take profit and stop loss targets.
        
        Args:
            entry_price: Entry price
            direction: Trading direction (LONG/SHORT)
            
        Returns:
            Tuple of (take_profit, stop_loss)
            
        Raises:
            ValueError: If entry_price is invalid
        """
        if entry_price <= 0:
            raise ValueError(f"Invalid entry price: {entry_price}")
            
        if direction == Direction.LONG:
            take_profit = entry_price * (1 + self.profit_pct)
            stop_loss = entry_price * (1 - self.stop_pct)
        elif direction == Direction.SHORT:
            take_profit = entry_price * (1 - self.profit_pct)
            stop_loss = entry_price * (1 + self.stop_pct)
        else:
            raise ValueError(f"Invalid direction: {direction}")
            
        # Round to tick size
        take_profit = self._round_to_tick(take_profit)
        stop_loss = self._round_to_tick(stop_loss)
        
        return take_profit, stop_loss
        
    def _round_to_tick(self, price: float) -> float:
        """
        Round price to nearest tick size.
        
        Args:
            price: Price to round
            
        Returns:
            Rounded price
        """
        return round(price / self.tick_size) * self.tick_size
