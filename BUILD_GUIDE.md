# NGIO Automation Suite - Build Guide

## Overview

The enhanced build system creates professional, distributable packages using **PyInstaller** to compile Python code into a single executable file.

## What Gets Built

### 1. Single-File Executable (Recommended for Users)
- **File**: `NGIO_Automation_Suite_v{version}.exe`
- **Size**: ~20-50 MB
- **Contains**: Everything (Python runtime + all dependencies + source code)
- **Requires**: Nothing! Just Windows 10/11
- **Distribution**: Best for Nexus Mods users

### 2. Complete Release Package
- **File**: `NGIO_Automation_Suite_v{version}_Release.zip`
- **Contains**: 
  - Single .exe file
  - Complete documentation
  - Quick start guide
  - README
- **Use case**: Main distribution package for Nexus Mods

### 3. Portable Source Package
- **File**: `NGIO_Automation_Suite_v{version}_Portable.zip`
- **Contains**:
  - Full source code
  - Launcher script
  - Documentation
  - requirements.txt
- **Requires**: Python 3.8+
- **Use case**: For developers or users who prefer source code

## Prerequisites

### System Requirements
- Windows 10/11
- Python 3.8 or newer
- ~500MB free disk space (for build process)

### Python Dependencies
```bash
pip install -r requirements.txt
```

Key dependency: **PyInstaller 6.0+** (for creating .exe)

## Build Instructions

### Quick Build (Everything)
```bash
# Option 1: Using batch file (recommended)
build.bat

# Option 2: Using Python directly
python build_release.py
```

### Selective Builds

**Build only single .exe:**
```bash
python build_release.py --exe-only
```

**Build only portable package:**
```bash
python build_release.py --portable-only
```

## Build Process Details

### Step 1: Dependency Check
The build system verifies all required packages are installed:
- PyInstaller (build tool)
- psutil, colorama, colorlog (runtime)
- PyYAML, win10toast, tqdm (features)

### Step 2: Clean Build
Removes previous build artifacts:
- `build/` - PyInstaller temp files
- `dist/` - Previous executables

### Step 3: PyInstaller Compilation
Creates single-file executable using `ngio_automation.spec`:
- Bundles Python interpreter
- Includes all source code
- Embeds all dependencies
- Compresses with UPX (reduces size by ~30%)

**Time**: 2-5 minutes (depends on CPU)

### Step 4: Package Creation
Creates distribution packages:
- Final release ZIP (exe + docs)
- Portable source ZIP
- Checksums file (SHA256)

### Step 5: Verification
Generates:
- `release_info.json` - Machine-readable metadata
- `CHECKSUMS_SHA256.txt` - Human-readable checksums

## Build Output

### Directory Structure
```
NGIO_AutomationSuite/
├── dist/
│   └── NGIO_Automation_Suite_v1.5.1.exe    # Standalone executable
├── release/
│   ├── NGIO_Automation_Suite_v1.5.1_Release.zip       # Main package
│   ├── NGIO_Automation_Suite_v1.5.1_Portable.zip      # Source package
│   ├── release_info.json                               # Build metadata
│   └── CHECKSUMS_SHA256.txt                            # Integrity verification
└── build/                                              # Temp files (auto-cleaned)
```

### File Sizes (Approximate)
- Single .exe: 25-45 MB
- Release package: 30-50 MB
- Portable package: 5-10 MB

## Distribution Checklist

### For Nexus Mods Upload

**Recommended Package**: `NGIO_Automation_Suite_v{version}_Release.zip`

**Contents to verify:**
- ✅ Single .exe file
- ✅ QUICK_START.txt
- ✅ README.md
- ✅ docs/ folder with:
  - NEXUS_DOCUMENTATION.txt
  - PAGEFILE_SETUP_GUIDE.txt
  - V1.5.1_RELEASE_NOTES.md

**Optional: Portable Version**
Upload `NGIO_Automation_Suite_v{version}_Portable.zip` as alternative download for users with Python.

**Checksums**
Include `CHECKSUMS_SHA256.txt` in description for users to verify integrity.

## Troubleshooting

### PyInstaller Not Found
```bash
pip install pyinstaller
```

### Build Fails with "Module not found"
Check that all dependencies are installed:
```bash
pip install -r requirements.txt
```

### .exe Size is Too Large (>100MB)
This is normal if:
- You have many extra packages installed in your Python environment
- PyInstaller is including unnecessary modules

**Solution**: Use a clean virtual environment:
```bash
python -m venv build_env
build_env\Scripts\activate
pip install -r requirements.txt
python build_release.py
```

### .exe Doesn't Run
Common causes:
1. **Antivirus blocking** - Add exception for the .exe
2. **Windows SmartScreen** - Click "More info" → "Run anyway"
3. **Missing Visual C++ Runtime** - User needs to install VC++ redistributable

### Build is Slow
First build: 3-5 minutes (normal)
Subsequent builds: 2-3 minutes

To speed up:
- Close other applications
- Use SSD storage
- Don't run antivirus scan during build

## Advanced Configuration

### Customizing PyInstaller

Edit `ngio_automation.spec` to modify:
- **Icon**: Set `icon='path/to/icon.ico'`
- **Console mode**: Set `console=False` for windowed app
- **UPX compression**: Set `upx=False` to disable compression (faster build, larger file)
- **Exclude modules**: Add to `excludes` list to reduce size

### Version Info (Windows Properties)

To add version info (visible in EXE properties):
1. Create version info file using PyInstaller's `pyi-grab_version`
2. Edit `ngio_automation.spec` → set `version_file='version_info.txt'`

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python build_release.py
      - uses: actions/upload-artifact@v2
        with:
          name: release-packages
          path: release/*.zip
```

## Support

For build issues:
1. Check this guide
2. Verify all prerequisites
3. Try clean build environment
4. Check PyInstaller documentation: https://pyinstaller.org/

---

**Last Updated**: 2025-12-01 (v1.5.1)

