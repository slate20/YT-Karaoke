#!/bin/bash

# YT-Karaoke Startup Script for Linux
# This script activates the virtual environment, starts the Flask app, and opens a browser

# Change to the script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv-linux" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv-linux
    source venv-linux/bin/activate
    pip install -r requirements.txt
else
    source venv-linux/bin/activate
fi

# Start the Flask app in the background
echo "Starting YT-Karaoke app..."

# Set Flask environment variables
export FLASK_APP=app.py

# Start the Flask server directly (skip the desktop client)
python -c "from app import app, socketio; socketio.run(app, debug=True)" &
APP_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 3

# Open the browser
echo "Opening browser..."
if command -v google-chrome &> /dev/null; then
    google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu --remote-debugging-port=9222 --disable-software-rasterizer http://127.0.0.1:5000
elif command -v chromium-browser &> /dev/null; then
    chromium-browser --no-sandbox --disable-dev-shm-usage --disable-gpu --remote-debugging-port=9222 --disable-software-rasterizer http://127.0.0.1:5000
elif command -v firefox &> /dev/null; then
    firefox http://127.0.0.1:5000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000
else
    echo "Could not find a browser to open. Please open http://127.0.0.1:5000 manually."
fi

# Trap Ctrl+C to gracefully shut down the app
trap 'echo "Shutting down..."; kill $APP_PID; exit' INT

# Keep the script running until the user presses Ctrl+C
echo "YT-Karaoke is running. Press Ctrl+C to stop."
wait $APP_PID
