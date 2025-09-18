# 🛠️ NGIO Automation Suite - Developer Setup

## Building and Contributing

This document is for **developers** who want to build the project from source, contribute code, or understand the build system.

---

## 🔧 **Developer Requirements**

### **Required Tools:**
- **Python 3.8+** with pip
- **Git** for version control
- **Text editor/IDE** (VS Code, PyCharm, etc.)

### **Optional Tools:**
- **7-Zip** for testing archives
- **Virtual environment** tools (venv, conda)

---

## 🚀 **Quick Start**

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/ngio-automation-suite.git
cd ngio-automation-suite
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Run from Source**
```bash
python ngio_automation_runner.py
```

### **4. Build Release**
```bash
python build_release.py
# or
.\build.bat
```

---

## 📦 **Build System Overview**

### **Build Files:**
- `build_release.py` - Main build script (like npm run build)
- `build.bat` - Windows batch launcher
- `pyproject.toml` - Modern Python packaging config
- `setup.py` - Legacy Python packaging (compatibility)
- `requirements.txt` - Runtime dependencies

### **Build Output:**
- `dist/` - Python packages (wheel, source)
- `release/` - User-friendly distribution files
- `build/` - Temporary build files (auto-generated)

### **Release Types:**
1. **Portable ZIP** - Extract and run, no installation
2. **Installer ZIP** - Professional installation with pip
3. **Source ZIP** - Full source code for developers
4. **Python Packages** - Wheel and source distribution

---

## 🏗️ **Build Process Details**

### **What `python build_release.py` Does:**

1. **Clean Directories** - Removes old build/dist/release
2. **Build Python Packages** - Creates wheel and source dist
3. **Create Portable Release** - User-friendly ZIP with launcher
4. **Create Source Release** - Developer source code ZIP  
5. **Create Installer Package** - Professional installation ZIP
6. **Generate Documentation** - Release notes and instructions

### **Output Structure:**
```
dist/
├── ngio_automation_suite-1.0.0-py3-none-any.whl
└── ngio_automation_suite-1.0.0.tar.gz

release/
├── ngio-automation-suite-1.0.0-portable.zip     # For end users
├── ngio-automation-suite-1.0.0-installer.zip    # For system install
├── ngio-automation-suite-1.0.0-source.zip       # For developers
├── README.txt                                    # User instructions
└── release_info.json                             # Build metadata
```

---

## 🧪 **Development Workflow**

### **Making Changes:**
1. Edit source code in `src/`
2. Test with `python ngio_automation_runner.py`
3. Run build with `python build_release.py`
4. Test portable release
5. Commit changes

### **Adding Features:**
1. Create new modules in `src/core/` or `src/utils/`
2. Update imports in main runner
3. Add any new dependencies to `requirements.txt`
4. Update version in `pyproject.toml` and `setup.py`
5. Test and build

### **Version Management:**
- Update version in **3 places**:
  - `pyproject.toml` → `version = "1.0.1"`
  - `setup.py` → `version="1.0.1"`
  - `build_release.py` → `VERSION = "1.0.1"`

---

## 📁 **Project Structure**

```
NGIO_AutomationSuite/
├── src/                          # Source code
│   ├── core/                     # Core automation logic
│   │   ├── automation_suite.py   # Main orchestrator
│   │   ├── game_manager.py       # Skyrim process management
│   │   ├── config_manager.py     # INI file handling
│   │   ├── file_processor.py     # File renaming/processing
│   │   ├── archive_creator.py    # ZIP archive creation
│   │   └── progress_monitor.py   # Progress tracking
│   └── utils/                    # Utilities
│       ├── logger.py             # Colored logging
│       ├── config_cache.py       # Persistent config
│       └── skyrim_detector.py    # Game detection
├── docs/                         # Documentation
├── ngio_automation_runner.py     # Main entry point
├── run_ngio_automation.bat       # Simple launcher
├── pyproject.toml               # Modern Python config
├── setup.py                     # Legacy Python config
├── requirements.txt             # Dependencies
├── build_release.py             # Build system
├── build.bat                    # Windows build launcher
└── README.md                    # Project overview
```

---

## 🔍 **Testing**

### **Manual Testing:**
1. Run `python ngio_automation_runner.py`
2. Test configuration wizard
3. Test single season generation (if you have Skyrim+NGIO)
4. Test build system with `python build_release.py`
5. Extract and test portable release

### **Build Testing:**
1. Run `python build_release.py`
2. Check `release/` directory has 5 files
3. Extract portable ZIP and run `start_ngio_automation.bat`
4. Try installing from installer ZIP

---

## 🚫 **What's in .gitignore**

### **Build Output (Don't Commit):**
- `build/` - Temporary build files
- `dist/` - Python packages  
- `release/` - Distribution files
- `*.whl` - Python wheels
- `*.egg-info/` - Package metadata

### **Runtime Files (Don't Commit):**
- `PrecacheGrass.txt` - Skyrim generation state
- `*.cgid` - Generated grass cache files
- `*.log` - Log files
- `__pycache__/` - Python bytecode

---

## 🎯 **Release Checklist**

Before releasing a new version:

- [ ] Update version in `pyproject.toml`, `setup.py`, `build_release.py`
- [ ] Test manual run: `python ngio_automation_runner.py`
- [ ] Test build system: `python build_release.py`
- [ ] Test portable release (extract and run)
- [ ] Test installer package
- [ ] Update `CHANGELOG.md` with new features
- [ ] Create Git tag: `git tag v1.0.1`
- [ ] Push to repository: `git push --tags`
- [ ] Upload release files to GitHub/Nexus

---

## 🆘 **Common Development Issues**

| Problem | Solution |
|---------|----------|
| Build fails | Check Python version, install `build` package |
| Import errors | Check `src/` structure, verify PYTHONPATH |
| Archive creation fails | Check file permissions, close file handles |
| Version mismatch | Update version in all 3 config files |
| Missing dependencies | Run `pip install -r requirements.txt` |

---

**Bottom Line:** Clone, install deps, run `python ngio_automation_runner.py` to test, run `python build_release.py` to build releases! 🚀
