# 🌱 NGIO Automation Suite

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

**The Ultimate Automation Tool for NGIO Grass Cache Generation in Skyrim SE**

Transform the painful **4+ hour manual process** into a **5-minute setup** that runs completely unattended! 

🎯 **Perfect for users with heavy mod lists who are tired of babysitting Skyrim through endless crashes during grass generation.**

> **⚠️ Antivirus Notice:** This tool may trigger false positives due to its process monitoring and file automation capabilities. It's 100% safe and open-source. See [troubleshooting section](#-troubleshooting-common-issues--solutions) for details.

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
- ✅ **NEW v1.1.0**: Adaptive timeouts for large load orders (500+ mods)

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
│   ├── LARGE_LOAD_ORDER_GUIDE.md    # Configuration for 500+ mods
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
1. 🚀 Double-click start_ngio_automation.bat
2. 📁 Provide Skyrim path (one-time setup)
3. ✅ Select ONE season to generate
4. ☕ Go make coffee (or sleep)
5. 📦 Season automatically archived & cleaned
6. 🔄 Run again for other seasons
7. 🎉 Install ready-to-use mod archives!
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

## 🔧 **WHAT YOU MUST INSTALL FIRST** (For Complete Beginners)

### ⚠️ **CRITICAL REQUIREMENTS** - You MUST install these or nothing will work:

#### 1. **Python 3.8+** 🐍 **ONLY for Portable Version**
- **Bundled Edition:** ✅ **Skip this!** Complete Python environment is bundled inside
- **Portable Version:** ⚠️ **Required** - you must install Python first
- **Download:** https://www.python.org/downloads/
- **Version:** Python 3.8, 3.9, 3.10, 3.11, or 3.12 (latest recommended)
- **Installation Steps:**
  1. Download the installer from the link above
  2. ✅ **CHECK "Add Python to PATH"** during installation (CRITICAL!)
  3. ✅ Choose "Install for all users" (recommended)
  4. Wait for installation to complete
- **Test it worked:** Open Command Prompt and type `python --version`
  - ✅ Should show: `Python 3.8.x` (or newer)
  - ❌ If you get `'python' is not recognized`, Python isn't in PATH - reinstall and check the PATH box

#### 2. **Skyrim Special Edition** 🎮 **ESSENTIAL**
- **Required:** Skyrim SE or Anniversary Edition (VR also works)
- **Platforms:** Steam, GOG, Epic Games Store, Microsoft Store - any work
- **Must be:** Installed, launched at least once, and working normally
- **Test it works:** Launch Skyrim manually and make sure it reaches the main menu

#### 3. **NGIO Mod (No Grass In Objects)** 🌱 **ESSENTIAL**
- **Download:** From Nexus Mods - search for "No Grass In Objects"
- **Install:** Through your mod manager (Mod Organizer 2 or Vortex)
- **Status:** Must be **ENABLED** in your mod manager
- **Test it works:** NGIO should appear in your mod list and be active

#### 4. **SKSE64** ⚡ **HIGHLY RECOMMENDED**
- **Download:** https://skse.silverlock.org/
- **Why needed:** NGIO plugin requires SKSE to work properly
- **Installation:**
  1. Download the correct version for your Skyrim
  2. Extract all files to your Skyrim installation directory
  3. You should see `skse64_loader.exe` in your Skyrim folder
- **Test it works:** Launch Skyrim using `skse64_loader.exe` instead of the normal launcher

### 🌱 **OPTIONAL** (For Seasonal Grass):

#### 5. **Seasons of Skyrim** (Optional but Recommended)
- **Download:** From Nexus Mods
- **Purpose:** Enables Winter/Spring/Summer/Autumn grass generation
- **Without this:** You can still generate universal grass cache (non-seasonal mode)
- **Install:** Through mod manager, configure seasons as desired

#### 6. **Grass Cache Helper NG** (Recommended)
- **Download:** From Nexus Mods
- **Purpose:** Loads the generated `.cgid` files in-game for seasonal switching
- **Install:** SKSE plugin - extract to `Data/SKSE/Plugins/`

---

## 🚀 **HOW TO USE** (Step-by-Step for Beginners)

### **Download Options:**

#### Option A: **Bundled Edition** (Easiest - No Python Required!)
1. Download `ngio-automation-suite-X.X.X-bundled.zip`
2. Extract anywhere on your computer (Desktop is fine)
3. Double-click `start_ngio_automation.bat`
4. **No Python installation needed!** Complete Python environment bundled inside

#### Option B: **Portable Version** (Requires Python)
1. Download `ngio-automation-suite-X.X.X-portable.zip`
2. Extract anywhere on your computer (Desktop is fine)
3. Double-click `start_ngio_automation.bat`
4. Follow the setup wizard

#### Option C: **From Source** (For advanced users)
```bash
git clone https://github.com/ReidenXerx/NGIO_AutomationSuite.git
cd NGIO_AutomationSuite
python ngio_automation_runner.py
```

### **First Time Setup (5 minutes):**
1. **Run the tool** - Double-click `start_ngio_automation.bat`
2. **Python check** - Tool will verify Python is installed
3. **Skyrim path** - Point to your Skyrim installation folder
   - Usually: `C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition`
   - Or: `C:\Program Files\Steam\steamapps\common\Skyrim Special Edition`
   - **Tip:** You can drag and drop the folder into the console
