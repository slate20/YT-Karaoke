@echo off
echo Building YouTube Karaoke Client...

:: Activate virtual environment
call venv\Scripts\activate

:: Install required packages if needed
pip install pyinstaller pywebview

:: Build the executable
pyinstaller --clean karaoke_client.spec

echo Build complete! The client executable is in the dist folder as YT_Karaoke_Client.exe
echo.
echo Press any key to exit...
pause
