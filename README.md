# YouTube Karaoke App

A desktop application for hosting karaoke nights using YouTube videos. This app provides a control panel for managing singers and songs, and a separate player window for displaying the karaoke videos in fullscreen. Now with multi-display support, drag-and-drop queue management, and available as a standalone desktop application with PyWebView!

## Features

- Add and manage singers
- Search for karaoke songs using YouTube API
- Display search results as visual tiles
- Add songs to queue and assign to singers
- Control player window (play, pause, next song)
- Fullscreen video playback using undetected-chromedriver
- Multi-display support with display selection modal
- Automatic ad skipping and popup dismissal
- Available as a standalone desktop application with PyWebView
- Drag-and-drop functionality for reordering the song queue
- Restart and mute buttons for better playback control
- User-configurable YouTube API key through settings page

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

### Web Application

1. Activate the virtual environment:
   ```
   .\venv\Scripts\activate  # Windows
   ```

2. Run the web application:
   ```
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Desktop Application

1. Simply double-click the `start_karaoke.bat` file (Windows)

OR

1. Activate the virtual environment:
   ```
   .\venv\Scripts\activate  # Windows
   ```

2. Run the desktop application:
   ```
   python karaoke_app.py
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

## Running as a Desktop Application

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   pip install pywebview
   ```

2. Run the desktop application:
   ```
   python karaoke_app.py
   ```

   Or simply double-click the `start_karaoke.bat` file (Windows)

3. The application will open in a dedicated window, no browser needed

## Features of the Desktop Application

- Runs in its own window without needing a web browser
- Simplified user experience with a single application window
- All the features of the web application in a desktop environment
- Restart button to replay the current song
- Mute button to control audio
- Drag-and-drop functionality for reordering the song queue
- Settings page for configuring your YouTube API key

## License

MIT
