"""
Market Data Module

Handles connection to exchange and provides real-time market data.
"""
from datetime import datetime
from typing import Callable, Optional
import asyncio
import logging
from time import sleep

logger = logging.getLogger(__name__)

class ConnectionError(Exception):
    """Exception raised when connection to exchange fails."""
    pass


class MarketData:
    """
    Connects to exchange and provides real-time market data.
    
    Attributes:
        symbol: Trading pair symbol
        on_tick: Callback function for tick data
    """
    
    def __init__(self, symbol: str, on_tick: Callable[[float, datetime], None]):
        """
        Initialize MarketData instance.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            on_tick: Callback function that receives price and timestamp
        """
        self.symbol = symbol
        self.on_tick = on_tick
        self.running = False
        self.connection_attempts = 0
        self.max_retries = 5
        
    def start(self) -> None:
        """
        Start receiving market data.
        
        Raises:
            ConnectionError: If connection to exchange fails after max retries
        """
        self.running = True
        self.connection_attempts = 0
        # Implementation would connect to exchange and start receiving data
        pass
        
    def stop(self) -> None:
        """Stop receiving market data."""
        self.running = False
        # Implementation would close connection to exchange
        pass
        
    def _handle_connection_error(self) -> bool:
        """
        Handle connection error with exponential backoff.
        
        Returns:
            bool: True if retry should be attempted, False otherwise
        """
        self.connection_attempts += 1
        if self.connection_attempts > self.max_retries:
            return False
            
        backoff_time = 2 ** self.connection_attempts
        logger.warning(f"Connection error, retrying in {backoff_time}s (attempt {self.connection_attempts}/{self.max_retries})")
        sleep(backoff_time)
        return True
