@echo off
title NGIO Automation Suite - Build Release
color 0A
cls

echo ================================================================================
echo                NGIO AUTOMATION SUITE - ENHANCED BUILD SYSTEM
echo                              Version 1.5.1
echo ================================================================================
echo.
echo This script creates professional release packages:
echo   [1] Single .exe file     - Recommended for users (no Python needed!)
echo   [2] Portable ZIP         - For users with Python installed
echo   [3] Complete package     - Both of the above + documentation
echo.
echo What will be created:
echo   🚀 Single .exe          - ~20-50MB, all dependencies embedded
echo   📦 Portable ZIP         - Source code + launcher
echo   📋 Documentation        - User guides and release notes
echo   🔐 SHA256 Checksums     - For integrity verification
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ and try again.
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python found:
python --version
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller not found - installing build dependencies...
    echo.
    python -m pip install pyinstaller
    
    REM Verify installation by trying to import again
    python -c "import PyInstaller" >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ❌ Failed to install PyInstaller!
        echo Try manually: pip install pyinstaller
        pause
        exit /b 1
    )
    echo.
    echo ✅ PyInstaller installed successfully
    echo.
)

echo.
echo ================================================================================
echo                           STARTING BUILD PROCESS
echo ================================================================================
echo.
echo This will take 2-5 minutes depending on your system...
echo Please wait while the build completes.
echo.

REM Run the enhanced build script
python build_release.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo                               BUILD FAILED!
    echo ================================================================================
    echo.
    echo Check the error messages above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                           BUILD COMPLETED SUCCESSFULLY!
echo ================================================================================
echo.
echo 📁 Output directories:
echo    📦 dist\     - Standalone .exe file (ready to distribute!)
echo    📦 release\  - Release packages (ZIP files with docs)
echo.
echo 🎯 What to distribute:
echo    For most users:    release\NGIO_Automation_Suite_v*_Release.zip
echo    For developers:    release\NGIO_Automation_Suite_v*_Portable.zip
echo    Standalone only:   dist\NGIO_Automation_Suite_v*.exe
echo.
echo 🔐 Checksums:          release\CHECKSUMS_SHA256.txt
echo.
echo ✅ Ready to upload to Nexus Mods!
echo.
pause
