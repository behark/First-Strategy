"""
Tests for the risk manager module.
"""
import pytest
from src.risk_manager import RiskManager
from src.signal_engine import Direction


class TestRiskManager:
    """Test suite for the RiskManager class."""
    
    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Default parameters
        risk_manager = RiskManager()
        assert risk_manager.profit_pct == 0.004
        assert risk_manager.stop_pct == 0.004
        assert risk_manager.tick_size == 0.0001
        
        # Custom parameters
        risk_manager = RiskManager(profit_pct=0.01, stop_pct=0.005, tick_size=0.01)
        assert risk_manager.profit_pct == 0.01
        assert risk_manager.stop_pct == 0.005
        assert risk_manager.tick_size == 0.01
        
    def test_compute_targets_long(self):
        """Test computing targets for long position."""
        risk_manager = RiskManager(profit_pct=0.01, stop_pct=0.005, tick_size=0.01)
        
        # Long position
        entry_price = 100.0
        take_profit, stop_loss = risk_manager.compute_targets(entry_price, Direction.LONG)
        
        # Take profit: entry * (1 + profit_pct)
        expected_tp = 101.0  # 100 * (1 + 0.01)
        assert take_profit == expected_tp
        
        # Stop loss: entry * (1 - stop_pct)
        expected_sl = 99.5  # 100 * (1 - 0.005)
        assert stop_loss == expected_sl
        
    def test_compute_targets_short(self):
        """Test computing targets for short position."""
        risk_manager = RiskManager(profit_pct=0.01, stop_pct=0.005, tick_size=0.01)
        
        # Short position
        entry_price = 100.0
        take_profit, stop_loss = risk_manager.compute_targets(entry_price, Direction.SHORT)
        
        # Take profit: entry * (1 - profit_pct)
        expected_tp = 99.0  # 100 * (1 - 0.01)
        assert take_profit == expected_tp
        
        # Stop loss: entry * (1 + stop_pct)
        expected_sl = 100.5  # 100 * (1 + 0.005)
        assert stop_loss == expected_sl
        
    def test_tick_size_rounding(self):
        """Test rounding to tick size."""
        risk_manager = RiskManager(profit_pct=0.01, stop_pct=0.005, tick_size=0.05)
        
        # Long position with non-round numbers
        entry_price = 100.0
        take_profit, stop_loss = risk_manager.compute_targets(entry_price, Direction.LONG)
        
        # Take profit: round(100 * 1.01 / 0.05) * 0.05 = round(101.0 / 0.05) * 0.05 = 101.0
        assert take_profit == 101.0
        
        # Stop loss: round(100 * 0.995 / 0.05) * 0.05 = round(99.5 / 0.05) * 0.05 = 99.5
        assert stop_loss == 99.5
        
        # Test with a different tick size
        risk_manager = RiskManager(profit_pct=0.01, stop_pct=0.005, tick_size=0.1)
        take_profit, stop_loss = risk_manager.compute_targets(entry_price, Direction.LONG)
        
        # Take profit: round(101.0 / 0.1) * 0.1 = 101.0
        assert take_profit == 101.0
        
        # Stop loss: round(99.5 / 0.1) * 0.1 = 99.5
        assert stop_loss == 99.5
        
    def test_invalid_entry_price(self):
        """Test handling of invalid entry price."""
        risk_manager = RiskManager()
        
        # Zero entry price
        with pytest.raises(ValueError):
            risk_manager.compute_targets(0.0, Direction.LONG)
            
        # Negative entry price
        with pytest.raises(ValueError):
            risk_manager.compute_targets(-100.0, Direction.SHORT)
            
    def test_invalid_direction(self):
        """Test handling of invalid direction."""
        risk_manager = RiskManager()
        
        # Invalid direction
        with pytest.raises(ValueError):
            risk_manager.compute_targets(100.0, None)
