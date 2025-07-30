#!/usr/bin/env python3
"""
AI Testing System CLI
Provides easy command-line access to AI-powered testing features.
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

from ai_test_analyzer import AITestAnalyzer, TelegramNotifier
from automated_test_runner import AutomatedTestRunner


class AITestCLI:
    """Command-line interface for AI testing system."""
    
    def __init__(self):
        self.config_file = Path("ai_test_config.json")
        self.config = self._load_config()
        self.analyzer = AITestAnalyzer()
        self.runner = AutomatedTestRunner(
            bot_token=self.config["telegram"]["bot_token"],
            chat_id=self.config["telegram"]["chat_id"]
        )
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "telegram": {
                    "bot_token": "7634324156:AAFupAZCihSHKq-mj3wBZ3tDLfeyzXl5aRo",
                    "chat_id": "1507876704",
                    "notifications_enabled": True
                },
                "testing": {
                    "continuous_testing_interval_minutes": 30,
                    "coverage_threshold": 80.0,
                    "quality_score_threshold": 0.7,
                    "enable_quick_tests": True,
                    "enable_full_analysis": True
                }
            }
    
    async def run_analysis(self):
        """Run AI analysis and send report."""
        print("🤖 Running AI test analysis...")
        metrics = await self.analyzer.run_coverage_analysis()
        report_file = await self.analyzer.generate_html_report(metrics)
        
        print(f"📊 Coverage: {metrics.coverage_percentage:.1f}%")
        print(f"🎯 Quality Score: {metrics.test_quality_score:.1f}/1.0")
        print(f"📄 Report generated: {report_file}")
        
        if self.config["telegram"]["notifications_enabled"]:
            notifier = TelegramNotifier(
                self.config["telegram"]["bot_token"],
                self.config["telegram"]["chat_id"]
            )
            success = await notifier.send_test_report(metrics)
            if success:
                print("✅ Report sent to Telegram!")
            else:
                print("❌ Failed to send to Telegram")
    
    async def run_full_test(self):
        """Run full test suite with AI analysis."""
        print("🚀 Running full test suite...")
        results = await self.runner.run_full_test_suite()
        print("✅ Full test suite completed!")
    
    async def run_quick_test(self):
        """Run quick test."""
        print("⚡ Running quick test...")
        results = await self.runner.run_quick_test()
        print("✅ Quick test completed!")
    
    def start_continuous(self, interval: int = None):
        """Start continuous testing."""
        if interval is None:
            interval = self.config["testing"]["continuous_testing_interval_minutes"]
        
        print(f"🔄 Starting continuous testing (every {interval} minutes)...")
        self.runner.start_continuous_testing(interval)
    
    def show_status(self):
        """Show current testing status."""
        history_file = Path("test_history.json")
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            if history:
                latest = history[-1]
                print("📊 Latest Test Results:")
                print(f"  Timestamp: {latest['timestamp']}")
                print(f"  Coverage: {latest['metrics']['coverage_percentage']:.1f}%")
                print(f"  Quality Score: {latest['metrics']['quality_score']:.1f}/1.0")
                print(f"  Total Tests: {len(history)}")
            else:
                print("📊 No test history available")
        else:
            print("📊 No test history found")
    
    def show_help(self):
        """Show help information."""
        help_text = """
🤖 AI Testing System CLI

Commands:
  analyze          Run AI analysis and send report
  test             Run full test suite with AI analysis
  quick            Run quick test
  continuous [N]   Start continuous testing (every N minutes, default 30)
  status           Show current testing status
  help             Show this help message

Examples:
  python ai_test_cli.py analyze
  python ai_test_cli.py test
  python ai_test_cli.py quick
  python ai_test_cli.py continuous 15
  python ai_test_cli.py status
        """
        print(help_text)


async def main():
    """Main CLI function."""
    cli = AITestCLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "analyze":
        await cli.run_analysis()
    elif command == "test":
        await cli.run_full_test()
    elif command == "quick":
        await cli.run_quick_test()
    elif command == "continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else None
        cli.start_continuous(interval)
    elif command == "status":
        cli.show_status()
    elif command == "help":
        cli.show_help()
    else:
        print(f"❌ Unknown command: {command}")
        cli.show_help()


if __name__ == "__main__":
    asyncio.run(main()) 