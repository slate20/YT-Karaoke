@echo off
echo Starting YouTube Karaoke...
cd /d "%~dp0"
call venv\Scripts\activate
python karaoke_app.py
