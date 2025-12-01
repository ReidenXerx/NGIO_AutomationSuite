#!/usr/bin/env python3
"""
NGIO Automation Suite - Enhanced Release Build System (v1.5.1)

Creates professional release packages:
1. Single-file executable (PyInstaller) - RECOMMENDED
2. Portable ZIP with source code
3. Complete documentation package

Usage:
    python build_release.py                  # Build everything
    python build_release.py --exe-only       # Build only single .exe
    python build_release.py --portable-only  # Build only portable ZIP
"""

import os
import sys
import shutil
import zipfile
import subprocess
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# Import version from single source of truth
sys.path.insert(0, str(Path(__file__).parent / "src"))
from __version__ import __version__, __title__

# Project configuration
PROJECT_NAME = "NGIO_Automation_Suite"
VERSION = __version__
PYTHON_PACKAGE_NAME = "ngio_automation_suite"

# Directories
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
RELEASE_DIR = ROOT_DIR / "release"


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def clean_directories():
    """Clean build directories."""
    print("🧹 Cleaning build directories...")
    
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            print(f"   🗑️  Removing {directory.name}")
            shutil.rmtree(directory)
        else:
            print(f"   ✅ {directory.name} doesn't exist, skipping")
    
    # Create fresh directories
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    print("   ✅ Created fresh directories")


def check_dependencies():
    """Check if required build dependencies are installed."""
    print("🔍 Checking build dependencies...")
    
    dependencies = {
        'PyInstaller': 'PyInstaller (for .exe generation)',  # Capital P!
        'psutil': 'psutil (runtime dependency)',
        'colorama': 'colorama (runtime dependency)',
        'colorlog': 'colorlog (runtime dependency)',
        'yaml': 'PyYAML (runtime dependency)',
        'win10toast': 'win10toast (runtime dependency)',
        'tqdm': 'tqdm (runtime dependency)',
    }
    
    missing = []
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {description}")
        except ImportError:
            print(f"   ❌ {description} - MISSING")
            missing.append(module)
    
    if missing:
        print("\n⚠️ Missing dependencies detected!")
        print("   Run this command to install them:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("   ✅ All dependencies installed")
    return True


def build_single_exe():
    """Build single-file executable using PyInstaller."""
    print("🚀 Building single-file executable with PyInstaller...")
    print("   This may take 2-5 minutes depending on your system...")
    
    spec_file = ROOT_DIR / "ngio_automation.spec"
    if not spec_file.exists():
        print(f"   ❌ Spec file not found: {spec_file}")
        return False
    
    # Run PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",  # Clean cache
        "--noconfirm",  # Overwrite without asking
        str(spec_file)
    ]
    
    print(f"   🔄 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ PyInstaller failed:")
        print(result.stderr)
        return False
    
    # Check if EXE was created
    exe_files = list(DIST_DIR.glob("*.exe"))
    if not exe_files:
        print("   ❌ No .exe file generated!")
        return False
    
    exe_file = exe_files[0]
    size_mb = exe_file.stat().st_size / 1024 / 1024
    print(f"   ✅ Created: {exe_file.name} ({size_mb:.1f} MB)")
    
    return True


