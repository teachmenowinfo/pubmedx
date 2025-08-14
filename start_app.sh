#!/bin/bash
# Script to start the PubMed Knowledge Graph application

echo "Starting PubMed Knowledge Graph Application..."
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python3.11 -m venv venv"
    echo "Then run: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check Python version
echo "Python version: $(python --version)"

# Start the application
echo "Starting FastAPI server..."
echo "Application will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 