from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import logging

class RiskManager:
    """
    Handles risk management for the trading strategy.
    """
    
    def __init__(self, max_position_size: float = 0.1, max_risk_per_trade: float = 0.02,
                 max_correlated_positions: int = 3, max_drawdown: float = 0.1):
        """
        Initialize the risk manager with configuration parameters.
        
        Args:
            max_position_size: Maximum size of a position as a fraction of account balance
            max_risk_per_trade: Maximum risk per trade as a fraction of account balance
            max_correlated_positions: Maximum number of correlated positions to hold
            max_drawdown: Maximum drawdown allowed before stopping trading
        """
        self.max_position_size = max_position_size
        self.max_risk_per_trade = max_risk_per_trade
        self.max_correlated_positions = max_correlated_positions
        self.max_drawdown = max_drawdown
        self.logger = logging.getLogger(__name__)
        
        # Track account metrics
        self.initial_balance = 0.0
        self.current_balance = 0.0
        self.peak_balance = 0.0
        self.positions = {}  # symbol -> position_size
        self.correlation_matrix = None
        
    def set_account_balance(self, balance: float) -> None:
        """
        Update the current account balance.
        
        Args:
            balance: Current account balance
        """
        if self.initial_balance == 0:
            self.initial_balance = balance
            self.peak_balance = balance
            
        self.current_balance = balance
        
        if balance > self.peak_balance:
            self.peak_balance = balance
            
    def update_position(self, symbol: str, position_size: float) -> None:
        """
        Update the position size for a symbol.
        
        Args:
            symbol: Trading symbol
            position_size: Current position size
        """
        self.positions[symbol] = position_size
        
    def update_correlation_matrix(self, price_data: Dict[str, pd.DataFrame]) -> None:
        """
        Update the correlation matrix between different symbols.
        
        Args:
            price_data: Dictionary mapping symbols to their price data
        """
        # Extract returns
        returns_dict = {}
        for symbol, df in price_data.items():
            if len(df) > 1:
                returns_dict[symbol] = df['close'].pct_change().dropna()
                
        if returns_dict:
            # Create DataFrame with returns
            returns_df = pd.DataFrame(returns_dict)
            # Calculate correlation matrix
            self.correlation_matrix = returns_df.corr()
            
    def calculate_current_drawdown(self) -> float:
        """
        Calculate the current drawdown from the peak balance.
        
        Returns:
            Current drawdown as a fraction
        """
        if self.peak_balance == 0:
            return 0.0
            
        return 1.0 - (self.current_balance / self.peak_balance)
        
    def check_drawdown_limit(self) -> bool:
        """
        Check if the current drawdown exceeds the maximum allowed.
        
        Returns:
            True if trading should continue, False if drawdown limit reached
        """
        current_drawdown = self.calculate_current_drawdown()
        
        if current_drawdown > self.max_drawdown:
            self.logger.warning(f"Drawdown limit reached: {current_drawdown:.2%}")
            return False
            
        return True
        
    def adjust_position_size(self, symbol: str, suggested_size: float, 
                            current_price: float) -> float:
        """
        Adjust the suggested position size based on risk parameters.
        
        Args:
            symbol: Trading symbol
            suggested_size: Originally suggested position size
            current_price: Current market price
            
        Returns:
            Adjusted position size
        """
        # Limit position size by max_position_size
        max_size = self.current_balance * self.max_position_size / current_price
        adjusted_size = min(suggested_size, max_size)
        
        # Check for correlated positions
        if self.correlation_matrix is not None and symbol in self.correlation_matrix:
            correlated_symbols = []
            
            for other_symbol in self.positions:
                if other_symbol in self.correlation_matrix:
                    correlation = self.correlation_matrix.loc[symbol, other_symbol]
                    if abs(correlation) > 0.7:  # High correlation threshold
                        correlated_symbols.append((other_symbol, correlation))
            
            # If we have too many correlated positions, reduce size
            if len(correlated_symbols) >= self.max_correlated_positions:
                self.logger.info(f"Reducing position size due to {len(correlated_symbols)} correlated positions")
                adjusted_size *= 0.5  # Reduce by half
                
        return adjusted_size
        
    def should_place_trade(self, symbol: str, signal: str, quantity: float, 
                          current_price: float) -> Tuple[bool, float]:
        """
        Determine if a trade should be placed and adjust its size.
        
        Args:
            symbol: Trading symbol
            signal: Trading signal ('BUY' or 'SELL')
            quantity: Proposed trade quantity
            current_price: Current market price
            
        Returns:
            Tuple of (should_trade, adjusted_quantity)
        """
        # Check overall risk limits
        if not self.check_drawdown_limit():
            return False, 0
            
        # Calculate the trade value
        trade_value = quantity * current_price
        
        # Check maximum risk per trade
        max_trade_value = self.current_balance * self.max_risk_per_trade
        if trade_value > max_trade_value:
            adjusted_quantity = max_trade_value / current_price
            self.logger.info(f"Adjusted trade quantity from {quantity} to {adjusted_quantity} due to risk limits")
            quantity = adjusted_quantity
            
        # Further adjust based on position size limits and correlations
        adjusted_quantity = self.adjust_position_size(symbol, quantity, current_price)
        
        return True, adjusted_quantity
