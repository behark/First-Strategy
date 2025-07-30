# First Strategy - Automated Trading System

A comprehensive automated trading system implementing technical analysis strategies with risk management and order execution capabilities.

## Features

- **Strategy Engine**: RSI and Moving Average based trading signals
- **Order Execution**: Flexible order management system with paper trading support
- **Risk Management**: Position sizing, correlation analysis, and drawdown protection
- **Performance Tracking**: Comprehensive metrics and logging
- **Configurable**: JSON-based configuration system

## Project Structure

```
First-Strategy/
├── strategy.py          # Core trading strategy logic
├── order_executor.py    # Order execution and management
├── risk_manager.py      # Risk management system
├── utils.py            # Utility functions and helpers
├── main.py             # Main execution script
├── config.json.example # Configuration template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/behark/First-Strategy.git
cd First-Strategy
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the strategy:
```bash
cp config.json.example config.json
# Edit config.json with your settings
```

## Usage

### Paper Trading (Recommended for testing)

```bash
python main.py --paper --config config.json
```

### Live Trading (Use with caution)

```bash
python main.py --config config.json
```

### Debug Mode

```bash
python main.py --paper --debug --config config.json
```

## Configuration

The strategy is configured through a JSON file. Key parameters include:

- `symbols`: List of trading pairs to monitor
- `risk_per_trade`: Risk percentage per trade (default: 2%)
- `lookback_period`: Period for technical indicators (default: 20)
- `initial_balance`: Starting balance for paper trading
- `rsi_threshold_low/high`: RSI oversold/overbought levels

## Strategy Logic

The current implementation uses:

1. **RSI (Relative Strength Index)**: Identifies oversold/overbought conditions
2. **Moving Averages**: Confirms trend direction
3. **Risk Management**: Position sizing based on volatility and correlation
4. **Stop Loss/Take Profit**: Automatic position management

## Risk Management

- Maximum position size limits
- Correlation-based position adjustment
- Maximum drawdown protection
- Dynamic position sizing based on volatility

## Performance Metrics

The system tracks:
- Total return and profit factor
- Win rate and Sharpe ratio
- Maximum drawdown
- Trade statistics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies and other financial instruments involves substantial risk and may not be suitable for all investors. Past performance is not indicative of future results. Use at your own risk.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue on GitHub.