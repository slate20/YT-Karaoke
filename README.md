# YouTube Karaoke App

A web application for hosting karaoke nights using YouTube videos. This app provides a control panel for managing singers and songs, and a separate player window for displaying the karaoke videos in fullscreen. Now with multi-display support and available as standalone executables for Windows and Linux!

## Features

- Add and manage singers
- Search for karaoke songs using YouTube API
- Display search results as visual tiles
- Add songs to queue and assign to singers
- Control player window (play, pause, next song)
- Fullscreen video playback using undetected-chromedriver
- Multi-display support with display selection modal
- Automatic ad skipping and popup dismissal
- Available as standalone executables for Windows and Linux

## Requirements

- Python 3.7+
- Chrome browser installed
- YouTube Data API key

## Installation

1. Clone this repository
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Edit the `.env` file and add your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

## Getting a YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create credentials (API key)
5. Copy the API key to your `.env` file

## Usage

1. Activate the virtual environment:
   ```
   .\venv\Scripts\activate  # Windows
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

4. Use the control panel to:
   - Add singers
   - Search for karaoke songs
   - Add songs to the queue
   - Start the player

5. The player window will open automatically when you click "Start Player", with an option to select which display to use

## How It Works

- The control panel allows you to manage singers and the song queue
- When you start the player, a display selection modal appears allowing you to choose which monitor to use
- A separate Chrome window opens on the selected display using undetected-chromedriver
- Songs are played in the order they were added to the queue
- You can skip to the next song using the "Next Song" button
- The player window will display the YouTube video in fullscreen mode
- Ads are automatically skipped and popups are dismissed

## Troubleshooting

- If videos are not loading, make sure you have Chrome installed
- If search doesn't work, verify your YouTube API key is correct
- If the player window doesn't open, check that you have the necessary permissions for Chrome to launch

## Building Executables

### Windows

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```
   build_windows_exe.bat
   ```

3. The executable will be created in the `dist` folder as `YT_Karaoke_Windows.exe`

### Linux

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```
   chmod +x build_linux_exe.sh
   ./build_linux_exe.sh
   ```

3. The executable will be created in the `dist` folder as `YT_Karaoke_Linux`

## Running the Executable

1. Make sure Chrome is installed on your system
2. Run the executable
3. The application will start and open in your browser automatically
4. No Python installation is required to run the packaged executable

## License

MIT
