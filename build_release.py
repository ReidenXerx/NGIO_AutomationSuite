#!/usr/bin/env python3
"""
NGIO Automation Suite - Release Build Script

This script creates a complete release package similar to 'npm run build'.
It handles all the steps needed to create distribution files for the
Skyrim grass cache automation tool.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
import json
from datetime import datetime

# Configuration
PROJECT_NAME = "ngio-automation-suite"
VERSION = "1.0.0"  # This should match setup.py and pyproject.toml
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")
RELEASE_DIR = Path("release")

def run_command(command, description="", check=True):
    """Run a shell command and handle errors."""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stdout:
            print(f"   📝 stdout: {e.stdout}")
        if e.stderr:
            print(f"   📝 stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def clean_directories():
    """Clean build and dist directories."""
    print("🧹 Cleaning build directories...")
    
    for dir_path in [BUILD_DIR, DIST_DIR, RELEASE_DIR]:
        if dir_path.exists():
            print(f"   🗑️  Removing {dir_path}")
            shutil.rmtree(dir_path)
        else:
            print(f"   ✅ {dir_path} doesn't exist, skipping")
    
    # Create fresh directories
    RELEASE_DIR.mkdir(exist_ok=True)
    print("   ✅ Created fresh directories")

def build_python_packages():
    """Build Python wheel and source distribution."""
    print("📦 Building Python packages...")
    
    # Install/upgrade build tools
    run_command("python -m pip install --upgrade build wheel setuptools", 
                "Installing/upgrading build tools")
    
    # Build wheel and source distribution
    run_command("python -m build", "Building wheel and source distribution")
    
    # List what was built
    if DIST_DIR.exists():
        built_files = list(DIST_DIR.glob("*"))
        print(f"   ✅ Built {len(built_files)} files:")
        for file in built_files:
            print(f"      📄 {file.name}")

def create_portable_release():
    """Create a portable ZIP release with all necessary files."""
    print("📦 Creating portable release...")
    
    portable_dir = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-portable"
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main files
    files_to_copy = [
        "ngio_automation_runner.py",
        "README.md",
        "LICENSE" if Path("LICENSE").exists() else None,
        "requirements.txt",
    ]
    
    for file_name in files_to_copy:
        if file_name and Path(file_name).exists():
            shutil.copy2(file_name, portable_dir)
            print(f"   📄 Copied {file_name}")
    
    # Copy src directory
    if Path("src").exists():
        shutil.copytree("src", portable_dir / "src")
        print("   📁 Copied src/ directory")
    
    # Copy docs directory
    if Path("docs").exists():
        shutil.copytree("docs", portable_dir / "docs")
        print("   📁 Copied docs/ directory")
    
    # Create the main portable launcher script
    launcher_content = '''@echo off
title NGIO Automation Suite - Portable Edition
color 0A
cls

echo ================================================================================
echo                         NGIO AUTOMATION SUITE
echo                      Portable Grass Cache Generator
echo                           Single-Season Workflow
echo ================================================================================
echo.
echo This portable version includes everything you need to run NGIO automation!
echo No installation required - just run this file.
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ and try again.
    echo Download from: https://www.python.org/downloads/
    echo.
    echo After installing Python, run this file again.
    echo.
    pause
    exit /b 1
)

echo Checking and installing dependencies...
python -m pip install -r requirements.txt --quiet --user

echo.
echo Starting NGIO Automation Suite...
echo.

python ngio_automation_runner.py

echo.
echo NGIO Automation Suite has finished running.
echo Check the output directory for your generated archives!
echo.
pause
'''
    
    with open(portable_dir / "start_ngio_automation.bat", "w") as f:
        f.write(launcher_content)
    print("   📄 Created start_ngio_automation.bat")
    
    # Create ZIP
    zip_path = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-portable.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(portable_dir)
                zipf.write(file_path, arc_name)
    
    print(f"   ✅ Created {zip_path.name} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # Clean up temp directory
    shutil.rmtree(portable_dir)

def create_source_release():
    """Create a source code ZIP release."""
    print("📦 Creating source release...")
    
    zip_path = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-source.zip"
    
    # Files and directories to include in source release
    include_patterns = [
        "src/**/*",
        "docs/**/*",
        "*.py",
        "*.bat",
        "*.md",
        "*.txt",
        "*.toml",
        "*.json",
        "LICENSE*",
    ]
    
    exclude_patterns = [
        "__pycache__/**",
        "*.pyc",
        ".git/**",
        "build/**",
        "dist/**",
        "release/**",
        ".pytest_cache/**",
        "*.log",
    ]
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pattern in include_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    # Check if file should be excluded
                    should_exclude = any(file_path.match(excl) for excl in exclude_patterns)
                    if not should_exclude:
                        zipf.write(file_path, file_path)
    
    print(f"   ✅ Created {zip_path.name} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")

def create_installer_package():
    """Create a Windows installer package."""
    print("📦 Creating installer package...")
    
    installer_dir = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-installer"
    installer_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy wheel file
    wheel_files = list(DIST_DIR.glob("*.whl"))
    if wheel_files:
        wheel_file = wheel_files[0]
        shutil.copy2(wheel_file, installer_dir)
        print(f"   📄 Copied {wheel_file.name}")
    
    # Create installer script
    installer_content = '''@echo off
title NGIO Automation Suite - Installer
color 0A
cls

echo ================================================================================
echo                    NGIO AUTOMATION SUITE - INSTALLER
echo                         Professional Installation
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ and try again.
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Installing NGIO Automation Suite...
echo.

REM Install the wheel package
for %%f in (*.whl) do (
    echo Installing %%f...
    python -m pip install "%%f" --user --force-reinstall
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install NGIO Automation Suite
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ================================================================================
echo                          INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo NGIO Automation Suite has been installed successfully!
echo.
echo To run the application:
echo   1. Open Command Prompt or PowerShell
echo   2. Type: ngio-automation
echo   3. Press Enter
echo.
echo Or create a desktop shortcut with the command: ngio-automation
echo.
pause
'''
    
    with open(installer_dir / "install.bat", "w") as f:
        f.write(installer_content)
    print("   📄 Created install.bat")
    
    # Create ZIP
    zip_path = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-installer.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(installer_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(installer_dir)
                zipf.write(file_path, arc_name)
    
    print(f"   ✅ Created {zip_path.name} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # Clean up temp directory
    shutil.rmtree(installer_dir)

def create_release_info():
    """Create release information file."""
    print("📋 Creating release information...")
    
    release_info = {
        "project": PROJECT_NAME,
        "version": VERSION,
        "build_date": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "files": [],
        "checksums": {},
        "installation": {
            "portable": "Extract ZIP and run start_ngio_automation.bat",
            "installer": "Extract ZIP and run install.bat",
            "pip": f"pip install {PROJECT_NAME}=={VERSION}",
            "requirements": "Python 3.8+ required"
        },
        "features": [
            "Fully automated grass cache generation",
            "Seasonal support (Winter, Spring, Summer, Autumn)",
            "Single-season workflow",
            "Crash detection and recovery", 
            "Progress preservation",
            "Archive generation with mod structure",
            "Intelligent completion detection",
            "SKSE integration",
            "Configuration persistence"
        ]
    }
    
    # List all files in release directory
    for file_path in RELEASE_DIR.glob("*"):
        if file_path.is_file():
            release_info["files"].append({
                "name": file_path.name,
                "size_mb": round(file_path.stat().st_size / 1024 / 1024, 2),
                "type": file_path.suffix
            })
    
    # Write release info
    info_path = RELEASE_DIR / "release_info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(release_info, f, indent=2)
    
    # Also create a human-readable version
    readme_content = f"""# NGIO Automation Suite v{VERSION}

