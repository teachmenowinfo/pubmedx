#!/bin/bash
# Script to activate the Python 3.11 virtual environment

echo "Activating Python 3.11 virtual environment..."
source venv/bin/activate

echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "To deactivate, run: deactivate"
echo "To start the application, run: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" 