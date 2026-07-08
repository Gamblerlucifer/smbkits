@echo off
chcp 65001 >nul
title SMBkits Mailer

echo.
echo  ================================
echo   SMBkits Cold Email Mailer
echo  ================================
echo.

cd /d "%~dp0"

if exist "scrapers\.venv\Scripts\activate.bat" (
    call scrapers\.venv\Scripts\activate.bat
) else (
    echo [오류] venv를 찾을 수 없습니다.
    pause
    exit /b 1
)

echo [실행] mailer.py 시작...
echo.
python scrapers/mailer.py

echo.
echo  ================================
echo   완료! 아무 키나 누르면 닫힙니다.
echo  ================================
pause
