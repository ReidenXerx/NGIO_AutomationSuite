@echo off
REM NGIO Automation Suite - Windows Launcher
REM This script launches the grass cache automation tool

title NGIO Automation Suite

echo.
echo ========================================
echo   🌱 NGIO AUTOMATION SUITE 🌱
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 🔍 Checking dependencies...
python -c "import psutil, colorlog, configparser" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo.
        echo Please run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencies OK
echo.

REM Launch the automation suite
echo 🚀 Starting NGIO Automation Suite...
echo.
REM Run Python with unbuffered output (-u flag) so you see messages immediately
python -u ngio_automation_runner.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Application exited with an error
    pause
)

echo.
echo 👋 Thanks for using NGIO Automation Suite!
timeout /t 3 >nul
