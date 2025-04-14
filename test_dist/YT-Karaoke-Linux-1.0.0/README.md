# YT-Karaoke for Linux

## Installation

1. Make sure you have Python 3.8+ installed:
   ```
   python3 --version
   ```

2. Make sure you have Google Chrome or Chromium installed:
   ```
   google-chrome --version
   # OR
   chromium-browser --version
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

## Troubleshooting

If you encounter issues with Chrome/Selenium:
- The application requires Chrome/Chromium and a graphical environment to run
- If you see errors related to Chrome, make sure it's properly installed
- The script includes necessary Chrome options for Linux: --no-sandbox, --disable-dev-shm-usage, etc.

## Configuration

- A config.json file will be created in the application directory to store settings
- You'll need to add your YouTube API key in the settings page

For more information, visit: https://github.com/yourusername/YT-Karaoke