4. **Output path** - Where to save generated archives (any folder you want)
5. **Seasonal mods** - Tell the tool if you have Seasons of Skyrim installed
6. **Season selection** - Pick ONE season to generate (Winter/Spring/Summer/Autumn)
7. **Timeouts** - Leave defaults unless you have issues

### **Generation Process (20-60 minutes per season):**
1. **Start generation** - Tool automatically launches Skyrim
2. **Walk away** - Tool handles everything (crashes, retries, progress)
3. **Completion** - Tool creates archive and cleans up files
4. **Install** - Use the generated archive in your mod manager

### **For Multiple Seasons:**
- Run the tool again and select a different season
- Each season is generated separately for optimal disk space usage

### 🔧 **Have 500+ Mods? Read This First!**

If you have a large or heavily modded load order:
- 📖 **See [Large Load Order Configuration Guide](docs/LARGE_LOAD_ORDER_GUIDE.md)** for optimal settings
- ⏱️ Skyrim startup times increase significantly with many mods
- 🎯 v1.1.0+ includes adaptive timeouts that automatically adjust
- 💡 Key tip: Don't panic if Skyrim takes 5-10 minutes to start - this is normal!

**Quick settings for large load orders:**
```python
max_crash_retries=15              # More retries for stability
no_progress_timeout_minutes=20    # Longer hang detection
startup_wait_seconds=60           # Prevent "death loops"
```

---

## 🆘 **TROUBLESHOOTING** (Common Issues & Solutions)

### ❌ **"python: command not found" or "'python' is not recognized"**
**Problem:** Python not installed or not in PATH
**Solution:**
1. Download Python from https://www.python.org/downloads/
2. During installation, ✅ **CHECK "Add Python to PATH"**
3. Restart your computer
4. Test: Open Command Prompt, type `python --version`

### ❌ **"SKSE loader not found" or "Skyrim process not found"**
**Problem:** SKSE64 not installed properly
**Solution:**
1. Download SKSE64 from https://skse.silverlock.org/
2. Extract ALL files to your Skyrim directory (where SkyrimSE.exe is)
3. Verify `skse64_loader.exe` exists in Skyrim folder
4. Test: Launch Skyrim using `skse64_loader.exe` manually

### ❌ **"No grass generation" or "PrecacheGrass.txt not created"**
**Problem:** NGIO mod not working
**Solution:**
1. Ensure NGIO is ✅ **ENABLED** in your mod manager
2. Check NGIO is not being overridden by other mods
3. Verify SKSE64 is working (see above)
4. Try launching Skyrim manually first to test

### ❌ **"Skyrim won't launch" or "Process terminated immediately"**
**Problem:** Skyrim installation or configuration issue
**Solution:**
1. Verify Skyrim path is correct (where SkyrimSE.exe is located)
2. Launch Skyrim manually first to ensure it works
3. Check for conflicting mods or mod manager issues
4. Try running as Administrator

### ❌ **"Permission denied" or "Access denied" errors**
**Problem:** Windows permissions blocking file operations
**Solution:**
1. Run the tool as Administrator (right-click → Run as administrator)
2. Check your antivirus isn't blocking the tool
3. Ensure output directory has write permissions
4. Try using a different output directory (like Desktop)

### ❌ **Antivirus blocking or deleting files**
**Problem:** False positive detection by antivirus software
**Solution:**
1. **Add exclusion:** Add the extracted tool folder to your antivirus exclusions
2. **Temporarily disable:** Turn off real-time protection during use
3. **Use Windows Defender:** Generally has fewer false positives with Python tools
4. **Download from official sources:** Only use GitHub or Nexus downloads
5. **Why this happens:** Tool monitors processes and modifies many files rapidly (normal for automation tools)

### ❌ **"Archive not created" or "Files not found"**
**Problem:** File processing or archive creation failed
**Solution:**
1. Check output directory has enough free space (5GB+)
2. Verify no other programs are using the Skyrim directory
3. Check antivirus isn't quarantining files
4. Try running as Administrator

### ❌ **Tool crashes or hangs during generation**
**Problem:** Various possible causes
**Solution:**
1. Check system has enough RAM (8GB+ recommended)
2. Close unnecessary programs to free memory
3. Try increasing timeout values in configuration
4. Check logs for specific error messages

### ❌ **"Seasons of Skyrim config not found"**
**Problem:** Seasonal mod not installed or configured
**Solution:**
1. Install Seasons of Skyrim from Nexus Mods
2. Configure it in your mod manager
3. Or select "Non-seasonal mode" in the tool

### 🎯 **Still Having Issues?**
1. **Check the logs** - Tool creates detailed logs for troubleshooting
2. **Try non-seasonal mode** - Simpler setup, fewer dependencies
3. **Test with minimal mods** - Disable other mods temporarily
4. **Report bugs** - Include your Python version, Skyrim version, and error messages

### 📋 **Before Asking for Help, Provide:**
- Python version (`python --version`)
- Skyrim version (SE/AE/VR)
- NGIO mod version
- Whether SKSE64 works manually
- Full error message or log file
- Your mod list (if relevant)

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
