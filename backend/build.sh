#!/bin/bash
# Force Python version for Render
echo "Setting up Python environment..."

# Check current Python version
python3 --version

# Try to use Python 3.11 if available
if command -v python3.11 &> /dev/null; then
    echo "Using Python 3.11"
    python3.11 -m pip install -r requirements.txt
else
    echo "Python 3.11 not found, using default"
    python3 -m pip install -r requirements.txt
fi
