@echo off
REM =========================================
REM AGRISMART - SETUP SCRIPT
REM =========================================

echo.
echo AgriSmart - Installation Script
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt -q
echo ✓ Dependencies installed

echo.
echo Initializing database and seeding data...
python seed.py
echo ✓ Database initialized

echo.
echo ==============================
echo Setup Complete!
echo ==============================
echo.
echo To start the development server:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Run: python run.py
echo   3. Visit: http://localhost:5000
echo.
echo Default Admin Credentials:
echo   Username: admin
echo   Password: admin123
echo.
pause