def create_portable_package():
    """Create portable ZIP package with source code and launcher."""
    print("📦 Creating portable package...")
    
    # Create portable directory
    portable_dir = RELEASE_DIR / f"{PROJECT_NAME}_v{VERSION}_Portable"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main runner
    runner_file = ROOT_DIR / "ngio_automation_runner.py"
    shutil.copy2(runner_file, portable_dir / "ngio_automation_runner.py")
    print("   📄 Copied ngio_automation_runner.py")
    
    # Copy source directory
    shutil.copytree(SRC_DIR, portable_dir / "src", dirs_exist_ok=True)
    print("   📁 Copied src/ directory")
    
    # Copy documentation
    docs_dir = ROOT_DIR / "docs"
    if docs_dir.exists():
        shutil.copytree(docs_dir, portable_dir / "docs", dirs_exist_ok=True)
        print("   📁 Copied docs/ directory")
    
    # Copy essential files
    essential_files = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        "run_ngio_automation.bat"
    ]
    
    for filename in essential_files:
        src_file = ROOT_DIR / filename
        if src_file.exists():
            shutil.copy2(src_file, portable_dir / filename)
            print(f"   📄 Copied {filename}")
    
    # Create portable launcher (with Python check)
    launcher_content = '''@echo off
REM NGIO Automation Suite - Portable Edition Launcher
REM Requires Python 3.8+ to be installed on your system

title NGIO Automation Suite - Portable Edition
color 0B

echo.
echo ================================================================================
echo                        NGIO AUTOMATION SUITE
echo                           Portable Edition v{version}
echo                         Requires Python 3.8+ Installed
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo This portable version requires Python 3.8 or newer.
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    echo Alternative: Use the single-file .exe version ^(no Python required^)
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import psutil, colorama, yaml, tqdm" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Some dependencies are missing. Installing...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo Failed to install dependencies!
        echo Try manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
)

echo.
echo Starting NGIO Automation Suite...
echo.

REM Run with unbuffered output
python -u ngio_automation_runner.py %*

echo.
pause
'''.format(version=VERSION)
    
    with open(portable_dir / "run_portable.bat", "w", encoding='utf-8') as f:
        f.write(launcher_content)
    print("   📄 Created run_portable.bat")
    
    # Create README for portable version
    portable_readme = f'''# NGIO Automation Suite - Portable Edition v{VERSION}

## What is this?

This is the **portable source code version** of NGIO Automation Suite.
It requires Python 3.8+ to be installed on your system.

## Requirements

- Python 3.8 or newer
- Windows 10/11
- Skyrim SE/AE/VR with NGIO mod installed

## Quick Start

1. **Install Python** (if not already installed):
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation!

2. **Run the tool**:
   - Double-click `run_portable.bat`
   - Or manually: `python ngio_automation_runner.py`

3. **Dependencies** (auto-installed on first run):
   - If needed, manually run: `pip install -r requirements.txt`

## Alternative: Single-File Executable

If you don't want to install Python, download the single-file .exe version instead:
- No Python installation required
- Just one file to download and run
- Same functionality as this portable version

## Documentation

See the `docs/` folder for complete documentation:
- NEXUS_DOCUMENTATION.txt - Complete user guide
- PAGEFILE_SETUP_GUIDE.txt - Important system setup
- V1.5.1_RELEASE_NOTES.md - Latest changes

## Support

For issues, suggestions, or questions:
- Check the documentation in `docs/`
- Visit the Nexus Mods page
- Read the main README.md

---

**Note:** This portable version is intended for developers and users who:
- Already have Python installed
- Want to modify the source code
- Prefer running scripts directly vs. executables
'''
    
    with open(portable_dir / "README_PORTABLE.txt", "w", encoding='utf-8') as f:
        f.write(portable_readme)
    print("   📄 Created README_PORTABLE.txt")
    
    # Create ZIP archive
    zip_path = RELEASE_DIR / f"{PROJECT_NAME}_v{VERSION}_Portable.zip"
    print(f"   🔄 Creating ZIP archive...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                # Skip .pyc files
                if file.endswith('.pyc'):
                    continue
                    
                file_path = Path(root) / file
                arcname = file_path.relative_to(portable_dir.parent)
                zipf.write(file_path, arcname)
    
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"   ✅ Created: {zip_path.name} ({size_mb:.1f} MB)")
    
    # Clean up extracted directory
    shutil.rmtree(portable_dir)
    
    return zip_path


