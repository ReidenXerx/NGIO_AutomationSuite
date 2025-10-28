#!/usr/bin/env python3
"""
Game Manager - Skyrim Process Handler
Manages Skyrim process launching, monitoring, and crash recovery
"""

import os
import sys
import time
import subprocess
import psutil
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass

from ..utils.logger import Logger


@dataclass
class ProcessInfo:
    """Information about a running Skyrim process"""
    pid: int
    process: psutil.Process
    start_time: float
    command_line: List[str]


class GameManager:
    """
    Manages Skyrim game process for grass cache generation
    
    Key responsibilities:
    - Launch Skyrim with correct parameters for grass generation
    - Monitor process health and detect crashes
    - Handle process cleanup
    - Manage grass generation state files
    """
    
    def __init__(self, skyrim_path: str):
        self.skyrim_path = skyrim_path
        self.logger = Logger("GameManager")
        
        # Process tracking
        self.current_process: Optional[ProcessInfo] = None
        self.grass_cache_file = os.path.join(skyrim_path, "PrecacheGrass.txt")
        
        # Track if we deleted the file (to distinguish from plugin deletion)
        self._we_deleted_precache_file = False
        
        # Progress protection file to prevent accidental deletion
        self.progress_lock_file = os.path.join(skyrim_path, ".ngio_generation_active")
        
        # Startup time tracking for adaptive timeouts
        self.startup_history: List[float] = []
        self.average_startup_time: float = 180.0  # Default 3 minutes
        
        # Validate Skyrim executable
        self.skyrim_exe = self._find_skyrim_executable()
        if not self.skyrim_exe:
            raise ValueError(f"Skyrim executable not found in {skyrim_path}")
    
    def is_skyrim_already_running(self) -> Optional[psutil.Process]:
        """
        Check if Skyrim is already running
        
        Returns:
            psutil.Process if found, None otherwise
        """
        skyrim_process_names = [
            'SkyrimSE.exe',
            'SkyrimAE.exe', 
            'SkyrimVR.exe',
            'Skyrim.exe',
            'SKSE64_loader.exe',
            'sksevr_loader.exe',
            'skse_loader.exe'
        ]
        
        try:
            for proc in psutil.process_iter(['name', 'pid', 'create_time']):
                proc_name = proc.info['name']
                if proc_name and proc_name in skyrim_process_names:
                    self.logger.warning(f"⚠️ Skyrim already running: {proc_name} (PID: {proc.info['pid']})")
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
        return None
    
    def wait_for_skyrim_to_close(self, timeout_seconds: int = 60) -> bool:
        """
        Wait for existing Skyrim process to close
        
        Args:
            timeout_seconds: How long to wait
            
        Returns:
            bool: True if Skyrim closed, False if timeout
        """
        self.logger.info("⏳ Waiting for Skyrim to close...")
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if not self.is_skyrim_already_running():
                self.logger.info("✅ Skyrim closed successfully")
                return True
            time.sleep(2)
        
        self.logger.warning(f"⏰ Timeout waiting for Skyrim to close after {timeout_seconds}s")
        return False
    
    def track_startup_duration(self, duration: float) -> float:
        """
        Track startup duration and return recommended hang timeout
        
        Args:
            duration: Startup duration in seconds
            
        Returns:
            float: Recommended hang timeout (2x average startup time)
        """
        self.startup_history.append(duration)
        if len(self.startup_history) > 5:
            self.startup_history.pop(0)
        
        self.average_startup_time = sum(self.startup_history) / len(self.startup_history)
        recommended_timeout = self.average_startup_time * 2
        
        self.logger.debug(f"📊 Average startup: {self.average_startup_time:.1f}s, Recommended timeout: {recommended_timeout:.1f}s")
        return recommended_timeout
    
    def _find_skyrim_executable(self) -> Optional[str]:
        """Find the correct Skyrim executable, prioritizing SKSE loader"""
        # SKSE loaders (preferred for NGIO functionality)
        skse_loaders = [
            "skse64_loader.exe",  # SKSE64 for SE/AE
            "sksevr_loader.exe",  # SKSE VR
            "skse_loader.exe"     # Original SKSE (LE)
        ]
        
        # Check for SKSE loaders first
        for loader in skse_loaders:
            loader_path = os.path.join(self.skyrim_path, loader)
            if os.path.exists(loader_path):
                self.logger.info(f"✅ Found SKSE loader: {loader}")
                self.logger.info("🔧 SKSE will be used for proper NGIO plugin support")
                return loader_path
        
        # Fallback to direct executables (not recommended for NGIO)
        direct_executables = [
            "SkyrimSE.exe",
            "SkyrimAE.exe", 
            "SkyrimVR.exe",
            "Skyrim.exe"
        ]
        
        for exe in direct_executables:
            exe_path = os.path.join(self.skyrim_path, exe)
            if os.path.exists(exe_path):
                self.logger.warning(f"⚠️ Using direct executable: {exe}")
                self.logger.warning("⚠️ SKSE loader not found - NGIO may not work properly")
                self.logger.warning("💡 Install SKSE64 for full NGIO functionality")
                return exe_path
                
        return None
    
    def launch_for_generation(self, is_retry: bool = False) -> Optional[ProcessInfo]:
        """
        Launch Skyrim configured for grass cache generation
        
        Returns:
            ProcessInfo if successful, None if failed
        """
        self.logger.info("🎮 Preparing to launch Skyrim for grass generation...")
        
        # Check if Skyrim is already running (prevents death loop)
        existing_process = self.is_skyrim_already_running()
        if existing_process:
            self.logger.warning("⚠️ Skyrim is already running!")
            self.logger.info("   This could cause crashes if we launch another instance.")
            self.logger.info("   Waiting for existing instance to close...")
            
            # Wait for it to close (with timeout)
            if not self.wait_for_skyrim_to_close(timeout_seconds=120):
                self.logger.error("❌ Skyrim did not close in time")
                self.logger.error("   Please close Skyrim manually and try again")
                return None
            
            # Add brief delay after closure
            self.logger.info("⏳ Brief cooldown period...")
            time.sleep(5)
        
        # Ensure PrecacheGrass.txt exists to trigger generation
        # Check for existing active generation
        if self._has_active_generation() and not is_retry:
            self.logger.warning("🔒 Previous generation appears to have been interrupted!")
            self.logger.warning("   Progress protection lock found - this indicates forced termination")
            
        if not self._create_precache_trigger(is_retry):
            return None
            
        # Cleanup any existing Skyrim processes
        self._cleanup_existing_processes()
        
        # Launch Skyrim
        try:
            self.logger.info(f"🚀 Launching: {self.skyrim_exe}")
            
            process = subprocess.Popen(
                [self.skyrim_exe],
                cwd=self.skyrim_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Handle SKSE loader vs direct executable differently
            if "skse" in self.skyrim_exe.lower():
                # SKSE loader will terminate itself and spawn the actual Skyrim process
                self.logger.info("⏳ SKSE loader started, waiting for Skyrim process to spawn...")
                
                # Wait for SKSE loader to finish and Skyrim to start
                time.sleep(5)
                
                # Find the actual Skyrim process that SKSE spawned
                skyrim_process = self._find_skyrim_process()
                if not skyrim_process:
                    self.logger.error("❌ SKSE loader completed but Skyrim process not found")
                    self.logger.error("💡 Possible causes:")
                    self.logger.error("   • SKSE version mismatch with Skyrim")
                    self.logger.error("   • Missing Visual C++ Redistributables")
                    self.logger.error("   • Antivirus blocking Skyrim launch")
                    self.logger.error("   • Missing NGIO plugin files")
                    return None
                
                # Use the spawned Skyrim process
                self.current_process = ProcessInfo(
                    pid=skyrim_process.pid,
                    process=skyrim_process,
                    start_time=time.time(),
                    command_line=skyrim_process.cmdline()
                )
                
                self.logger.info(f"✅ Skyrim launched successfully (PID: {skyrim_process.pid})")
                
            else:
                # Direct executable launch
                time.sleep(3)
                
                # Verify it's still running
                if process.poll() is not None:
                    exit_code = process.returncode
                    self.logger.error(f"❌ Skyrim process terminated immediately (exit code: {exit_code})")
                    return None
                
                # Create ProcessInfo for direct launch
                psutil_process = psutil.Process(process.pid)
                self.current_process = ProcessInfo(
                    pid=process.pid,
                    process=psutil_process,
                    start_time=time.time(),
                    command_line=psutil_process.cmdline()
                )
                
                self.logger.info(f"✅ Skyrim launched successfully (PID: {process.pid})")
                
            return self.current_process
            
        except Exception as e:
            self.logger.error(f"💥 Failed to launch Skyrim: {e}")
            return None
    
    def _create_precache_trigger(self, is_retry: bool = False) -> bool:
        """Create or preserve PrecacheGrass.txt to trigger grass generation"""
        try:
            # Check if we have existing grass cache files (indicating previous completion)
            grass_cache_exists = self._has_existing_grass_cache()
            precache_file_exists = os.path.exists(self.grass_cache_file)
            
            # SCENARIO 1: No PrecacheGrass.txt + Grass cache exists = Previous completion
            if not precache_file_exists and grass_cache_exists:
                self.logger.info("✅ Previous grass generation completed successfully!")
                self.logger.info("🌱 Found existing grass cache files, no PrecacheGrass.txt")
                self.logger.info("🔄 Creating fresh trigger for new season/generation...")
                
                # Create new trigger file for this generation
                with open(self.grass_cache_file, 'w') as f:
                    f.write("")  # Empty file is sufficient
                self.logger.info(f"✅ Created fresh grass cache trigger: {self.grass_cache_file}")
                return True
            
            # SCENARIO 2: PrecacheGrass.txt exists (interrupted generation)
            if precache_file_exists:
                if is_retry:
                    # File exists from previous attempt - preserve it for resume!
                    status = self.check_precache_file_status()
                    self.logger.info(f"🔄 Found existing PrecacheGrass.txt with {status['content_lines']} cells - will resume")
                    return True
                else:
                    # First attempt but file exists - ask user what to do
                    status = self.check_precache_file_status()
                    if status['content_lines'] > 0:
                        return self._handle_existing_progress(status)
                    else:
                        # Empty file - safe to remove
                        self.logger.info("🗑️ Removing empty PrecacheGrass.txt from previous session")
                        self._we_deleted_precache_file = True
                        os.remove(self.grass_cache_file)
            
            # SCENARIO 3: No PrecacheGrass.txt + No grass cache = First time
            # Create new empty trigger file
            with open(self.grass_cache_file, 'w') as f:
                f.write("")  # Empty file is sufficient
                
            if grass_cache_exists:
                self.logger.info("✅ Created grass cache trigger (will overwrite existing cache)")
            else:
                self.logger.info("✅ Created fresh grass cache trigger (first generation)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create grass cache trigger: {e}")
            return False
    
    def _handle_existing_progress(self, status: dict) -> bool:
        """Handle existing PrecacheGrass.txt with progress"""
        self.logger.warning("⚠️ Found existing grass generation progress!")
        self.logger.warning(f"   📊 {status['content_lines']} cells already processed")
        self.logger.warning(f"   📁 File size: {status['size']} bytes")
        
        self.logger.info("")
        self.logger.info("🤔 This could be:")
        self.logger.info("   1. Script restarted after a glitch (RESUME generation)")
        self.logger.info("   2. New season generation (START from scratch)")
        self.logger.info("")
        
        while True:
            try:
                choice = input("Resume existing progress or start fresh? (r/f): ").strip().lower()
                
                if choice in ['r', 'resume']:
                    self.logger.info("🔄 Resuming existing generation progress...")
                    return True
                elif choice in ['f', 'fresh']:
                    self.logger.info("🗑️ Starting fresh - removing existing progress...")
                    self._we_deleted_precache_file = True
                    os.remove(self.grass_cache_file)
                    return True
                else:
                    self.logger.error("Please enter 'r' to resume or 'f' for fresh start")
                    
            except KeyboardInterrupt:
                self.logger.warning("⚠️ Operation cancelled by user")
                return False
            except Exception as e:
                self.logger.error(f"Input error: {e}")
                continue
    
    def _cleanup_existing_processes(self) -> None:
        """Kill any existing Skyrim processes"""
        skyrim_processes = self._find_skyrim_processes()
        
        if skyrim_processes:
            self.logger.info(f"🧹 Terminating {len(skyrim_processes)} existing Skyrim processes...")
            
            for proc in skyrim_processes:
                try:
                    proc.terminate()
                    proc.wait(timeout=10)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try:
                        proc.kill()
                    except psutil.NoSuchProcess:
                        pass
                        
            time.sleep(2)  # Allow processes to fully terminate
    
    def _find_skyrim_processes(self) -> List[psutil.Process]:
        """Find all running Skyrim processes"""
        skyrim_processes = []
        skyrim_names = ["SkyrimSE.exe", "SkyrimAE.exe", "SkyrimVR.exe", "Skyrim.exe"]
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in skyrim_names:
                    skyrim_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return skyrim_processes
    
    def is_process_running(self) -> bool:
        """Check if current Skyrim process is still running"""
        if not self.current_process:
            return False
            
        try:
            # If we launched SKSE loader, check for the actual Skyrim process
            if "skse" in self.skyrim_exe.lower():
                return self._is_skyrim_game_running()
            else:
                # Direct executable launch
                return self.current_process.process.is_running()
        except psutil.NoSuchProcess:
            return False
    
    def _is_skyrim_game_running(self) -> bool:
        """Check if the actual Skyrim game process is running (when launched via SKSE)"""
        skyrim_process_names = ["SkyrimSE.exe", "SkyrimAE.exe", "SkyrimVR.exe", "Skyrim.exe"]
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in skyrim_process_names:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def get_process_status(self) -> dict:
        """Get detailed status information about current process"""
        if not self.current_process or not self.is_process_running():
            return {"running": False}
            
        try:
            proc = self.current_process.process
            
            # Get memory and CPU usage
            memory_info = proc.memory_info()
            cpu_percent = proc.cpu_percent(interval=1)
            
            # Calculate uptime
            uptime = time.time() - self.current_process.start_time
            
            return {
                "running": True,
                "pid": self.current_process.pid,
                "uptime_seconds": uptime,
                "memory_mb": memory_info.rss / (1024 * 1024),
                "cpu_percent": cpu_percent,
                "status": proc.status()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting process status: {e}")
            return {"running": False, "error": str(e)}
    
    def detect_crash(self) -> bool:
        """
        Detect if Skyrim has crashed or terminated unexpectedly
        
        Returns:
            True if crashed, False if still running normally
        """
        if not self.current_process:
            return True
            
        try:
            proc = self.current_process.process
            
            # Check if process is still running
            if not proc.is_running():
                exit_code = proc.wait()  # Get exit code
                
                # Log crash information
                uptime = time.time() - self.current_process.start_time
                self.logger.warning(f"💥 Skyrim process terminated (PID: {self.current_process.pid})")
                self.logger.warning(f"   Exit code: {exit_code}")
                self.logger.warning(f"   Uptime: {uptime:.1f} seconds")
                
                return True
                
            # Check for zombie/unresponsive state
            if proc.status() == psutil.STATUS_ZOMBIE:
                self.logger.warning("🧟 Skyrim process is in zombie state")
                return True
                
            return False
            
        except psutil.NoSuchProcess:
            self.logger.warning("👻 Skyrim process no longer exists")
            return True
        except Exception as e:
            self.logger.error(f"Error detecting crash: {e}")
            return True
    
    def detect_hang(self, timeout_minutes: int = 10) -> bool:
        """
        Detect if Skyrim is hanging/frozen
        
        Args:
            timeout_minutes: How long to wait for CPU activity
            
        Returns:
            True if process appears hung, False if active
        """
        if not self.is_process_running():
            return False
            
        try:
            proc = self.current_process.process
            
            # Monitor CPU usage over time to detect hangs
            cpu_samples = []
            sample_interval = 2  # seconds
            num_samples = min(5, (timeout_minutes * 60) // sample_interval)
            
            for _ in range(num_samples):
                cpu_percent = proc.cpu_percent(interval=sample_interval)
                cpu_samples.append(cpu_percent)
                
                # If we see any significant CPU usage, it's not hung
                if cpu_percent > 5:
                    return False
                    
            # Check memory usage changes (another sign of activity)
            initial_memory = proc.memory_info().rss
            time.sleep(5)
            final_memory = proc.memory_info().rss
            memory_change = abs(final_memory - initial_memory)
            
            # If memory usage is changing significantly, process is active
            if memory_change > 1024 * 1024:  # 1MB threshold
                return False
                
            # If CPU is consistently low and memory stable, likely hung
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            if avg_cpu < 2:
                self.logger.warning(f"🔒 Skyrim appears hung (avg CPU: {avg_cpu:.1f}%)")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting hang: {e}")
            return False
    
    def force_terminate(self) -> bool:
        """Force terminate the current Skyrim process and any related processes"""
        success = True
        
        # If we launched via SKSE, terminate all related processes
        if self.current_process and "skse" in self.skyrim_exe.lower():
            success &= self._terminate_skse_and_skyrim_processes()
        elif self.current_process:
            success &= self._terminate_single_process(self.current_process.process)
            
        self.current_process = None
        return success
    
    def _terminate_skse_and_skyrim_processes(self) -> bool:
        """Terminate both SKSE loader and actual Skyrim processes"""
        success = True
        terminated_processes = []
        
        # Find and terminate all Skyrim-related processes
        skyrim_process_names = ["SkyrimSE.exe", "SkyrimAE.exe", "SkyrimVR.exe", "Skyrim.exe"]
        skse_process_names = ["skse64_loader.exe", "sksevr_loader.exe", "skse_loader.exe"]
        all_process_names = skyrim_process_names + skse_process_names
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in all_process_names:
                    self.logger.warning(f"🔪 Force terminating {proc.info['name']} (PID: {proc.info['pid']})")
                    success &= self._terminate_single_process(proc)
                    terminated_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if terminated_processes:
            self.logger.info(f"✅ Terminated processes: {', '.join(terminated_processes)}")
        else:
            self.logger.info("✅ No Skyrim processes found to terminate")
            
        return success
    
    def _terminate_single_process(self, proc: psutil.Process) -> bool:
        """Terminate a single process gracefully, then forcefully if needed"""
        try:
            if proc.is_running():
                # Try graceful termination first
                proc.terminate()
                
                try:
                    proc.wait(timeout=10)
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    self.logger.warning("⚡ Graceful termination failed, force killing...")
                    proc.kill()
                    proc.wait()
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error force terminating process: {e}")
            return False
    
    def _find_skyrim_process(self) -> Optional[psutil.Process]:
        """Find the actual Skyrim game process (used after SKSE launch)"""
        skyrim_process_names = ["SkyrimSE.exe", "SkyrimAE.exe", "SkyrimVR.exe", "Skyrim.exe"]
        
        # Look for Skyrim processes, preferring the most recently started one
        found_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                if proc.info['name'] in skyrim_process_names:
                    found_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not found_processes:
            return None
        
        # Return the most recently started process
        return max(found_processes, key=lambda p: p.create_time())
    
    def check_precache_file_status(self) -> dict:
        """
        Check the status of PrecacheGrass.txt file for generation progress
        
        Returns:
            dict: Status information about the precache file
        """
        status = {
            "exists": False,
            "size": 0,
            "modified_time": 0,
            "content_lines": 0,
            "last_cell": "",
            "is_active": False
        }
        
        try:
            if os.path.exists(self.grass_cache_file):
                status["exists"] = True
                
                # Get file stats
                stat = os.stat(self.grass_cache_file)
                status["size"] = stat.st_size
                status["modified_time"] = stat.st_mtime
                
                # Read content to check progress
                with open(self.grass_cache_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    status["content_lines"] = len(lines)
                    
                    if lines:
                        # Get last processed cell
                        last_line = lines[-1].strip()
                        status["last_cell"] = last_line
                        
                        # File is active if it has content and was recently modified
                        time_since_modified = time.time() - status["modified_time"]
                        status["is_active"] = time_since_modified < 30  # Modified within 30 seconds
                        
        except Exception as e:
            self.logger.debug(f"Error checking precache file: {e}")
        
        return status
    
    def wait_for_precache_completion(self, timeout_minutes: int = 60) -> bool:
        """
        Wait for grass generation completion by monitoring PrecacheGrass.txt
        
        SMART TIMEOUT LOGIC:
        - If file is actively growing: NO timeout (can run indefinitely)
        - If no activity for 5+ minutes: Consider hung/crashed
        - Hard timeout only applies if no progress for extended period
        
        This prevents killing active long-running generations!
        
        Args:
            timeout_minutes: Maximum time to wait WITHOUT ACTIVITY
            
        Returns:
            bool: True if completed successfully, False if failed/timeout
        """
        self.logger.info("👁️ Monitoring PrecacheGrass.txt for completion...")
        self.logger.info(f"⏰ Will timeout after {timeout_minutes} minutes of NO ACTIVITY (active generation can run indefinitely)")
        
        # Reset deletion flag - we're starting fresh monitoring
        self._we_deleted_precache_file = False
        
        # Create progress protection lock
        self._create_progress_lock()
        
        start_time = time.time()
        last_size = 0
        last_modified = 0
        last_activity_time = start_time
        no_activity_timeout_seconds = timeout_minutes * 60
        
        # Track progress for user feedback
        progress_report_interval = 300  # Report every 5 minutes
        last_progress_report = start_time
        
        while True:  # No hard timeout - only activity-based timeout
            current_time = time.time()
            status = self.check_precache_file_status()
            
            if not status["exists"]:
                # File was deleted - but by whom?
                if self._we_deleted_precache_file:
                    # We deleted it during cleanup - this is NOT completion
                    self.logger.warning("🗑️ PrecacheGrass.txt was deleted by cleanup - generation interrupted")
                    return False
                else:
                    # Plugin deleted it - this means generation completed!
                    total_time = (current_time - start_time) / 60
                    self.logger.success(f"🎉 PrecacheGrass.txt deleted by plugin - Generation completed in {total_time:.1f} minutes!")
                    
                    # Remove progress protection lock
                    self._remove_progress_lock()
                    
                    # Additional verification: check if Skyrim is still running
                    if self.is_process_running():
                        self.logger.info("🎮 Skyrim still running after completion - will close automatically")
                    else:
                        self.logger.info("✅ Skyrim closed automatically after completion")
                    
                    return True
            
            # Check for file activity
            if status["size"] != last_size or status["modified_time"] != last_modified:
                # File is being updated - generation is ACTIVE
                last_activity_time = current_time  # Reset activity timer
                
                if status["content_lines"] > 0:
                    self.logger.info(f"📊 Processing: {status['content_lines']} cells completed")
                    if status["last_cell"]:
                        self.logger.debug(f"   Last cell: {status['last_cell']}")
                
                last_size = status["size"]
                last_modified = status["modified_time"]
            else:
                # No file changes detected - check for timeout
                time_since_activity = current_time - last_activity_time
                
                if time_since_activity > no_activity_timeout_seconds:
                    # No activity for too long - likely hung or crashed
                    self.logger.error(f"⏰ No activity for {timeout_minutes} minutes - generation appears hung")
                    
                    # Check if process is still running
                    if not self.is_process_running():
                        self.logger.warning("💥 Process not running and no activity - crashed")
                        return False
                    else:
                        self.logger.warning("🔒 Process running but no progress - likely hung")
                        return False
                elif time_since_activity > 300:  # 5 minutes no activity - warning only
                    minutes_inactive = time_since_activity / 60
                    self.logger.warning(f"⚠️ No activity for {minutes_inactive:.1f} minutes (will timeout at {timeout_minutes} minutes)")
            
            # Periodic progress report for long-running generations
            if current_time - last_progress_report > progress_report_interval:
                total_time = (current_time - start_time) / 60
                time_since_activity = (current_time - last_activity_time) / 60
                
                if time_since_activity < 1:
                    self.logger.info(f"⏱️ Generation running for {total_time:.1f} minutes - ACTIVE")
                else:
                    self.logger.info(f"⏱️ Generation running for {total_time:.1f} minutes - idle for {time_since_activity:.1f} minutes")
                
                last_progress_report = current_time
            
            # Brief sleep to avoid excessive file system checks
            time.sleep(5)
    
    def _create_progress_lock(self) -> None:
        """Create a lock file to indicate generation is active"""
        try:
            with open(self.progress_lock_file, 'w') as f:
                f.write(f"NGIO Generation Active - Started: {time.ctime()}\n")
                f.write("This file protects PrecacheGrass.txt from cleanup\n")
            self.logger.debug("🔒 Created progress protection lock")
        except Exception as e:
            self.logger.warning(f"Failed to create progress lock: {e}")
    
    def _remove_progress_lock(self) -> None:
        """Remove the progress lock file"""
        try:
            if os.path.exists(self.progress_lock_file):
                os.remove(self.progress_lock_file)
                self.logger.debug("🔓 Removed progress protection lock")
        except Exception as e:
            self.logger.warning(f"Failed to remove progress lock: {e}")
    
    def _has_active_generation(self) -> bool:
        """Check if there's an active generation (lock file exists)"""
        return os.path.exists(self.progress_lock_file)
    
    def _has_existing_grass_cache(self) -> bool:
        """Check if grass cache files exist from previous generation"""
        try:
            grass_dir = os.path.join(self.skyrim_path, "Data", "Grass")
            if not os.path.exists(grass_dir):
                return False
            
            # Look for .cgid files (grass cache files)
            cgid_files = []
            for root, dirs, files in os.walk(grass_dir):
                for file in files:
                    if file.endswith('.cgid'):
                        cgid_files.append(file)
            
            if cgid_files:
                self.logger.debug(f"🌱 Found {len(cgid_files)} existing grass cache files")
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Failed to check existing grass cache: {e}")
            return False
    
    def cleanup_processes(self) -> None:
        """Clean up all Skyrim-related processes and files"""
        self.logger.info("🧹 Cleaning up Skyrim processes and files...")
        
        # Terminate current process
        if self.current_process:
            self.force_terminate()
            
        # Clean up any remaining Skyrim processes
        self._cleanup_existing_processes()
        
        # Clean up grass cache trigger file (but preserve progress)
        try:
            if os.path.exists(self.grass_cache_file):
                status = self.check_precache_file_status()
                
                # Check if there's an active generation lock
                if self._has_active_generation():
                    self.logger.info("🔒 Active generation detected - preserving all progress files")
                    self.logger.info(f"💾 Preserving PrecacheGrass.txt with {status['content_lines']} cells")
                elif status['content_lines'] > 0:
                    self.logger.info(f"💾 Preserving PrecacheGrass.txt with {status['content_lines']} cells for resume")
                else:
                    self._we_deleted_precache_file = True
                    os.remove(self.grass_cache_file)
                    self.logger.info("🗑️ Removed empty grass cache trigger file")
            
            # Always try to remove the progress lock during cleanup
            self._remove_progress_lock()
            
        except Exception as e:
            self.logger.warning(f"Failed to clean grass cache trigger: {e}")
    
    def get_crash_logs(self) -> List[str]:
        """Get recent crash logs and dumps for analysis"""
        crash_info = []
        
        # Look for common crash log locations
        crash_locations = [
            os.path.join(self.skyrim_path, "Logs"),
            os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "My Games", "Skyrim Special Edition", "Logs"),
            os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "My Games", "Skyrim VR", "Logs"),
        ]
        
        for location in crash_locations:
            if os.path.exists(location):
                try:
                    for file in os.listdir(location):
                        if file.endswith(('.log', '.dmp')) and 'crash' in file.lower():
                            crash_info.append(os.path.join(location, file))
                except Exception:
                    continue
                    
        return crash_info[-5:]  # Return up to 5 most recent crash files
