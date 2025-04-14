#!/bin/bash

# YT-Karaoke Startup Script for Linux
# This script activates the virtual environment, starts the Flask app, and opens a browser

# Function to check and install Chrome
check_chrome() {
    if command -v google-chrome &> /dev/null; then
        echo "Google Chrome is installed."
        return 0
    elif command -v chromium-browser &> /dev/null; then
        echo "Chromium browser is installed."
        return 0
    else
        echo "Chrome/Chromium is not installed but is required for this application."
        echo "Would you like to install Chrome now? (y/n)"
        read -r answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            # Detect the Linux distribution
            if command -v apt &> /dev/null; then
                # Debian/Ubuntu
                echo "Installing Chrome on Debian/Ubuntu..."
                wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
                echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
                sudo apt update
                sudo apt install -y google-chrome-stable
            elif command -v dnf &> /dev/null; then
                # Fedora/RHEL/CentOS
                echo "Installing Chrome on Fedora/RHEL/CentOS..."
                sudo dnf install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            elif command -v pacman &> /dev/null; then
                # Arch Linux
                echo "Installing Chrome on Arch Linux..."
                sudo pacman -S --noconfirm chromium
            elif command -v zypper &> /dev/null; then
                # openSUSE
                echo "Installing Chrome on openSUSE..."
                sudo zypper install -y google-chrome-stable
            else
                echo "Unsupported Linux distribution. Please install Chrome manually."
                echo "Visit: https://www.google.com/chrome/"
                return 1
            fi
            
            # Check if installation was successful
            if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
                echo "Chrome/Chromium installed successfully."
                return 0
            else
                echo "Failed to install Chrome/Chromium. Please install it manually."
                echo "Visit: https://www.google.com/chrome/"
                return 1
            fi
        else
            echo "Chrome/Chromium is required for this application. Please install it manually."
            echo "Visit: https://www.google.com/chrome/"
            return 1
        fi
    fi
}

# Change to the script directory
cd "$(dirname "$0")"

# Check if Chrome is installed
check_chrome
if [ $? -ne 0 ]; then
    echo "Chrome/Chromium is required. Exiting."
    exit 1
fi

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
python -c "from app import app, socketio; socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)" &
APP_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 3

# Open the browser using the system's default browser
echo "Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000
elif command -v sensible-browser &> /dev/null; then
    sensible-browser http://127.0.0.1:5000
elif command -v firefox &> /dev/null; then
    firefox http://127.0.0.1:5000
elif command -v google-chrome &> /dev/null; then
    # Modified Chrome options to remove --no-sandbox
    google-chrome --disable-dev-shm-usage --disable-gpu --remote-debugging-port=9222 --disable-software-rasterizer http://127.0.0.1:5000
elif command -v chromium-browser &> /dev/null; then
    # Modified Chrome options to remove --no-sandbox
    chromium-browser --disable-dev-shm-usage --disable-gpu --remote-debugging-port=9222 --disable-software-rasterizer http://127.0.0.1:5000
else
    echo "Could not find a browser to open. Please open http://127.0.0.1:5000 manually."
fi

# Trap Ctrl+C to gracefully shut down the app
trap 'echo "Shutting down..."; kill $APP_PID; exit' INT

# Keep the script running until the user presses Ctrl+C
echo "YT-Karaoke is running. Press Ctrl+C to stop."
wait $APP_PID
