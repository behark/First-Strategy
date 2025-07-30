"""
Tests for utility functions.
"""
import pytest
import json
import pandas as pd
import numpy as np
from datetime import datetime

from utils import load_config, save_results, calculate_performance_metrics, resample_ohlcv


def test_load_config_success(tmp_path):
    """Test successful configuration loading."""
    config = {'symbols': ['BTC/USDT'], 'risk_per_trade': 0.02}
    config_file = tmp_path / 'config.json'
    config_file.write_text(json.dumps(config))
    result = load_config(str(config_file))
    assert result == config


def test_load_config_failure(tmp_path, caplog):
    """Test configuration loading failure handling."""
    missing_file = tmp_path / 'nonexistent.json'
    result = load_config(str(missing_file))
    assert result == {}
    assert 'Failed to load configuration' in caplog.text


def test_save_results_success(tmp_path):
    """Test successful results saving."""
    results = {'total_trades': 10, 'profit': 123.45}
    output_file = tmp_path / 'results.json'
    success = save_results(results, str(output_file))
    assert success
    assert output_file.exists()
    assert json.loads(output_file.read_text()) == results


def test_save_results_failure(monkeypatch, caplog):
    """Test results saving failure handling."""
    monkeypatch.setattr('builtins.open', lambda *args, **kwargs: (_ for _ in ()).throw(Exception('disk error')))
    success = save_results({'a': 1}, 'dummy.json')
    assert not success
    assert 'Failed to save results' in caplog.text


def test_calculate_performance_metrics_no_trades():
    """Test performance metrics calculation with no trades."""
    metrics = calculate_performance_metrics([], initial_balance=1000.0)
    expected = {
        'total_trades': 0,
        'win_rate': 0,
        'profit_factor': 0,
        'sharpe_ratio': 0,
        'max_drawdown': 0,
        'total_return': 0
    }
    assert metrics == expected


def test_calculate_performance_metrics_basic():
    """Test performance metrics calculation with sample trades."""
    trades = [
        {'profit': 100, 'timestamp': datetime.now()},
        {'profit': -50, 'timestamp': datetime.now()},
        {'profit': 150, 'timestamp': datetime.now()}
    ]
    metrics = calculate_performance_metrics(trades, initial_balance=1000.0)
    assert metrics['total_trades'] == 3
    assert metrics['win_rate'] == pytest.approx(2/3)
    assert metrics['total_return'] == pytest.approx((100 - 50 + 150) / 1000.0)


def test_resample_ohlcv():
    """Test OHLCV data resampling functionality."""
    timestamps = pd.date_range(start='2021-01-01', periods=60, freq='min')
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': np.arange(60.0),
        'high': np.arange(60.0) + 1,
        'low': np.arange(60.0) - 1,
        'close': np.arange(60.0) * 2,
        'volume': np.ones(60)
    })
    resampled = resample_ohlcv(df, timeframe='1H')
    assert isinstance(resampled, pd.DataFrame)
    assert len(resampled) == 1
    for col in ['open', 'high', 'low', 'close', 'volume']:
        assert col in resampled.columns


def test_config_example_keys():
    """Test that config.json.example contains all required keys."""
    config = load_config('config.json.example')
    required_keys = [
        'symbols', 'risk_per_trade', 'lookback_period', 
        'initial_balance', 'rsi_threshold_low', 'rsi_threshold_high'
    ]
    for key in required_keys:
        assert key in config 