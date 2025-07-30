"""
Signal Engine Module

Evaluates market conditions and generates trading signals.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Direction(Enum):
    """Trading direction enum."""
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Signal:
    """
    Trading signal data class.
    
    Attributes:
        direction: Trading direction (LONG/SHORT)
        entry_price: Price at signal generation
        stop_loss: Stop loss price
        take_profit: Take profit price
        timestamp: Signal generation timestamp
    """
    direction: Direction
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime


class SignalEngine:
    """
    Evaluates market conditions and generates trading signals.
    
    Attributes:
        long_threshold: RSI threshold for long signals
        short_threshold: RSI threshold for short signals
        last_rsi: Last RSI value
        crossed_long_threshold: Whether RSI crossed below long threshold
        crossed_short_threshold: Whether RSI crossed above short threshold
    """
    
    def __init__(self, long_threshold: float = 10.0, short_threshold: float = 90.0):
        """
        Initialize SignalEngine instance.
        
        Args:
            long_threshold: RSI threshold for long signals (default: 10.0)
            short_threshold: RSI threshold for short signals (default: 90.0)
        """
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        self.last_rsi: Optional[float] = None
        self.crossed_long_threshold = False
        self.crossed_short_threshold = False
        
    def evaluate(self, price: float, rsi: float, ema: float) -> Optional[Signal]:
        """
        Evaluate market conditions and generate trading signal.
        
        Args:
            price: Current price
            rsi: Current RSI value
            ema: Current EMA value
            
        Returns:
            Signal object if signal is generated, None otherwise
        """
        # Determine bias based on price vs EMA
        if price > ema:
            bias = Direction.LONG
        elif price < ema:
            bias = Direction.SHORT
        else:
            # No bias if price equals EMA
            bias = None
            
        # Check for RSI threshold crossings
        if self.last_rsi is not None:
            # Check for long signal
            if bias == Direction.LONG:
                if self.last_rsi < self.long_threshold and rsi >= self.long_threshold:
                    self.crossed_long_threshold = True
                elif self.crossed_long_threshold and self.last_rsi <= rsi:
                    # RSI crossed back above threshold and is now rising
                    self.crossed_long_threshold = False
                    return self._create_signal(Direction.LONG, price)
                    
            # Check for short signal
            elif bias == Direction.SHORT:
                if self.last_rsi > self.short_threshold and rsi <= self.short_threshold:
                    self.crossed_short_threshold = True
                elif self.crossed_short_threshold and self.last_rsi >= rsi:
                    # RSI crossed back below threshold and is now falling
                    self.crossed_short_threshold = False
                    return self._create_signal(Direction.SHORT, price)
                    
        # Update last RSI value
        self.last_rsi = rsi
        
        # No signal generated
        return None
        
    def _create_signal(self, direction: Direction, price: float) -> Signal:
        """
        Create a signal object.
        
        Args:
            direction: Trading direction
            price: Current price
            
        Returns:
            Signal object
        """
        # Note: Stop loss and take profit will be calculated by RiskManager
        # This is just a placeholder
        return Signal(
            direction=direction,
            entry_price=price,
            stop_loss=0.0,
            take_profit=0.0,
            timestamp=datetime.utcnow()
        )
