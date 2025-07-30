#!/usr/bin/env python3
"""
Automated Test Runner with AI Integration
Provides continuous testing, coverage analysis, and intelligent notifications.
"""
import asyncio
import subprocess
import time
import schedule
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json

from ai_test_analyzer import AITestAnalyzer, TelegramNotifier, CoverageMetrics


class AutomatedTestRunner:
    """
    Automated test runner that provides continuous testing with AI analysis
    and Telegram notifications.
    """
    
    def __init__(self, 
                 bot_token: str = "7634324156:AAFupAZCihSHKq-mj3wBZ3tDLfeyzXl5aRo",
                 chat_id: str = "1507876704",
                 project_root: str = "."):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.project_root = Path(project_root)
        self.analyzer = AITestAnalyzer(project_root)
        self.notifier = TelegramNotifier(bot_token, chat_id)
        self.test_history = []
        self.is_running = False
        
    async def run_full_test_suite(self) -> Dict:
        """Run complete test suite with AI analysis."""
        print("🚀 Starting automated test suite...")
        
        # Run tests
        test_results = await self._run_tests()
        
        # Run AI analysis
        metrics = await self.analyzer.run_coverage_analysis()
        
        # Generate report
        report_file = await self.analyzer.generate_html_report(metrics)
        
        # Send notifications
        await self._send_notifications(test_results, metrics)
        
        # Store results
        self._store_test_results(test_results, metrics)
        
        return {
            "test_results": test_results,
            "metrics": metrics,
            "report_file": report_file
        }
    
    async def _run_tests(self) -> Dict:
        """Run all tests and collect results."""
        try:
            # Run unit tests
            unit_cmd = ["python", "-m", "pytest", "tests/test_utils.py", "-v"]
            unit_result = subprocess.run(unit_cmd, capture_output=True, text=True, cwd=self.project_root)
            
            # Run integration tests
            integration_cmd = ["python", "-m", "pytest", "tests/test_integration.py", "-v"]
            integration_result = subprocess.run(integration_cmd, capture_output=True, text=True, cwd=self.project_root)
            
            # Run main test suite
            main_cmd = ["python", "-m", "pytest", "test_trading_system.py", "-v"]
            main_result = subprocess.run(main_cmd, capture_output=True, text=True, cwd=self.project_root)
            
            return {
                "unit_tests": {
                    "returncode": unit_result.returncode,
                    "passed": "passed" in unit_result.stdout.lower(),
                    "output": unit_result.stdout
                },
                "integration_tests": {
                    "returncode": integration_result.returncode,
                    "passed": "passed" in integration_result.stdout.lower(),
                    "output": integration_result.stdout
                },
                "main_tests": {
                    "returncode": main_result.returncode,
                    "passed": "passed" in main_result.stdout.lower(),
                    "output": main_result.stdout
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "unit_tests": {"returncode": 1, "passed": False},
                "integration_tests": {"returncode": 1, "passed": False},
                "main_tests": {"returncode": 1, "passed": False}
            }
    
    async def _send_notifications(self, test_results: Dict, metrics: CoverageMetrics):
        """Send comprehensive notifications to Telegram."""
        # Create status summary
        all_passed = all([
            test_results["unit_tests"]["passed"],
            test_results["integration_tests"]["passed"],
            test_results["main_tests"]["passed"]
        ])
        
        status_emoji = "✅" if all_passed else "❌"
        status_text = "PASSED" if all_passed else "FAILED"
        
        # Send status message
        status_message = f"""
{status_emoji} <b>Automated Test Run Complete</b>

📊 <b>Test Status:</b> {status_text}
• Unit Tests: {'✅' if test_results['unit_tests']['passed'] else '❌'}
• Integration Tests: {'✅' if test_results['integration_tests']['passed'] else '❌'}
• Main Tests: {'✅' if test_results['main_tests']['passed'] else '❌'}

📈 <b>Coverage:</b> {metrics.coverage_percentage:.1f}%
🎯 <b>Quality Score:</b> {metrics.test_quality_score:.1f}/1.0

🕐 <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self.notifier.send_message(status_message.strip())
        
        # Send detailed report if there are issues
        if not all_passed or metrics.coverage_percentage < 80:
            await self.notifier.send_test_report(metrics)
    
    def _store_test_results(self, test_results: Dict, metrics: CoverageMetrics):
        """Store test results for historical analysis."""
        result_entry = {
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "metrics": {
                "coverage_percentage": metrics.coverage_percentage,
                "quality_score": metrics.test_quality_score,
                "total_lines": metrics.total_lines,
                "covered_lines": metrics.covered_lines
            }
        }
        
        self.test_history.append(result_entry)
        
        # Keep only last 50 results
        if len(self.test_history) > 50:
            self.test_history = self.test_history[-50:]
        
        # Save to file
        history_file = self.project_root / "test_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.test_history, f, indent=2)
    
    def start_continuous_testing(self, interval_minutes: int = 30):
        """Start continuous testing with scheduled runs."""
        print(f"🔄 Starting continuous testing (every {interval_minutes} minutes)...")
        
        self.is_running = True
        
        # Schedule the test runs
        schedule.every(interval_minutes).minutes.do(self._run_scheduled_tests)
        
        # Run initial test
        asyncio.run(self.run_full_test_suite())
        
        # Start the scheduler in a separate thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print(f"✅ Continuous testing started. Tests will run every {interval_minutes} minutes.")
        print("Press Ctrl+C to stop...")
        
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_continuous_testing()
    
    def _run_scheduled_tests(self):
        """Run scheduled tests (for use with schedule library)."""
        asyncio.run(self.run_full_test_suite())
    
    def stop_continuous_testing(self):
        """Stop continuous testing."""
        print("🛑 Stopping continuous testing...")
        self.is_running = False
    
    async def run_quick_test(self) -> Dict:
        """Run a quick test without full analysis."""
        print("⚡ Running quick test...")
        
        # Run basic tests
        cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        
        passed = result.returncode == 0
        status_emoji = "✅" if passed else "❌"
        
        # Send quick notification
        message = f"""
{status_emoji} <b>Quick Test Complete</b>

📊 <b>Status:</b> {'PASSED' if passed else 'FAILED'}
🕐 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

{result.stdout[-500:] if len(result.stdout) > 500 else result.stdout}
        """
        
        await self.notifier.send_message(message.strip())
        
        return {
            "passed": passed,
            "output": result.stdout,
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Main function for automated test runner."""
    runner = AutomatedTestRunner()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run":
            await runner.run_full_test_suite()
        elif command == "quick":
            await runner.run_quick_test()
        elif command == "continuous":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            runner.start_continuous_testing(interval)
        else:
            print("Usage: python automated_test_runner.py [run|quick|continuous [interval_minutes]]")
    else:
        # Default: run full test suite
        await runner.run_full_test_suite()


if __name__ == "__main__":
    asyncio.run(main()) 