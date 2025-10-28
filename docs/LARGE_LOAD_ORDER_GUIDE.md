# Large Load Order Configuration Guide

## For Users with 500+ Mods/Plugins

If you have a heavily modded Skyrim setup with hundreds of plugins, this guide will help you configure the NGIO Automation Suite for optimal stability and performance.

---

## Table of Contents

1. [Understanding the Challenge](#understanding-the-challenge)
2. [Automatic vs Manual Configuration](#automatic-vs-manual-configuration)
3. [Key Configuration Parameters](#key-configuration-parameters)
4. [Recommended Settings by Load Order Size](#recommended-settings-by-load-order-size)
5. [Preventing the "Death Loop"](#preventing-the-death-loop)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Tips](#advanced-tips)

---

## Understanding the Challenge

### Why Large Load Orders Are Different

With 500+ mods, Skyrim's startup time increases significantly:
- **Loading plugins**: More ESM/ESP files = longer initialization
- **Script initialization**: Complex mods with many scripts take time
- **Asset loading**: More textures, meshes, and resources to load
- **Conflict resolution**: More potential conflicts to resolve

**Typical Startup Times:**
- **< 100 plugins**: 30-60 seconds
- **100-300 plugins**: 1-3 minutes
- **300-500 plugins**: 3-5 minutes
- **500-1000 plugins**: 5-10 minutes
- **1000+ plugins**: 10-15+ minutes

### What Can Go Wrong

If your timeouts are too aggressive:
1. **"Death Loop"**: Script thinks Skyrim is hung, restarts it, but previous instance is still loading
2. **Multiple Instances**: Two Skyrim processes running → guaranteed crash
3. **Premature Termination**: Skyrim is actually fine, just loading slowly

---

## Automatic vs Manual Configuration

### ✅ Automatic (Recommended)

The suite now includes **adaptive timeout detection**:

```python
config = AutomationConfig(
    skyrim_path="C:/Games/Skyrim Special Edition",
    adaptive_timeouts=True  # <-- Enabled by default
)
```

**How it works:**
1. **First Launch**: Uses conservative defaults (3 minutes startup, 6 minutes hang detection)
2. **Learning**: Tracks your actual startup times
3. **Adaptation**: Adjusts timeouts based on your system's performance
4. **Optimization**: After 5 launches, timeouts are perfectly tuned for your setup

### 🔧 Manual (Advanced Users)

If you prefer explicit control:

```python
config = AutomationConfig(
    skyrim_path="C:/Games/Skyrim Special Edition",
    max_crash_retries=15,  # More retries for stability
    no_progress_timeout_minutes=20,  # Longer hang detection
    startup_wait_seconds=60,  # Longer wait between retries
    adaptive_timeouts=False  # Disable auto-adjustment
)
```

---

## Key Configuration Parameters

### 1. `max_crash_retries`

**What it does:** How many times to restart Skyrim if it crashes during generation.

**Default:** `10` (increased from 5 in v1.1.0)

**Recommendations:**
| Load Order Size | Recommended Value | Reasoning |
|----------------|-------------------|-----------|
| < 300 plugins  | 5-7               | Stable setups crash rarely |
| 300-500 plugins | 8-10             | Moderate complexity |
| 500-1000 plugins | 10-15           | High complexity, more crashes |
| 1000+ plugins | 15-20              | Maximum stability buffer |

**Example:**
```python
max_crash_retries=15  # For heavy load orders
```

### 2. `no_progress_timeout_minutes`

**What it does:** How long to wait with no file activity before considering Skyrim "hung".

**Default:** `15` minutes (increased from 10 in v1.1.0)

**Recommendations:**
| Load Order Size | Recommended Value | Reasoning |
|----------------|-------------------|-----------|
| < 300 plugins  | 10 minutes        | Fast startup |
| 300-500 plugins | 15 minutes        | Moderate startup |
| 500-1000 plugins | 20-25 minutes    | Slow startup |
| 1000+ plugins | 30+ minutes        | Very slow startup |

**Warning Signs You Need More:**
- Skyrim restarts before reaching main menu
- Log shows "Process appears hung" but Skyrim is loading normally
- You see loading screens when the restart happens

### 3. `startup_wait_seconds`

**What it does:** Base wait time between retry attempts (multiplied by retry number).

**Default:** `30` seconds

**How it scales:**
- **Retry 1**: 30 seconds
- **Retry 2**: 60 seconds  
- **Retry 3**: 90 seconds
- **Retry 4+**: 120 seconds (capped)

**Recommendations:**
| Load Order Size | Recommended Value |
|----------------|-------------------|
| < 500 plugins  | 30 seconds        |
| 500-1000 plugins | 45-60 seconds   |
| 1000+ plugins | 60-90 seconds      |

**Why this matters:**
- Prevents "death loop" where restarts happen too quickly
- Gives system time to clean up resources
- Allows previous Skyrim instance to fully terminate

### 4. `adaptive_timeouts`

**What it does:** Automatically learns and adjusts timeouts based on your system.

**Default:** `True` (enabled)

**When to disable:**
- You have very unpredictable startup times
- You want strict, consistent behavior
- You're troubleshooting timeout issues

---

## Recommended Settings by Load Order Size

### Small Load Order (< 300 plugins)

**Just use defaults!** The automatic settings work great.

```python
config = AutomationConfig(
    skyrim_path="C:/Games/Skyrim Special Edition",
    # All defaults are fine
)
```

### Medium Load Order (300-500 plugins)

```python
config = AutomationConfig(
    skyrim_path="C:/Games/Skyrim Special Edition",
    max_crash_retries=10,
    no_progress_timeout_minutes=15,
    startup_wait_seconds=40
)
```

### Large Load Order (500-1000 plugins)

```python
config = AutomationConfig(
    skyrim_path="C:/Games/Skyrim Special Edition",
    max_crash_retries=15,
    no_progress_timeout_minutes=20,
    startup_wait_seconds=60
)
```

### Massive Load Order (1000+ plugins)

```python
config = AutomationConfig(
    skyrim_path="C:/Games/Skyrim Special Edition",
    max_crash_retries=20,
    no_progress_timeout_minutes=30,
    startup_wait_seconds=90
)
```

---

## Preventing the "Death Loop"

### What is the Death Loop?

The "death loop" occurs when:
1. Skyrim is launching (slow, heavy load order)
2. Script thinks it's taking too long → kills it
3. Script launches Skyrim again
4. Previous instance **still loading** → two instances running
5. Crash guaranteed → repeat

### How We Prevent It (v1.1.0+)

#### 1. **Already Running Detection** ✅
The suite now checks if Skyrim is already running before launching:

```
⚠️ Skyrim already running: SkyrimSE.exe (PID: 12345)
   This could cause crashes if we launch another instance.
   Waiting for existing instance to close...
⏳ Waiting for Skyrim to close...
✅ Skyrim closed successfully
⏳ Brief cooldown period...
```

#### 2. **Intelligent Wait Times** ✅
Wait time increases with each retry:
- **First retry**: 30s wait
- **Second retry**: 60s wait
- **Third retry**: 90s wait
- **Fourth+ retry**: 120s wait (capped)

This gives Skyrim time to fully shut down before restarting.

#### 3. **Startup Time Tracking** ✅
The suite learns how long **your** Skyrim takes to start:

```
📊 Average startup: 287.3s, Recommended timeout: 574.6s
```

### Manual Prevention Steps

If you're still experiencing death loops:

1. **Increase `no_progress_timeout_minutes`**:
   ```python
   no_progress_timeout_minutes=25  # Or higher
   ```

2. **Increase `startup_wait_seconds`**:
   ```python
   startup_wait_seconds=60  # Double the default
   ```

3. **Monitor the first generation** carefully to see how long Skyrim actually takes to start.

---

## Troubleshooting

### Problem: Skyrim keeps restarting before reaching main menu

**Cause:** `no_progress_timeout_minutes` is too low for your load order.

**Solution:**
```python
no_progress_timeout_minutes=25  # Increase by 5-10 minutes
```

**How to diagnose:**
- Watch Skyrim's loading screens when restart happens
- If you see loading screens → timeout is too aggressive
- Check log for "Process appears hung"

### Problem: Multiple Skyrim instances running

**Cause:** Death loop due to aggressive timeouts.

**Solution:**
1. Close all Skyrim instances manually
2. Increase timeouts:
   ```python
   no_progress_timeout_minutes=20
   startup_wait_seconds=60
   ```
3. Restart generation

**Prevention:** v1.1.0+ includes automatic detection, but increase timeouts anyway.

### Problem: "Max retries exceeded" for certain worldspaces

**Cause:** Some worldspaces (complex areas) crash more often.

**Solution:**
```python
max_crash_retries=15  # Or higher
```

**Which worldspaces are problematic:**
- Tamriel (main worldspace) - **most complex**
- Solstheim (if you have Dragonborn)
- Large mod-added worldspaces

### Problem: Generation takes forever

**Cause:** Either your timeouts are too conservative, or generation is actually progressing slowly.

**Diagnosis:**
1. Check if `.cgid` files are growing in Skyrim directory
2. Look for "Processing" messages in log
3. Monitor Skyrim's CPU usage (should be 20-50% during generation)

**If files are growing:** Everything is fine, just slow. This is normal for large load orders.

**If files aren't growing:** Skyrim might actually be hung:
```python
no_progress_timeout_minutes=15  # Reduce timeout
```

---

## Advanced Tips

### 1. Test Manual Generation First

Before running full automation:
1. Create empty `PrecacheGrass.txt` in Skyrim folder
2. Launch Skyrim manually
3. Time how long it takes to reach main menu
4. Note if grass generation starts automatically

**Use this timing to set your timeout:**
```
Startup time × 2 = Recommended hang detection timeout
```

Example: 300s startup → 600s (10 minutes) hang detection

### 2. Monitor the First Season

The first season generation is **critical** for adaptive timeouts:
- Don't walk away during first generation
- Watch for restart patterns
- Check if timeouts seem appropriate
- Subsequent seasons will be better tuned

### 3. Use the Debug Log

Enable detailed logging to diagnose issues:
```python
from src.utils.logger import Logger
Logger.set_level("DEBUG")
```

Look for:
- `📊 Average startup:` messages
- `⏰ Timeout waiting for` warnings
- `⚠️ Skyrim already running` alerts

### 4. Worldspace-Specific Strategies

**For Tamriel (main worldspace):**
- Expect the most crashes here
- Reserve more retries for this season
- May take 4-6 hours for 1000+ plugins

**For Solstheim:**
- Usually more stable than Tamriel
- Fewer cells = faster generation
- But can still crash in complex areas

### 5. System Performance Optimization

**Before generation:**
- Close browser/Discord (free RAM)
- Disable antivirus real-time scanning (temporarily)
- Ensure Skyrim is on SSD for faster loading
- Close mod organizer after configuration

**During generation:**
- Don't use computer for other tasks
- Monitor RAM usage (should stay < 90%)
- Keep an eye on temperatures
- Check Skyrim process in Task Manager

### 6. Load Order Optimization

**Reduce crashes by:**
- Running LOOT to sort load order
- Checking for missing masters
- Resolving obvious conflicts with SSEEdit
- Disabling script-heavy mods temporarily (if possible)
- Ensuring SKSE and all SKSE plugins are up to date

---

## Real-World Example

**User Report (from setsofnumbers):**

> "I have a very big load order so sometimes when it tries to start up SKSE might try and open before the last attempt at opening my load order has completed, which will cause a crash"

**Analysis:**
- Large load order = slow startup (5-10+ minutes)
- Multiple restart attempts before previous instance loads fully
- Classic "death loop" scenario

**Solution (now implemented in v1.1.0+):**
1. ✅ Already running detection prevents multiple instances
2. ✅ Intelligent wait times (30s → 60s → 90s → 120s)
3. ✅ Startup tracking learns actual load times
4. ✅ Increased default retries (5 → 10)
5. ✅ Increased default hang timeout (10 → 15 minutes)

**User's Tip:**
> "make sure 1) your timer for 'hangs' is appropriate and 2) you have enough restarts to see you through buggier zones"

This is exactly what the new configuration system addresses!

---

## Quick Reference Card

```python
# 💾 Copy-paste configurations for different setups

# SMALL (< 300 plugins)
AutomationConfig(
    skyrim_path="...",
    # Use all defaults
)

# MEDIUM (300-500 plugins)
AutomationConfig(
    skyrim_path="...",
    max_crash_retries=10,
    no_progress_timeout_minutes=15,
    startup_wait_seconds=40
)

# LARGE (500-1000 plugins)
AutomationConfig(
    skyrim_path="...",
    max_crash_retries=15,
    no_progress_timeout_minutes=20,
    startup_wait_seconds=60
)

# MASSIVE (1000+ plugins)
AutomationConfig(
    skyrim_path="...",
    max_crash_retries=20,
    no_progress_timeout_minutes=30,
    startup_wait_seconds=90
)
```

---

## Need More Help?

1. **Check logs** in `logs/` directory
2. **Enable debug mode** for detailed information
3. **Report issues** with:
   - Your load order size (plugin count)
   - Observed startup time
   - At which point restarts occur
   - Full log file

Remember: Grass cache generation with large load orders is inherently challenging. The automation suite can't prevent all crashes, but it can intelligently handle them and resume progress!

🌱 **Happy grass generating!** 🌱

