#!/bin/bash
# Simple health check script for signal bot

# Check if the main process is running
if pgrep -f "python -m src.main" > /dev/null; then
    # Process is running
    exit 0
else
    # Process is not running
    exit 1
fi
