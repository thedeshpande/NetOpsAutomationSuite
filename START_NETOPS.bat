@echo off
setlocal EnableExtensions
title NetOps Automation Suite

set "PROJECT_DIR=%~dp0"
set "VENV_PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"

echo.
echo ============================================================
echo              NETOPS AUTOMATION SUITE
echo ============================================================
echo.

if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found.
    echo.
    echo This appears to be the first run on this laptop.
    echo.
    echo Please run:
    echo     SETUP_NETOPS.bat
    echo.
    echo After setup is completed, use START_NETOPS.bat normally.
    echo.
    pause
    exit /b 1
)

echo Virtual environment found.
echo.
echo Starting Flask server...
echo.

start "NetOps Flask Server" cmd /k ""%VENV_PYTHON%" "%PROJECT_DIR%web\app.py""

echo Waiting for Flask server...

:WAIT_FOR_SERVER
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:5000' -UseBasicParsing -TimeoutSec 1 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1

if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_FOR_SERVER
)

echo.
echo Flask server is ready.
echo Opening NetOps Automation Suite...
echo.

start "" "http://127.0.0.1:5000"

echo.
echo ============================================================
echo              APPLICATION STARTED
echo ============================================================
echo.
echo Browser:
echo http://127.0.0.1:5000
echo.
echo Keep the Flask server window running while using the suite.
echo ============================================================
echo.

exit /b 0
