@echo off
echo Starting YouTube Karaoke Application...
cd /d "%~dp0"

:: Start the server in a separate window
start "YouTube Karaoke Server" cmd /c "call venv\Scripts\activate && python app.py"

:: Wait for the server to start
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

:: Start the client application
echo Starting client application...
start "" "dist\YT_Karaoke_Client.exe"

echo YouTube Karaoke application started successfully!
