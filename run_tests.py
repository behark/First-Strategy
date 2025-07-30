#!/usr/bin/env python3
"""
Test runner for First-Strategy trading system.
Provides easy access to different types of tests and coverage reporting.
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    print("🧪 First-Strategy Test Suite")
    print("="*60)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Test options
    tests = {
        "1": ("Unit Tests", ["pytest", "tests/", "-v", "-m", "unit"]),
        "2": ("Integration Tests", ["pytest", "tests/", "-v", "-m", "integration"]),
        "3": ("All Tests", ["pytest", "tests/", "-v"]),
        "4": ("Coverage Report", ["pytest", "tests/", "--cov=.", "--cov-report=html", "--cov-report=term-missing"]),
        "5": ("Quick Test", ["pytest", "tests/test_utils.py", "-v"]),
        "6": ("Exit", None)
    }
    
    while True:
        print("\nSelect test type:")
        for key, (name, _) in tests.items():
            print(f"  {key}. {name}")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "6":
            print("👋 Goodbye!")
            break
        elif choice in tests:
            name, cmd = tests[choice]
            if cmd:
                success = run_command(cmd, name)
                if not success:
                    print(f"\n❌ {name} failed!")
                else:
                    print(f"\n✅ {name} completed successfully!")
            else:
                print("👋 Goodbye!")
                break
        else:
            print("❌ Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main() 