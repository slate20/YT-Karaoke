# YouTube Karaoke App

A web application for hosting karaoke nights using YouTube videos. This app provides a control panel for managing singers and songs, and a separate player window for displaying the karaoke videos in fullscreen.

## Features

- Add and manage singers
- Search for karaoke songs using YouTube API
- Display search results as visual tiles
- Add songs to queue and assign to singers
- Control player window (play, pause, next song)
- Fullscreen video playback using undetected-chromedriver

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

5. The player window will open automatically when you click "Start Player"

## How It Works

- The control panel allows you to manage singers and the song queue
- When you start the player, a separate Chrome window opens using undetected-chromedriver
- Songs are played in the order they were added to the queue
- You can skip to the next song using the "Next Song" button
- The player window will display the YouTube video in fullscreen mode

## Troubleshooting

- If videos are not loading, make sure you have Chrome installed
- If search doesn't work, verify your YouTube API key is correct
- If the player window doesn't open, check that you have the necessary permissions for Chrome to launch

## License

MIT
