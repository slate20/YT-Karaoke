@echo off
echo Cleaning up project directory...

:: Create a backup directory
mkdir backup 2>nul

:: Move redundant scripts to backup
echo Moving redundant scripts to backup...
move karaoke_app.py backup\ 2>nul
move youtube_karaoke.spec backup\ 2>nul
move build_windows_exe.bat backup\ 2>nul
move build_linux_exe.sh backup\ 2>nul
move start_karaoke.bat backup\ 2>nul
move start_karaoke_app.bat backup\ 2>nul
move start_server.bat backup\ 2>nul
move build_client.bat backup\ 2>nul
move create_icon.py backup\ 2>nul

:: Remove build artifacts
echo Removing build artifacts...
rmdir /s /q __pycache__ 2>nul
rmdir /s /q build 2>nul

echo Cleanup complete!
echo All removed files have been backed up to the 'backup' directory.
echo.
echo Essential files remaining:
echo - app.py (Main application)
echo - karaoke_client.py (Desktop client)
echo - karaoke_client.spec (Client build spec)
echo - karaoke_server.spec (Server build spec)
echo - build_package.bat (Main build script)
echo - config.json (Configuration)
echo - templates/ (HTML templates)
echo - static/ (Static assets)
echo - dist/YT_Karaoke_App/ (Distribution package)
echo.
echo Press any key to exit...
pause
