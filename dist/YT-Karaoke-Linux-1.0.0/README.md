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
