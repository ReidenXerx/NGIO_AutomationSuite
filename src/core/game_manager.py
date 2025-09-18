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
        
        # Validate Skyrim executable
        self.skyrim_exe = self._find_skyrim_executable()
        if not self.skyrim_exe:
            raise ValueError(f"Skyrim executable not found in {skyrim_path}")
    
    def _find_skyrim_executable(self) -> Optional[str]:
        """Find the correct Skyrim executable"""
        possible_executables = [
            "SkyrimSE.exe",
            "SkyrimAE.exe", 
            "SkyrimVR.exe",
            "Skyrim.exe"
        ]
        
        for exe in possible_executables:
            exe_path = os.path.join(self.skyrim_path, exe)
            if os.path.exists(exe_path):
                self.logger.info(f"Found Skyrim executable: {exe}")
                return exe_path
                
        return None
    
    def launch_for_generation(self) -> Optional[ProcessInfo]:
        """
        Launch Skyrim configured for grass cache generation
        
        Returns:
            ProcessInfo if successful, None if failed
        """
        self.logger.info("🎮 Preparing to launch Skyrim for grass generation...")
        
        # Ensure PrecacheGrass.txt exists to trigger generation
        if not self._create_precache_trigger():
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
            
            # Give the process a moment to start
            time.sleep(3)
            
            # Verify it's still running
            if process.poll() is not None:
                self.logger.error("❌ Skyrim process terminated immediately")
                return None
                
            # Create ProcessInfo
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
    
    def _create_precache_trigger(self) -> bool:
        """Create PrecacheGrass.txt to trigger grass generation"""
        try:
            # Remove existing file if it exists
            if os.path.exists(self.grass_cache_file):
                os.remove(self.grass_cache_file)
                
            # Create new empty trigger file
            with open(self.grass_cache_file, 'w') as f:
                f.write("")  # Empty file is sufficient
                
            self.logger.info(f"✅ Created grass cache trigger: {self.grass_cache_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create grass cache trigger: {e}")
            return False
    
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
            return self.current_process.process.is_running()
        except psutil.NoSuchProcess:
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
        """Force terminate the current Skyrim process"""
        if not self.current_process:
            return True
            
        try:
            proc = self.current_process.process
            
            if proc.is_running():
                self.logger.warning(f"🔪 Force terminating Skyrim (PID: {self.current_process.pid})")
                
                # Try graceful termination first
                proc.terminate()
                
                try:
                    proc.wait(timeout=10)
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    self.logger.warning("⚡ Graceful termination failed, force killing...")
                    proc.kill()
                    proc.wait()
                    
            self.current_process = None
            return True
            
        except Exception as e:
            self.logger.error(f"Error force terminating process: {e}")
            return False
    
    def cleanup_processes(self) -> None:
        """Clean up all Skyrim-related processes and files"""
        self.logger.info("🧹 Cleaning up Skyrim processes and files...")
        
        # Terminate current process
        if self.current_process:
            self.force_terminate()
            
        # Clean up any remaining Skyrim processes
        self._cleanup_existing_processes()
        
        # Clean up grass cache trigger file
        try:
            if os.path.exists(self.grass_cache_file):
                os.remove(self.grass_cache_file)
                self.logger.info("🗑️ Removed grass cache trigger file")
        except Exception as e:
            self.logger.warning(f"Failed to remove grass cache trigger: {e}")
    
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
