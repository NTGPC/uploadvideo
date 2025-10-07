@echo off
echo Installing TikTok Reup Offline...
echo.

REM Create directories
if not exist "data\videos" mkdir "data\videos"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\music" mkdir "data\music"
if not exist "data\fonts" mkdir "data\fonts"
if not exist "logs" mkdir "logs"
if not exist "tools" mkdir "tools"

echo Created directories.

REM Install Python packages
echo Installing Python packages...
pip install -r requirements.txt

echo.
echo Installation completed!
echo.
echo Please download FFmpeg and place ffmpeg.exe in the tools\ folder
echo You can download FFmpeg from: https://ffmpeg.org/download.html
echo.
echo Then run: python main.py
pause
