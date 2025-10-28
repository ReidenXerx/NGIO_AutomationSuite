#!/usr/bin/env python3
"""
NGIO Automation Suite - Release Build System
Creates bundled release package with complete Python environment (no Python installation required)
"""

import os
import sys
import shutil
import zipfile
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Import version from single source of truth
sys.path.insert(0, str(Path(__file__).parent / "src"))
from __version__ import __version__, __title__

# Project configuration
PROJECT_NAME = "ngio-automation-suite"
VERSION = __version__
PYTHON_PACKAGE_NAME = "ngio_automation_suite"

# Directories
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
RELEASE_DIR = ROOT_DIR / "release"


def clean_directories():
    """Clean build directories."""
    print("🧹 Cleaning build directories...")
    
    for directory in [BUILD_DIR, DIST_DIR, RELEASE_DIR]:
        if directory.exists():
            print(f"   🗑️  Removing {directory.name}")
            shutil.rmtree(directory)
        else:
            print(f"   ✅ {directory.name} doesn't exist, skipping")
    
    # Create fresh directories
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    print("   ✅ Created fresh directories")


def build_python_packages():
    """Build Python wheel and source distributions."""
    print("📦 Building Python packages...")
    
    # Install/upgrade build tools
    print("🔄 Installing/upgrading build tools")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "--upgrade", 
        "build", "wheel", "setuptools"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"   ✅ {result.stdout.strip()}")
    else:
        print(f"   ⚠️ {result.stderr}")
    
    # Build wheel and source distribution
    print("🔄 Building wheel and source distribution")
    result = subprocess.run([
        sys.executable, "-m", "build"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅", result.stdout)
        
        # List built files
        if DIST_DIR.exists():
            files = list(DIST_DIR.glob("*"))
            print(f"   ✅ Built {len(files)} files:")
            for file in files:
                print(f"      📄 {file.name}")
    else:
        print(f"   ❌ Build failed: {result.stderr}")
        return False
    
    return True


def create_bundled_release():
    """Create bundled release with complete Python environment."""
    print("📦 Creating bundled release...")
    
    # Create bundled package directory
    bundled_dir = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-bundled"
    bundled_dir.mkdir(parents=True, exist_ok=True)
    
    # Instead of venv, copy the entire Python installation to make it truly portable
    python_dir = bundled_dir / "python"
    print("   🔄 Creating portable Python environment...")
    
    try:
        python_home = Path(sys.executable).parent
        
        # Copy the entire Python directory
        print("   📦 Copying Python installation...")
        shutil.copytree(python_home, python_dir, 
                       ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'),
                       dirs_exist_ok=True)
        print("   ✅ Python installation copied")
        
        # Set up Python paths
        venv_python = python_dir / "python.exe"
        venv_pip = python_dir / "Scripts" / "pip.exe"
        
        if not venv_python.exists():
            print(f"   ❌ Python executable not found at: {venv_python}")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to create portable Python environment: {e}")
        return None
    
    # Test the Python executable
    try:
        result = subprocess.run([
            str(venv_python), "-c", "print('Python test successful')"
        ], capture_output=True, text=True, check=True)
        print("   ✅ Python executable verified")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Python executable test failed: {e}")
        return None
    
    # Install dependencies in the bundled environment
    print("   🔄 Installing dependencies in bundled environment...")
    
    try:
        # Upgrade pip
        print("   🔄 Upgrading pip...")
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
        ], capture_output=True, text=True)
        
        # Install project dependencies
        print("   🔄 Installing project dependencies...")
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("   ✅ Dependencies installed in bundled environment")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        return None
    
    # Copy main runner
    runner_file = ROOT_DIR / "ngio_automation_runner.py"
    if runner_file.exists():
        shutil.copy2(runner_file, bundled_dir / "ngio_automation_runner.py")
        print("   📄 Copied ngio_automation_runner.py")
    
    # Copy source files
    shutil.copytree(SRC_DIR, bundled_dir / "src", dirs_exist_ok=True)
    print("   📁 Copied src/ directory")
    
    # Copy documentation
    if (ROOT_DIR / "docs").exists():
        shutil.copytree(ROOT_DIR / "docs", bundled_dir / "docs", dirs_exist_ok=True)
        print("   📁 Copied docs/ directory")
    
    # Copy documentation and license files
    for file in ["README.md", "LICENSE"]:
        src_file = ROOT_DIR / file
        if src_file.exists():
            shutil.copy2(src_file, bundled_dir / file)
            print(f"   📄 Copied {file}")
    
    # Create bundled launcher script
    launcher_content = f'''@echo off
REM NGIO Automation Suite - Bundled Edition Launcher
REM No Python installation required!

title NGIO Automation Suite (Bundled Edition)

echo.
echo ================================================================================
echo                        NGIO AUTOMATION SUITE
echo                       Bundled Edition (No Python Required!)
echo                           Complete Python Environment Included
echo ================================================================================
echo.
echo This bundled version includes a complete Python environment!
echo No Python installation required - everything is self-contained.
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Use the bundled Python interpreter
set BUNDLED_PYTHON=%SCRIPT_DIR%python\\python.exe

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

REM Run NGIO Automation Suite using bundled Python
"%BUNDLED_PYTHON%" "%SCRIPT_DIR%ngio_automation_runner.py"

echo.
echo NGIO Automation Suite has finished running.
echo Check the output directory for your generated archives!
echo.
pause
'''
    
    with open(bundled_dir / "run_bundled.bat", "w") as f:
        f.write(launcher_content)
    print("   📄 Created run_bundled.bat")
    
    # Create ZIP archive
    zip_path = RELEASE_DIR / f"{PROJECT_NAME}-{VERSION}-bundled.zip"
    print("   🔄 Creating ZIP archive (this may take a moment)...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(bundled_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(bundled_dir.parent)
                zipf.write(file_path, arcname)
    
    # Clean up extracted directory
    shutil.rmtree(bundled_dir)
    
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"   ✅ Created {zip_path.name} ({size_mb:.1f} MB)")
    
    return zip_path


def create_release_info():
    """Create release information JSON."""
    print("📋 Creating release information...")
    
    release_info = {
        "project": PROJECT_NAME,
        "version": VERSION,
        "build_date": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "release_type": "bundled",
        "python_required": False,
        "description": "Complete self-contained package with Python environment included",
        "files": [],
        "checksums": {}
    }
    
    # Add file information
    for file in RELEASE_DIR.glob("*.zip"):
        size_mb = file.stat().st_size / 1024 / 1024
        release_info["files"].append({
            "name": file.name,
            "size_mb": round(size_mb, 2),
            "type": "bundled"
        })
    
    # Write release info
    info_path = RELEASE_DIR / "release_info.json"
    with open(info_path, 'w') as f:
        json.dump(release_info, f, indent=2)
    
    print(f"   ✅ Created {info_path.name}")


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
        
        # Step 4: Create release information
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

