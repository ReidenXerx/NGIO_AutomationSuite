# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

NGIO Automation Suite is a Python-based automation tool for Skyrim Special Edition modding. It automates the tedious 4+ hour manual process of generating seasonal grass cache files using the No Grass In Objects (NGIO) mod, reducing it to a 5-minute setup that runs unattended.

## Common Development Commands

### Running the Application
```powershell
# Run from source (development)
python ngio_automation_runner.py

# Run with launcher script
.\run_ngio_automation.bat
```

### Building and Packaging
```powershell
# Build all release packages (portable, installer, source)
python build_release.py

# Alternative Windows launcher
.\build.bat
```

### Dependencies
```powershell
# Install runtime dependencies
pip install -r requirements.txt

# Core dependencies are: psutil, colorama, colorlog
```

### Testing
```powershell
# No automated test framework - manual testing required
# Test by running: python ngio_automation_runner.py
# Test builds by running: python build_release.py
```

## Architecture Overview

### Core Design Pattern
The application follows a **Manager Pattern** with a central orchestrator (`NGIOAutomationSuite`) that coordinates specialized managers for different aspects of the automation workflow.

### Main Components

**Entry Point**
- `ngio_automation_runner.py` - Main CLI interface with menu system and user interaction

**Core Automation Engine (`src/core/`)**
- `automation_suite.py` - Master orchestrator that coordinates the entire workflow
- `game_manager.py` - Handles Skyrim process lifecycle (launch, monitor, crash detection)
- `config_manager.py` - Manages INI file backup/modification/restoration for seasonal mods
- `file_processor.py` - High-performance multithreaded file operations (renaming, moving)
- `progress_monitor.py` - Tracks grass generation progress via file system monitoring
- `archive_creator.py` - Creates installable mod archives with proper structure

**Utilities (`src/utils/`)**
- `logger.py` - Colored, contextual logging system
- `config_cache.py` - Persistent user configuration storage
- `skyrim_detector.py` - Auto-detection of Skyrim installations and mod managers

### Key Workflow States
The automation follows a strict state machine:
1. **Setup & Validation** - Verify paths, dependencies, Skyrim installation
2. **Configuration Backup** - Save original seasonal mod settings
3. **Season Generation Loop** - For each season: modify config → launch Skyrim → monitor progress → handle crashes → process files
4. **Archive Creation** - Package generated files into installable mods
5. **Restoration & Cleanup** - Restore original settings and clean temporary files

### Season Management
Uses an enum-based system (`Season`) that maps to:
- Seasonal mod configuration values (1=Winter, 2=Spring, etc.)
- File naming conventions (.WIN.cgid, .SPR.cgid, etc.)
- Archive naming and organization

## Development Workflow

### Making Code Changes
1. Edit source code in `src/` directory
2. Test with `python ngio_automation_runner.py`
3. Build release with `python build_release.py` for full testing
4. Test the portable release extraction and execution

### Version Management
Update version in **3 locations** when releasing:
- `pyproject.toml` → `version = "X.Y.Z"`
- `setup.py` → `version="X.Y.Z"`
- `build_release.py` → `VERSION = "X.Y.Z"`

### Build System
The build system creates multiple distribution formats:
- **Portable Release** - ZIP with launcher script for end users
- **Python Packages** - Standard wheel and source distributions
- **Source Release** - Developer-friendly source code package
- **Installer Package** - Professional installation option

### Error Handling Philosophy
The codebase emphasizes **graceful degradation** and **automatic recovery**:
- Skyrim crashes are expected and handled with intelligent retry logic
- File operations use atomic moves and backup strategies  
- Configuration changes are always reversible
- Progress monitoring includes multiple timeout mechanisms

## Platform-Specific Notes

### Windows-Specific Behavior
- Process monitoring uses Windows-specific psutil features
- INI file handling accounts for Windows file locking
- Batch launchers provide user-friendly entry points
- File paths use Windows conventions throughout

### Skyrim Integration Points
- Works with SE/AE/VR editions via executable detection
- Integrates with mod managers (MO2/Vortex) through profile detection
- Monitors SKSE64 processes specifically
- Handles Data directory structure and permissions

## Dependencies and Requirements

### Runtime Requirements
- Python 3.8+ (tested through 3.12)
- Windows 10/11
- Skyrim SE/AE/VR with NGIO mod
- SKSE64 (recommended for stability)

### Optional Dependencies
- Seasons of Skyrim mod (for seasonal generation)
- Mod Organizer 2 or Vortex (for profile detection)

## File Structure Conventions

### Source Organization
- `src/core/` - Core automation logic (no UI dependencies)
- `src/utils/` - Shared utilities and helpers
- `docs/` - User and developer documentation
- `scripts/` - Build and utility scripts
- `release/` - Generated distribution files (gitignored)

### Generated Files
- `PrecacheGrass.txt` - Skyrim progress tracking file
- `*.cgid` - Generated grass cache files  
- `*.log` - Application logs
- Archives follow naming: `NGIO_GrassCache_{Season}_{Date}.zip`

## Common Gotchas

### File System Timing
- Grass generation involves large file operations - always check file locks
- Progress monitoring relies on file modification times - account for file system delays
- Archive creation requires exclusive file access

### Process Management
- Skyrim processes may spawn multiple child processes
- SKSE64 launches differently than base game
- Crash detection must differentiate between intentional and unintentional exits

### Configuration State
- Seasonal mod configs are shared between different automation runs
- Backup and restoration must be atomic operations
- User settings persist between sessions via JSON cache