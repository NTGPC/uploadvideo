@echo off
title TikTok Reup Offline
echo.
echo ========================================
echo    TikTok Reup Offline - KHONG CAN DANG NHAP
echo ========================================
echo.
echo Dang khoi dong ung dung...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo LOI: Python chua duoc cai dat!
    echo Vui long cai dat Python tu https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo LOI: Khong tim thay file main.py
    echo Vui long chay file nay trong thu muc TikTokReupOffline
    echo.
    pause
    exit /b 1
)

REM Install required packages if needed
echo Kiem tra va cai dat cac goi can thiet...
python -c "import yt_dlp, selenium, PIL, requests" >nul 2>&1
if errorlevel 1 (
    echo Cai dat cac goi Python...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo LOI: Khong the cai dat cac goi can thiet
        echo Vui long kiem tra ket noi internet
        pause
        exit /b 1
    )
)

REM Create necessary directories
if not exist "data\videos" mkdir "data\videos"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\music" mkdir "data\music"
if not exist "data\fonts" mkdir "data\fonts"
if not exist "logs" mkdir "logs"

echo.
echo Mo ung dung TikTok Reup Offline...
echo.

REM Run the application
python main.py

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo LOI: Co loi xay ra khi chay ung dung
    echo Vui long kiem tra log trong thu muc logs/
    echo.
    pause
)
