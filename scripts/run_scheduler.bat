@echo off
REM Hermes Scheduler Runner
REM Run this script to start the data collection scheduler

cd /d "%~dp0.."

echo ========================================
echo Hermes Data Collection Scheduler
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.11+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install APScheduler if needed
pip show apscheduler >nul 2>&1
if errorlevel 1 (
    echo Installing APScheduler...
    pip install apscheduler
)

echo.
echo Starting scheduler...
echo Press Ctrl+C to stop
echo.

python scheduler.py %*

pause
