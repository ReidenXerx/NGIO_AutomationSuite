# 🔍 NGIO Automation Suite - Detection Mechanisms

## Overview

The NGIO Automation Suite uses sophisticated detection mechanisms to reliably identify when Skyrim crashes and when grass generation completes for each season. This document explains the current production implementation of these systems.

**Key Features:**
- **Dual Timeout System**: Separate timeouts for process crashes (5min) and file inactivity (10min)
- **Smart Activity Monitoring**: Only triggers timeouts when no progress is detected
- **Progress Preservation**: Protects `PrecacheGrass.txt` and generated files during interruptions
- **SKSE Integration**: Proper handling of SKSE loader vs actual Skyrim process
- **Season Completion Detection**: Recognizes already-completed seasons at startup

---

## 🚨 **Crash Detection System (Dual Timeout)**

### **1. Process Crash Detection (5-minute timeout)**
```python
def is_process_running(self) -> bool:
    """Check if the current Skyrim process is still running"""
    if not self.current_process:
        return False
    
    try:
        if self.used_skse_loader and self.skyrim_process:
            # For SKSE launches, monitor the actual Skyrim process
            return self.skyrim_process.is_running()
        else:
            # For direct launches, monitor the original process
            return self.current_process.process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
```

**How it works:**
- Monitors if `SkyrimSE.exe` process is still running (not the SKSE loader)
- Detects immediate crashes when process terminates unexpectedly
- 5-minute timeout when process is not running
- Handles SKSE loader vs actual Skyrim process distinction

### **2. Activity-Based Timeout (10-minute no-progress timeout)**
```python
def wait_for_precache_completion(self, timeout_minutes: int = 10) -> tuple[bool, str]:
    """
    Wait for grass generation to complete by monitoring PrecacheGrass.txt
    Uses smart timeout that only triggers after no file activity
    """
    last_activity_time = time.time()
    no_activity_timeout_seconds = timeout_minutes * 60
    
    while True:
        # Check if process crashed (separate from file activity)
        if not self.is_process_running():
            return False, "Process crashed or terminated"
        
        status = self.check_precache_file_status()
        
        # Check if generation completed (file deleted by plugin)
        if not status['exists']:
            if not self._we_deleted_precache_file:
                self.logger.info("✅ PrecacheGrass.txt deleted by plugin - generation complete!")
                return True, "Completion detected"
        
        # Update activity time if file changed
        if status['exists'] and status['last_modified'] > last_activity_time:
            last_activity_time = status['last_modified']
            self.logger.info(f"📊 Progress: {status['content_lines']} cells processed")
        
        # Check for no-activity timeout (only if no recent file changes)
        if time.time() - last_activity_time > no_activity_timeout_seconds:
            return False, f"No progress for {timeout_minutes} minutes (file not updating)"
        
        time.sleep(5)  # Check every 5 seconds
```

**How it works:**
- Monitors `PrecacheGrass.txt` modification times for activity detection
- Only triggers timeout after 10 minutes of NO file updates
- Allows long-running generations to proceed indefinitely if still active
- Separate from process crash detection - handles hangs and stalls

---

## 🎯 **Season Completion Detection System**

### **1. Runtime Completion Detection**
```python
def wait_for_precache_completion(self, timeout_minutes: int = 10) -> tuple[bool, str]:
    """Primary completion detection via PrecacheGrass.txt deletion"""
    while True:
        status = self.check_precache_file_status()
        
        # Success: Plugin deleted the file after completion
        if not status['exists'] and not self._we_deleted_precache_file:
            self.logger.info("✅ PrecacheGrass.txt deleted by plugin - generation complete!")
            return True, "Completion detected"
```

**How it works:**
- NGIO plugin deletes `PrecacheGrass.txt` when generation completes
- Tool distinguishes between plugin deletion (success) and script deletion (cleanup)
- Immediate detection when completion occurs