**Build Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎮 What is this?

NGIO Automation Suite is a fully automated grass cache generation tool for Skyrim SE.
It transforms the manual 4+ hour process into a 5-minute automated workflow with
full seasonal support.

## 📦 Release Files

"""
    
    for file_info in release_info["files"]:
        readme_content += f"- **{file_info['name']}** ({file_info['size_mb']} MB)\n"
    
    readme_content += f"""
## 🚀 Quick Start

### Option 1: Portable (Recommended)
1. Download `{PROJECT_NAME}-{VERSION}-portable.zip`
2. Extract to any folder
3. Run `start_ngio_automation.bat`

### Option 2: Professional Installation
1. Download `{PROJECT_NAME}-{VERSION}-installer.zip`
2. Extract and run `install.bat`
3. Use `ngio-automation` command from anywhere

## ✨ Features

"""
    
    for feature in release_info["features"]:
        readme_content += f"- {feature}\n"
    
    readme_content += f"""
## 🔧 Requirements

- **Python 3.8+** (Download from https://python.org)
- **Windows 10/11**
- **Skyrim SE with NGIO mod**
- **SKSE64** (Recommended)

## 📖 Documentation

See the `docs/` folder for detailed documentation including:
- Installation guide
- Configuration options  
- Troubleshooting
- Technical details

## 🎯 Next Steps

1. Install the tool using one of the methods above
2. Run the configuration wizard on first launch
3. Select your season (Winter, Spring, Summer, or Autumn)
4. Let the automation handle the rest!

---

**Happy Modding!** 🌱
"""
    
    readme_path = RELEASE_DIR / "README.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"   ✅ Created release_info.json and README.txt")

def create_standalone_executable():
    """Create standalone executable using PyInstaller"""
    print("🔧 Creating standalone executable...")
    
    try:
        # Check if PyInstaller is available
        result = subprocess.run([sys.executable, "-c", "import PyInstaller"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("   ⚠️ PyInstaller not found - installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"], 
                         check=True)
        
        # Build executable using spec file
        print("   🔄 Building executable with PyInstaller...")
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            "--noconfirm", 
            "ngio_automation.spec"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"   ❌ PyInstaller build failed:")
            print(f"   {result.stderr}")
            return None
        
        # Check if executable was created
        exe_path = Path("dist") / "NGIO_Automation_Suite.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Created NGIO_Automation_Suite.exe ({size_mb:.1f} MB)")
            return exe_path
        else:
            print("   ❌ Executable not found after build")
            return None
            
    except Exception as e:
        print(f"   ❌ Standalone executable creation failed: {e}")
        return None

def create_bundled_release():
    """Create a bundled release with complete Python environment (like safe-resource-packer)"""
    print("📦 Creating bundled release...")
    
    # Create bundled package directory
    bundled_dir = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-bundled"
    bundled_dir.mkdir(parents=True, exist_ok=True)
    
    # Create virtual environment inside the package
    venv_dir = bundled_dir / "venv"
    print("   🔄 Creating virtual environment...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "venv", str(venv_dir)
        ], capture_output=True, text=True, check=True)
        print("   ✅ Virtual environment created")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to create virtual environment: {e}")
        return None
    
    # Install dependencies in the virtual environment
    print("   🔄 Installing dependencies in bundled environment...")
    venv_python = venv_dir / "Scripts" / "python.exe"
    venv_pip = venv_dir / "Scripts" / "pip.exe"
    
    try:
        # Use python -m pip instead of direct pip to avoid path issues
        print("   🔄 Upgrading pip...")
        result = subprocess.run([
            str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"   ⚠️ Pip upgrade warning: {result.stderr}")
            print("   🔄 Continuing with existing pip version...")
        
        # Install our dependencies
        print("   🔄 Installing project dependencies...")
        result = subprocess.run([
            str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("   ✅ Dependencies installed in bundled environment")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        print(f"   Error output: {e.stderr if hasattr(e, 'stderr') else 'No error details'}")
        return None
    
    # Copy main files
    files_to_copy = [
        "ngio_automation_runner.py",
        "README.md",
        "LICENSE" if Path("LICENSE").exists() else None,
    ]
    
    for file_name in files_to_copy:
        if file_name and Path(file_name).exists():
            shutil.copy2(file_name, bundled_dir)
            print(f"   📄 Copied {file_name}")
    
    # Copy src directory
    if Path("src").exists():
        shutil.copytree("src", bundled_dir / "src")
        print("   📁 Copied src/ directory")
    
    # Copy docs directory
    if Path("docs").exists():
        shutil.copytree("docs", bundled_dir / "docs")
        print("   📁 Copied docs/ directory")
    
    # Create the bundled launcher script (like safe-resource-packer)
    launcher_content = '''@echo off
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
set BUNDLED_PYTHON=%SCRIPT_DIR%venv\\Scripts\\python.exe

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
'''
    
    with open(bundled_dir / "start_ngio_automation.bat", "w") as f:
        f.write(launcher_content)
    print("   📄 Created start_ngio_automation.bat")
    
    # Create ZIP
    zip_path = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-bundled.zip"
    print("   🔄 Creating ZIP archive (this may take a moment)...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(bundled_dir):
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, file_path.relative_to(bundled_dir))
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"   ✅ Created {zip_path.name} ({size_mb:.1f} MB)")
    return zip_path

def main():
    """Main build process."""
    print("🚀 Starting NGIO Automation Suite build process...")
    print("=" * 80)
    
    try:
        # Step 1: Clean directories
        clean_directories()
        print()
        
        # Step 2: Build Python packages
        build_python_packages()
        print()
        
        # Step 3: Create bundled release (complete Python environment)
        create_bundled_release()
        print()
        
        # Step 4: Create portable release
        create_portable_release()
        print()
        
        # Step 5: Create source release
        create_source_release()
        print()
        
        # Step 6: Create installer package
        create_installer_package()
        print()
        
        # Step 7: Create release information
        create_release_info()
        print()
        
        # Summary
        print("=" * 80)
        print("🎉 Build completed successfully!")
        print()
        print("📁 Output directories:")
        print(f"   📦 dist/     - Python packages (wheel, source)")
        print(f"   📦 release/  - Distribution files")
        print()
        
        if RELEASE_DIR.exists():
            release_files = list(RELEASE_DIR.glob("*"))
            total_size = sum(f.stat().st_size for f in release_files if f.is_file())
            print(f"📊 Release summary:")
            print(f"   📄 {len(release_files)} files created")
            print(f"   💾 Total size: {total_size / 1024 / 1024:.1f} MB")
            print()
            print("📋 Release files:")
            for file_path in sorted(release_files):
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / 1024 / 1024
                    print(f"   📄 {file_path.name} ({size_mb:.1f} MB)")
        
        print()
        print("🎯 Ready for distribution!")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