def create_final_release_package():
    """Create final release package with EXE + docs."""
    print("📦 Creating final release package...")
    
    release_name = f"{PROJECT_NAME}_v{VERSION}_Release"
    release_dir = RELEASE_DIR / release_name
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy EXE
    exe_files = list(DIST_DIR.glob("*.exe"))
    if exe_files:
        exe_file = exe_files[0]
        shutil.copy2(exe_file, release_dir / exe_file.name)
        print(f"   📄 Copied {exe_file.name}")
    else:
        print("   ⚠️ No .exe file found to include")
    
    # Copy documentation
    docs_dir = ROOT_DIR / "docs"
    if docs_dir.exists():
        target_docs = release_dir / "docs"
        target_docs.mkdir(exist_ok=True)
        
        # Copy essential documentation only
        essential_docs = [
            "NEXUS_DOCUMENTATION.txt",
            "PAGEFILE_SETUP_GUIDE.txt",
            "V1.5.1_RELEASE_NOTES.md"
        ]
        
        for doc in essential_docs:
            src_doc = docs_dir / doc
            if src_doc.exists():
                shutil.copy2(src_doc, target_docs / doc)
                print(f"   📄 Copied docs/{doc}")
    
    # Copy README
    readme = ROOT_DIR / "README.md"
    if readme.exists():
        shutil.copy2(readme, release_dir / "README.md")
        print("   📄 Copied README.md")
    
    # Create Quick Start guide
    quick_start = f'''# NGIO Automation Suite v{VERSION} - Quick Start

## What's in this package?

- **NGIO_Automation_Suite_v{VERSION}.exe** - The main application (single file, no Python needed!)
- **docs/** - Complete documentation and guides
- **README.md** - Full project documentation

## Quick Start (3 Steps)

1. **Setup your pagefile** (CRITICAL!):
   - Read: docs/PAGEFILE_SETUP_GUIDE.txt
   - Ensure at least 20GB pagefile allocated

2. **Run the application**:
   - Double-click the .exe file
   - Follow the interactive prompts

3. **Select your season(s)**:
   - Single season: ~60-90 minutes
   - All 4 seasons (overnight): ~4-6 hours

## Important Notes

⚠️ **PAGEFILE SETUP IS MANDATORY**
Without proper pagefile, Skyrim WILL crash during generation!

📁 **First-Time Setup**
The tool will guide you through:
- Locating your Skyrim installation
- Selecting output directory
- Choosing grass generation profile

🌱 **Grass Profiles**
- Fast: ~30-45 minutes (basic density)
- LOD Compatible: ~60-90 minutes (recommended for DynDOLOD)
- Maximum Quality: ~90-120 minutes (highest density)

## Documentation

- **Complete Guide**: docs/NEXUS_DOCUMENTATION.txt
- **Pagefile Setup**: docs/PAGEFILE_SETUP_GUIDE.txt
- **Release Notes**: docs/V1.5.1_RELEASE_NOTES.md
- **Full README**: README.md

## System Requirements

- Windows 10/11
- Skyrim SE/AE/VR with NGIO mod
- 16GB+ RAM (recommended)
- 20GB+ pagefile (required!)
- SKSE64 (recommended)

---

Enjoy your automated grass cache generation! 🌱
'''
    
    with open(release_dir / "QUICK_START.txt", "w", encoding='utf-8') as f:
        f.write(quick_start)
    print("   📄 Created QUICK_START.txt")
    
    # Create ZIP of final package
    zip_path = RELEASE_DIR / f"{release_name}.zip"
    print(f"   🔄 Creating final release ZIP...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(release_dir.parent)
                zipf.write(file_path, arcname)
    
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"   ✅ Created: {zip_path.name} ({size_mb:.1f} MB)")
    
    # Clean up extracted directory
    shutil.rmtree(release_dir)
    
    return zip_path


