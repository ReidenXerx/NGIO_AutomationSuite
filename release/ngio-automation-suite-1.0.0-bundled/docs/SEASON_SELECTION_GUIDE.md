# 🌱 Season Selection Guide - NGIO Automation Suite

## Overview

The NGIO Automation Suite supports flexible season selection to accommodate different user setups and preferences. Whether you use seasonal mods or not, the tool can generate exactly what you need.

---

## 🌿 **Mode Selection**

### **1. Seasonal Mode (Default)**
- **For users with**: Seasons of Skyrim, True Seasons, or similar seasonal mods
- **Generates**: Separate grass cache for each selected season
- **Files created**: `.WIN.cgid`, `.SPR.cgid`, `.SUM.cgid`, `.AUT.cgid`
- **Configuration**: Modifies `po3_SeasonsOfSkyrim.ini` for each season

### **2. Non-Seasonal Mode**
- **For users without**: Any seasonal mods
- **Generates**: Single universal grass cache
- **Files created**: `.cgid` (standard naming)
- **Configuration**: No seasonal config modifications needed

---

## 🎯 **Season Selection Options**

### **Option 1: All Seasons (Default)**
```
Selected: Winter, Spring, Summer, Autumn
Time: ~2-4 hours total
Archives: 4 separate mod archives
Best for: Complete seasonal coverage
```

### **Option 2: Custom Selection**
```
Example: Winter ✓, Spring ✗, Summer ✓, Autumn ✗
Selected: Winter, Summer only
Time: ~1-2 hours total  
Archives: 2 mod archives
Best for: Specific season preferences
```

### **Option 3: Popular Combinations**

#### **Winter + Summer** (Most Popular)
```
Covers: Cold and warm seasons
Time: ~1-2 hours
Use case: Maximum contrast between seasons
```

#### **Spring + Autumn** 
```
Covers: Transitional seasons
Time: ~1-2 hours  
Use case: Moderate seasonal variation
```

#### **Winter + Spring**
```
Covers: Cold to moderate transition
Time: ~1-2 hours
Use case: Early year seasons
```

#### **Summer + Autumn**
```
Covers: Warm to cool transition  
Time: ~1-2 hours
Use case: Late year seasons
```

---

## 🔧 **Configuration Examples**

### **Seasonal User - All Seasons**
```
🌿 Do you use seasonal mods? y
🌱 Which seasons to generate?
   Choice: 1 (All seasons)

Result: Winter, Spring, Summer, Autumn
Output: 4 mod archives
```

### **Seasonal User - Winter + Summer Only**
```
🌿 Do you use seasonal mods? y  
🌱 Which seasons to generate?
   Choice: 3 (Specific combinations)
   Choose combination: a (Winter + Summer)

Result: Winter, Summer
Output: 2 mod archives
```

### **Non-Seasonal User**
```
🌿 Do you use seasonal mods? n
✅ Configured for non-seasonal grass cache generation

Result: Single grass cache generation
Output: 1 mod archive
```

### **Custom Selection Example**
```
🌿 Do you use seasonal mods? y
🌱 Which seasons to generate?
   Choice: 2 (Custom selection)
   Include Winter? y
   Include Spring? n  
   Include Summer? y
   Include Autumn? n

Result: Winter, Summer
Output: 2 mod archives  
```

---

## 📦 **Output Structure**

### **Seasonal Mode Output**
```
Generated_Mods/
├── Grass_Cache_Winter_Season.zip
│   └── Data/Grass/*.WIN.cgid
├── Grass_Cache_Summer_Season.zip  
│   └── Data/Grass/*.SUM.cgid
└── INSTALLATION_GUIDE.txt
```

### **Non-Seasonal Mode Output**
```
Generated_Mods/
├── Grass_Cache_Universal.zip
│   └── Data/Grass/*.cgid
└── INSTALLATION_GUIDE.txt
```

---

## ⏱️ **Time Estimates**

| Selection | Estimated Time | Archives Created |
|-----------|---------------|------------------|
| All 4 Seasons | 2-4 hours | 4 archives |
| 3 Seasons | 1.5-3 hours | 3 archives |
| 2 Seasons | 1-2 hours | 2 archives |  
| 1 Season | 30-60 minutes | 1 archive |
| Non-Seasonal | 30-60 minutes | 1 archive |

*Times vary based on mod count, worldspace size, and system performance*

---

## 🎯 **Use Case Recommendations**

### **First Time Users**
- **Recommendation**: Winter + Summer combination
- **Why**: Good coverage, reasonable time investment
- **Command**: Choose option 3a during setup

### **Performance Testing**
- **Recommendation**: Single season (Winter)
- **Why**: Quick test to verify everything works
- **Command**: Custom selection, Winter only

### **Complete Coverage**
- **Recommendation**: All seasons
- **Why**: Maximum flexibility for different playthroughs
- **Command**: Default option 1

### **Non-Seasonal Setups**
- **Recommendation**: Non-seasonal mode
- **Why**: No seasonal mods = no need for seasonal cache
- **Command**: Answer 'n' to seasonal mods question

### **Mod Testing**
- **Recommendation**: Single season
- **Why**: Quick iteration for testing mod combinations
- **Command**: Custom selection, one season

---

## 🔄 **Changing Selection Later**

You can always change your season selection:

1. **Run the tool again**
2. **Choose option 2: Configure Paths and Settings**
3. **Update your preferences**
4. **Your settings are automatically saved**

---

## 🛠️ **Technical Details**

### **Season Type Mapping**
```python
Season Types:
0 = No Seasons (non-seasonal mode)
1 = Winter  
2 = Spring
3 = Summer
4 = Autumn
5 = Seasonal (restoration mode)
```

### **File Extensions**
```
.cgid      = Non-seasonal/standard
.WIN.cgid  = Winter
.SPR.cgid  = Spring  
.SUM.cgid  = Summer
.AUT.cgid  = Autumn
```

### **Configuration Changes**
- **Seasonal Mode**: Modifies `po3_SeasonsOfSkyrim.ini` for each season
- **Non-Seasonal**: No configuration changes needed
- **Restoration**: Sets season type back to 5 (seasonal) when complete

---

## 💡 **Tips and Best Practices**

### **For New Users**
1. Start with 1-2 seasons to test your setup
2. Use Winter + Summer for maximum variety
3. Verify output before generating all seasons

### **For Experienced Users**  
1. Custom selections save significant time
2. Non-seasonal mode works great without seasonal mods
3. You can mix and match based on your current playthrough

### **For Mod Authors/Testers**
1. Single season generation for quick iteration
2. Non-seasonal mode for universal compatibility testing
3. All seasons for comprehensive mod validation

---

## 🚨 **Important Notes**

### **Seasonal Mods Required**
- If you select seasonal mode, you **must** have Seasons of Skyrim or similar
- The tool will validate this during setup
- Missing seasonal mods will cause generation to fail

### **Non-Seasonal Compatibility**
- Works with **any** grass mod setup
- No seasonal mod dependencies
- Single universal grass cache file
- Compatible with all mod managers

### **Archive Installation**
- Each selected season creates a separate installable mod archive
- Install only the seasons you want to use
- Disable NGIO after installing the archives
- Enable Grass Cache Helper NG for seasonal switching

---

This flexible system ensures the NGIO Automation Suite works perfectly for **every type of Skyrim setup**! 🌱✨