### **2. Startup Completion Detection**
```python
def _is_season_completed(self, season: Season) -> bool:
    """Check if a season's grass cache generation is already completed"""
    try:
        # Check if PrecacheGrass.txt exists
        precache_file = os.path.join(self.config.skyrim_path, "PrecacheGrass.txt")
        if os.path.exists(precache_file):
            return False  # Still in progress or not started
        
        # Check for season-specific grass cache files
        grass_dir = os.path.join(self.config.skyrim_path, "Data", "Grass")
        if not os.path.exists(grass_dir):
            return False
        
        # Look for files with the season's extension
        season_files = []
        for root, dirs, files in os.walk(grass_dir):
            for file in files:
                if file.endswith(season.extension):
                    season_files.append(file)
        
        if season_files:
            self.logger.debug(f"🌱 Found {len(season_files)} {season.display_name} grass cache files")
            return True
        
        return False
    except Exception as e:
        self.logger.warning(f"Failed to check {season.display_name} completion status: {e}")
        return False
```

**How it works:**
- Checks for absence of `PrecacheGrass.txt` (no active generation)
- Verifies presence of season-specific `.cgid` files (e.g., `.WIN.cgid`)
- Prevents unnecessary re-generation of completed seasons
- Allows user to resume where they left off

## 🛡️ **Progress Preservation System**

### **1. Signal Handling**
```python
def emergency_shutdown(signum=None, frame=None):
    """Handle emergency shutdown while preserving progress"""
    if automation_suite:
        try:
            print("\n🚨 Emergency shutdown - preserving progress...")
            automation_suite._emergency_cleanup()
        except Exception as e:
            print(f"Error during emergency shutdown: {e}")
    sys.exit(1)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, emergency_shutdown)  # Ctrl+C
signal.signal(signal.SIGTERM, emergency_shutdown)  # Termination signal
atexit.register(emergency_shutdown)  # Normal exit
```

**How it works:**
- Catches Ctrl+C, termination signals, and normal exits
- Calls emergency cleanup to preserve `PrecacheGrass.txt`
- Ensures generated `.cgid` files are not lost

### **2. Progress Lock File System**
```python
def _create_progress_lock(self) -> None:
    """Create a lock file to indicate active generation"""
    try:
        with open(self.progress_lock_file, 'w') as f:
            f.write(f"NGIO generation started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"PID: {os.getpid()}\n")
    except Exception as e:
        self.logger.warning(f"Failed to create progress lock: {e}")

def cleanup_processes(self) -> None:
    """Clean up processes while preserving progress if interrupted"""
    if self._has_active_generation():
        self.logger.info("🔒 Active generation detected - preserving all progress files")
        # Don't delete PrecacheGrass.txt if generation was forcefully terminated
    else:
        # Normal cleanup
        if os.path.exists(self.grass_cache_file):
            os.remove(self.grass_cache_file)
```

**How it works:**
- Creates `.ngio_generation_active` lock file when generation starts
- If script is forcefully terminated (e.g., closing terminal), lock remains
- On next cleanup, detects lock and preserves `PrecacheGrass.txt`
- Prevents accidental progress loss from forceful termination

### **3. Resume Functionality**
```python
def _handle_existing_progress(self, status: dict) -> bool:
    """Handle existing PrecacheGrass.txt with progress"""
    self.logger.warning("⚠️ Found existing grass generation progress!")
    self.logger.warning(f"   📊 {status['content_lines']} cells already processed")
    
    while True:
        choice = input("Resume existing progress or start fresh? (r/f): ").strip().lower()
        
        if choice in ['r', 'resume']:
            self.logger.info("🔄 Resuming existing generation progress...")
            return True
        elif choice in ['f', 'fresh']:
            self.logger.info("🗑️ Starting fresh - removing existing progress...")
            os.remove(self.grass_cache_file)
            return True
```

**How it works:**
- Detects existing `PrecacheGrass.txt` with content on startup
- Prompts user to resume from where they left off or start fresh
- Preserves user choice and prevents accidental progress loss

## 🔧 **SKSE Integration System**

