"""
Main Trading Strategy Module

Orchestrates all components of the trading strategy with improved modularity.
"""
import asyncio
import logging
import argparse
import os
from datetime import datetime
from typing import Dict, List, Optional

from strategy import TradingStrategy
from order_executor import OrderExecutor
from risk_manager import RiskManager
from market_data_provider import MarketDataProvider
from utils import setup_logging, load_config, save_results, calculate_performance_metrics

logger = logging.getLogger(__name__)

class TradingSystem:
    """
    Main trading system that orchestrates all components.
    
    Attributes:
        config: Configuration dictionary
        strategy: Trading strategy instance
        order_executor: Order execution component
        risk_manager: Risk management component
        market_data: Market data provider
        symbols: List of trading symbols
        trades: List of executed trades
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the trading system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.symbols = config.get('symbols', ['BTC/USDT', 'ETH/USDT'])
        self.trades = []
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all trading system components."""
        # Initialize strategy
        self.strategy = TradingStrategy(
            symbols=self.symbols,
            lookback_period=self.config.get('lookback_period', 20),
            rsi_threshold_low=self.config.get('rsi_threshold_low', 30),
            rsi_threshold_high=self.config.get('rsi_threshold_high', 70)
        )
        
        # Initialize order executor
        self.order_executor = OrderExecutor(
            api_key=self.config.get('api_key', ''),
            api_secret=self.config.get('api_secret', ''),
            paper_trading=self.config.get('paper_trading', True)
        )
        
        # Initialize risk manager
        self.risk_manager = RiskManager(
            max_position_size=self.config.get('max_position_size', 0.1),
            max_risk_per_trade=self.config.get('max_risk_per_trade', 0.02),
            max_correlated_positions=self.config.get('max_correlated_positions', 3),
            max_drawdown=self.config.get('max_drawdown', 0.1)
        )
        
        # Initialize market data provider
        self.market_data = MarketDataProvider(
            symbols=self.symbols,
            lookback_period=self.config.get('lookback_period', 20)
        )
        
    async def start(self):
        """Start the trading system."""
        logger.info(f"Starting trading system with {len(self.symbols)} symbols")
        
        # Connect to broker
        if not await self.order_executor.connect():
            logger.error("Failed to connect to broker API")
            return False
            
        # Initialize account balance
        initial_balance = self.config.get('initial_balance', 10000.0)
        self.risk_manager.set_account_balance(initial_balance)
        
        logger.info("Trading system started successfully")
        return True
        
    async def stop(self):
        """Stop the trading system."""
        logger.info("Stopping trading system")
        await self.order_executor.disconnect()
        
    async def run_trading_cycle(self):
        """Run one complete trading cycle."""
        try:
            # Fetch market data
            price_data = await self.market_data.fetch_data()
            
            # Update strategy with new data
            for symbol, data in price_data.items():
                self.strategy.update_data(symbol, data)
            
            # Update risk manager correlation matrix
            self.risk_manager.update_correlation_matrix(price_data)
            
            # Generate trading signals
            signals = self.strategy.generate_signals()
            logger.debug(f"Generated signals: {signals}")
            
            # Process signals
            await self._process_signals(signals, price_data)
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
            
    async def _process_signals(self, signals: Dict[str, str], price_data: Dict):
        """Process generated trading signals."""
        risk_per_trade = self.config.get('risk_per_trade', 0.02)
        
        for symbol, signal in signals.items():
            if signal == "HOLD":
                continue
                
            current_price = price_data[symbol]['close'].iloc[-1]
            
            # Calculate position size
            suggested_size = self.strategy.get_position_size(
                symbol=symbol,
                account_balance=self.risk_manager.current_balance,
                risk_per_trade=risk_per_trade
            )
            
            if suggested_size is None:
                continue
                
            # Check risk limits
            should_trade, adjusted_size = self.risk_manager.should_place_trade(
                symbol=symbol,
                signal=signal,
                quantity=suggested_size,
                current_price=current_price
            )
            
            if should_trade and adjusted_size > 0:
                # Execute the trade
                order_id = await self.order_executor.execute_signal(
                    symbol=symbol,
                    signal=signal,
                    quantity=adjusted_size,
                    current_price=current_price
                )
                
                if order_id:
                    await self._record_trade(symbol, signal, current_price, adjusted_size, order_id)
                    
    async def _record_trade(self, symbol: str, signal: str, price: float, 
                           quantity: float, order_id: str):
        """Record an executed trade."""
        logger.info(f"Executed {signal} order for {symbol}: {quantity} units at {price}")
        
        trade = {
            "symbol": symbol,
            "type": signal,
            "price": price,
            "quantity": quantity,
            "timestamp": datetime.now().isoformat(),
            "order_id": order_id,
            "profit": 0.0  # Will be calculated when position is closed
        }
        
        self.trades.append(trade)
        
        # Update positions in risk manager
        position_value = quantity * price
        position_direction = 1 if signal == "BUY" else -1
        self.risk_manager.update_position(symbol, position_value * position_direction)
        
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics."""
        initial_balance = self.config.get('initial_balance', 10000.0)
        return calculate_performance_metrics(self.trades, initial_balance)
        
    def save_results(self):
        """Save trading results to file."""
        metrics = self.get_performance_metrics()
        results = {
            "trades": self.trades,
            "metrics": metrics,
            "final_balance": self.risk_manager.current_balance
        }
        
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if save_results(results, filename):
            logger.info(f"Results saved to {filename}")
        else:
            logger.error("Failed to save results")


async def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--config', type=str, default='config.json', help='Path to configuration file')
    parser.add_argument('--paper', action='store_true', help='Use paper trading mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    # Load configuration
    config_path = args.config
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return
        
    config = load_config(config_path)
    if not config:
        logger.error("Failed to load configuration")
        return
        
    # Update config with command line arguments
    config['paper_trading'] = args.paper
    
    # Create and start trading system
    trading_system = TradingSystem(config)
    
    try:
        if not await trading_system.start():
            return
            
        # Main trading loop
        update_interval = config.get('update_interval', 60)
        
        while True:
            await trading_system.run_trading_cycle()
            await asyncio.sleep(update_interval)
            
    except KeyboardInterrupt:
        logger.info("Strategy stopped by user")
    except Exception as e:
        logger.error(f"Error in main loop: {e}", exc_info=True)
    finally:
        # Calculate and log performance metrics
        metrics = trading_system.get_performance_metrics()
        logger.info(f"Strategy performance: {metrics}")
        
        # Save results
        trading_system.save_results()
        
        # Stop the system
        await trading_system.stop()
        
        logger.info("Strategy execution completed")


if __name__ == "__main__":
    asyncio.run(main())
