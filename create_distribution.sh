#!/bin/bash

# Create a distributable package for Linux
VERSION="1.0.0"
DIST_NAME="YT-Karaoke-Linux-$VERSION"

# Create distribution directory
mkdir -p dist/$DIST_NAME

# Copy necessary files
cp -r app.py templates requirements.txt start_karaoke.sh dist/$DIST_NAME/

# Check for .env file and copy if it exists
if [ -f .env ]; then
    cp .env dist/$DIST_NAME/
else
    # Create a placeholder .env file
    echo "# Add your environment variables here" > dist/$DIST_NAME/.env
    echo "SECRET_KEY=default_secret_key" >> dist/$DIST_NAME/.env
fi

# Create static directory if it doesn't exist
mkdir -p dist/$DIST_NAME/static

# Create a README
cat > dist/$DIST_NAME/README.md << 'EOF'
# YT-Karaoke for Linux

## About This Distribution

This is the Linux browser-based version of YT-Karaoke. It runs the application in your web browser rather than as a standalone desktop application. This approach ensures maximum compatibility across different Linux distributions.

## Installation

1. Make sure you have Python 3.8+ installed:
   ```
   python3 --version
   ```

2. The application requires Google Chrome or Chromium:
   The startup script will check if Chrome/Chromium is installed and offer to install it automatically if it's not found. Alternatively, you can install it manually:
   ```
   # For Debian/Ubuntu
   sudo apt install google-chrome-stable
   
   # For Fedora/RHEL/CentOS
   sudo dnf install google-chrome-stable
   
   # For Arch Linux
   sudo pacman -S chromium
   ```

3. Make the startup script executable:
   ```
   chmod +x start_karaoke.sh
   ```

4. Run the application:
   ```
   ./start_karaoke.sh
   ```

The first time you run the script, it will create a virtual environment and install all dependencies.

## How It Works

- The script starts a Flask web server on your local machine
- It then opens your web browser to http://127.0.0.1:5000
- All karaoke functionality runs in the browser

## Troubleshooting

If you encounter issues with Chrome/Selenium:
- The application requires Chrome/Chromium and a graphical environment to run
- If you see errors related to Chrome, make sure it's properly installed
- The script includes necessary Chrome options for Linux: --no-sandbox, --disable-dev-shm-usage, etc.

## Configuration

- A config.json file will be created in the application directory to store settings
- You'll need to add your YouTube API key in the settings page

For more information, visit: https://github.com/yourusername/YT-Karaoke
EOF

# Create the archive
cd dist
tar -czf $DIST_NAME.tar.gz $DIST_NAME

echo "Distribution package created at dist/$DIST_NAME.tar.gz"
