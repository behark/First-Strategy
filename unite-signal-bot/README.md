# Micro-Scalp Signal Bot

A low-latency trading signal bot that generates alerts based on 2-period RSI and 8-period EMA on 1-minute or tick data.

## Features

- **Real-time Market Data**: Connects to exchange and processes tick data with minimal latency
- **Technical Indicators**: Calculates 2-period RSI and 8-period EMA
- **Signal Generation**: Applies bias filter and entry logic based on price/EMA relationship and RSI crossovers
- **Risk Management**: Automatically calculates profit targets and stop-loss levels
- **Telegram Notifications**: Sends real-time alerts to Telegram with entry price, take profit, and stop loss
- **Robust Error Handling**: Implements exponential backoff, rate limiting, and comprehensive error recovery
- **Low Latency**: Optimized for <300ms end-to-end processing time from tick to alert

## Architecture

The bot is built with a modular architecture consisting of the following components:

1. **MarketData**: Connects to exchange and provides real-time market data
2. **Indicators**: Calculates technical indicators (RSI and EMA)
3. **SignalEngine**: Evaluates market conditions and generates trading signals
4. **RiskManager**: Calculates profit targets and stop-loss levels
5. **TelegramNotifier**: Sends alerts to Telegram

## Signal Logic

- **Bias**: LONG if price > EMA; SHORT if price < EMA
- **Entry**: 
  - LONG: RSI crosses below 10, then back above
  - SHORT: RSI crosses above 90, then back below
- **Risk Management**:
  - LONG: TP = entry * (1 + profit_pct), SL = entry * (1 - stop_pct)
  - SHORT: TP = entry * (1 - profit_pct), SL = entry * (1 + stop_pct)

## Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/unite-signal-bot.git
   cd unite-signal-bot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. Run the bot:
   ```bash
   python -m src.main
   ```

### Docker Deployment

1. Configure environment variables in `infra/docker-compose.yml`

2. Build and start the container:
   ```bash
   cd infra
   docker-compose up -d
   ```

3. Check logs:
   ```bash
   docker-compose logs -f
   ```

## Configuration

The bot can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TRADING_SYMBOL` | Trading pair symbol | `BTCUSDT` |
| `PERIOD_RSI` | Period for RSI calculation | `2` |
| `PERIOD_EMA` | Period for EMA calculation | `8` |
| `PROFIT_PCT` | Take profit percentage | `0.004` |
| `STOP_PCT` | Stop loss percentage | `0.004` |
| `TELEGRAM_TOKEN` | Telegram bot token | - |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | - |

## Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage report:

```bash
pytest --cov=src tests/
```

## Performance

The bot is designed to meet the following latency targets:

| Step | Target Latency |
|------|---------------:|
| Tick ingestion | < 50 ms |
| Indicator update | < 10 ms |
| Signal evaluation | < 5 ms |
| Target computation | < 2 ms |
| Telegram send | < 200 ms |
| **End-to-end (tick→alert)** | < 300 ms total |

## License

MIT

## Disclaimer

This software is for educational purposes only. Use at your own risk. The authors accept no responsibility for any financial losses incurred through the use of this software.
