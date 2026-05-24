#!/bin/bash

# --- NEON PUC-MAN AUTOMATED LAUNCHER ---
# This script ensures dependencies are set up and launches the game in the local virtual environment.

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "⚡ Starting Neon Puc-Man (Retro-Modern Python) ⚡"
echo "=================================================="

# 1. Verify virtual environment exists, if not, create it
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment. Please ensure python3 is installed."
        exit 1
    fi
fi

# 2. Activate virtual environment
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate virtual environment."
    exit 1
fi

# 3. Double-check requirements
echo "Checking dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "⚠️ Warning: pip install failed. Checking if pygame is already available..."
fi

# 4. Launch game
echo "🚀 Launching game window..."
python -m src.main
if [ $? -ne 0 ]; then
    echo "❌ Error: The game crashed or failed to launch. Check terminal messages above."
fi

deactivate
echo "Goodbye! Thanks for playing Neon Puc-Man! 🕹️"
