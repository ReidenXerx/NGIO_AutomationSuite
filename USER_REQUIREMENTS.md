# 🎮 NGIO Automation Suite - User Requirements

## What Users Need to Install/Setup Manually

This document clearly outlines what **users must do themselves** before they can use the NGIO Automation Suite.

---

## 🔧 **REQUIRED - Users Must Install These**

### 1. **Python 3.8+** ⚠️ **CRITICAL**
- **Download:** https://www.python.org/downloads/
- **Version:** Python 3.8 or newer (3.12 recommended)
- **Installation:** 
  - ✅ **Check "Add Python to PATH"** during installation
  - ✅ Choose "Install for all users" (recommended)
- **Verify:** Open Command Prompt and type `python --version`

### 2. **Skyrim Special Edition** ⚠️ **CRITICAL**
- **Required:** Skyrim SE (Anniversary Edition also works)
- **Platform:** Steam, GOG, Epic Games Store, etc.
- **Must be installed and working**

### 3. **NGIO Mod (No Grass In Objects)** ⚠️ **CRITICAL**
- **Download:** From Nexus Mods
- **Install:** Via your mod manager (MO2/Vortex)
- **Status:** Must be **ENABLED** and working
- **Note:** This is the core mod that generates grass cache

### 4. **SKSE64** 🔥 **HIGHLY RECOMMENDED**
- **Download:** https://skse.silverlock.org/
- **Why:** Required for NGIO plugin to work properly
- **Installation:** Extract to Skyrim directory
- **Verify:** `skse64_loader.exe` should exist in Skyrim folder

---

## 🌱 **OPTIONAL - For Seasonal Support**

### 5. **Seasons of Skyrim** (Optional)
- **Download:** From Nexus Mods
- **Purpose:** Enables Winter/Spring/Summer/Autumn grass generation
- **Without this:** Can still generate universal grass cache
- **Install:** Via mod manager, configure seasons

### 6. **Grass Cache Helper NG** 🔥 **RECOMMENDED**
- **Download:** From Nexus Mods  
- **Purpose:** Loads the generated `.cgid` files in-game
- **Install:** SKSE plugin, install to Data/SKSE/Plugins/

---

## 📁 **WHAT THE AUTOMATION HANDLES**

### ✅ **Users DON'T Need To Do This** - Fully Automated:

- ❌ **Manual grass cache generation** (4+ hours of clicking)
- ❌ **File renaming** (`.cgid` → `.WIN.cgid`, etc.)
- ❌ **Configuration switching** (seasonal settings)
- ❌ **Process monitoring** (crash detection, resume)
- ❌ **Archive creation** (mod-ready ZIP files)
- ❌ **File cleanup** (removing processed files)
- ❌ **Progress tracking** (PrecacheGrass.txt monitoring)
- ❌ **Error handling** (timeout, hang detection)

---

## 🚀 **USAGE WORKFLOW**

### **Step 1: One-Time Setup**
1. Install Python 3.8+ ✅
2. Install Skyrim SE ✅  
3. Install NGIO mod ✅
4. Install SKSE64 ✅
5. (Optional) Install Seasons of Skyrim ✅
6. (Optional) Install Grass Cache Helper NG ✅

### **Step 2: Download & Run Automation**
1. Download `ngio-automation-suite-X.X.X-portable.zip`
2. Extract anywhere on your computer
3. Run `start_ngio_automation.bat`
4. Follow the configuration wizard (first-time only)
5. Select your season (Winter/Spring/Summer/Autumn)
6. Let automation run (20-60 minutes per season)
7. Install generated archive in mod manager

### **Step 3: Repeat for Other Seasons**
1. Run `start_ngio_automation.bat` again
2. Select different season
3. Automation handles everything else

---

## ⚠️ **COMMON USER MISTAKES**

### **Python Issues:**
- ❌ **Not adding Python to PATH** → Commands don't work
- ❌ **Installing Python 3.7 or older** → Compatibility issues
- ❌ **Multiple Python versions** → Version conflicts

### **Skyrim Issues:**
- ❌ **NGIO not installed/enabled** → No grass generation
- ❌ **SKSE not installed** → Plugin doesn't load
- ❌ **Wrong Skyrim path** → Can't find game files

### **Mod Manager Issues:**
- ❌ **NGIO disabled** → Generation fails
- ❌ **Seasons mod misconfigured** → Wrong season generated
- ❌ **Missing dependencies** → Mods don't work

---

## 🎯 **SUCCESS CRITERIA**

### **User Setup is Complete When:**
1. ✅ `python --version` shows 3.8+ in Command Prompt
2. ✅ Skyrim SE launches and runs normally
3. ✅ NGIO mod is enabled in mod manager
4. ✅ `skse64_loader.exe` exists in Skyrim directory
5. ✅ NGIO automation script runs without Python errors

### **Generation is Working When:**
1. ✅ Skyrim launches automatically from script
2. ✅ `PrecacheGrass.txt` appears in Skyrim directory
3. ✅ Cell count increases in console output
4. ✅ Archive is created in output directory
5. ✅ Script completes with success message

---

## 🆘 **TROUBLESHOOTING QUICK FIXES**

| Problem | Solution |
|---------|----------|
| `python: command not found` | Reinstall Python, check "Add to PATH" |
| `SKSE loader not found` | Download SKSE64, extract to Skyrim folder |
| `No grass generation` | Enable NGIO mod, check mod load order |
| `Skyrim won't launch` | Verify Skyrim path, run Skyrim manually first |
| `Permission denied` | Run as Administrator, check antivirus |
| `Archive not created` | Check output directory permissions |

---

## 📞 **SUPPORT**

- **Documentation:** Check `docs/` folder in release
- **Nexus Page:** [Link to Nexus mod page]
- **Issues:** Report on GitHub or Nexus
- **Requirements:** Always mention your Python version, Skyrim version, and mod setup

---

**Bottom Line:** Users need Python, Skyrim SE, NGIO mod, and SKSE64. Everything else is automated! 🚀
