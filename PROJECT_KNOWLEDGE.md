# NGIO Automation Suite - Project Knowledge Base

**Last Updated:** 2025-11-27  
**Version:** 1.5.0  
**Purpose:** Complete context for AI assistants and developers working on this project

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Development Setup](#development-setup)
6. [Key Concepts](#key-concepts)
7. [Important Files & Their Roles](#important-files--their-roles)
8. [Data Flow](#data-flow)
9. [Code Patterns & Conventions](#code-patterns--conventions)
10. [Known Issues & Quirks](#known-issues--quirks)
11. [Common Tasks](#common-tasks)
12. [Testing](#testing)
13. [Release & Distribution](#release--distribution)
14. [Troubleshooting](#troubleshooting)

---

## 📖 Project Overview

**NGIO Automation Suite** is a Python-based automation tool that transforms the painful 4+ hour manual process of generating grass cache files for Skyrim SE/AE/VR into a 5-minute setup that runs completely unattended.

### Core Functionality:

- **Automated Grass Cache Generation**: Handles the complete workflow of generating NGIO (No Grass In Objects) cache files for all four seasons
- **Intelligent Process Management**: Automatically launches Skyrim, monitors progress, detects crashes, and handles recovery
- **Season-by-Season Generation**: Generates, processes, and archives each season individually to optimize disk space
- **High-Speed File Processing**: Multithreaded file operations (10-25x faster than batch scripts)
- **Crash Recovery**: Smart retry logic with adaptive timeouts for heavily modded setups
- **Archive Creation**: Generates ready-to-install mod archives for each season

### Problem It Solves:

**Traditional NGIO Process (Manual):**
- ⏱️ 4+ hours of manual work across 4 seasons
- 🔄 Constant manual restarts when Skyrim crashes
- 📝 Manual config editing for each season
- 📁 Manual file renaming after each generation
- 🎮 Constant babysitting required

**With NGIO Automation Suite:**
- 🚀 5 minutes setup, walk away
- 🤖 Fully automated crash recovery
- ⚡ Intelligent process management
- 📦 Per-season archive creation
- 🛌 Run before bed, wake up completed

### User Flow:

1. User runs the automation suite (`ngio_automation_runner.py`)
2. Provides Skyrim path and selects ONE season to generate
3. Suite backs up configuration files
4. Suite modifies seasonal settings in `po3_SeasonsOfSkyrim.ini`
5. Launches Skyrim via SKSE for grass generation
6. Monitors `PrecacheGrass.txt` file for progress
7. Handles crashes/hangs with intelligent retry logic
8. Processes and renames `.cgid` files with seasonal extensions
9. Creates mod archive for the season
10. Cleans up seasonal files to save disk space
11. Restores original configurations
12. User runs again for other seasons as needed

---

## 🏗️ Architecture

### High-Level Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│              NGIO Automation Suite (Python)                  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         ngio_automation_runner.py (Entry Point)        │ │
│  │  • User Interface (CLI Menu)                           │ │
│  │  • Configuration Collection                            │ │
│  │  • ConfigCache Management                              │ │
│  └──────────────────┬─────────────────────────────────────┘ │
│                     │                                         │
│  ┌──────────────────▼─────────────────────────────────────┐ │
│  │         NGIOAutomationSuite (Orchestrator)             │ │
│  │  • Workflow coordination                               │ │
│  │  • Season-by-season processing                         │ │
│  │  • Error handling & recovery                           │ │
│  └─────────┬──────────┬──────────┬──────────┬─────────────┘ │
│            │          │          │          │                │
│  ┌─────────▼──┐  ┌───▼────┐  ┌──▼───────┐  ┌▼──────────┐   │
│  │   Game     │  │Config  │  │   File   │  │ Archive   │   │
│  │  Manager   │  │Manager │  │Processor │  │ Creator   │   │
│  │            │  │        │  │          │  │           │   │
│  │ • Launch   │  │ • INI  │  │ • Multi- │  │ • ZIP     │   │
│  │   Skyrim   │  │   Edit │  │   thread │  │   Create  │   │
│  │ • Monitor  │  │ • Backup│  │ • Rename │  │ • Meta    │   │
│  │ • Detect   │  │ • Season│  │ • Verify │  │ • FOMOD   │   │
│  │   Crash    │  │   Switch│  │          │  │           │   │
│  └────────────┘  └────────┘  └──────────┘  └───────────┘   │
│                                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌─────▼──────┐   ┌──▼──────────┐
   │ Skyrim  │    │   SKSE64   │   │Config Files │
   │   SE    │    │   Loader   │   │  (.ini)     │
   │         │    │            │   │             │
   └─────────┘    └────────────┘   └─────────────┘
```

### Key Components:

1. **ngio_automation_runner.py** (Entry Point)
   - User-facing CLI menu system
   - Configuration collection and validation
   - Orchestrates the automation suite
   - Signal handling for graceful shutdown

2. **NGIOAutomationSuite** (Core Orchestrator)
   - Master controller for the entire workflow
   - Season-by-season generation loop
   - Coordination between managers
   - Error handling and recovery
   - Progress reporting

3. **GameManager** (Process Management)
   - Launches Skyrim via SKSE64
   - Monitors process health
   - Detects crashes and hangs
   - Manages `PrecacheGrass.txt` lifecycle
   - Prevents "death loops" with multiple instances

4. **ConfigManager** (Configuration Management)
   - Backs up original `.ini` files
   - Modifies season settings (1→2→3→4→5)
   - Preserves INI formatting and comments
   - Restores configurations after completion

5. **FileProcessor** (High-Speed Operations)
   - Multithreaded file renaming (16 workers)
   - Renames `.cgid` → `.WIN.cgid`, `.SPR.cgid`, etc.
   - 10-25x faster than batch scripts
   - File integrity validation

6. **ArchiveCreator** (Mod Packaging)
   - Creates installable ZIP archives
   - Proper Data/Grass folder structure
   - Includes README, meta.ini, FOMOD installer
   - Per-season archives to save disk space

7. **Supporting Utilities**
   - **Logger**: Colorized console output with emoji indicators
   - **ConfigCache**: Persistent user settings storage
   - **SkyrimDetector**: Auto-detect Skyrim installation paths

---

## 🛠️ Technology Stack

### Core Language & Runtime

- **Python**: 3.8+ (tested up to 3.12)
- **Platform**: Windows 10/11 (required for Skyrim)

### Core Dependencies

- **psutil** (>=5.8.0): Process management, system monitoring
- **colorama** (>=0.4.4): Cross-platform colored terminal output  
- **colorlog** (>=6.7.0): Colored logging with emoji support

### Standard Library (Heavily Used)

- **subprocess**: Process launching and management
- **configparser**: INI file parsing and modification
- **concurrent.futures**: Multithreaded file operations
- **pathlib**: Modern path handling
- **zipfile**: Archive creation
- **json**: Configuration persistence

### Build & Distribution

- **setuptools**: Package building
- **build**: Modern build backend
- **wheel**: Distribution format
- **pyproject.toml**: Modern Python project configuration

### External Dependencies (Runtime)

- **Skyrim SE/AE/VR**: Target game
- **SKSE64**: Script Extender (required for NGIO)
- **NGIO Plugin**: Grass cache generation plugin
- **Seasons of Skyrim**: Seasonal mod (optional, for seasonal mode)

---

## 📁 Project Structure

```
NGIO_AutomationSuite/
│
├── src/                              # Source code root
│   ├── __version__.py               # Single source of truth for version
│   │
│   ├── core/                        # Core automation components
│   │   ├── automation_suite.py     # Master orchestrator (NGIOAutomationSuite)
│   │   ├── game_manager.py         # Skyrim process management
│   │   ├── config_manager.py       # INI file manipulation
│   │   ├── file_processor.py       # Multithreaded file operations
│   │   ├── progress_monitor.py     # Progress tracking & reporting
│   │   └── archive_creator.py      # Mod archive generation
│   │
│   └── utils/                       # Utility modules
│       ├── logger.py                # Colorized logging system
│       ├── config_cache.py          # Persistent user settings
│       └── skyrim_detector.py       # Auto-detect Skyrim paths
│
├── docs/                            # Documentation
│   ├── LARGE_LOAD_ORDER_GUIDE.md   # Configuration for 500+ mods
│   ├── SEASON_SELECTION_GUIDE.md   # Per-season generation workflow
│   ├── DETECTION_MECHANISMS.md     # How crash/hang detection works
│   ├── VERSION_MANAGEMENT.md       # Version numbering strategy
│   ├── NEXUS_DOCUMENTATION.txt     # User-facing documentation
│   ├── NEXUS_DESCRIPTION_BBCODE.txt # Nexus mod page description
│   └── V1.1.0_RELEASE_NOTES.md     # Release history
│
├── ngio_automation_runner.py        # Main entry point (CLI)
├── build_release.py                 # Release build system
│
├── pyproject.toml                   # Project metadata & build config
├── setup.py                         # Backward-compatible setup
├── requirements.txt                 # Python dependencies
├── MANIFEST.in                      # Package file inclusion rules
│
├── run_ngio_automation.bat          # Windows launcher script
├── build.bat                        # Build automation script
│
├── dist/                            # Built distributions (wheels, tarballs)
├── release/                         # Release packages
│   ├── ngio-automation-suite-X.X.X-bundled.zip  # Bundled with Python
│   └── release_info.json           # Release metadata
│
├── README.md                        # Project overview
├── LICENSE                          # MIT License
├── DEVELOPER_SETUP.md               # Developer onboarding
└── WARP.md                          # Project context summary
```

### Key Directory Purposes:

- **src/core/**: Business logic for automation workflow
- **src/utils/**: Reusable utilities and helpers
- **docs/**: User guides and technical documentation
- **dist/**: Python packages (wheel, source distribution)
- **release/**: End-user distribution files (bundled with Python)

---

## 🛠️ Development Setup

### Prerequisites

1. **Python 3.8+** installed and in PATH
2. **Windows 10/11** (required for Skyrim)
3. **Git** for version control
4. **Skyrim SE/AE/VR** with NGIO mod (for testing)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ngio-automation-suite.git
cd ngio-automation-suite

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running from Source

```bash
# Activate virtual environment
venv\Scripts\activate

# Run the automation suite
python ngio_automation_runner.py

# Or use the batch file
run_ngio_automation.bat
```

### Building for Distribution

```bash
# Install build tools
pip install build wheel setuptools

# Build Python packages (wheel + source)
python -m build

# Build bundled release (includes Python)
python build_release.py
```

### Project Configuration Files

**pyproject.toml**: Modern Python project config
- Package metadata
- Build system configuration
- Tool settings (black, mypy)

**setup.py**: Backward compatibility
- Fallback for older build systems
- Entry point definitions
- Package discovery

**requirements.txt**: Runtime dependencies
- Minimal dependencies for core functionality
- Development dependencies commented out

**MANIFEST.in**: Package inclusion rules
- Ensures docs/, LICENSE, README are included
- Required for source distributions

---

## 🔑 Key Concepts

### 1. Season-by-Season Workflow (v1.1.0+)

**Design Decision**: Generate, archive, and clean up ONE season at a time instead of all seasons simultaneously.

**Rationale**:
- **Disk Space**: 4 seasons of grass cache can exceed 50GB
- **User Flexibility**: Users may only want specific seasons
- **Failure Isolation**: If one season fails, others aren't affected
- **Progress Preservation**: Completed seasons are safe even if later ones fail

**Workflow**:
```
For each selected season:
  1. Configure season (modify INI)
  2. Launch Skyrim → Generate cache
  3. Process files (rename with season extension)
  4. Create archive (ZIP)
  5. Clean up files (free disk space)
  6. Move to next season
```

### 2. Crash Detection & Recovery

**Three Types of Failures**:

1. **Process Crash**: Skyrim exits unexpectedly
   - Detected by: Process no longer exists
   - Recovery: Wait → Relaunch Skyrim

2. **Process Hang**: Skyrim running but frozen
   - Detected by: No CPU activity for extended period
   - Recovery: Force terminate → Relaunch

3. **Generation Stall**: Skyrim running but no file activity
   - Detected by: `PrecacheGrass.txt` not growing
   - Recovery: Terminate → Relaunch (preserves progress)

**Intelligent Retry Logic**:
- **Adaptive Timeouts**: Learns from startup times (v1.1.0+)
- **Escalating Wait Times**: 30s → 60s → 90s → 120s between retries
- **Death Loop Prevention**: Checks if Skyrim already running before launch
- **Worldspace Awareness**: More retries for complex areas (Tamriel)

### 3. PrecacheGrass.txt Lifecycle

**Purpose**: Communication file between NGIO plugin and automation suite

**States**:
1. **Doesn't exist**: No generation active
2. **Empty file**: Generation trigger (created by automation)
3. **Contains cells**: Generation in progress (written by NGIO)
4. **Deleted by plugin**: Generation completed successfully
5. **Deleted by automation**: Cleanup after interruption

**Monitoring Logic**:
```python
if file_exists and growing:
    # Generation active, keep monitoring
elif file_exists and not_growing_for_15min:
    # Skyrim hung, restart
elif not_exists and cgid_files_exist:
    # Plugin deleted it = Success!
elif not_exists and no_cgid_files:
    # First generation, create trigger
```

### 4. File Processing Pipeline

**Input**: `.cgid` files (generic grass cache)
**Output**: `.WIN.cgid`, `.SPR.cgid`, `.SUM.cgid`, `.AUT.cgid` (seasonal)

**Multithreaded Approach**:
```python
# Find all .cgid files
cgid_files = find_all_cgid_files(grass_dir)  # ~10,000+ files

# Create rename operations
operations = [
    FileOperation("file1.cgid" → "file1.WIN.cgid"),
    FileOperation("file2.cgid" → "file2.WIN.cgid"),
    # ... 10,000+ operations
]

# Execute with ThreadPoolExecutor (16 workers)
with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(rename, op) for op in operations]
    # Processes 10,000 files in ~2-5 seconds vs 60-120s for batch
```

**Performance**: 10-25x faster than sequential batch scripts

### 5. Configuration Management

**Files Modified**:
- `Data/SKSE/Plugins/po3_SeasonsOfSkyrim.ini` (season type)
- `Data/SKSE/Plugins/GrassControl.ini` (NGIO settings)

**Season Type Values**:
- `0` = No Seasons (non-seasonal mode)
- `1` = Winter
- `2` = Spring  
- `3` = Summer
- `4` = Autumn
- `5` = Seasonal (automatic season switching)

**Preservation Approach**:
- Backup entire files before any changes
- Use line-by-line editing to preserve formatting
- Keep comments and empty lines intact
- Restore to seasonal mode (type 5) after completion

### 6. Archive Structure

**Per-Season Mod Archive**:
```
Grass_Cache_Winter_Season.zip
├── Data/
│   └── Grass/
│       ├── file1.WIN.cgid
│       ├── file2.WIN.cgid
│       └── ... (thousands of files)
├── README.txt           # Installation instructions
├── meta.ini            # MO2 metadata
└── fomod/              # FOMOD installer
    ├── ModuleConfig.xml
    └── info.xml
```

**Installation**: Drop into Mod Organizer 2 or Vortex as a regular mod

---

## 📄 Important Files & Their Roles

### Core Application Files

#### `ngio_automation_runner.py`
**Purpose**: Main entry point and user interface  
**Key Responsibilities**:
- CLI menu system
- User configuration collection via `ConfigCache`
- Workflow initiation
- Signal handling (Ctrl+C, termination)
- Emergency shutdown with progress preservation

**Key Functions**:
- `main()`: Application loop
- `handle_grass_generation()`: Starts automation workflow
- `handle_configuration()`: Collects paths from user
- `emergency_shutdown()`: Graceful cleanup on interruption

#### `src/core/automation_suite.py`
**Purpose**: Master orchestrator  
**Key Class**: `NGIOAutomationSuite`  
**Responsibilities**:
- Phase-based workflow execution
- Season iteration loop (v1.1.0+: one season at a time)
- Component coordination (GameManager, ConfigManager, etc.)
- Error handling and recovery
- Progress reporting

**Key Methods**:
- `run_full_automation()`: Main workflow entry point
- `_generate_season_cache()`: Per-season generation
- `_run_generation_with_monitoring()`: Crash recovery loop
- `_create_single_season_archive()`: Archive creation (v1.1.0+)
- `_cleanup_season_files()`: Disk space management (v1.1.0+)

**Season Enum**:
```python
class Season(Enum):
    WINTER = (1, "Winter", ".WIN.cgid")
    SPRING = (2, "Spring", ".SPR.cgid")
    SUMMER = (3, "Summer", ".SUM.cgid")
    AUTUMN = (4, "Autumn", ".AUT.cgid")
    NO_SEASONS = (0, "No Seasons", ".cgid")
```

#### `src/core/game_manager.py`
**Purpose**: Skyrim process lifecycle management  
**Key Class**: `GameManager`  
**Responsibilities**:
- Launch Skyrim via SKSE64 loader
- Monitor process health (CPU, memory)
- Detect crashes and hangs
- Manage `PrecacheGrass.txt` trigger file
- Prevent multiple instances (death loop prevention)
- Track startup times for adaptive timeouts (v1.1.0+)

**Critical Methods**:
- `launch_for_generation()`: Launch Skyrim with generation trigger
- `wait_for_precache_completion()`: Monitor generation progress
- `detect_crash()`: Check if process terminated
- `detect_hang()`: Check if process frozen
- `force_terminate()`: Kill Skyrim processes
- `is_skyrim_already_running()`: Prevent multiple instances (v1.1.0+)
- `wait_for_skyrim_to_close()`: Death loop prevention (v1.1.0+)

**Death Loop Prevention** (v1.1.0+):
```python
# Before launching, check if already running
existing = self.is_skyrim_already_running()
if existing:
    self.logger.warning("Skyrim already running!")
    self.wait_for_skyrim_to_close(timeout_seconds=120)
    time.sleep(5)  # Cooldown period
```

#### `src/core/config_manager.py`
**Purpose**: INI file manipulation  
**Key Class**: `ConfigManager`  
**Responsibilities**:
- Backup `.ini` files before changes
- Modify season settings
- Preserve INI formatting (comments, spacing, case)
- Restore original configurations
- BOM (Byte Order Mark) handling

**INI Editing Approach**:
```python
# Line-by-line editing preserves formatting
def _modify_ini_value(file_path, section, key, new_value):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find target line and replace only value part
    for i, line in enumerate(lines):
        if key_matches(line, key):
            lines[i] = preserve_format(line, new_value)
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
```

**Why Not ConfigParser?**:
- ConfigParser doesn't preserve comments
- Doesn't preserve key case (normalizes to lowercase)
- Doesn't preserve spacing/formatting
- Manual line editing maintains exact original format

#### `src/core/file_processor.py`
**Purpose**: High-speed file operations  
**Key Class**: `FileProcessor`  
**Responsibilities**:
- Multithreaded file renaming (16 workers)
- File integrity validation
- Progress tracking
- Error handling per file

**Performance Architecture**:
```python
class FileProcessor:
    max_workers = 16  # Optimal for most systems
    
    def process_season_files(files, season):
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = {executor.submit(rename, f): f for f in files}
            for future in as_completed(futures):
                # Track progress as each completes
```

**Benchmark**: Processes 10,000 files in 2-5 seconds (vs 60-120s for batch)

#### `src/core/archive_creator.py`
**Purpose**: Mod archive generation  
**Key Class**: `ArchiveCreator`  
**Responsibilities**:
- Create ZIP archives per season (v1.1.0+)
- Generate mod metadata (README, meta.ini)
- Create FOMOD installer configuration
- Validate archive integrity

**Per-Season Archives** (v1.1.0+):
```python
# Old: Create all archives at end
create_all_season_archives()  # 4 seasons × 10GB+ = 40GB+ disk

# New: Create archive after each season
for season in seasons:
    generate(season)
    create_archive(season)   # ~10GB archive
    cleanup_files(season)    # Free 10GB disk space
    # Next season now has 10GB available
```

### Utility Files

#### `src/utils/logger.py`
**Purpose**: Colorized logging with emoji indicators  
**Features**:
- Colored output (error=red, success=green, etc.)
- Emoji indicators (🌱, ✅, ❌, ⚠️, 💥)
- Progress bars
- Separators for visual organization

**Usage**:
```python
logger = Logger("ComponentName")
logger.info("ℹ️ Information message")
logger.success("✅ Success message")
logger.warning("⚠️ Warning message")
logger.error("❌ Error message")
logger.separator("Section Title")
```

#### `src/utils/config_cache.py`
**Purpose**: Persistent user settings  
**Storage**: JSON file in user's AppData  
**Contains**:
- Skyrim installation path
- Output directory
- Season preferences
- Timeout configurations
- Last used settings

**Lifecycle**:
```python
cache = ConfigCache()
cache.load_config()           # Load from disk
cache.collect_user_paths()    # Interactive prompts
cache.save_config()           # Persist to disk
cache.validate_and_update_config()  # Ensure valid
```

#### `src/__version__.py`
**Purpose**: Single source of truth for version number  
**Used By**:
- `pyproject.toml`
- `setup.py`
- `build_release.py`
- `ngio_automation_runner.py` (banner)

**Format**:
```python
__version__ = "1.1.2"
__version_info__ = (1, 1, 2)
__title__ = "NGIO Automation Suite"
__description__ = "Automated grass cache generation for Skyrim SE"
__author__ = "Dudu"
__license__ = "MIT"
```

### Build & Distribution Files

#### `build_release.py`
**Purpose**: Automated release building  
**Creates**:
1. Python wheel (`dist/ngio_automation_suite-1.1.2-py3-none-any.whl`)
2. Source distribution (`dist/ngio_automation_suite-1.1.2.tar.gz`)
3. Bundled release with complete Python environment

**Bundled Release** (Most Important for Users):
```
ngio-automation-suite-1.1.2-bundled.zip
├── python/              # Complete Python installation
│   ├── python.exe
│   ├── Scripts/
│   └── Lib/
├── src/                # Source code
├── docs/               # Documentation
├── ngio_automation_runner.py
└── run_bundled.bat    # No Python installation required!
```

**Why Bundled?**:
- Most users don't have Python installed
- Eliminates "Python not found" errors
- Simplifies installation to "extract and run"
- Self-contained, no dependencies

#### `pyproject.toml`
**Purpose**: Modern Python project configuration (PEP 518)  
**Sections**:
- `[build-system]`: Build tool requirements
- `[project]`: Package metadata
- `[project.urls]`: Links (GitHub, Nexus, docs)
- `[project.scripts]`: Entry point definitions
- `[tool.*]`: Tool configurations (black, mypy)

#### `setup.py`
**Purpose**: Backward compatibility for older Python/pip  
**Relationship**: Reads from `pyproject.toml` and `__version__.py`  
**Still Needed**: Some environments don't support PEP 518 yet

### Documentation Files

#### `README.md`
**Purpose**: User-facing project overview  
**Audience**: End users and potential users  
**Contents**:
- What the tool does (problem/solution)
- Features and benefits
- Installation instructions (bundled vs source)
- Quick start guide
- Requirements
- Troubleshooting basics

#### `docs/LARGE_LOAD_ORDER_GUIDE.md`
**Purpose**: Configuration for heavily modded setups (500+ mods)  
**Key Topics**:
- Understanding startup time scaling
- Adaptive timeout configuration
- Death loop prevention
- Recommended settings by plugin count
- Real-world examples from users

**Critical for**: Users with 500-1000+ plugins where startup takes 5-10+ minutes

#### `docs/SEASON_SELECTION_GUIDE.md`
**Purpose**: Explains per-season workflow (v1.1.0+)  
**Key Topics**:
- Why one season at a time?
- Disk space management
- How to generate multiple seasons
- Archive installation per season

#### `docs/DETECTION_MECHANISMS.md`
**Purpose**: Technical details on crash/hang detection  
**Audience**: Developers and curious users  
**Contents**:
- How crash detection works
- How hang detection works
- PrecacheGrass.txt monitoring
- Process state analysis
- Timeout calculations

#### `docs/VERSION_MANAGEMENT.md`
**Purpose**: Version numbering and release strategy  
**Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)  
**Example**: `1.1.2`
  - Major: Breaking changes
  - Minor: New features (backward compatible)
  - Patch: Bug fixes

---

## 🔄 Data Flow

### Complete Generation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INITIATES GENERATION                 │
│         (Selects one season, provides Skyrim path)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 1: Setup & Validation                                  │
│  • Validate Skyrim path                                      │
│  • Check for Skyrim executable (SkyrimSE.exe)                │
│  • Verify SKSE64 (skse64_loader.exe)                         │
│  • Create output directory                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 2: Configuration Backup                                │
│  • Backup po3_SeasonsOfSkyrim.ini                            │
│  • Backup GrassControl.ini                                   │
│  • Store in timestamped backup directory                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 3: Season Generation (Per-Season Loop)                 │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ For selected season (e.g., Winter):                     │  │
│ │                                                          │  │
│ │ STEP 1: Configure Season                                │  │
│ │  • Modify po3_SeasonsOfSkyrim.ini                       │  │
│ │  • Set Season Type = 1 (Winter)                         │  │
│ │                                                          │  │
│ │ STEP 2: Launch & Monitor                                │  │
│ │  ┌─────────────────────────────────────────┐            │  │
│ │  │ Check if Skyrim already running         │            │  │
│ │  │  └─> Wait for it to close (120s)        │            │  │
│ │  │ Create PrecacheGrass.txt trigger file   │            │  │
│ │  │ Launch SKSE64 loader                    │            │  │
│ │  │  └─> SKSE spawns SkyrimSE.exe          │            │  │
│ │  │ Track startup time for adaptive timeout │            │  │
│ │  │                                         │            │  │
│ │  │ MONITORING LOOP (until completion):     │            │  │
│ │  │  • Check PrecacheGrass.txt exists       │            │  │
│ │  │  • Monitor file size growth             │            │  │
│ │  │  • Track last modified time             │            │  │
│ │  │  • Check process still running          │            │  │
│ │  │  • Monitor CPU activity                 │            │  │
│ │  │                                         │            │  │
│ │  │  IF file deleted by plugin:             │            │  │
│ │  │   └─> SUCCESS! Generation complete     │            │  │
│ │  │                                         │            │  │
│ │  │  IF no file growth for 15+ min:        │            │  │
│ │  │   └─> HANG DETECTED → Retry           │            │  │
│ │  │        ├─> Force terminate Skyrim      │            │  │
│ │  │        ├─> Wait (30s → 60s → 90s)     │            │  │
│ │  │        └─> Relaunch (preserve progress)│            │  │
│ │  │                                         │            │  │
│ │  │  IF process not running:                │            │  │
│ │  │   └─> CRASH DETECTED → Retry          │            │  │
│ │  │        ├─> Wait (escalating)           │            │  │
│ │  │        └─> Relaunch                    │            │  │
│ │  │                                         │            │  │
│ │  │  Max retries: 10 (15 for large setups) │            │  │
│ │  └─────────────────────────────────────────┘            │  │
│ │                                                          │  │
│ │ STEP 3: Process Files                                   │  │
│ │  • Find all .cgid files in Data/Grass/                 │  │
│ │  • Rename with season extension:                       │  │
│ │    file.cgid → file.WIN.cgid                           │  │
│ │  • Multithreaded (16 workers)                          │  │
│ │  • ~10,000 files processed in 2-5 seconds              │  │
│ │                                                          │  │
│ │ STEP 4: Create Archive                                  │  │
│ │  • Create temp directory                               │  │
│ │  • Build Data/Grass structure                          │  │
│ │  • Copy seasonal files                                 │  │
│ │  • Generate README.txt                                 │  │
│ │  • Generate meta.ini (MO2)                             │  │
│ │  • Generate FOMOD installer                            │  │
│ │  • Create ZIP: Grass_Cache_Winter_Season.zip          │  │
│ │  • Validate archive integrity                          │  │
│ │                                                          │  │
│ │ STEP 5: Cleanup Seasonal Files (v1.1.0+)               │  │
│ │  • Find all .WIN.cgid files                            │  │
│ │  • Delete seasonal files                               │  │
│ │  • Free ~10GB disk space                               │  │
│ │  • Preserves archives only                             │  │
│ │                                                          │  │
│ └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 4: Configuration Restoration                           │
│  • Set Season Type = 5 (Seasonal mode)                       │
│  • Restore original INI files from backup                    │
│  • Cleanup backup files (keep latest 3)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 5: Completion Report                                   │
│  • Display total time                                        │
│  • Show completed seasons                                    │
│  • Show failed seasons (if any)                              │
│  • Show archive locations                                    │
│  • Display next steps for user                               │
└──────────────────────────────────────────────────────────────┘
```

### File State Transitions

```
PrecacheGrass.txt Lifecycle:
┌─────────────────────────────────────────────────────────┐
│ [Not Exists] ──create trigger──> [Empty File]           │
│      │                                 │                 │
│      │                                 │                 │
│      │                          NGIO writes cells        │
│      │                                 │                 │
│      │                                 ▼                 │
│      │                        [File with Content]        │
│      │                          (contains cells)         │
│      │                                 │                 │
│      │                                 │                 │
│      │                          More cells written        │
│      │                                 │                 │
│      │                                 ▼                 │
│      │                        [Growing File]             │
│      │                     (monitoring sees growth)      │
│      │                                 │                 │
│      │                                 │                 │
│      │                    ┌────────────┼────────────┐    │
│      │                    │            │            │    │
│      │              Generation    Generation    Generation│
│      │              completes     hangs         crashes   │
│      │                    │            │            │    │
│      ▼                    ▼            ▼            ▼    │
│ [Not Exists]      [Not Exists]  [Stale File]  [Stale File]
│  (normal)          (success)      (retry)       (retry)   │
└─────────────────────────────────────────────────────────┘

.cgid File Lifecycle (Per Season):
┌─────────────────────────────────────────────────────────┐
│ [Generation]                                             │
│   NGIO creates: tamriel.cgid, solstheim.cgid, etc.      │
│                                 │                         │
│                                 ▼                         │
│ [Processing]                                             │
│   Automation renames:                                    │
│     tamriel.cgid → tamriel.WIN.cgid                      │
│     solstheim.cgid → solstheim.WIN.cgid                  │
│                                 │                         │
│                                 ▼                         │
│ [Archiving]                                              │
│   Files copied to archive structure:                     │
│     Grass_Cache_Winter_Season.zip/Data/Grass/            │
│                                 │                         │
│                                 ▼                         │
│ [Cleanup] (v1.1.0+)                                      │
│   Original .WIN.cgid files deleted                       │
│   Archive preserved                                      │
│   Disk space freed for next season                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Code Patterns & Conventions

### 1. Logging Conventions

**Emoji Indicators**:
- 🌱 = Grass/NGIO related
- ✅ = Success
- ❌ = Error/Failure
- ⚠️ = Warning
- 💥 = Crash/Exception
- 📁 = File operation
- 📦 = Archive/Package
- ⚡ = Performance/Speed
- 🔄 = Retry/Loop
- ⏱️ = Time/Duration
- 🎮 = Skyrim/Game
- 🔧 = Configuration
- 💾 = Save/Backup
- 🗑️ = Delete/Cleanup
- 🔍 = Detection/Search
- 📊 = Statistics/Progress

**Color Coding**:
```python
logger.info()     # Blue - informational
logger.success()  # Green - positive outcomes
logger.warning()  # Yellow - caution
logger.error()    # Red - errors
logger.debug()    # Cyan - debugging info
```

### 2. Error Handling Pattern

```python
def some_operation():
    try:
        # Main operation
        result = perform_work()
        logger.success("✅ Operation completed successfully")
        return result
        
    except FileNotFoundError:
        logger.error("❌ Required file not found")
        return None
        
    except PermissionError:
        logger.error("❌ Permission denied - try running as Administrator")
        return None
        
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return None
```

**Pattern**: Specific exceptions first, generic Exception last

### 3. Configuration Pattern

```python
@dataclass
class SomeConfig:
    """Configuration with sensible defaults"""
    required_param: str
    optional_param: int = 10
    flag: bool = True
    
    def __post_init__(self):
        """Validation after initialization"""
        if not self.required_param:
            raise ValueError("required_param cannot be empty")
```

**Pattern**: Use dataclasses for configuration objects

### 4. Process Management Pattern

```python
def manage_process():
    process = None
    try:
        process = launch_process()
        result = monitor_process(process)
        return result
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Process interrupted by user")
        cleanup_process(process)
        return False
        
    finally:
        if process:
            ensure_terminated(process)
```

**Pattern**: Always clean up processes in finally block

### 5. File Operations Pattern

```python
def safe_file_operation(file_path: str):
    """Perform file operation with proper error handling"""
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False
    
    try:
        # File operation
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process content
        result = process(content)
        
        # Write result
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return True
        
    except PermissionError:
        logger.error(f"❌ Permission denied: {file_path}")
        return False
        
    except Exception as e:
        logger.error(f"💥 File operation failed: {e}")
        return False
```

**Pattern**: Check existence, use context managers, handle encoding

### 6. Retry Logic Pattern

```python
def operation_with_retry(max_retries: int = 5):
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = attempt_operation()
            if result:
                logger.success(f"✅ Succeeded on attempt {retry_count + 1}")
                return result
                
        except Exception as e:
            logger.warning(f"⚠️ Attempt {retry_count + 1} failed: {e}")
        
        retry_count += 1
        
        if retry_count < max_retries:
            wait_time = calculate_wait_time(retry_count)
            logger.info(f"🔄 Retry in {wait_time}s ({max_retries - retry_count} attempts remaining)")
            time.sleep(wait_time)
    
    logger.error(f"❌ All {max_retries} attempts failed")
    return None
```

**Pattern**: Escalating wait times, clear progress reporting

### 7. Progress Reporting Pattern

```python
def process_large_batch(items: List):
    total = len(items)
    processed = 0
    
    for item in items:
        process(item)
        processed += 1
        
        # Report every 10%
        if processed % max(1, total // 10) == 0:
            percentage = (processed / total) * 100
            logger.info(f"📊 Progress: {processed}/{total} ({percentage:.1f}%)")
    
    logger.success(f"✅ Processed all {total} items")
```

**Pattern**: Report at meaningful intervals (every 10%)

### 8. Resource Cleanup Pattern

```python
class ResourceManager:
    def __init__(self):
        self.resources = []
    
    def acquire_resource(self, resource):
        self.resources.append(resource)
        return resource
    
    def cleanup(self):
        """Cleanup all acquired resources"""
        for resource in self.resources:
            try:
                resource.close()
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup resource: {e}")
        
        self.resources.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

**Pattern**: Context manager for automatic cleanup

### 9. Validation Pattern

```python
def validate_configuration(config: AutomationConfig) -> Tuple[bool, List[str]]:
    """Validate configuration and return issues"""
    issues = []
    
    # Check required fields
    if not config.skyrim_path:
        issues.append("Skyrim path not provided")
    
    if not os.path.exists(config.skyrim_path):
        issues.append(f"Skyrim path does not exist: {config.skyrim_path}")
    
    # Check file existence
    skyrim_exe = os.path.join(config.skyrim_path, "SkyrimSE.exe")
    if not os.path.exists(skyrim_exe):
        issues.append("SkyrimSE.exe not found")
    
    # Validate numeric ranges
    if config.max_crash_retries < 1:
        issues.append("max_crash_retries must be at least 1")
    
    success = len(issues) == 0
    
    if success:
        logger.success("✅ Configuration valid")
    else:
        logger.error(f"❌ Found {len(issues)} configuration issues")
        for issue in issues:
            logger.error(f"   • {issue}")
    
    return success, issues
```

**Pattern**: Collect all issues before returning, detailed reporting

### 10. Naming Conventions

**Variables**:
- `snake_case` for variables and functions
- `SCREAMING_SNAKE_CASE` for constants
- Descriptive names (no single letters except loop indices)

**Classes**:
- `PascalCase` for class names
- Manager/Handler/Creator/Processor suffixes

**Files**:
- `snake_case.py` for modules
- Match primary class name: `game_manager.py` → `GameManager`

**Methods**:
- Public methods: `method_name()`
- Private methods: `_method_name()` (single underscore)
- Internal helpers: `__method_name()` (double underscore, rare)

---

## ⚠️ Known Issues & Quirks

### 1. Death Loop with Large Load Orders

**Issue**: On systems with 500+ mods, Skyrim startup can take 5-10 minutes. If `no_progress_timeout_minutes` is too aggressive, the suite may kill Skyrim before it finishes loading, then immediately relaunch it. The previous instance continues loading in the background, leading to multiple Skyrim processes and guaranteed crashes.

**Mitigation** (v1.1.0+):
- Already-running detection before launch
- Escalating wait times between retries (30s → 60s → 90s → 120s)
- Adaptive timeout learning from actual startup times
- Increased default timeout (10 → 15 minutes)

**User Action Required**:
- For 500+ mods: Increase `no_progress_timeout_minutes` to 20-25
- For 1000+ mods: Increase to 30+ minutes
- See `docs/LARGE_LOAD_ORDER_GUIDE.md`

### 2. Antivirus False Positives

**Issue**: Antivirus software may flag the tool as malicious due to:
- Process monitoring (psutil)
- Launching external processes (Skyrim)
- Rapid file operations (thousands of renames)
- Keyboard hooks (future feature)

**Mitigation**:
- Open source code available for inspection
- Minimal dependencies (only psutil, colorama, colorlog)
- No obfuscation or packing
- Clear documentation of behavior

**User Action Required**:
- Add tool directory to antivirus exclusions
- Use Windows Defender (fewer false positives than third-party)
- Download only from official sources (GitHub, Nexus)

### 3. SKSE Loader vs Direct Executable

**Issue**: The tool prioritizes SKSE loaders (`skse64_loader.exe`) over direct executables (`SkyrimSE.exe`). SKSE loader launches then terminates, spawning the actual Skyrim process. This complicates process tracking.

**Behavior**:
```python
# Launch skse64_loader.exe (PID 1000)
process = subprocess.Popen(["skse64_loader.exe"])

# Loader exits quickly (PID 1000 terminates)
# But spawns SkyrimSE.exe (PID 2000)

# Must find the spawned process
skyrim_process = find_skyrim_process()  # Find PID 2000
```

**Mitigation**:
- Special handling in `launch_for_generation()`
- Searches for spawned Skyrim process
- Fallback to direct launch if SKSE not found

**User Action Required**:
- Install SKSE64 for full NGIO functionality
- Tool warns if SKSE not found

### 4. INI File Encoding Issues

**Issue**: Some text editors save INI files with BOM (Byte Order Mark), which breaks Python's `configparser`. Additionally, ConfigParser doesn't preserve comments, formatting, or key case.

**Mitigation**:
- Custom `_read_config_with_bom_handling()` method
- Line-by-line editing instead of ConfigParser for modifications
- Tries multiple encodings (utf-8-sig, utf-8, utf-16, cp1252)
- Preserves exact formatting, comments, and case

**User Action Required**: None (handled automatically)

### 5. PrecacheGrass.txt Ambiguity

**Issue**: When `PrecacheGrass.txt` is deleted, it's unclear who deleted it:
- NGIO plugin deletes it on successful completion
- Automation suite might delete it during cleanup
- User might manually delete it

This creates ambiguity in determining success vs failure.

**Mitigation** (v1.1.0+):
- Track `_we_deleted_precache_file` flag
- Check for `.cgid` files to confirm completion
- Progress lock file (`.ngio_generation_active`) prevents accidental cleanup

**Determination Logic**:
```python
if not file_exists:
    if we_deleted_it:
        return False  # We cleaned up, not completion
    elif cgid_files_exist:
        return True   # Plugin deleted it, success!
    else:
        return False  # First generation
```

### 6. Worldspace-Specific Crash Rates

**Issue**: Tamriel (main worldspace) crashes significantly more than other worldspaces due to:
- Complexity (thousands of cells)
- Mod conflicts more likely
- Memory pressure
- Script-heavy areas

**Behavior**: Spring (Tamriel) might crash 8 times, while Summer (Solstheim) completes on first try.

**Mitigation**:
- Higher default `max_crash_retries` (10, up to 20 for large setups)
- Progress preservation through retries
- Per-worldspace crash tracking (informational only)

**User Action Required**:
- Expect Tamriel to take longest
- Don't panic at multiple crashes
- Increase retries if needed

### 7. Disk Space Requirements

**Issue**: Full 4-season grass cache can exceed 50GB:
- Each season: 10,000+ files, 10-15GB
- Total: 40-60GB
- Archives: 10-15GB each

**Mitigation** (v1.1.0+):
- Per-season workflow: Generate → Archive → Cleanup
- Cleanup deletes source files after archiving
- Only archives are kept (~10-15GB per season vs ~50GB for all files)

**User Action Required**:
- Ensure 20GB free space (one season + archive)
- Archives can be deleted after installation if needed

### 8. Windows Path Length Limit

**Issue**: Windows has a 260-character path limit. With nested mod structures and long worldspace names, paths can exceed this.

**Example**:
```
C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition\
Data\Grass\TamrielWorld_123456789_012345_SomeVeryLongCellName.WIN.cgid
```

**Mitigation**:
- Most paths stay under limit with reasonable install locations
- Python 3.6+ handles long paths better
- Use shorter output directory paths

**User Action Required**:
- Install Skyrim to shorter path if issues occur
- Enable long path support in Windows 10/11:
  ```
  Computer Configuration > Administrative Templates > 
  System > Filesystem > Enable Win32 long paths
  ```

### 9. Multiple Mod Manager Profiles

**Issue**: Mod Organizer 2 users may have multiple profiles with different season settings. The automation modifies the base INI files, which affects ALL profiles.

**Behavior**:
- Changes apply to all MO2 profiles
- Per-profile overrides may conflict

**Mitigation**:
- Backup and restore ensures no permanent changes
- User should disable profile-specific overrides during generation

**User Action Required**:
- Use the same MO2 profile for generation and normal gameplay
- Or regenerate cache after switching profiles with different mods

### 10. Race Condition on Startup

**Issue**: Rare race condition where:
1. Suite checks if Skyrim is running → Not running
2. Previous instance starts loading (slow startup)
3. Suite launches new instance
4. Two instances running → crash

**Mitigation** (v1.1.0+):
- Double-check with cooldown period
- Wait times between retries prevent this
- Process name checking (not just PID)

**User Action Required**: None (v1.1.0+ handles this)

---

## 🛠️ Common Tasks

### Task 1: Add New Season Type

**Files to Modify**:
1. `src/core/automation_suite.py` - Add to `Season` enum
2. Update documentation

**Example**: Adding "Fall" as alternative to "Autumn"

```python
# src/core/automation_suite.py
class Season(Enum):
    WINTER = (1, "Winter", ".WIN.cgid")
    SPRING = (2, "Spring", ".SPR.cgid")
    SUMMER = (3, "Summer", ".SUM.cgid")
    AUTUMN = (4, "Autumn", ".AUT.cgid")
    FALL = (4, "Fall", ".AUT.cgid")  # Same as Autumn
    NO_SEASONS = (0, "No Seasons", ".cgid")
```

### Task 2: Adjust Default Timeouts

**Files to Modify**:
1. `src/core/automation_suite.py` - `AutomationConfig` dataclass

```python
@dataclass
class AutomationConfig:
    # ...
    max_crash_retries: int = 15  # Change from 10 to 15
    no_progress_timeout_minutes: int = 20  # Change from 15 to 20
    startup_wait_seconds: int = 45  # Change from 30 to 45
```

### Task 3: Add New Skyrim Executable Support

**Files to Modify**:
1. `src/core/game_manager.py` - Update executable lists

**Example**: Adding GOG version

```python
def _find_skyrim_executable(self) -> Optional[str]:
    # SKSE loaders (preferred)
    skse_loaders = [
        "skse64_loader.exe",
        "sksevr_loader.exe",
        "skse_loader.exe"
    ]
    
    # Direct executables
    direct_executables = [
        "SkyrimSE.exe",
        "SkyrimAE.exe",
        "SkyrimVR.exe",
        "Skyrim.exe",
        "SkyrimSE_GOG.exe"  # Add GOG version
    ]
```

### Task 4: Change Worker Thread Count

**Files to Modify**:
1. `src/core/file_processor.py` - `FileProcessor.__init__()`

```python
class FileProcessor:
    def __init__(self, max_workers: int = None):
        if max_workers is None:
            # Change formula: CPU cores * 2 → CPU cores * 4
            max_workers = min(32, (os.cpu_count() or 4) * 4)
        
        self.max_workers = max_workers
```

**Considerations**:
- More workers = faster but more CPU/memory
- 16 is optimal for most systems
- Diminishing returns beyond 32

### Task 5: Add Custom Logging Level

**Files to Modify**:
1. `src/utils/logger.py` - Add new level

```python
class Logger:
    def critical(self, message: str):
        """Critical error that requires immediate attention"""
        self.logger.critical(f"🚨 {message}")
```

### Task 6: Modify Archive Structure

**Files to Modify**:
1. `src/core/archive_creator.py` - `_create_mod_structure()`

**Example**: Adding a "Scripts" folder

```python
def _create_mod_structure(self, temp_dir: str, season, seasonal_files: List[str]):
    mod_root = os.path.join(temp_dir, f"Grass_Cache_{season.display_name}")
    data_dir = os.path.join(mod_root, "Data")
    grass_dir = os.path.join(data_dir, "Grass")
    scripts_dir = os.path.join(data_dir, "Scripts")  # New
    
    os.makedirs(grass_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)  # New
    
    # Copy files...
```

### Task 7: Change Version Number

**Files to Modify** (in order):
1. `src/__version__.py` - **ONLY FILE TO EDIT**
   ```python
   __version__ = "1.1.3"  # Change here
   ```

2. All other files read from `__version__.py`:
   - `pyproject.toml` (reads automatically)
   - `setup.py` (reads automatically)
   - `build_release.py` (imports)
   - `ngio_automation_runner.py` (imports)

**Never manually edit** version in multiple places!

### Task 8: Add New Configuration Parameter

**Files to Modify**:
1. `src/core/automation_suite.py` - `AutomationConfig` dataclass
2. `src/utils/config_cache.py` - Prompt user for new parameter
3. `ngio_automation_runner.py` - Pass parameter to config

**Example**: Adding "verbose_logging"

```python
# 1. src/core/automation_suite.py
@dataclass
class AutomationConfig:
    # ... existing params ...
    verbose_logging: bool = False  # Add new parameter

# 2. src/utils/config_cache.py
def collect_user_preferences(self):
    # ... existing prompts ...
    verbose = input("Enable verbose logging? (y/n): ").strip().lower()
    self.preferences.verbose_logging = (verbose == 'y')

# 3. ngio_automation_runner.py
automation_config = AutomationConfig(
    skyrim_path=paths.skyrim_path,
    # ... existing params ...
    verbose_logging=preferences.verbose_logging  # Pass new param
)
```

### Task 9: Customize FOMOD Installer

**Files to Modify**:
1. `src/core/archive_creator.py` - `_generate_fomod_config()`

**Example**: Adding option for different grass density

```xml
<group name="Grass Density" type="SelectExactlyOne">
    <plugins>
        <plugin name="Normal Density">
            <description>Standard grass density</description>
            <files>
                <folder source="Data" destination="Data" priority="0" />
            </files>
        </plugin>
        <plugin name="High Density">
            <description>Increased grass density (performance impact)</description>
            <files>
                <folder source="Data_HD" destination="Data" priority="0" />
            </files>
        </plugin>
    </plugins>
</group>
```

### Task 10: Add New Detection Mechanism

**Files to Modify**:
1. `src/core/game_manager.py` - Add new detection method
2. `src/core/automation_suite.py` - Use new detection

**Example**: Detecting if NGIO is disabled

```python
# src/core/game_manager.py
def is_ngio_enabled(self) -> bool:
    """Check if NGIO plugin is enabled"""
    plugin_path = os.path.join(self.skyrim_path, "Data", "SKSE", "Plugins", "GrassControl.dll")
    if not os.path.exists(plugin_path):
        self.logger.error("❌ NGIO plugin not found")
        return False
    return True

# src/core/automation_suite.py
def _setup_and_validate(self) -> bool:
    # ... existing validation ...
    if not self.game_manager.is_ngio_enabled():
        self.logger.error("❌ NGIO plugin must be enabled")
        return False
```

---

## 🧪 Testing

### Current Testing Status

**Note**: The project currently has **no automated test suite**. Testing is manual and integration-focused.

### Manual Testing Checklist

#### Basic Functionality
- [ ] Launch application
- [ ] Navigate menu system
- [ ] Configure paths (first-time setup)
- [ ] Load existing configuration
- [ ] Reset configuration

#### Single Season Generation
- [ ] Generate Winter season
- [ ] Monitor for crashes
- [ ] Verify crash recovery
- [ ] Check file renaming (`.cgid` → `.WIN.cgid`)
- [ ] Verify archive creation
- [ ] Check cleanup (files deleted after archiving)

#### Multiple Seasons
- [ ] Generate all four seasons sequentially
- [ ] Verify disk space management
- [ ] Check archive integrity for each
- [ ] Confirm configurations restored

#### Edge Cases
- [ ] Skyrim already running (should detect and wait)
- [ ] Missing SKSE (should warn)
- [ ] Invalid Skyrim path (should error)
- [ ] Interrupted generation (Ctrl+C)
- [ ] Insufficient disk space
- [ ] Slow startup (1000+ mods)

#### Configuration Management
- [ ] INI backup created
- [ ] Season settings modified correctly
- [ ] Original formatting preserved
- [ ] Configuration restored after completion
- [ ] Backup cleanup (old backups removed)

### Test Environments

**Recommended Test Setups**:

1. **Minimal Setup** (< 100 mods)
   - Fast startup, low crash rate
   - Good for testing basic functionality
   - Generation completes in 15-30 minutes

2. **Medium Setup** (300-500 mods)
   - Moderate startup times
   - Occasional crashes
   - Realistic user experience

3. **Heavy Setup** (500-1000+ mods)
   - Slow startup (5-10+ minutes)
   - Frequent crashes
   - Tests timeout handling
   - Tests death loop prevention

### Future Testing Improvements

**Unit Tests** (Not Yet Implemented):
```python
# tests/test_file_processor.py
def test_rename_cgid_files():
    processor = FileProcessor()
    # Create test files
    # Run processor
    # Assert renamed correctly

# tests/test_config_manager.py
def test_season_modification():
    manager = ConfigManager()
    # Backup test INI
    # Modify season
    # Assert value changed
    # Assert formatting preserved
```

**Integration Tests** (Not Yet Implemented):
```python
# tests/integration/test_workflow.py
def test_single_season_generation():
    # Full workflow test with mock Skyrim process
    # Verify all phases complete
    # Check outputs exist
```

**Mocking Skyrim** (Not Yet Implemented):
- Mock `subprocess.Popen()` for Skyrim launching
- Simulate `PrecacheGrass.txt` growth
- Simulate process crashes/hangs
- Test recovery logic without actual Skyrim

### Manual Testing Script

For developers testing changes:

```python
# tests/manual_test.py
"""
Manual testing helper
Run specific scenarios without full generation
"""

def test_file_processor_performance():
    """Test file processor with 10,000 dummy files"""
    processor = FileProcessor()
    # Create test files
    # Run benchmark
    # Print results

def test_crash_recovery():
    """Simulate crash and verify recovery"""
    # Create PrecacheGrass.txt with content
    # Kill mock process
    # Verify automation detects and retries

# Run with: python tests/manual_test.py
```

### Validation Checklist

Before release:

**Code Quality**:
- [ ] All functions have docstrings
- [ ] Type hints on public APIs
- [ ] No commented-out code
- [ ] Consistent naming conventions

**Documentation**:
- [ ] README updated
- [ ] Changelog updated
- [ ] Version number incremented
- [ ] Known issues documented

**Build**:
- [ ] Python packages build successfully
- [ ] Bundled release builds successfully
- [ ] No errors in build logs
- [ ] Release info JSON generated

**User Experience**:
- [ ] Clear error messages
- [ ] Progress reporting works
- [ ] Archives installable in MO2/Vortex
- [ ] README in archives is clear

---

## 📦 Release & Distribution

### Version Management

**Single Source of Truth**: `src/__version__.py`

```python
__version__ = "1.1.2"
__version_info__ = (1, 1, 2)
```

All other files import from here. Never manually edit version elsewhere.

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR** (1.x.x): Breaking changes, major overhauls
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.2): Bug fixes, small improvements

**Examples**:
- `1.0.0` → `1.1.0`: Added per-season workflow (new feature)
- `1.1.0` → `1.1.1`: Fixed crash detection bug (bug fix)
- `1.1.2` → `2.0.0`: Complete rewrite with new architecture (breaking)

### Build Process

#### Step 1: Update Version

```bash
# Edit src/__version__.py only
__version__ = "1.1.3"
```

#### Step 2: Update Documentation

```bash
# Update docs/V1.1.3_RELEASE_NOTES.md
# Update README.md if needed
# Update CHANGELOG.md
```

#### Step 3: Build Packages

```bash
# Activate virtual environment
venv\Scripts\activate

# Build Python packages (wheel + source)
python -m build

# Creates:
# dist/ngio_automation_suite-1.1.3-py3-none-any.whl
# dist/ngio_automation_suite-1.1.3.tar.gz
```

#### Step 4: Build Bundled Release

```bash
# Build bundled release with complete Python environment
python build_release.py

# Creates:
# release/ngio-automation-suite-1.1.3-bundled.zip (~150-200MB)
# release/release_info.json
```

#### Step 5: Test Bundles

```bash
# Extract bundled release
cd release
unzip ngio-automation-suite-1.1.3-bundled.zip
cd ngio-automation-suite-1.1.3-bundled

# Test with bundled Python (NO Python installation required)
run_bundled.bat

# Verify:
# - Launches correctly
# - Displays correct version
# - Menu navigation works
# - Configuration collection works
# - Can start generation (test with minimal setup)
```

#### Step 6: Create GitHub Release

```bash
# Commit changes
git add .
git commit -m "Release v1.1.3"
git push origin master

# Create tag
git tag -a v1.1.3 -m "Version 1.1.3"
git push origin v1.1.3

# On GitHub:
# - Create new release from tag
# - Upload bundled ZIP
# - Upload wheel file
# - Copy release notes from docs/
```

#### Step 7: Upload to Nexus Mods

**Files to Upload**:
1. `ngio-automation-suite-1.1.3-bundled.zip` (main file)
2. `ngio-automation-suite-1.1.3-py3-none-any.whl` (optional file)

**Mod Page Updates**:
- Update version number
- Update description with new features
- Update changelog/release notes
- Update images/screenshots if UI changed

### Distribution Formats

#### Format 1: Bundled Edition (Recommended for Users)

**File**: `ngio-automation-suite-1.1.3-bundled.zip`  
**Size**: ~150-200MB  
**Contains**:
- Complete Python 3.x environment
- All dependencies pre-installed
- Source code
- Documentation
- Launcher script (`run_bundled.bat`)

**Advantages**:
- No Python installation required
- No dependency issues
- Works offline
- Guaranteed compatibility

**Disadvantages**:
- Large download size
- Platform-specific (Windows only)

**User Installation**:
```bash
1. Extract ZIP anywhere
2. Double-click run_bundled.bat
3. Done!
```

#### Format 2: Wheel Package (For Python Users)

**File**: `ngio_automation_suite-1.1.3-py3-none-any.whl`  
**Size**: ~50KB  
**Requires**: Python 3.8+ installed

**User Installation**:
```bash
pip install ngio_automation_suite-1.1.3-py3-none-any.whl
```

**Advantages**:
- Small download
- Integrates with Python ecosystem
- Easy updates via pip

**Disadvantages**:
- Requires Python knowledge
- Dependency management needed
- Not beginner-friendly

#### Format 3: Source Distribution

**File**: `ngio_automation_suite-1.1.3.tar.gz`  
**For**: Developers, advanced users

**Installation**:
```bash
pip install ngio_automation_suite-1.1.3.tar.gz
```

### Build System Details

#### `build_release.py` Workflow

```python
def create_bundled_release():
    """
    1. Create temp directory
    2. Copy ENTIRE Python installation
    3. Install dependencies in copied environment
    4. Copy source code
    5. Copy documentation
    6. Create launcher script (run_bundled.bat)
    7. ZIP everything
    8. Cleanup temp directory
    """
```

**Key Decision**: Copy entire Python vs virtual environment
- Virtual environments have path dependencies
- Copying entire Python makes it truly portable
- Result: 150MB but completely self-contained

#### `pyproject.toml` Configuration

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ngio-automation-suite"
version = "1.1.2"  # Auto-synced from __version__.py
dependencies = [
    "psutil>=5.8.0",
    "colorama>=0.4.4",
    "colorlog>=6.7.0"
]

[project.scripts]
ngio-automation = "ngio_automation_runner:main"
```

**Entry Point**: Allows `ngio-automation` command after pip install

### Release Checklist

**Pre-Release**:
- [ ] Version bumped in `src/__version__.py`
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Manual testing passed
- [ ] No known critical bugs
- [ ] Git working tree clean

**Build**:
- [ ] Python packages build without errors
- [ ] Bundled release builds without errors
- [ ] `release_info.json` generated
- [ ] All files in `dist/` and `release/`

**Testing**:
- [ ] Bundled release extracts cleanly
- [ ] Bundled Python runs correctly
- [ ] Version displays correctly in app
- [ ] Basic workflow functions

**Distribution**:
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Files uploaded to GitHub
- [ ] Release notes published
- [ ] Nexus Mods updated (if applicable)

**Post-Release**:
- [ ] Announcement in community forums
- [ ] Discord notification (if applicable)
- [ ] Monitor for user feedback
- [ ] Address critical issues quickly

---

## 🔧 Troubleshooting

### Developer Issues

#### Issue: Import errors when running from source

**Symptom**:
```
ModuleNotFoundError: No module named 'src'
```

**Cause**: Python path not set correctly

**Solution**:
```bash
# Option 1: Run from project root
cd C:\path\to\NGIO_AutomationSuite
python ngio_automation_runner.py

# Option 2: Install in development mode
pip install -e .
```

#### Issue: Build fails with "version not found"

**Symptom**:
```
RuntimeError: Unable to find version string in __version__.py
```

**Cause**: `src/__version__.py` malformed or missing

**Solution**:
```python
# Verify src/__version__.py contains:
__version__ = "1.1.2"  # Must be exactly this format
```

#### Issue: Bundled release Python doesn't work

**Symptom**:
```
'python' is not recognized as an internal or external command
```

**Cause**: Python not copied correctly or PATH issue

**Solution**:
```bash
# Verify python.exe exists
dir release\ngio-automation-suite-*\python\python.exe

# Check run_bundled.bat uses correct relative path
set BUNDLED_PYTHON=%SCRIPT_DIR%python\python.exe
```

#### Issue: Dependencies not installing in bundled environment

**Symptom**:
```
ModuleNotFoundError: No module named 'psutil'
```

**Cause**: Pip install failed during bundle creation

**Solution**:
```bash
# Run build_release.py with more verbose output
python build_release.py

# Check for pip errors in output
# Manually test pip in bundled environment:
release\ngio-automation-suite-*\python\python.exe -m pip list
```

### User-Reported Issues (Common Support Questions)

#### Issue: "Python not found" error

**Symptom**: User double-clicks `ngio_automation_runner.py`, nothing happens

**Cause**: Python not installed or not in PATH

**Solution (for users)**:
1. Use bundled edition instead (no Python needed)
2. Or install Python 3.8+ from python.org
3. During install, check "Add Python to PATH"

**Solution (for developers)**:
- Direct users to bundled edition
- Update documentation to emphasize bundled edition for non-technical users

#### Issue: Skyrim won't launch

**Symptom**: "SKSE loader not found" or "Skyrim process not found"

**Cause**: SKSE not installed or incorrect Skyrim path

**Solution**:
1. Verify Skyrim path contains `SkyrimSE.exe`
2. Install SKSE64 from https://skse.silverlock.org/
3. Verify `skse64_loader.exe` in Skyrim directory
4. Test manual launch: Run `skse64_loader.exe` directly

**Prevention**:
- Better path validation in `_setup_and_validate()`
- Check for SKSE before starting

#### Issue: Generation keeps restarting

**Symptom**: Skyrim launches, loads for a while, then restarts repeatedly

**Cause**: Timeout too aggressive for user's load order size

**Solution**:
1. Determine plugin count in user's load order
2. Adjust `no_progress_timeout_minutes`:
   - 500-1000 plugins: 20-25 minutes
   - 1000+ plugins: 30+ minutes
3. Direct user to `docs/LARGE_LOAD_ORDER_GUIDE.md`

**Prevention**:
- Prompt user for approximate plugin count
- Suggest timeout based on plugin count
- Make adaptive timeouts more aggressive in learning

#### Issue: No grass in-game after installation

**Symptom**: User installed archives but no grass appears

**Cause**: Multiple possible causes
1. NGIO still enabled (should be disabled)
2. Grass Cache Helper NG not installed
3. Wrong season active vs installed cache
4. Archives not installed correctly

**Solution**:
1. Disable NGIO mod
2. Install Grass Cache Helper NG
3. Match season in seasonal mod with installed cache
4. Verify Data/Grass folder in archive is correct structure
5. Check mod manager load order (grass cache should load after NGIO)

**Prevention**:
- Clearer installation instructions in archive README
- Verification script to check installation
- Troubleshooting section in user docs

#### Issue: Antivirus deletes files

**Symptom**: Tool runs but files disappear, or tool won't launch

**Cause**: Antivirus false positive

**Solution**:
1. Add tool directory to antivirus exclusions
2. Download only from official sources (GitHub, Nexus)
3. Verify file signatures/checksums
4. Use Windows Defender (fewer false positives)

**Prevention**:
- Document in README prominently
- Consider code signing certificate (expensive)
- Provide checksums for all releases

### Debugging Tools

#### Enable Debug Logging

```python
# Add to ngio_automation_runner.py
from src.utils.logger import Logger

Logger.set_level("DEBUG")  # Before other imports
```

**Result**: More verbose console output with debug messages

#### Inspect Process State

```python
# In src/core/game_manager.py
def get_process_status(self):
    # Already implemented
    # Returns: PID, uptime, memory, CPU, status
    
# Use during debugging:
status = self.game_manager.get_process_status()
print(f"Process status: {status}")
```

#### Monitor File Activity

```python
# Add to automation workflow
def monitor_file_changes(file_path):
    import os
    import time
    
    if os.path.exists(file_path):
        stat = os.stat(file_path)
        print(f"File: {file_path}")
        print(f"  Size: {stat.st_size} bytes")
        print(f"  Modified: {time.ctime(stat.st_mtime)}")
        print(f"  Accessed: {time.ctime(stat.st_atime)}")

# Call every 5 seconds during generation
```

#### Analyze Crash Logs

```python
# src/core/game_manager.py - Already implemented
crash_logs = self.game_manager.get_crash_logs()
for log_path in crash_logs:
    print(f"Crash log: {log_path}")
    # Parse and analyze
```

### Development Environment Issues

#### Issue: Virtual environment not activating

**Symptom**:
```
'venv' is not recognized as an internal or external command
```

**Solution**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# If that fails, try full path
C:\Users\YourName\Projects\NGIO_AutomationSuite\venv\Scripts\activate.bat
```

#### Issue: Dependencies install but imports fail

**Symptom**:
```
pip list shows psutil
import psutil raises ModuleNotFoundError
```

**Cause**: Multiple Python installations, wrong environment

**Solution**:
```bash
# Check which Python is running
python -c "import sys; print(sys.executable)"

# Check where psutil is installed
pip show psutil

# Ensure both point to same environment
```

#### Issue: Linter errors in IDE

**Symptom**: IDE shows import errors but code runs fine

**Cause**: IDE not configured for project structure

**Solution** (VS Code):
```json
// .vscode/settings.json
{
    "python.analysis.extraPaths": ["src"],
    "python.autoComplete.extraPaths": ["src"]
}
```

---

## 📚 Additional Resources

### Documentation Files

- **README.md**: User-facing overview and quick start
- **DEVELOPER_SETUP.md**: Developer onboarding
- **docs/LARGE_LOAD_ORDER_GUIDE.md**: Configuration for 500+ mods
- **docs/SEASON_SELECTION_GUIDE.md**: Per-season workflow explanation
- **docs/DETECTION_MECHANISMS.md**: Technical details on crash detection
- **docs/VERSION_MANAGEMENT.md**: Version strategy
- **docs/NEXUS_DOCUMENTATION.txt**: Nexus mod page content

### External Links

- **NGIO Mod**: Nexus Mods (search "No Grass In Objects")
- **Grass Cache Helper NG**: Nexus Mods (enables seasonal loading)
- **Seasons of Skyrim**: Nexus Mods (seasonal mod requirement)
- **SKSE64**: https://skse.silverlock.org/

### Community

- **GitHub Issues**: Bug reports and feature requests
- **Nexus Comments**: User feedback and support
- **Discord**: Community discussions (if applicable)

---

## 🌱 v1.5.0: NGIO Settings & Grass Profiles

**Release Date:** November 27, 2025  
**Major Update:** Complete NGIO configuration system with preset profiles

### Critical Fixes

#### 1. Missing NGIO Settings (7 new settings added!)

Previously, we only configured 4 basic NGIO settings. v1.5.0 adds **7 critical missing settings**:

```ini
# NEW in v1.5.0:
ExtendGrassDistance=True        # Required for LOD compatibility
ExtendGrassCount=False          # Can add 2-6 hours to generation!
SuperDenseGrass=False           # Can add MANY hours!
OverwriteMinGrassSize=67        # Grass density (BAKED into cache)
GlobalGrassScale=1.0            # Grass height (BAKED into cache)
EnsureMaxGrassTypesPerTextureSetting=15  # Grass variety (BAKED)
OnlyPregenerateWorldSpaces=...  # Optional filter (can halve generation time)
```

**Impact:**
- LOD compatibility now properly configured
- Performance warnings for slow settings
- Prevents accidental multi-hour generations
- Proper grass density and appearance control

#### 2. OnlyLoadFromCache State Management Bug

**The Bug:**
- Set `OnlyLoadFromCache=False` during generation ✅ Correct
- **Never set it back to True after completion** ❌ Bug!
- Result: Game tries to regenerate cache on every launch

**The Fix (v1.5.0):**
- Properly set `OnlyLoadFromCache=True` after all generations complete
- Game now uses pre-generated cache (fast loading)
- Added to cleanup/restore phase

### New Features

#### Grass Generation Profiles

Users can now choose from preset profiles or customize settings interactively:

**Profile 1: Fast Generation**
```yaml
extend_grass_distance: false
overwrite_min_grass_size: 80
ensure_max_grass_types: 7
Estimated Time: 30-45 minutes
```
- Quick testing
- Lower density
- No extended features

**Profile 2: LOD Compatible** (Recommended)
```yaml
extend_grass_distance: true
overwrite_min_grass_size: 67
ensure_max_grass_types: 15
Estimated Time: 60-90 minutes
```
- Works with DynDOLOD grass LOD
- Medium density (Cathedral Landscapes default)
- Best balance of quality/time

**Profile 3: Maximum Quality**
```yaml
extend_grass_distance: true
extend_grass_count: true
overwrite_min_grass_size: 40
global_grass_scale: 1.15
Estimated Time: 2-6 hours!
```
- Highest quality
- Very dense grass
- ⚠️  WARNING: Takes significantly longer

**Profile 4: Custom**
- Interactive configuration
- Modify any setting
- Real-time impact warnings

#### Interactive Profile Selection

```
┌──────────────────────────────────────────────────────┐
│        🌱 Grass Generation Profile Selection         │
└──────────────────────────────────────────────────────┘

⚠️  IMPORTANT: These settings are PERMANENTLY BAKED!
   Once generated, you must regenerate to change them.

1. Fast (30-45 min)
2. LOD Compatible (60-90 min) [Recommended]
3. Maximum Quality (2-6 hours)
4. Custom Settings

Select profile [1-4]: _
```

After selection:
- Shows complete settings summary
- Estimated time warning
- Options: [C]ontinue, [M]odify, [B]ack
- Interactive override for individual settings

#### Baked Settings Warning

**Critical User Education:**

Some settings are **permanently written into grass cache files**:
- `OverwriteMinGrassSize` - Density
- `GlobalGrassScale` - Height
- `ExtendGrassDistance` - Distance
- `ExtendGrassCount` - Count
- `SuperDenseGrass` - Ultra density
- `EnsureMaxGrassTypesPerTextureSetting` - Variety

**Consequence:** Must regenerate ALL seasons to change these!

Users are warned:
1. During profile selection
2. On confirmation screen
3. In YAML config comments
4. In documentation

### Technical Implementation

#### New Files

**`src/utils/grass_profiles.py`**
- `ProfileType` enum
- `GrassProfile` dataclass
- Preset profile definitions
- Interactive selection system
- Settings modification interface

#### Updated Files

**`src/core/config_manager.py`**
- `configure_ngio_for_generation()` now accepts all 7 new settings
- Logs important settings and warnings
- Validates boolean/numeric types

**`src/core/automation_suite.py`**
- `AutomationConfig` includes all 7 new settings
- Calls `configure_ngio_for_generation()` with settings
- Calls `configure_ngio_for_cache_use()` after completion (FIX!)

**`ngio_automation_runner.py`**
- Integrates profile selection into grass generation flow
- Passes profile settings to `AutomationConfig`

**`src/utils/config_loader.py`**
- `NGIOConfig` dataclass includes new settings
- YAML template updated with:
  - All 7 new settings
  - Profile recommendations
  - Performance warnings
  - "BAKED" warnings

### Research Sources

Based on comprehensive research from:
- [Step Modifications: Grass LOD Guide](https://stepmodifications.org/wiki/SkyrimSE:Grass_LOD_Guide)
- [Nexus: NGIO Generation Guide](https://www.nexusmods.com/skyrimspecialedition/articles/6919)
- [Nexus: NGIO Seasonal Guide](https://www.nexusmods.com/skyrimspecialedition/articles/6920)

See `NGIO_RESEARCH_FINDINGS.md` for complete analysis.

### User Impact

**Before v1.5.0:**
- 36% of NGIO settings configured (4/11)
- OnlyLoadFromCache bug caused slow loading
- No guidance on performance impact
- Users couldn't customize grass appearance
- No warnings about multi-hour generation times

**After v1.5.0:**
- 100% of NGIO settings configured (11/11) ✅
- OnlyLoadFromCache properly managed ✅
- Clear performance warnings ✅
- Flexible profile system ✅
- User-friendly customization ✅
- "Baked settings" education ✅

### Backwards Compatibility

**Configuration:**
- New settings have sensible defaults
- Old YAML configs still work (uses defaults)
- CLI arguments not affected

**Generated Files:**
- No changes to file format
- Archives remain compatible
- No re-generation required

**Process:**
- Profile selection is interactive (skippable via YAML/CLI)
- Default profile is "LOD Compatible" (recommended)

---

## 🔮 Future Enhancements

### Planned Features (Updated for v1.5.0+)

1. **DynDOLOD & TexGen Integration** (v1.6.0 - HIGH PRIORITY)
   - Automatic TexGen billboard generation
   - DynDOLOD grass LOD creation
   - Include LODs in archives
   - Complete grass LOD workflow
   - See `NGIO_RESEARCH_FINDINGS.md` for details

2. **Worldspace Filtering** (v1.5.1 or v1.6.0)
   - xEdit script integration
   - Auto-detect worldspaces with grass
   - Filter irrelevant worldspaces
   - Can cut generation time by 25-50%

3. **GUI Version** (Future)

1. **GUI Version** (Future)
   - Tkinter or PyQt interface
   - Real-time progress visualization
   - Log viewer
   - Configuration wizard

2. **Parallel Season Generation** (Experimental)
   - Generate multiple seasons simultaneously
   - Requires significant disk space
   - Increased crash complexity

3. **Automated Testing** (Priority)
   - Unit tests for core components
   - Integration tests with mocked Skyrim
   - CI/CD pipeline

4. **Installation Verification** (High Priority)
   - Script to verify archive installation
   - Check for common configuration errors
   - In-game detection of active cache

5. **Cloud Backup** (Future)
   - Upload generated archives to cloud
   - Share caches between installations
   - Community cache repository

6. **Performance Metrics** (Low Priority)
   - Track generation times per worldspace
   - Compare crash rates across seasons
   - Benchmark file processing performance

---

**End of PROJECT_KNOWLEDGE.md**

This document will be updated as the project evolves. Last comprehensive update: 2025-11-27

