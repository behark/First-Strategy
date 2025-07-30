"""
Test suite for the refactored trading system.
"""
import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime

from strategy import TradingStrategy
from risk_manager import RiskManager
from market_data_provider import SyntheticMarketDataProvider
from order_executor import OrderExecutor


class TestTradingStrategy:
    """Test cases for TradingStrategy class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = TradingStrategy(
            symbols=['BTC/USDT', 'ETH/USDT'],
            lookback_period=10,
            rsi_threshold_low=30,
            rsi_threshold_high=70
        )
        
    def test_initialization(self):
        """Test strategy initialization."""
        assert self.strategy.symbols == ['BTC/USDT', 'ETH/USDT']
        assert self.strategy.lookback_period == 10
        assert self.strategy.rsi_threshold_low == 30
        assert self.strategy.rsi_threshold_high == 70
        
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        # Create test price data
        prices = np.array([100, 101, 102, 101, 100, 99, 98, 97, 96, 95])
        rsi = self.strategy.calculate_rsi(prices)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
        
    def test_sma_calculation(self):
        """Test SMA calculation."""
        prices = np.array([100, 101, 102, 103, 104])
        sma = self.strategy.calculate_sma(prices, 3)
        
        assert isinstance(sma, float)
        assert sma == 103.0  # (102 + 103 + 104) / 3
        
    def test_signal_generation(self):
        """Test signal generation with synthetic data."""
        # Create synthetic data
        dates = pd.date_range(start='2023-01-01', periods=20, freq='1min')
        data = pd.DataFrame({
            'close': np.random.normal(100, 5, 20),
            'open': np.random.normal(100, 5, 20),
            'high': np.random.normal(105, 5, 20),
            'low': np.random.normal(95, 5, 20),
            'volume': np.random.poisson(1000, 20)
        }, index=dates)
        
        self.strategy.update_data('BTC/USDT', data)
        signals = self.strategy.generate_signals()
        
        assert isinstance(signals, dict)
        assert 'BTC/USDT' in signals
        assert signals['BTC/USDT'] in ['BUY', 'SELL', 'HOLD']


class TestRiskManager:
    """Test cases for RiskManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(
            max_position_size=0.1,
            max_risk_per_trade=0.02,
            max_correlated_positions=3,
            max_drawdown=0.1
        )
        
    def test_initialization(self):
        """Test risk manager initialization."""
        assert self.risk_manager.max_position_size == 0.1
        assert self.risk_manager.max_risk_per_trade == 0.02
        assert self.risk_manager.max_correlated_positions == 3
        assert self.risk_manager.max_drawdown == 0.1
        
    def test_account_balance_setting(self):
        """Test account balance setting."""
        self.risk_manager.set_account_balance(10000.0)
        assert self.risk_manager.current_balance == 10000.0
        assert self.risk_manager.initial_balance == 10000.0
        assert self.risk_manager.peak_balance == 10000.0
        
    def test_drawdown_calculation(self):
        """Test drawdown calculation."""
        self.risk_manager.set_account_balance(10000.0)
        self.risk_manager.set_account_balance(9000.0)  # 10% drawdown
        
        drawdown = self.risk_manager.calculate_current_drawdown()
        assert abs(drawdown - 0.1) < 1e-10  # Use approximate comparison for floating point
        
    def test_position_sizing(self):
        """Test position sizing logic."""
        self.risk_manager.set_account_balance(10000.0)
        
        should_trade, adjusted_size = self.risk_manager.should_place_trade(
            symbol='BTC/USDT',
            signal='BUY',
            quantity=1.0,
            current_price=50000.0
        )
        
        assert isinstance(should_trade, bool)
        assert isinstance(adjusted_size, float)
        assert adjusted_size >= 0


class TestMarketDataProvider:
    """Test cases for MarketDataProvider class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = SyntheticMarketDataProvider(
            symbols=['BTC/USDT', 'ETH/USDT'],
            lookback_period=10
        )
        
    @pytest.mark.asyncio
    async def test_data_fetching(self):
        """Test market data fetching."""
        data = await self.provider.fetch_data()
        
        assert isinstance(data, dict)
        assert 'BTC/USDT' in data
        assert 'ETH/USDT' in data
        
        # Check data structure
        for symbol, df in data.items():
            assert isinstance(df, pd.DataFrame)
            assert 'open' in df.columns
            assert 'high' in df.columns
            assert 'low' in df.columns
            assert 'close' in df.columns
            assert 'volume' in df.columns
            assert len(df) > 0


class TestOrderExecutor:
    """Test cases for OrderExecutor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = OrderExecutor(
            api_key="test_key",
            api_secret="test_secret",
            paper_trading=True
        )
        
    @pytest.mark.asyncio
    async def test_connection(self):
        """Test broker connection."""
        result = await self.executor.connect()
        assert result is True
        
    @pytest.mark.asyncio
    async def test_signal_execution(self):
        """Test signal execution."""
        await self.executor.connect()
        
        order_id = await self.executor.execute_signal(
            symbol='BTC/USDT',
            signal='BUY',
            quantity=0.1,
            current_price=50000.0
        )
        
        assert isinstance(order_id, str)
        assert order_id.startswith('order_')
        
    @pytest.mark.asyncio
    async def test_disconnection(self):
        """Test broker disconnection."""
        await self.executor.connect()
        await self.executor.disconnect()
        # Should not raise any exceptions


@pytest.mark.asyncio
async def test_integration():
    """Integration test for the complete trading system."""
    # Create components
    strategy = TradingStrategy(['BTC/USDT'], lookback_period=10)
    risk_manager = RiskManager()
    provider = SyntheticMarketDataProvider(['BTC/USDT'], lookback_period=10)
    executor = OrderExecutor(paper_trading=True)
    
    # Set up risk manager
    risk_manager.set_account_balance(10000.0)
    
    # Fetch data
    data = await provider.fetch_data()
    
    # Update strategy
    for symbol, df in data.items():
        strategy.update_data(symbol, df)
    
    # Generate signals
    signals = strategy.generate_signals()
    
    # Test signal processing
    for symbol, signal in signals.items():
        if signal != "HOLD":
            current_price = data[symbol]['close'].iloc[-1]
            
            # Calculate position size
            suggested_size = strategy.get_position_size(
                symbol=symbol,
                account_balance=risk_manager.current_balance,
                risk_per_trade=0.02
            )
            
            if suggested_size is not None:
                # Check risk limits
                should_trade, adjusted_size = risk_manager.should_place_trade(
                    symbol=symbol,
                    signal=signal,
                    quantity=suggested_size,
                    current_price=current_price
                )
                
                if should_trade and adjusted_size > 0:
                    # Execute trade
                    order_id = await executor.execute_signal(
                        symbol=symbol,
                        signal=signal,
                        quantity=adjusted_size,
                        current_price=current_price
                    )
                    
                    assert isinstance(order_id, str)
                    assert order_id.startswith('order_')


if __name__ == "__main__":
    pytest.main([__file__]) 