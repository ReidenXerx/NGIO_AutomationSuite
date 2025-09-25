@echo off
title NGIO Automation Suite - Bundled Edition
color 0A
cls

echo ================================================================================
echo                         NGIO AUTOMATION SUITE
echo                        Bundled Edition (No Python Required!)
echo                           Complete Python Environment Included
echo ================================================================================
echo.
echo This bundled version includes a complete Python environment!
echo No Python installation required - everything is self-contained.
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Use the bundled Python interpreter
set BUNDLED_PYTHON=%SCRIPT_DIR%venv\Scripts\python.exe

REM Check if bundled Python exists
if not exist "%BUNDLED_PYTHON%" (
    echo ERROR: Bundled Python interpreter not found!
    echo Expected location: %BUNDLED_PYTHON%
    echo.
    echo This may indicate a corrupted installation.
    echo Please re-download the bundled package.
    pause
    exit /b 1
)

echo Using bundled Python environment...
echo Python location: %BUNDLED_PYTHON%
echo.

REM Run the automation suite using bundled Python
"%BUNDLED_PYTHON%" "%SCRIPT_DIR%ngio_automation_runner.py"

echo.
echo NGIO Automation Suite has finished running.
echo Check the output directory for your generated archives!
echo.
pause
