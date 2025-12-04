#!/bin/bash
# VA21 OS - Main Entry Point
# Om Vinayaka - The remover of obstacles 🙏

cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "                     🙏 OM VINAYAKA 🙏"
echo "                  VA21 OS - Starting..."
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Start VA21 Core
cd linux_os
python3 -m va21_core
