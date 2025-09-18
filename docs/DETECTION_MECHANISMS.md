# 🔍 NGIO Automation Suite - Detection Mechanisms

## Overview

The NGIO Automation Suite uses sophisticated detection mechanisms to reliably identify when Skyrim crashes and when grass generation completes for each season. This document explains how these systems work.

---

## 🚨 **Crash Detection System**

### **1. Process Termination Detection**
```python
def detect_crash(self) -> bool:
    if not proc.is_running():
        exit_code = proc.wait()
        self.logger.warning(f"💥 Skyrim process terminated (PID: {pid})")
        self.logger.warning(f"   Exit code: {exit_code}")
        return True
```

**How it works:**
- Continuously monitors if `SkyrimSE.exe` process is still running
- Non-zero exit codes typically indicate crashes
- Logs crash details including uptime and exit code

### **2. Zombie Process Detection**
```python
if proc.status() == psutil.STATUS_ZOMBIE:
    self.logger.warning("🧟 Skyrim process is in zombie state")
    return True
```

**How it works:**
- Detects when process exists but is unresponsive
- Indicates severe crashes or system issues

### **3. Hang Detection**
```python
# Monitor CPU usage over time
for _ in range(5):
    cpu_percent = proc.cpu_percent(interval=2)
    if cpu_percent > 5:  # Still active
        return False

# Check memory changes
if memory_change > 1MB:  # Process still working
    return False
```

**How it works:**
- Samples CPU usage every 2 seconds for 10 seconds
- If CPU consistently < 1% and no memory changes = hung
- Triggers force restart after 5 minutes of no activity

---

## 🎯 **Season Completion Detection System**

### **Primary Method: PrecacheGrass.txt Monitoring** ⭐

This is the **most reliable** detection method based on NGIO's behavior:

#### **File Lifecycle:**
1. **Creation**: We create empty `PrecacheGrass.txt` next to `SkyrimSE.exe`
2. **Population**: NGIO plugin writes each processed cell to this file
3. **Deletion**: When complete, NGIO shows modal "Grass generation complete" and **deletes the file**
4. **Game Close**: Skyrim closes itself automatically

#### **Implementation:**
```python
def wait_for_precache_completion(self, timeout_minutes: int = 60) -> bool:
    while time.time() - start_time < timeout_seconds:
        status = self.check_precache_file_status()
        
        if not status["exists"]:
            # File deleted = Generation completed!
            self.logger.success("🎉 PrecacheGrass.txt deleted - Generation completed!")
            return True
        
        # Monitor file activity
        if status["size"] != last_size or status["modified_time"] != last_modified:
            self.logger.info(f"📊 Processing: {status['content_lines']} cells completed")
            last_size = status["size"]
            no_activity_start = None  # Reset timeout
```

#### **What We Monitor:**
- **File Existence**: Primary completion signal
- **File Size**: Tracks progress (grows as cells are processed)  
- **Modification Time**: Detects activity vs. hangs
- **Content Lines**: Shows how many cells have been completed
- **Last Cell**: Debug info showing current progress

#### **Activity Detection:**
- File size increases = generation active
- File modified recently = generation active  
- No changes for 5+ minutes = possible hang
- File deleted = **COMPLETION!**

### **Secondary Method: Console Output Parsing**

```python
self.patterns = {
    "completion": [
        "Grass generation complete",
        "Grass precache finished", 
        "All grass cache generated successfully"
    ]
}
```

**How it works:**
- Parses Skyrim console/log output for completion messages
- Less reliable than file monitoring but provides backup detection
- Used in conjunction with file monitoring

---

## 🔄 **Complete Detection Flow**

### **Season Generation Workflow:**