def create_release_info():
    """Create release information JSON with checksums."""
    print("📋 Creating release information...")
    
    release_info = {
        "project": PROJECT_NAME,
        "version": VERSION,
        "build_date": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "files": [],
        "checksums": {}
    }
    
    # Process all release files
    for file in sorted(RELEASE_DIR.glob("*.zip")):
        size_mb = file.stat().st_size / 1024 / 1024
        checksum = calculate_checksum(file)
        
        file_type = "unknown"
        if "Portable" in file.name:
            file_type = "portable_source"
        elif "Release" in file.name:
            file_type = "single_exe_package"
        
        release_info["files"].append({
            "name": file.name,
            "size_mb": round(size_mb, 2),
            "type": file_type,
            "sha256": checksum
        })
        
        release_info["checksums"][file.name] = checksum
    
    # Add standalone EXE if exists
    exe_files = list(DIST_DIR.glob("*.exe"))
    if exe_files:
        exe_file = exe_files[0]
        size_mb = exe_file.stat().st_size / 1024 / 1024
        checksum = calculate_checksum(exe_file)
        
        release_info["files"].append({
            "name": exe_file.name,
            "size_mb": round(size_mb, 2),
            "type": "standalone_exe",
            "sha256": checksum,
            "note": "Standalone executable (no Python required)"
        })
        
        release_info["checksums"][exe_file.name] = checksum
    
    # Write release info
    info_path = RELEASE_DIR / "release_info.json"
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(release_info, f, indent=2)
    
    print(f"   ✅ Created {info_path.name}")
    
    # Also create human-readable checksums file
    checksums_path = RELEASE_DIR / "CHECKSUMS_SHA256.txt"
    with open(checksums_path, 'w', encoding='utf-8') as f:
        f.write(f"# SHA256 Checksums - {PROJECT_NAME} v{VERSION}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for filename, checksum in sorted(release_info["checksums"].items()):
            f.write(f"{checksum}  {filename}\n")
    
    print(f"   ✅ Created {checksums_path.name}")


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description="Build NGIO Automation Suite releases")
    parser.add_argument('--exe-only', action='store_true', help='Build only single .exe')
    parser.add_argument('--portable-only', action='store_true', help='Build only portable ZIP')
    args = parser.parse_args()
    
    print("🚀 NGIO Automation Suite - Enhanced Build System v1.5.1")
    print("=" * 80)
    print(f"   Project: {PROJECT_NAME}")
    print(f"   Version: {VERSION}")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Check dependencies
        if not check_dependencies():
            print("\n❌ Build aborted: Missing dependencies")
            sys.exit(1)
        print()
        
        # Step 2: Clean directories
        clean_directories()
        print()
        
        # Step 3: Build based on arguments
        if args.portable_only:
            print("📦 Building portable package only...")
            create_portable_package()
        elif args.exe_only:
            print("🚀 Building single .exe only...")
            if not build_single_exe():
                raise Exception("EXE build failed")
            create_final_release_package()
        else:
            # Build everything
            print("🎯 Building all release packages...")
            print()
            
            # Build single EXE
            if not build_single_exe():
                raise Exception("EXE build failed")
            print()
            
            # Create final release package
            create_final_release_package()
            print()
            
            # Create portable package
            create_portable_package()
            print()
        
        # Step 4: Create release information
        create_release_info()
        print()
        
        # Summary
        print("=" * 80)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        
        # List all release files
        print("📦 Release files created:")
        release_files = sorted(RELEASE_DIR.glob("*"))
        total_size = 0
        
        for file_path in release_files:
            if file_path.is_file():
                size_mb = file_path.stat().st_size / 1024 / 1024
                total_size += size_mb
                
                icon = "📄"
                if file_path.suffix == ".zip":
                    icon = "📦"
                elif file_path.suffix == ".json":
                    icon = "📋"
                elif file_path.suffix == ".txt":
                    icon = "📝"
                
                print(f"   {icon} {file_path.name} ({size_mb:.1f} MB)")
        
        # Show EXE in dist folder too
        print()
        print("📦 Executable (dist/):")
        exe_files = list(DIST_DIR.glob("*.exe"))
        for exe_file in exe_files:
            size_mb = exe_file.stat().st_size / 1024 / 1024
            total_size += size_mb
            print(f"   🚀 {exe_file.name} ({size_mb:.1f} MB)")
        
        print()
        print(f"💾 Total size: {total_size:.1f} MB")
        print()
        print("🎯 Ready for distribution!")
        print()
        print("📁 Directories:")
        print("   📦 dist/    - Standalone .exe file")
        print("   📦 release/ - Distribution packages (ZIP files)")
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
