"""
Main Module

Orchestrates all components of the trading signal bot.
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from src.market_data import MarketData
from src.indicators import Indicators
from src.signal_engine import SignalEngine, Signal
from src.risk_manager import RiskManager
from src.telegram_notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("signal_bot.log")
    ]
)
logger = logging.getLogger(__name__)

class SignalBot:
    """
    Main class that orchestrates all components of the trading signal bot.
    
    Attributes:
        symbol: Trading pair symbol
        period_rsi: Period for RSI calculation
        period_ema: Period for EMA calculation
        profit_pct: Take profit percentage
        stop_pct: Stop loss percentage
    """
    
    def __init__(
        self,
        symbol: str,
        period_rsi: int = 2,
        period_ema: int = 8,
        profit_pct: float = 0.004,
        stop_pct: float = 0.004,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        """
        Initialize SignalBot instance.
        
        Args:
            symbol: Trading pair symbol
            period_rsi: Period for RSI calculation
            period_ema: Period for EMA calculation
            profit_pct: Take profit percentage
            stop_pct: Stop loss percentage
            telegram_token: Telegram bot token
            telegram_chat_id: Telegram chat ID
        """
        self.symbol = symbol
        
        # Initialize components
        self.indicators = Indicators(period_rsi=period_rsi, period_ema=period_ema)
        self.signal_engine = SignalEngine()
        self.risk_manager = RiskManager(profit_pct=profit_pct, stop_pct=stop_pct)
        self.market_data = MarketData(symbol=symbol, on_tick=self._on_tick)
        
        # Initialize Telegram notifier if credentials are provided
        self.telegram_notifier = None
        if telegram_token and telegram_chat_id:
            self.telegram_notifier = TelegramNotifier(
                bot_token=telegram_token,
                chat_id=telegram_chat_id
            )
            
        # Performance metrics
        self.tick_count = 0
        self.signal_count = 0
        self.last_tick_time: Optional[datetime] = None
        self.processing_times = []
        
    async def start(self):
        """Start the signal bot."""
        logger.info(f"Starting signal bot for {self.symbol}")
        self.market_data.start()
        
    async def stop(self):
        """Stop the signal bot."""
        logger.info("Stopping signal bot")
        self.market_data.stop()
        
    def _on_tick(self, price: float, timestamp: datetime):
        """
        Process new tick data.
        
        Args:
            price: Latest price
            timestamp: Timestamp of the tick
        """
        start_time = datetime.utcnow()
        self.tick_count += 1
        
        try:
            # Update indicators
            self.indicators.update(price)
            
            # Get indicator values
            try:
                rsi = self.indicators.current_rsi()
                ema = self.indicators.current_ema()
                
                # Evaluate signal
                signal = self.signal_engine.evaluate(price, rsi, ema)
                
                # Process signal if generated
                if signal:
                    self._process_signal(signal)
                    
            except ValueError as e:
                # Not enough data for indicators yet
                logger.debug(f"Indicator calculation skipped: {e}")
                
        except Exception as e:
            logger.error(f"Error processing tick: {e}")
            
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000  # in ms
        self.processing_times.append(processing_time)
        
        # Log performance metrics periodically
        if self.tick_count % 100 == 0:
            self._log_performance_metrics()
            
        # Store last tick time for latency calculation
        self.last_tick_time = timestamp
        
    def _process_signal(self, signal: Signal):
        """
        Process generated trading signal.
        
        Args:
            signal: Trading signal
        """
        self.signal_count += 1
        logger.info(f"Signal generated: {signal.direction.value} @ {signal.entry_price}")
        
        try:
            # Calculate risk parameters
            take_profit, stop_loss = self.risk_manager.compute_targets(
                signal.entry_price, signal.direction
            )
            
            # Update signal with risk parameters
            signal.take_profit = take_profit
            signal.stop_loss = stop_loss
            
            # Send notification if Telegram is configured
            if self.telegram_notifier:
                self.telegram_notifier.send_signal(signal)
                
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
            
    def _log_performance_metrics(self):
        """Log performance metrics."""
        if not self.processing_times:
            return
            
        avg_time = sum(self.processing_times) / len(self.processing_times)
        max_time = max(self.processing_times)
        
        logger.info(
            f"Performance metrics: "
            f"Ticks: {self.tick_count}, "
            f"Signals: {self.signal_count}, "
            f"Avg processing time: {avg_time:.2f}ms, "
            f"Max processing time: {max_time:.2f}ms"
        )
        
        # Reset processing times list to avoid memory growth
        self.processing_times = self.processing_times[-100:]


async def main():
    """Main entry point."""
    # Get configuration from environment variables
    symbol = os.getenv("TRADING_SYMBOL", "BTCUSDT")
    period_rsi = int(os.getenv("PERIOD_RSI", "2"))
    period_ema = int(os.getenv("PERIOD_EMA", "8"))
    profit_pct = float(os.getenv("PROFIT_PCT", "0.004"))
    stop_pct = float(os.getenv("STOP_PCT", "0.004"))
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Create and start signal bot
    bot = SignalBot(
        symbol=symbol,
        period_rsi=period_rsi,
        period_ema=period_ema,
        profit_pct=profit_pct,
        stop_pct=stop_pct,
        telegram_token=telegram_token,
        telegram_chat_id=telegram_chat_id
    )
    
    try:
        await bot.start()
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
