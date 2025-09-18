@echo off
setlocal enabledelayedexpansion

rem ===============================================
rem   NGIO AUTOMATION SUITE - Main Launcher
rem          The Ultimate Grass Cache Tool
rem ===============================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "PYTHON_SCRIPT=%PROJECT_ROOT%\src\core\automation_suite.py"

echo.
echo ===============================================
echo   🌱 NGIO AUTOMATION SUITE v1.0
echo      The Ultimate Grass Cache Generator
echo ===============================================
echo.
echo ⚡ Transform 4+ hours of manual work into 5 minutes of setup!
echo 🛌 Run before bed, wake up with all seasons completed!
echo 🤖 Fully automated crash recovery and process management
echo.

rem Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! 
    echo.
    echo This tool requires Python 3.7+ to run.
    echo.
    choice /c YN /m "Would you like to download and install Python now"
    if errorlevel 2 goto :manual_install
    if errorlevel 1 goto :install_python
)

echo ✅ Python is available
echo.

rem Check if dependencies are installed
echo 🔍 Checking dependencies...
python -c "import psutil, yaml" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Required dependencies not found. Installing...
    pip install -r "%PROJECT_ROOT%\requirements.txt"
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        goto :error_exit
    )
    echo ✅ Dependencies installed successfully
)

echo.
echo 🚀 Starting NGIO Automation Suite...
echo.
echo ⚠️  IMPORTANT NOTES:
echo    • This will modify your Skyrim configuration files
echo    • Skyrim will launch and restart multiple times automatically  
echo    • The process may take 2-4 hours to complete
echo    • You can safely leave the computer during this time
echo.

choice /c YN /m "Are you ready to start the automation"
if errorlevel 2 goto :normal_exit
if errorlevel 1 goto :run_automation

:run_automation
echo.
echo ===============================================
echo 🌱 Starting Automated Grass Cache Generation
echo ===============================================
echo.

cd /d "%PROJECT_ROOT%"
python "%PYTHON_SCRIPT%"

if errorlevel 1 (
    echo.
    echo ❌ Automation failed. Check the logs for details.
    goto :error_exit
)

echo.
echo 🎉 Automation completed successfully!
goto :normal_exit

:install_python
echo.
echo 📥 This feature is not yet implemented.
echo Please visit https://www.python.org/downloads/ to install Python.
echo Make sure to check "Add Python to PATH" during installation.
echo.
goto :manual_exit

:manual_install
echo.
echo Manual Python installation:
echo 1. Go to https://www.python.org/downloads/
echo 2. Download Python 3.7 or higher
echo 3. Run the installer and check "Add Python to PATH"
echo 4. Restart command prompt and run this script again
echo.
goto :manual_exit

:error_exit
echo.
echo ===============================================
echo ❌ Script execution failed
echo ===============================================
echo.
echo Please check:
echo • Your Skyrim installation
echo • Required mods (NGIO, Seasons of Skyrim, SKSE)
echo • Python installation and dependencies
echo.
echo For help, visit: https://github.com/ReidenXerx/ngio-automation-suite
echo.
pause
exit /b 1

:manual_exit
pause
exit /b 0

:normal_exit
echo.
echo ===============================================
echo 🎊 Thank you for using NGIO Automation Suite!
echo ===============================================
echo.
echo If this tool saved you time, please:
echo ⭐ Star the project: https://github.com/ReidenXerx/ngio-automation-suite
echo 🐛 Report bugs or suggest features on GitHub
echo 💬 Share with the Skyrim modding community!
echo.
pause
exit /b 0
