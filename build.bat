@echo off
title NGIO Automation Suite - Build Release
color 0A
cls

echo ================================================================================
echo                     NGIO AUTOMATION SUITE - BUILD RELEASE
echo                           npm run build equivalent
echo ================================================================================
echo.
echo This script creates a complete release package with:
echo   - Python wheel and source distributions
echo   - Portable ZIP with batch launcher
echo   - Professional installer package
echo   - Source code ZIP
echo   - Release documentation
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Starting build process...
echo.

REM Run the build script
python build_release.py

echo.
echo ================================================================================
echo                            BUILD COMPLETED!
echo ================================================================================
echo.
echo Check the following directories:
echo   📁 dist/     - Python packages (wheel, source)
echo   📁 release/  - Distribution files ready for users
echo.
echo Release files are ready for:
echo   🎮 End users (portable ZIP)
echo   💻 Developers (source ZIP)
echo   🔧 System installation (installer package)
echo.
pause
