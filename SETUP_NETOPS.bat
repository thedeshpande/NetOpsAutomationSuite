@echo off
setlocal EnableExtensions
title NetOps Automation Suite - First Time Setup

set "PROJECT_DIR=%~dp0"
set "VENV_PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"
set "REQUIREMENTS=%PROJECT_DIR%requirements.txt"

echo.
echo ============================================================
echo        NETOPS AUTOMATION SUITE - FIRST TIME SETUP
echo ============================================================
echo.
echo Project:
echo %PROJECT_DIR%
echo.

echo [1/5] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found on this laptop.
    echo Please install an approved Python version and make sure
    echo Python is available from the command line.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"

if not defined PYTHON_EXE (
    echo ERROR: Python was detected but could not be started.
    pause
    exit /b 1
)

echo PASS - Python: %PYTHON_EXE%
echo.

echo [2/5] Checking requirements.txt...
if not exist "%REQUIREMENTS%" (
    echo.
    echo ERROR: requirements.txt was not found.
    echo Expected: %REQUIREMENTS%
    echo.
    pause
    exit /b 1
)
echo PASS - requirements.txt found.
echo.

echo [3/5] Checking virtual environment...
if exist "%VENV_PYTHON%" (
    echo PASS - Existing .venv found.
    echo.
    goto VENV_READY
)

echo .venv was not found. Creating virtual environment...
echo.
python -m venv "%PROJECT_DIR%.venv"

if errorlevel 1 (
    echo.
    echo ERROR: Unable to create the virtual environment.
    echo Check Python installation and permissions.
    echo.
    pause
    exit /b 1
)

if not exist "%VENV_PYTHON%" (
    echo.
    echo ERROR: Virtual environment creation failed.
    echo.
    pause
    exit /b 1
)

echo PASS - Virtual environment created.
echo.

:VENV_READY

echo [4/5] Installing project dependencies...
echo.
echo This may take several minutes.
echo.

"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo WARNING: pip upgrade failed.
    echo Continuing with the existing pip version...
    echo.
)

"%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Dependency installation failed.
    echo ============================================================
    echo.
    echo Possible causes:
    echo - Internet is unavailable
    echo - Corporate proxy restrictions
    echo - Internal package repository restrictions
    echo - Package installation is blocked
    echo - A dependency is incompatible with the installed Python
    echo.
    pause
    exit /b 1
)

echo.
echo PASS - Dependencies installed.
echo.

echo [5/5] Verifying installation...
echo.

"%VENV_PYTHON%" -c "import flask; print('PASS - Flask ' + flask.__version__)"
if errorlevel 1 (
    echo.
    echo ERROR: Flask verification failed.
    echo.
    pause
    exit /b 1
)

"%VENV_PYTHON%" -c "import netmiko; print('PASS - Netmiko ' + netmiko.__version__)"
if errorlevel 1 (
    echo.
    echo ERROR: Netmiko verification failed.
    echo.
    pause
    exit /b 1
)

"%VENV_PYTHON%" -c "import sys; print('PASS - Python ' + sys.version.split()[0])"

echo.
echo ============================================================
echo              SETUP COMPLETED SUCCESSFULLY
echo ============================================================
echo.
echo NetOps Automation Suite is now ready on this laptop.
echo.
echo You can now use:
echo     START_NETOPS.bat
echo.
echo for normal day-to-day launches.
echo ============================================================
echo.

pause
exit /b 0
