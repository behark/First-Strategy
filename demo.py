"""
Demo script for the refactored trading system.
"""
import asyncio
import logging
from datetime import datetime

from main import TradingSystem
from utils import load_config, setup_logging

async def run_demo():
    """Run a demonstration of the trading system."""
    print("🚀 First-Strategy Trading System Demo")
    print("=" * 50)
    
    # Setup logging
    setup_logging(logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_config('config.json')
    if not config:
        print("❌ Failed to load configuration")
        return
    
    print(f"📊 Trading Symbols: {config.get('symbols', [])}")
    print(f"💰 Initial Balance: ${config.get('initial_balance', 10000):,.2f}")
    print(f"🎯 Risk per Trade: {config.get('risk_per_trade', 0.02):.1%}")
    print(f"📈 Paper Trading: {'Yes' if config.get('paper_trading', True) else 'No'}")
    print()
    
    # Create trading system
    trading_system = TradingSystem(config)
    
    try:
        # Start the system
        print("🔄 Starting trading system...")
        if not await trading_system.start():
            print("❌ Failed to start trading system")
            return
        
        print("✅ Trading system started successfully!")
        print()
        
        # Run a few trading cycles
        print("📈 Running trading cycles...")
        for cycle in range(3):
            print(f"\n🔄 Trading Cycle {cycle + 1}")
            print("-" * 30)
            
            # Run one trading cycle
            await trading_system.run_trading_cycle()
            
            # Show current performance
            metrics = trading_system.get_performance_metrics()
            print(f"📊 Total Trades: {metrics.get('total_trades', 0)}")
            print(f"💰 Current Balance: ${trading_system.risk_manager.current_balance:,.2f}")
            
            if metrics.get('total_trades', 0) > 0:
                print(f"🎯 Win Rate: {metrics.get('win_rate', 0):.1%}")
                print(f"📈 Total Return: {metrics.get('total_return', 0):.1%}")
        
        print("\n" + "=" * 50)
        print("📊 Final Performance Summary")
        print("=" * 50)
        
        # Show final metrics
        final_metrics = trading_system.get_performance_metrics()
        print(f"📈 Total Trades: {final_metrics.get('total_trades', 0)}")
        print(f"🎯 Win Rate: {final_metrics.get('win_rate', 0):.1%}")
        print(f"💰 Profit Factor: {final_metrics.get('profit_factor', 0):.2f}")
        print(f"📊 Sharpe Ratio: {final_metrics.get('sharpe_ratio', 0):.2f}")
        print(f"📉 Max Drawdown: {final_metrics.get('max_drawdown', 0):.1%}")
        print(f"💰 Total Return: {final_metrics.get('total_return', 0):.1%}")
        print(f"💵 Final Balance: ${trading_system.risk_manager.current_balance:,.2f}")
        
        # Save results
        trading_system.save_results()
        print(f"\n💾 Results saved to file")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        logger.error(f"Demo error: {e}", exc_info=True)
    finally:
        # Stop the system
        print("\n🔄 Stopping trading system...")
        await trading_system.stop()
        print("✅ Demo completed!")


def main():
    """Main entry point for the demo."""
    print("🎯 First-Strategy Trading System")
    print("A modular, scalable algorithmic trading system")
    print()
    
    # Run the demo
    asyncio.run(run_demo())


if __name__ == "__main__":
    main() 