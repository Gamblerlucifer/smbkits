@echo off
chcp 65001 >nul
title SMBkits 설치

echo.
echo  ================================
echo   SMBkits 최초 설치 스크립트
echo   (한 번만 실행하면 됩니다)
echo  ================================
echo.

cd /d "%~dp0"

REM ── 1. Python 설치 확인 ──────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] Python이 없습니다. 자동 다운로드 중...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo [1/4] Python 설치 중... (잠깐 기다려주세요)
    python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
    del python_installer.exe
    echo [1/4] Python 설치 완료!
    echo.
    echo ** Python PATH 적용을 위해 이 창을 닫고 install.bat을 다시 실행해주세요 **
    pause
    exit /b
) else (
    echo [1/4] Python 확인 완료
)

REM ── 2. venv 생성 ─────────────────────────────────────────────
echo [2/4] 가상환경 생성 중...
if not exist "scrapers\.venv" (
    python -m venv scrapers\.venv
)
call scrapers\.venv\Scripts\activate.bat
echo [2/4] 완료

REM ── 3. 패키지 설치 ───────────────────────────────────────────
echo [3/4] 패키지 설치 중... (시간이 걸릴 수 있습니다)
pip install --quiet --upgrade pip
pip install --quiet playwright gspread google-auth google-generativeai python-dotenv browser-cookie3 curl-cffi
echo [3/4] 완료

REM ── 4. Playwright Chromium 설치 ──────────────────────────────
echo [4/4] 브라우저(Chromium) 설치 중...
playwright install chromium
echo [4/4] 완료

echo.
echo  ================================
echo   설치 완료!
echo   이제 run_scraper.bat을 실행하세요.
echo  ================================
echo.
pause
