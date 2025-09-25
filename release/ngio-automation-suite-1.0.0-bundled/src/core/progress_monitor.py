#!/usr/bin/env python3
"""
Progress Monitor - Skyrim Console Output Parsing
Monitors Skyrim process and parses console output for grass generation progress
"""

import os
import time
import psutil
import subprocess
import threading
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import Logger


class GenerationState(Enum):
    """States of grass generation process"""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    GENERATING = "generating"
    COMPLETED = "completed"
    CRASHED = "crashed"
    HUNG = "hung"
    TIMEOUT = "timeout"


@dataclass
class GenerationProgress:
    """Progress information for grass generation"""
    state: GenerationState
    current_worldspace: str = ""
    processed_cells: int = 0
    total_cells: int = 0
    progress_percentage: float = 0.0
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0
    last_activity: float = 0.0


@dataclass
class MonitoringResult:
    """Result from monitoring a grass generation process"""
    completed: bool
    crashed: bool
    hung: bool
    timeout: bool
    final_progress: GenerationProgress
    crash_details: Optional[Dict] = None
    console_output: List[str] = None


class ProgressMonitor:
    """
    Monitors Skyrim process during grass cache generation
    
    Key responsibilities:
    - Parse console output for generation progress
    - Detect completion, crashes, and hangs
    - Track progress across worldspaces
    - Provide real-time status updates
    """
    
    def __init__(self):
        self.logger = Logger("ProgressMonitor")
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.progress_callback: Optional[Callable] = None
        
        # Progress tracking
        self.current_progress = GenerationProgress(GenerationState.NOT_STARTED)
        self.console_buffer: List[str] = []
        self.max_console_buffer = 1000  # Keep last 1000 lines
        
        # Detection patterns for console output
        self.patterns = {
            "start_generation": [
                "Starting grass precache generation",
                "Beginning grass cache creation",
                "Initializing grass precache"
            ],
            "resume_generation": [
                "Resuming grass cache generation",
                "Continuing grass precache"
            ],
            "worldspace_start": [
                "Processing worldspace:",
                "Generating grass for:",
                "Starting worldspace"
            ],
            "cell_progress": [
                "Processing cell",
                "Grass generated for cell",
                "Cell completed"
            ],
            "completion": [
                "Grass generation complete",
                "Grass precache finished",
                "All grass cache generated successfully"
            ],
            "error": [
                "Error:",
                "Fatal error",
                "Crash detected",
                "Exception:",
                "Access violation"
            ]
        }
    
    def monitor_generation_process(self, process_info, season, 
                                 timeout_minutes: int = 60,
                                 progress_callback: Optional[Callable] = None) -> MonitoringResult:
        """
        Monitor grass generation process until completion or failure
        
        Args:
            process_info: ProcessInfo from GameManager
            season: Season being generated
            timeout_minutes: Maximum time to wait
            progress_callback: Optional callback for progress updates
            
        Returns:
            MonitoringResult with final status
        """
        self.logger.info(f"👁️ Starting monitoring for {season.display_name} generation...")
        
        self.is_monitoring = True
        self.progress_callback = progress_callback
        self.current_progress = GenerationProgress(GenerationState.INITIALIZING)
        self.console_buffer.clear()
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_activity = start_time
        
        try:
            while self.is_monitoring and time.time() - start_time < timeout_seconds:
                # Check if process is still running
                if not process_info.process.is_running():
                    self.logger.warning("💥 Process terminated unexpectedly")
                    return self._create_crash_result(process_info, start_time)
                
                # Read console output (if available)
                self._read_console_output(process_info)
                
                # Update progress based on console output
                activity_detected = self._update_progress_from_console()
                
                if activity_detected:
                    last_activity = time.time()
                
                # Check for completion
                if self.current_progress.state == GenerationState.COMPLETED:
                    self.logger.success(f"🎉 {season.display_name} generation completed!")
                    return MonitoringResult(
                        completed=True,
                        crashed=False,
                        hung=False,
                        timeout=False,
                        final_progress=self.current_progress,
                        console_output=self.console_buffer.copy()
                    )
                
                # Check for crashes
                if self.current_progress.state == GenerationState.CRASHED:
                    self.logger.error(f"💥 {season.display_name} generation crashed")
                    return self._create_crash_result(process_info, start_time)
                
                # Check for hangs (no activity for extended period)
                if time.time() - last_activity > 300:  # 5 minutes no activity
                    if self._detect_process_hang(process_info):
                        self.logger.warning(f"🔒 {season.display_name} generation appears hung")
                        return MonitoringResult(
                            completed=False,
                            crashed=False,
                            hung=True,
                            timeout=False,
                            final_progress=self.current_progress,
                            console_output=self.console_buffer.copy()
                        )
                
                # Update progress callback
                if self.progress_callback:
                    self.progress_callback(self.current_progress)
                
                # Brief sleep to avoid excessive CPU usage
                time.sleep(2)
            
            # Timeout reached
            self.logger.warning(f"⏰ {season.display_name} generation timed out after {timeout_minutes} minutes")
            return MonitoringResult(
                completed=False,
                crashed=False,
                hung=False,
                timeout=True,
                final_progress=self.current_progress,
                console_output=self.console_buffer.copy()
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error during monitoring: {e}")
            return MonitoringResult(
                completed=False,
                crashed=True,
                hung=False,
                timeout=False,
                final_progress=self.current_progress,
                crash_details={"error": str(e)},
                console_output=self.console_buffer.copy()
            )
        finally:
            self.is_monitoring = False
    
    def _read_console_output(self, process_info) -> None:
        """
        Read console output from Skyrim process
        
        Note: This is challenging because Skyrim doesn't typically write to stdout.
        We may need to use alternative methods like:
        - Reading log files
        - Memory scanning
        - SKSE plugin integration
        """
        try:
            # Method 1: Try to read from process stdout (if available)
            if hasattr(process_info.process, 'stdout') and process_info.process.stdout:
                # This likely won't work for Skyrim, but included for completeness
                pass
            
            # Method 2: Read from Skyrim log files
            self._read_skyrim_logs()
            
            # Method 3: Read from NGIO log files
            self._read_ngio_logs()
            
        except Exception as e:
            self.logger.debug(f"Error reading console output: {e}")
    
    def _read_skyrim_logs(self) -> None:
        """Read from Skyrim log files"""
        try:
            # Common Skyrim log locations
            log_paths = [
                os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "My Games", "Skyrim Special Edition", "Logs", "Script"),
                os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "My Games", "Skyrim VR", "Logs", "Script")
            ]
            
            for log_dir in log_paths:
                if os.path.exists(log_dir):
                    # Look for recent log files
                    for file in os.listdir(log_dir):
                        if file.endswith('.log'):
                            log_file = os.path.join(log_dir, file)
                            if os.path.getmtime(log_file) > time.time() - 300:  # Modified in last 5 minutes
                                self._parse_log_file(log_file)
                            
        except Exception as e:
            self.logger.debug(f"Error reading Skyrim logs: {e}")
    
    def _read_ngio_logs(self) -> None:
        """Read from NGIO-specific log files"""
        try:
            # NGIO might write to its own log files
            # This would need to be determined based on NGIO's actual logging behavior
            pass
        except Exception as e:
            self.logger.debug(f"Error reading NGIO logs: {e}")
    
    def _parse_log_file(self, log_file: str) -> None:
        """Parse a log file for grass generation messages"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read only new lines (we could track file position)
                lines = f.readlines()
                
                for line in lines[-50:]:  # Check last 50 lines
                    line = line.strip()
                    if line:
                        self.console_buffer.append(line)
                        
                        # Trim buffer if too large
                        if len(self.console_buffer) > self.max_console_buffer:
                            self.console_buffer = self.console_buffer[-self.max_console_buffer:]
                            
        except Exception as e:
            self.logger.debug(f"Error parsing log file {log_file}: {e}")
    
    def _update_progress_from_console(self) -> bool:
        """
        Update progress based on console output
        
        Returns:
            bool: True if activity was detected, False otherwise
        """
        if not self.console_buffer:
            return False
        
        activity_detected = False
        recent_lines = self.console_buffer[-10:]  # Check last 10 lines
        
        for line in recent_lines:
            line_lower = line.lower()
            
            # Check for generation start
            if any(pattern.lower() in line_lower for pattern in self.patterns["start_generation"]):
                if self.current_progress.state != GenerationState.GENERATING:
                    self.current_progress.state = GenerationState.GENERATING
                    self.current_progress.last_activity = time.time()
                    self.logger.info("🌱 Grass generation started")
                    activity_detected = True
            
            # Check for resume
            elif any(pattern.lower() in line_lower for pattern in self.patterns["resume_generation"]):
                if self.current_progress.state != GenerationState.GENERATING:
                    self.current_progress.state = GenerationState.GENERATING
                    self.current_progress.last_activity = time.time()
                    self.logger.info("🔄 Grass generation resumed")
                    activity_detected = True
            
            # Check for worldspace processing
            elif any(pattern.lower() in line_lower for pattern in self.patterns["worldspace_start"]):
                # Extract worldspace name if possible
                worldspace = self._extract_worldspace_name(line)
                if worldspace and worldspace != self.current_progress.current_worldspace:
                    self.current_progress.current_worldspace = worldspace
                    self.current_progress.last_activity = time.time()
                    self.logger.info(f"🗺️ Processing worldspace: {worldspace}")
                    activity_detected = True
            
            # Check for cell progress
            elif any(pattern.lower() in line_lower for pattern in self.patterns["cell_progress"]):
                self.current_progress.processed_cells += 1
                self.current_progress.last_activity = time.time()
                
                # Update progress percentage if we have total cells
                if self.current_progress.total_cells > 0:
                    self.current_progress.progress_percentage = (
                        self.current_progress.processed_cells / self.current_progress.total_cells
                    ) * 100
                
                activity_detected = True
                
                # Log progress periodically
                if self.current_progress.processed_cells % 100 == 0:
                    self.logger.progress(
                        "Processing cells",
                        self.current_progress.processed_cells,
                        self.current_progress.total_cells
                    )
            
            # Check for completion
            elif any(pattern.lower() in line_lower for pattern in self.patterns["completion"]):
                self.current_progress.state = GenerationState.COMPLETED
                self.current_progress.progress_percentage = 100.0
                self.current_progress.last_activity = time.time()
                activity_detected = True
            
            # Check for errors
            elif any(pattern.lower() in line_lower for pattern in self.patterns["error"]):
                self.current_progress.state = GenerationState.CRASHED
                self.current_progress.last_activity = time.time()
                self.logger.error(f"💥 Error detected in console: {line}")
                activity_detected = True
        
        return activity_detected
    
    def _extract_worldspace_name(self, line: str) -> Optional[str]:
        """Extract worldspace name from log line"""
        try:
            # Simple extraction - this would need refinement based on actual log format
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    return parts[1].strip().split()[0]
        except Exception:
            pass
        return None
    
    def _detect_process_hang(self, process_info) -> bool:
        """
        Detect if the process is hung based on CPU and memory usage
        
        Returns:
            bool: True if process appears hung
        """
        try:
            proc = process_info.process
            
            # Sample CPU usage over a short period
            cpu_samples = []
            for _ in range(3):
                cpu_percent = proc.cpu_percent(interval=1)
                cpu_samples.append(cpu_percent)
            
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            
            # Get memory info
            memory_info = proc.memory_info()
            
            # Consider hung if:
            # - Very low CPU usage (< 1%)
            # - Memory usage stable
            # - No recent console activity
            if avg_cpu < 1.0:
                self.logger.debug(f"Low CPU usage detected: {avg_cpu:.1f}%")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error detecting hang: {e}")
            return False
    
    def _create_crash_result(self, process_info, start_time: float) -> MonitoringResult:
        """Create a crash result with details"""
        try:
            # Get exit code if available
            exit_code = None
            if hasattr(process_info.process, 'poll'):
                exit_code = process_info.process.poll()
            
            crash_details = {
                "exit_code": exit_code,
                "uptime_seconds": time.time() - start_time,
                "last_console_lines": self.console_buffer[-10:] if self.console_buffer else []
            }
            
            return MonitoringResult(
                completed=False,
                crashed=True,
                hung=False,
                timeout=False,
                final_progress=self.current_progress,
                crash_details=crash_details,
                console_output=self.console_buffer.copy()
            )
            
        except Exception as e:
            self.logger.error(f"Error creating crash result: {e}")
            return MonitoringResult(
                completed=False,
                crashed=True,
                hung=False,
                timeout=False,
                final_progress=self.current_progress,
                crash_details={"error": str(e)},
                console_output=self.console_buffer.copy()
            )
    
    def get_current_progress(self) -> GenerationProgress:
        """Get current progress information"""
        return self.current_progress
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring process"""
        self.is_monitoring = False
    
    def estimate_remaining_time(self) -> float:
        """
        Estimate remaining time based on current progress
        
        Returns:
            float: Estimated remaining time in seconds
        """
        if (self.current_progress.progress_percentage <= 0 or 
            self.current_progress.elapsed_time <= 0):
            return 0.0
        
        try:
            # Simple linear estimation
            total_estimated = (
                self.current_progress.elapsed_time / 
                (self.current_progress.progress_percentage / 100)
            )
            remaining = total_estimated - self.current_progress.elapsed_time
            return max(0, remaining)
            
        except (ZeroDivisionError, ValueError):
            return 0.0
    
    def get_console_output(self, lines: int = 50) -> List[str]:
        """
        Get recent console output
        
        Args:
            lines: Number of recent lines to return
            
        Returns:
            List[str]: Recent console lines
        """
        return self.console_buffer[-lines:] if self.console_buffer else []
    
    def save_console_log(self, file_path: str) -> bool:
        """
        Save console output to file
        
        Args:
            file_path: Path to save log file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("NGIO Automation Suite - Console Log\n")
                f.write("=" * 50 + "\n\n")
                
                for line in self.console_buffer:
                    f.write(f"{line}\n")
            
            self.logger.info(f"📝 Console log saved to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Failed to save console log: {e}")
            return False


def main():
    """Test the ProgressMonitor functionality"""
    print("🧪 Testing ProgressMonitor...")
    
    monitor = ProgressMonitor()
    
    # Simulate some console output
    monitor.console_buffer.extend([
        "Starting grass precache generation",
        "Processing worldspace: Tamriel",
        "Processing cell 1, 1",
        "Processing cell 1, 2",
        "Grass generation complete"
    ])
    
    # Test progress parsing
    activity = monitor._update_progress_from_console()
    print(f"Activity detected: {activity}")
    print(f"Current state: {monitor.current_progress.state}")
    print(f"Current worldspace: {monitor.current_progress.current_worldspace}")


if __name__ == "__main__":
    main()
