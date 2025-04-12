@echo off
echo Building YouTube Karaoke Windows Executable...
pyinstaller --clean youtube_karaoke.spec
echo Build complete! The executable is in the dist folder.
pause
