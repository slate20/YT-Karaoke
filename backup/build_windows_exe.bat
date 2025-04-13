@echo off
echo Building YouTube Karaoke Windows Executable...

:: Activate virtual environment
call venv\Scripts\activate

:: Install required packages if needed
pip install pyinstaller pywebview

:: Build the executable
pyinstaller --clean youtube_karaoke.spec

:: Copy config.json to dist folder if it exists
if exist config.json (
    echo Copying config.json to dist folder...
    copy config.json dist\YT_Karaoke_Windows\
)

echo Build complete! The executable is in the dist folder as YT_Karaoke_Windows.exe
echo.
echo Press any key to exit...
pause
