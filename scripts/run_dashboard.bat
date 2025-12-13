@echo off
REM Hermes Dashboard Runner
REM Run this script to start the Streamlit dashboard

cd /d "%~dp0.."

echo ========================================
echo Hermes Intelligence Dashboard
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

echo.
echo Starting Hermes Dashboard...
echo Dashboard will open at http://localhost:8501
echo Press Ctrl+C to stop
echo.

streamlit run hermes_dashboard.py

pause
