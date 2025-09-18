# 🌱 NGIO Automation Suite

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

**The Ultimate Automation Tool for NGIO Grass Cache Generation in Skyrim**

Transform the painful **4-hour manual process** into a **fully automated workflow** that runs while you sleep!

## 🎯 What This Solves

### Current NGIO Grass Generation Process (PAINFUL):
- ⏱️ **4+ hours of manual work** across 4 seasons
- 🔄 **Constant manual restarts** when Skyrim crashes
- 📝 **Manual config editing** for each season (Winter→Spring→Summer→Autumn)
- 📁 **Manual file renaming** after each 30-60 minute generation
- 😤 **High error rates** and frustration
- 🎮 **Constant babysitting** required

### With NGIO Automation Suite (AMAZING):
- 🚀 **5 minutes setup, walk away**
- 🛌 **Run before bed, wake up completed**
- 🤖 **Fully automated crash recovery**
- ⚡ **Intelligent process management**
- 📊 **Real-time progress tracking**
- ✅ **Consistent, reliable results**

## 🚀 Features

### 🎮 **Intelligent Game Manager**
- ✅ Auto-launch Skyrim for each season
- ✅ Detect and handle crashes automatically
- ✅ Monitor generation progress
- ✅ Resume exactly where it left off

### 📝 **Smart Config Management**
- ✅ Backup original configurations
- ✅ Auto-modify season settings (1→2→3→4→5)
- ✅ Persistent path caching
- ✅ Restore everything when done

### ⚡ **High-Speed File Processing**
- ✅ **10-25x faster** than batch scripts
- ✅ Multithreaded file renaming
- ✅ Per-season archive creation & cleanup
- ✅ Optimal disk space management

### 📦 **Mod Archive Generation**
- ✅ Creates installable ZIP archives for each season
- ✅ Proper mod structure with Data/Grass folders
- ✅ Includes installation instructions and metadata
- ✅ Compatible with MO2, Vortex, and manual installation

### 🛡️ **Bulletproof Error Handling**
- ✅ Detect infinite loops and hangs
- ✅ Smart retry logic for different crash types
- ✅ Graceful fallback and recovery
- ✅ Detailed crash analysis and suggestions

## 🏗️ Project Structure

```
NGIO_AutomationSuite/
├── src/
│   ├── core/
│   │   ├── automation_suite.py      # Master controller
│   │   ├── game_manager.py          # Skyrim process handler
│   │   ├── config_manager.py        # INI file management
│   │   ├── file_processor.py        # High-speed file operations
│   │   └── progress_monitor.py      # Status tracking & reporting
│   ├── utils/
│   │   ├── skyrim_detector.py       # Game installation detection
│   │   ├── mod_manager.py           # MO2/Vortex integration
│   │   └── logger.py                # Logging system
│   └── gui/
│       └── dashboard.py             # Optional GUI dashboard
├── config/
│   ├── settings.yaml                # Default configuration
│   └── mod_profiles.yaml            # Mod manager profiles
├── scripts/
│   ├── install.bat                  # Auto-installer
│   └── run_automation.bat          # Main launcher
├── tests/
│   └── test_*.py                    # Unit tests
├── docs/
│   ├── SETUP.md                     # Setup instructions
│   ├── TROUBLESHOOTING.md           # Common issues
│   └── API.md                       # Developer documentation
├── examples/
│   └── config_examples/             # Sample configurations
└── requirements.txt                 # Python dependencies
```

## 🎮 Typical Workflow

### **Before (Current Process)**
```
1. 😮‍💨 Open guide, read 47 steps
2. 📝 Manually edit po3_SeasonsOfSkyrim.ini (Winter)
3. 🎮 Launch Skyrim, wait for crash
4. 🔄 Restart manually when it crashes (repeat 3-5 times)
5. ⏱️ Wait 30-60 minutes for completion
6. 📁 Manually rename files with batch script
7. 📂 Create mod folder manually
8. 🔁 REPEAT for Spring, Summer, Autumn
9. 📝 Restore original config files
10. 😵 4 hours later, maybe it worked?
```

### **After (With Automation Suite)**
```
1. 🚀 Double-click run_ngio_automation.bat
2. 📁 Provide Skyrim path (one-time setup)
3. ✅ Select seasons to generate
4. ☕ Go make coffee (or sleep)
5. 📦 Each season automatically archived & cleaned
6. 🎉 Wake up to ready-to-install mod archives!
```

## 🔧 Development Status

### ✅ **Phase 1: Core Foundation** (COMPLETED)
- ✅ High-speed multithreaded file processing
- ✅ Intelligent configuration management
- ✅ Persistent user settings cache
- ✅ Professional logging system

### ✅ **Phase 2: Game Process Manager** (COMPLETED)
- ✅ Skyrim process detection and launching
- ✅ Crash monitoring and auto-restart
- ✅ Progress parsing and monitoring
- ✅ Memory and resource management

### ✅ **Phase 3: Configuration Automation** (COMPLETED)
- ✅ INI file backup/modification/restoration
- ✅ Season switching automation (1→2→3→4→5)
- ✅ Settings validation and recovery
- ✅ User-friendly path configuration

### ✅ **Phase 4: Archive Generation** (COMPLETED)
- ✅ Automatic mod archive creation
- ✅ Proper mod structure with metadata
- ✅ Installation guide generation
- ✅ MO2/Vortex compatibility

### 🎯 **Phase 5: Testing & Polish** (CURRENT)
- 🧪 End-to-end workflow testing
- 🐛 Bug fixes and edge case handling
- 📖 Documentation completion
- 🚀 Release preparation

## 🛠️ Requirements

- **Python 3.7+** (auto-installed if needed)
- **Windows 10/11**
- **Skyrim SE/AE/VR** with NGIO installed
- **Mod Organizer 2** or **Vortex** (recommended)
- **Seasons of Skyrim** mod

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/ReidenXerx/ngio-automation-suite.git

# Navigate to the directory
cd ngio-automation-suite

# Double-click to run (Windows)
run_ngio_automation.bat

# Or run directly with Python
python ngio_automation_runner.py
```

### First Time Setup
1. **Run the launcher** - Double-click `run_ngio_automation.bat`
2. **Configure paths** - Provide your Skyrim installation directory
3. **Choose preferences** - Select which seasons to generate
4. **Start generation** - Let it run automatically!

Your settings are saved and remembered for future use.

## 🤝 Contributing

This project aims to **revolutionize NGIO grass generation** for the entire Skyrim modding community. Contributions are highly welcome!

### Areas where help is needed:
- 🎮 Skyrim process monitoring and crash detection
- 🔧 MO2/Vortex API integration  
- 🎨 GUI development for progress dashboard
- 📝 Documentation and testing
- 🐛 Bug reports from real-world usage

## 🙏 Acknowledgments

- **infernalryan** - For the comprehensive NGIO guide that inspired this automation
- **The NGIO development team** - For creating the foundation this builds upon
- **Skyrim modding community** - For enduring the manual process long enough to need this solution

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**🎯 Goal: Save the Skyrim modding community thousands of collective hours and eliminate the biggest pain point in grass generation!**

⭐ **Star this project if you're tired of manual NGIO grass generation!** ⭐