```
1. Set season in po3_SeasonsOfSkyrim.ini (Winter=1, Spring=2, etc.)
   ↓
2. Create empty PrecacheGrass.txt trigger file
   ↓  
3. Launch SkyrimSE.exe
   ↓
4. Monitor PrecacheGrass.txt:
   - File appears and starts growing ✅
   - Each line = one processed cell
   - File size increases regularly
   ↓
5. COMPLETION DETECTED:
   - PrecacheGrass.txt gets DELETED by NGIO
   - Skyrim shows "Grass generation complete" modal
   - Skyrim closes automatically
   ↓
6. Process generated .cgid files:
   - Rename: file.cgid → file.WIN.cgid (for Winter)
   - Create mod archive
   ↓
7. Move to next season (Spring=2) and repeat
```

### **Crash Recovery Workflow:**

```
1. Launch Skyrim for season generation
   ↓
2. Multiple monitoring systems active:
   - Process status monitoring
   - PrecacheGrass.txt file monitoring  
   - CPU/memory usage tracking
   ↓
3. CRASH DETECTED (any of):
   - Process terminated unexpectedly
   - PrecacheGrass.txt stopped growing for 5+ minutes
   - Process in zombie state
   - CPU < 1% for extended period
   ↓
4. RECOVERY ACTION:
   - Log crash details
   - Clean up processes and files
   - Wait 5 seconds
   - Retry (up to 5 attempts per season)
   ↓
5. SUCCESS or FAILURE:
   - Success: Continue to file processing
   - Max retries exceeded: Skip season, continue with next
```

---

## 🎯 **Key Advantages of This System**

### **Reliability:**
- **PrecacheGrass.txt deletion** is the most reliable completion signal
- Multiple fallback detection methods
- Handles all known crash scenarios

### **Precision:**
- Knows exactly when each season completes
- Can track progress within each season (cell count)
- Distinguishes between crashes, hangs, and completion

### **Robustness:**
- Automatic retry logic with intelligent backoff
- Graceful handling of edge cases
- Comprehensive logging for debugging

### **Performance:**
- Minimal system overhead (5-second check intervals)
- No heavy process scanning or memory inspection
- Efficient file monitoring

---

## 🛠️ **Technical Implementation Details**

### **File Status Checking:**
```python
def check_precache_file_status(self) -> dict:
    return {
        "exists": bool,           # File exists on disk
        "size": int,             # File size in bytes  
        "modified_time": float,   # Last modification timestamp
        "content_lines": int,     # Number of processed cells
        "last_cell": str,        # Last processed cell identifier
        "is_active": bool        # Recently modified (< 30 seconds)
    }
```

### **Retry Logic:**
- **Max Retries**: 5 attempts per season (configurable)
- **Retry Delay**: 5 seconds between attempts
- **Timeout**: 60 minutes per attempt (configurable)
- **Hang Detection**: 5 minutes of no file activity

### **Error Scenarios Handled:**
1. **Immediate Crash**: Process dies right after launch
2. **Mid-Generation Crash**: Process dies while generating
3. **Hang/Freeze**: Process alive but no progress
4. **Partial Generation**: Some cells processed, then crash
5. **File System Issues**: Permission errors, disk full, etc.

---

## 📊 **Monitoring Output Examples**

### **Successful Generation:**
```
🎮 Launching Skyrim for Winter (attempt 1)
⏳ Waiting for grass generation to begin...
✅ PrecacheGrass.txt found - generation active
👁️ Monitoring PrecacheGrass.txt for completion...
📊 Processing: 1247 cells completed
📊 Processing: 2891 cells completed
📊 Processing: 4556 cells completed
🎉 PrecacheGrass.txt deleted - Generation completed!
🎉 Winter generation completed successfully!
```

### **Crash and Recovery:**
```
🎮 Launching Skyrim for Spring (attempt 1)
⏳ Waiting for grass generation to begin...
✅ PrecacheGrass.txt found - generation active
📊 Processing: 856 cells completed
💥 Process not running but file still exists
🔄 Retrying generation (attempt 2/5)
🎮 Launching Skyrim for Spring (attempt 2)
...
🎉 PrecacheGrass.txt deleted - Generation completed!
```

---

This detection system ensures **maximum reliability** while providing **detailed progress feedback** throughout the grass cache generation process! 🌱✨
