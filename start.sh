#!/bin/bash
# Start script for backend

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one with your API keys."
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Run the application
echo "Starting backend server..."
python app.py


