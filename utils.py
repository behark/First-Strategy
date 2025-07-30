import pandas as pd
import numpy as np
import logging
import json
import os
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

# Configure logging
def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"strategy_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )

def load_config(config_path: str) -> Dict:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Dictionary containing configuration parameters
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return {}

def save_results(results: Dict, filename: str) -> bool:
    """
    Save trading results to a file.
    
    Args:
        results: Dictionary of results
        filename: Output filename
        
    Returns:
        Success status
    """
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Failed to save results: {e}")
        return False

def calculate_performance_metrics(trades: List[Dict], initial_balance: float) -> Dict:
    """
    Calculate performance metrics from a list of trades.
    
    Args:
        trades: List of trade dictionaries
        initial_balance: Initial account balance
        
    Returns:
        Dictionary of performance metrics
    """
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "sharpe_ratio": 0,
            "max_drawdown": 0,
            "total_return": 0
        }
    
    # Extract profits/losses
    profits = [t['profit'] for t in trades]
    winning_trades = [p for p in profits if p > 0]
    losing_trades = [p for p in profits if p < 0]
    
    # Calculate metrics
    total_trades = len(trades)
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
    
    total_profit = sum(winning_trades) if winning_trades else 0
    total_loss = abs(sum(losing_trades)) if losing_trades else 0
    profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
    
    # Calculate cumulative balance over time
    balance = initial_balance
    balances = [balance]
    
    for trade in trades:
        balance += trade['profit']
        balances.append(balance)
    
    # Calculate max drawdown
    peak = initial_balance
    max_drawdown = 0
    
    for b in balances:
        if b > peak:
            peak = b
        else:
            drawdown = (peak - b) / peak
            max_drawdown = max(max_drawdown, drawdown)
    
    # Calculate returns
    returns = [balances[i] / balances[i-1] - 1 for i in range(1, len(balances))]
    
    # Calculate Sharpe ratio (assuming risk-free rate of 0)
    if returns:
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe_ratio = mean_return / std_return * np.sqrt(252) if std_return > 0 else 0
    else:
        sharpe_ratio = 0
    
    total_return = (balances[-1] - initial_balance) / initial_balance if initial_balance > 0 else 0
    
    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "total_return": total_return
    }

def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample OHLCV data to a different timeframe.
    
    Args:
        df: DataFrame with OHLCV data
        timeframe: Target timeframe (e.g., '1H', '4H', '1D')
        
    Returns:
        Resampled DataFrame
    """
    # Make sure DataFrame has a proper datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'timestamp' in df.columns:
            df = df.set_index('timestamp')
        else:
            return df  # Can't resample without datetime index
    
    resampled = df.resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    
    return resampled.dropna()
