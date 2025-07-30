"""
Tests for the indicators module.
"""
import pytest
import numpy as np
from src.indicators import Indicators


class TestIndicators:
    """Test suite for the Indicators class."""
    
    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Default parameters
        indicators = Indicators()
        assert indicators.period_rsi == 2
        assert indicators.period_ema == 8
        
        # Custom parameters
        indicators = Indicators(period_rsi=3, period_ema=10)
        assert indicators.period_rsi == 3
        assert indicators.period_ema == 10
        
    def test_update_with_valid_price(self):
        """Test updating with valid price data."""
        indicators = Indicators()
        
        # First update
        indicators.update(100.0)
        assert len(indicators.prices) == 1
        assert indicators.prices[0] == 100.0
        assert len(indicators.gains) == 0
        assert len(indicators.losses) == 0
        
        # Second update (price increase)
        indicators.update(101.0)
        assert len(indicators.prices) == 2
        assert indicators.prices[1] == 101.0
        assert len(indicators.gains) == 1
        assert indicators.gains[0] == 1.0
        assert len(indicators.losses) == 1
        assert indicators.losses[0] == 0.0
        
        # Third update (price decrease)
        indicators.update(100.5)
        assert len(indicators.prices) == 3
        assert indicators.prices[2] == 100.5
        assert len(indicators.gains) == 2
        assert indicators.gains[1] == 0.0
        assert len(indicators.losses) == 2
        assert indicators.losses[1] == 0.5
        
    def test_update_with_invalid_price(self):
        """Test updating with invalid price data."""
        indicators = Indicators()
        
        # Test with NaN
        with pytest.raises(ValueError):
            indicators.update(float('nan'))
            
        # Test with infinity
        with pytest.raises(ValueError):
            indicators.update(float('inf'))
            
        # Test with non-numeric
        with pytest.raises(ValueError):
            indicators.update("not a number")
            
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        indicators = Indicators(period_rsi=2)
        
        # Not enough data
        with pytest.raises(ValueError):
            indicators.current_rsi()
            
        # Add price data
        indicators.update(100.0)
        
        # Still not enough data
        with pytest.raises(ValueError):
            indicators.current_rsi()
            
        # Add more price data
        indicators.update(101.0)  # Gain: 1.0, Loss: 0.0
        indicators.update(102.0)  # Gain: 1.0, Loss: 0.0
        
        # Calculate RSI: 100 - (100 / (1 + (1.0 / 0.0)))
        # With no losses, RSI should be 100
        assert indicators.current_rsi() == 100.0
        
        # Add a price decrease
        indicators.update(101.0)  # Gain: 0.0, Loss: 1.0
        
        # Calculate RSI: 100 - (100 / (1 + (0.5 / 0.5)))
        # With equal gains and losses, RSI should be 50
        assert indicators.current_rsi() == 50.0
        
    def test_ema_calculation(self):
        """Test EMA calculation."""
        indicators = Indicators(period_ema=3)
        
        # Not enough data
        with pytest.raises(ValueError):
            indicators.current_ema()
            
        # Add price data
        indicators.update(100.0)
        indicators.update(101.0)
        
        # Still not enough data
        with pytest.raises(ValueError):
            indicators.current_ema()
            
        # Add final data point to complete the period
        indicators.update(102.0)
        
        # Initial EMA should be SMA of the period
        assert indicators.current_ema() == 101.0
        
        # Add a new price
        indicators.update(103.0)
        
        # EMA calculation: (Price - Previous EMA) * Multiplier + Previous EMA
        # Multiplier = 2 / (Period + 1) = 2 / 4 = 0.5
        # EMA = (103.0 - 101.0) * 0.5 + 101.0 = 102.0
        assert indicators.current_ema() == 102.0
        
    def test_buffer_trimming(self):
        """Test that buffers are trimmed to required size."""
        indicators = Indicators(period_rsi=2, period_ema=3)
        
        # Add more data than needed
        for i in range(10):
            indicators.update(100.0 + i)
            
        # Check buffer sizes
        assert len(indicators.prices) <= max(indicators.period_rsi + 1, indicators.period_ema)
        assert len(indicators.gains) <= indicators.period_rsi
        assert len(indicators.losses) <= indicators.period_rsi