### **SKSE Loader Handling**
```python
def launch_for_generation(self, is_retry: bool = False) -> Optional[ProcessInfo]:
    """Launch Skyrim via SKSE loader and monitor actual Skyrim process"""
    process = subprocess.Popen([self.skyrim_exe])  # Launch skse64_loader.exe
    
    if "skse" in self.skyrim_exe.lower():
        # SKSE loader will terminate itself and spawn Skyrim
        time.sleep(5)  # Wait for SKSE to launch Skyrim
        
        # Find the actual Skyrim process that SKSE spawned
        skyrim_process = self._find_skyrim_process()
        if not skyrim_process:
            self.logger.error("❌ SKSE loader completed but Skyrim process not found")
            return None
        
        # Monitor the spawned Skyrim process, not the SKSE loader
        self.current_process = ProcessInfo(
            pid=skyrim_process.pid,
            process=skyrim_process,
            start_time=time.time(),
            command_line=skyrim_process.cmdline()
        )
```

**How it works:**
- Launches `skse64_loader.exe` which terminates after spawning Skyrim
- Waits for SKSE to complete and finds the actual `SkyrimSE.exe` process
- Monitors the correct process for crash detection
- Handles both SKSE and direct executable launches

---

## 📊 **Complete Generation Workflow**

### **Single Season Workflow (Current Implementation)**
```
1. 🔍 Startup Detection
   ├── Check if season already completed (_is_season_completed)
   ├── If completed: Skip to post-processing
   └── If not: Proceed to generation

2. 🎮 Game Launch
   ├── Create/preserve PrecacheGrass.txt (_create_precache_trigger)
   ├── Launch Skyrim via SKSE (launch_for_generation)
   ├── Find actual Skyrim process (_find_skyrim_process)
   └── Create progress lock file (_create_progress_lock)

3. 📊 Progress Monitoring
   ├── Monitor PrecacheGrass.txt for updates (wait_for_precache_completion)
   ├── Check process running status (is_process_running)
   ├── Dual timeout system (5min crash, 10min no-progress)
   └── Log progress updates in real-time

4. ✅ Completion Detection
   ├── Plugin deletes PrecacheGrass.txt (success)
   ├── Process crash detected (retry)
   ├── No-progress timeout (retry)
   └── Maximum retries reached (failure)

5. 📁 Post-Processing
   ├── Process generated files (_process_generated_files)
   ├── Rename files with season extensions (.cgid → .WIN.cgid)
   ├── Create mod archive (_create_single_season_archive)
   ├── Clean up season files (_cleanup_season_files)
   └── Remove progress lock (_remove_progress_lock)

6. 🔄 Multi-Season Support
   ├── User runs script again for next season
   ├── Each season processed independently
   └── Optimal disk space management
```

### **Error Handling & Recovery**
- **Process Crashes**: Automatic restart with progress preservation
- **Hangs/Stalls**: Activity-based timeout with retry
- **Script Interruption**: Signal handlers preserve all progress
- **Forceful Termination**: Progress lock system prevents data loss
- **Resume Capability**: User choice to continue or start fresh

### **Key Advantages**
- **Reliability**: Multiple detection methods with fallbacks
- **Performance**: Activity-based timeouts allow long generations
- **Safety**: Progress preservation prevents data loss
- **User-Friendly**: Clear prompts and automatic handling
- **Efficiency**: Single-season workflow optimizes disk usage

---

## 🎯 **Summary**

The NGIO Automation Suite uses a sophisticated multi-layered approach to ensure reliable grass cache generation:

1. **Dual Timeout System**: Separates process crashes from file inactivity
2. **Smart Activity Monitoring**: Only triggers timeouts when no progress is detected
3. **Progress Preservation**: Protects user progress during any type of interruption
4. **SKSE Integration**: Properly handles SKSE loader vs actual Skyrim process
5. **Season Completion Detection**: Avoids unnecessary re-generation
6. **Single-Season Workflow**: Optimizes performance and disk usage

This robust system transforms the unreliable manual NGIO process into a fully automated, set-and-forget solution that users can trust to complete successfully.
