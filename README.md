# First-Strategy Trading System

A modular, scalable trading system built with Python that implements algorithmic trading strategies with comprehensive risk management and real-time market data processing.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns with dedicated components for strategy, execution, risk management, and market data
- **Async Support**: Built with asyncio for high-performance, non-blocking operations
- **Multiple Data Sources**: Support for synthetic data (testing) and real exchange data
- **Comprehensive Risk Management**: Position sizing, correlation analysis, drawdown protection
- **Real-time Processing**: Efficient market data processing and signal generation
- **Extensible Design**: Easy to add new strategies, data sources, and execution methods

## 📁 Project Structure

```
First-Strategy/
├── main.py                 # Main entry point with TradingSystem orchestrator
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── strategy.py           # Trading strategy implementation
├── order_executor.py     # Order execution and broker integration
├── risk_manager.py       # Risk management and position sizing
├── market_data_provider.py # Market data fetching and management
├── utils.py              # Utility functions and helpers
└── unite-signal-bot/     # Separate signal bot implementation
    ├── src/
    │   ├── main.py       # Signal bot orchestrator
    │   ├── signal_engine.py # Signal generation engine
    │   ├── indicators.py # Technical indicators
    │   ├── market_data.py # Market data handling
    │   ├── risk_manager.py # Risk management
    │   └── telegram_notifier.py # Telegram notifications
    ├── tests/            # Test suite
    └── infra/           # Docker and deployment files
```

## 🏗️ Architecture

### Core Components

1. **TradingSystem** (`main.py`)
   - Main orchestrator that coordinates all components
   - Manages the trading lifecycle
   - Handles configuration and logging

2. **TradingStrategy** (`strategy.py`)
   - Implements trading logic and signal generation
   - Supports multiple technical indicators (RSI, SMA, etc.)
   - Calculates position sizes based on risk parameters

3. **OrderExecutor** (`order_executor.py`)
   - Handles order submission and management
   - Supports paper trading and live trading modes
   - Async implementation for better performance

4. **RiskManager** (`risk_manager.py`)
   - Manages position sizing and risk limits
   - Tracks correlation between positions
   - Implements drawdown protection

5. **MarketDataProvider** (`market_data_provider.py`)
   - Abstract interface for market data sources
   - Supports synthetic data for testing
   - Extensible for real exchange integration

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd First-Strategy
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the system**
   - Copy `config.json` and modify settings
   - Add API keys if using real exchange data
   - Adjust risk parameters as needed

## 🚀 Usage

### Basic Usage

```bash
# Run with default configuration
python main.py

# Run with custom config file
python main.py --config my_config.json

# Enable paper trading
python main.py --paper

# Enable debug logging
python main.py --debug
```

### Configuration

The system is configured via `config.json`:

```json
{
  "symbols": ["BTC/USDT", "ETH/USDT"],
  "paper_trading": true,
  "risk_per_trade": 0.02,
  "max_position_size": 0.1,
  "market_data": {
    "provider": "synthetic",
    "exchange": "binance"
  }
}
```

### Adding New Strategies

1. **Extend TradingStrategy class**:
   ```python
   class MyCustomStrategy(TradingStrategy):
       def generate_signals(self) -> Dict[str, str]:
           # Implement your strategy logic
           pass
   ```

2. **Add new indicators**:
   ```python
   def calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20):
       # Implement Bollinger Bands calculation
       pass
   ```

### Adding New Data Sources

1. **Implement MarketDataProvider**:
   ```python
   class MyExchangeProvider(MarketDataProvider):
       async def fetch_data(self) -> Dict[str, pd.DataFrame]:
           # Implement data fetching logic
           pass
   ```

2. **Update configuration**:
   ```json
   {
     "market_data": {
       "provider": "my_exchange"
     }
   }
   ```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_strategy.py
```

## 📊 Performance Monitoring

The system includes built-in performance monitoring:

- **Processing times**: Track signal generation and execution latency
- **Risk metrics**: Monitor drawdown, correlation, and position exposure
- **Trading metrics**: Win rate, profit factor, Sharpe ratio

## 🔧 Development

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black .

# Check types
mypy .

# Lint code
flake8 .
```

### Adding Features

1. **Follow the modular pattern**: Each component should have a clear interface
2. **Use async/await**: For I/O operations and better performance
3. **Add comprehensive tests**: For new functionality
4. **Update documentation**: Keep README and docstrings current

## 🚨 Risk Disclaimer

This software is for educational and research purposes. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
- Create an issue on GitHub
- Check the documentation in each module
- Review the test files for usage examples 