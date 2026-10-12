#!/bin/bash

# =========================================
# AGRISMART - SETUP SCRIPT (Linux/Mac)
# =========================================

echo ""
echo "AgriSmart - Installation Script"
echo "=============================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

echo ""
echo "Initializing database and seeding data..."
python3 seed.py
echo "✓ Database initialized"

echo ""
echo "=============================="
echo "Setup Complete!"
echo "=============================="
echo ""
echo "To start the development server:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run: python3 run.py"
echo "  3. Visit: http://localhost:5000"
echo ""
echo "Default Admin Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
