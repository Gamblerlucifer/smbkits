@echo off
chcp 65001 >nul
title SMBkits Scraper

echo.
echo  ================================
echo   SMBkits TripAdvisor Scraper
echo  ================================
echo.

cd /d "%~dp0"

REM venv 확인 후 활성화
if exist "scrapers\.venv\Scripts\activate.bat" (
    call scrapers\.venv\Scripts\activate.bat
) else (
    echo [오류] venv를 찾을 수 없습니다.
    echo scrapers\.venv 폴더를 확인하세요.
    pause
    exit /b 1
)

echo [실행] tripadvisor_scraper.py 시작...
echo.
python scrapers/tripadvisor_scraper.py

echo.
echo  ================================
echo   완료! 아무 키나 누르면 닫힙니다.
echo  ================================
pause
