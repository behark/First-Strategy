"""
Tests for the signal engine module.
"""
import pytest
from datetime import datetime
from src.signal_engine import SignalEngine, Direction


class TestSignalEngine:
    """Test suite for the SignalEngine class."""
    
    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Default parameters
        engine = SignalEngine()
        assert engine.long_threshold == 10.0
        assert engine.short_threshold == 90.0
        assert engine.last_rsi is None
        assert engine.crossed_long_threshold is False
        assert engine.crossed_short_threshold is False
        
        # Custom parameters
        engine = SignalEngine(long_threshold=20.0, short_threshold=80.0)
        assert engine.long_threshold == 20.0
        assert engine.short_threshold == 80.0
        
    def test_long_signal_generation(self):
        """Test long signal generation."""
        engine = SignalEngine()
        
        # Initial state
        assert engine.last_rsi is None
        
        # No signal on first update (no previous RSI)
        signal = engine.evaluate(price=100.0, rsi=15.0, ema=99.0)
        assert signal is None
        assert engine.last_rsi == 15.0
        
        # RSI crosses below threshold
        signal = engine.evaluate(price=100.0, rsi=9.0, ema=99.0)
        assert signal is None
        assert engine.crossed_long_threshold is False
        
        # RSI crosses above threshold
        signal = engine.evaluate(price=100.0, rsi=11.0, ema=99.0)
        assert signal is None
        assert engine.crossed_long_threshold is True
        
        # RSI continues to rise
        signal = engine.evaluate(price=100.0, rsi=12.0, ema=99.0)
        assert signal is not None
        assert signal.direction == Direction.LONG
        assert signal.entry_price == 100.0
        assert engine.crossed_long_threshold is False
        
    def test_short_signal_generation(self):
        """Test short signal generation."""
        engine = SignalEngine()
        
        # Initial state
        assert engine.last_rsi is None
        
        # No signal on first update (no previous RSI)
        signal = engine.evaluate(price=100.0, rsi=85.0, ema=101.0)
        assert signal is None
        assert engine.last_rsi == 85.0
        
        # RSI crosses above threshold
        signal = engine.evaluate(price=100.0, rsi=91.0, ema=101.0)
        assert signal is None
        assert engine.crossed_short_threshold is False
        
        # RSI crosses below threshold
        signal = engine.evaluate(price=100.0, rsi=89.0, ema=101.0)
        assert signal is None
        assert engine.crossed_short_threshold is True
        
        # RSI continues to fall
        signal = engine.evaluate(price=100.0, rsi=88.0, ema=101.0)
        assert signal is not None
        assert signal.direction == Direction.SHORT
        assert signal.entry_price == 100.0
        assert engine.crossed_short_threshold is False
        
    def test_bias_filter(self):
        """Test bias filter based on price vs EMA."""
        engine = SignalEngine()
        
        # Set up initial state
        engine.last_rsi = 50.0
        engine.crossed_long_threshold = True
        
        # Price above EMA (LONG bias)
        signal = engine.evaluate(price=101.0, rsi=51.0, ema=100.0)
        assert signal is not None
        assert signal.direction == Direction.LONG
        
        # Reset state
        engine = SignalEngine()
        engine.last_rsi = 50.0
        engine.crossed_long_threshold = True
        
        # Price below EMA (SHORT bias) - should not generate LONG signal
        signal = engine.evaluate(price=99.0, rsi=51.0, ema=100.0)
        assert signal is None
        
        # Reset state
        engine = SignalEngine()
        engine.last_rsi = 50.0
        engine.crossed_short_threshold = True
        
        # Price below EMA (SHORT bias)
        signal = engine.evaluate(price=99.0, rsi=49.0, ema=100.0)
        assert signal is not None
        assert signal.direction == Direction.SHORT
        
        # Reset state
        engine = SignalEngine()
        engine.last_rsi = 50.0
        engine.crossed_short_threshold = True
        
        # Price above EMA (LONG bias) - should not generate SHORT signal
        signal = engine.evaluate(price=101.0, rsi=49.0, ema=100.0)
        assert signal is None
        
    def test_no_bias(self):
        """Test behavior when price equals EMA (no bias)."""
        engine = SignalEngine()
        
        # Set up initial state
        engine.last_rsi = 50.0
        engine.crossed_long_threshold = True
        
        # Price equals EMA (no bias)
        signal = engine.evaluate(price=100.0, rsi=51.0, ema=100.0)
        assert signal is None
        
        # Reset state
        engine = SignalEngine()
        engine.last_rsi = 50.0
        engine.crossed_short_threshold = True
        
        # Price equals EMA (no bias)
        signal = engine.evaluate(price=100.0, rsi=49.0, ema=100.0)
        assert signal is None
