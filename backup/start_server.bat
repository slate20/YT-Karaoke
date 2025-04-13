@echo off
echo Starting YouTube Karaoke Server...
cd /d "%~dp0"
call venv\Scripts\activate
python app.py
