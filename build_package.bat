@echo off
echo Building YouTube Karaoke Package...

:: Activate virtual environment
call venv\Scripts\activate

:: Install required packages if needed
pip install pyinstaller pywebview

:: Build the server executable
echo Building server executable...
pyinstaller --clean karaoke_server.spec

:: Build the client executable
echo Building client executable...
pyinstaller --clean karaoke_client.spec

:: Create a distribution folder
echo Creating distribution package...
mkdir dist\YT_Karaoke_App
copy dist\YT_Karaoke_Server.exe dist\YT_Karaoke_App\
copy dist\YT_Karaoke_Client.exe dist\YT_Karaoke_App\

:: Create a launcher script
echo @echo off > dist\YT_Karaoke_App\start_karaoke.bat
echo echo Starting YouTube Karaoke Application... >> dist\YT_Karaoke_App\start_karaoke.bat
echo start "YouTube Karaoke Server" /min YT_Karaoke_Server.exe >> dist\YT_Karaoke_App\start_karaoke.bat
echo echo Waiting for server to start... >> dist\YT_Karaoke_App\start_karaoke.bat
echo timeout /t 5 /nobreak ^> nul >> dist\YT_Karaoke_App\start_karaoke.bat
echo echo Starting client application... >> dist\YT_Karaoke_App\start_karaoke.bat
echo start "" YT_Karaoke_Client.exe >> dist\YT_Karaoke_App\start_karaoke.bat

:: Create a default config file
echo { > dist\YT_Karaoke_App\config.json
echo     "youtube_api_key": "" >> dist\YT_Karaoke_App\config.json
echo } >> dist\YT_Karaoke_App\config.json

echo Build complete! The packaged application is in the dist\YT_Karaoke_App folder.
echo You can distribute this entire folder to users.
echo.
echo Press any key to exit...
pause
