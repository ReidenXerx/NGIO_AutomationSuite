#!/usr/bin/env python3
"""
Logger - Colored Console Logging System
Provides rich, colored console output with different log levels
"""

import os
import sys
import logging
import colorlog
from datetime import datetime
from typing import Optional
from pathlib import Path


class Logger:
    """
    Enhanced logger with colored console output and file logging
    
    Features:
    - Colored console output with emojis
    - Multiple log levels with distinct formatting
    - File logging for debugging
    - Progress indicators
    - Performance timing
    """
    
    def __init__(self, name: str = "NGIO", log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self.logger.setLevel(logging.DEBUG)
        
        # Setup console handler with colors
        self._setup_console_handler()
        
        # Setup file handler if requested
        if log_file:
            self._setup_file_handler(log_file)
        elif os.environ.get("NGIO_LOG_FILE"):
            self._setup_file_handler(os.environ["NGIO_LOG_FILE"])
    
    def _setup_console_handler(self) -> None:
        """Setup colored console output handler"""
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Define color scheme
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        console_handler.setFormatter(color_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self, log_file: str) -> None:
        """Setup file logging handler"""
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # File format without colors
            file_formatter = logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            self.info(f"📝 Logging to file: {log_file}")
            
        except Exception as e:
            self.warning(f"Failed to setup file logging: {e}")
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(f"🔧 {message}")
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def success(self, message: str) -> None:
        """Log success message (using info level with green color)"""
        # For console, we'll use info level but with success emoji
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(f"⚠️  {message}")
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(f"❌ {message}")
    
    def critical(self, message: str) -> None:
        """Log critical message"""
        self.logger.critical(f"💥 {message}")
    
    def progress(self, message: str, current: int = 0, total: int = 0) -> None:
        """Log progress message with optional progress bar"""
        if total > 0:
            percentage = (current / total) * 100
            bar_length = 20
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            self.info(f"📊 {message} [{bar}] {percentage:.1f}% ({current}/{total})")
        else:
            self.info(f"📊 {message}")
    
    def step(self, step_num: int, total_steps: int, message: str) -> None:
        """Log step progress"""
        self.info(f"🔹 Step {step_num}/{total_steps}: {message}")
    
    def season_start(self, season_name: str) -> None:
        """Log season generation start"""
        self.info("=" * 50)
        self.info(f"🌱 Starting {season_name} Grass Cache Generation")
        self.info("=" * 50)
    
    def season_complete(self, season_name: str, duration_minutes: float) -> None:
        """Log season generation completion"""
        self.info(f"🎉 {season_name} generation completed in {duration_minutes:.1f} minutes!")
    
    def crash_detected(self, process_name: str, uptime_seconds: float) -> None:
        """Log crash detection"""
        self.warning(f"💥 {process_name} crashed after {uptime_seconds:.1f} seconds")
    
    def retry_attempt(self, attempt: int, max_attempts: int, reason: str) -> None:
        """Log retry attempt"""
        self.info(f"🔄 Retry {attempt}/{max_attempts}: {reason}")
    
    def file_operation(self, operation: str, file_count: int, duration_seconds: float) -> None:
        """Log file operation completion"""
        rate = file_count / max(duration_seconds, 0.001)  # Avoid division by zero
        self.info(f"⚡ {operation}: {file_count} files in {duration_seconds:.2f}s ({rate:.1f} files/sec)")
    
    def separator(self, title: str = "") -> None:
        """Print a visual separator"""
        if title:
            title_len = len(title)
            padding = (50 - title_len - 2) // 2
            separator = "=" * padding + f" {title} " + "=" * padding
            if len(separator) < 50:
                separator += "="
        else:
            separator = "=" * 50
        
        self.info(separator)
    
    def table_header(self, headers: list) -> None:
        """Print table header"""
        header_str = " | ".join(f"{header:^15}" for header in headers)
        self.info(header_str)
        self.info("-" * len(header_str))
    
    def table_row(self, values: list) -> None:
        """Print table row"""
        row_str = " | ".join(f"{str(value):^15}" for value in values)
        self.info(row_str)
    
    def timing_start(self, operation: str) -> float:
        """Start timing an operation"""
        start_time = datetime.now().timestamp()
        self.debug(f"⏱️  Starting: {operation}")
        return start_time
    
    def timing_end(self, operation: str, start_time: float) -> float:
        """End timing an operation"""
        duration = datetime.now().timestamp() - start_time
        self.debug(f"⏱️  Completed: {operation} in {duration:.2f}s")
        return duration
    
    def system_info(self, skyrim_path: str, python_version: str, os_info: str) -> None:
        """Log system information"""
        self.separator("System Information")
        self.info(f"🎮 Skyrim Path: {skyrim_path}")
        self.info(f"🐍 Python Version: {python_version}")
        self.info(f"💻 OS: {os_info}")
        self.separator()
    
    def configuration_summary(self, config_dict: dict) -> None:
        """Log configuration summary"""
        self.separator("Configuration Summary")
        for key, value in config_dict.items():
            if isinstance(value, (list, tuple)):
                value = f"[{len(value)} items]"
            elif isinstance(value, str) and len(value) > 50:
                value = value[:47] + "..."
            self.info(f"⚙️  {key}: {value}")
        self.separator()
    
    def final_report(self, completed: list, failed: list, total_time: float) -> None:
        """Log final completion report"""
        self.separator("NGIO AUTOMATION SUITE - FINAL REPORT")
        self.info(f"⏱️  Total Time: {total_time/60:.1f} minutes")
        self.info(f"✅ Completed: {len(completed)} seasons")
        self.info(f"❌ Failed: {len(failed)} seasons")
        
        if completed:
            self.info("📝 Successful seasons:")
            for season in completed:
                self.info(f"   ✅ {season}")
        
        if failed:
            self.info("📝 Failed seasons:")
            for season in failed:
                self.info(f"   ❌ {season}")
        
        if not failed:
            self.info("🎊 ALL SEASONS COMPLETED SUCCESSFULLY!")
            self.info("🎯 Next Steps:")
            self.info("   1. Enable seasonal grass cache mods in your mod manager")
            self.info("   2. Disable NGIO mod")  
            self.info("   3. Ensure Grass Cache Helper NG is enabled")
            self.info("   4. Launch Skyrim and enjoy your automated grass cache!")
        else:
            self.warning("⚠️  Some seasons failed. Check the logs above for details.")
        
        self.separator()
    
    def mod_validation(self, mod_name: str, status: str, details: str = "") -> None:
        """Log mod validation results"""
        status_emoji = "✅" if status == "found" else "❌"
        message = f"{status_emoji} {mod_name}: {status}"
        if details:
            message += f" ({details})"
        self.info(message)
    
    def performance_stats(self, stats_dict: dict) -> None:
        """Log performance statistics"""
        self.separator("Performance Statistics")
        for stat_name, stat_value in stats_dict.items():
            if isinstance(stat_value, float):
                if 'time' in stat_name.lower() or 'duration' in stat_name.lower():
                    self.info(f"📊 {stat_name}: {stat_value:.2f}s")
                else:
                    self.info(f"📊 {stat_name}: {stat_value:.2f}")
            else:
                self.info(f"📊 {stat_name}: {stat_value}")
        self.separator()
    
    def memory_usage(self, process_name: str, memory_mb: float, cpu_percent: float) -> None:
        """Log memory and CPU usage"""
        self.debug(f"💾 {process_name}: {memory_mb:.1f}MB RAM, {cpu_percent:.1f}% CPU")
    
    def crash_analysis(self, crash_type: str, crash_details: dict) -> None:
        """Log detailed crash analysis"""
        self.separator(f"Crash Analysis - {crash_type}")
        for key, value in crash_details.items():
            self.error(f"💥 {key}: {value}")
        self.separator()
    
    def user_prompt(self, message: str) -> None:
        """Log user prompt/question"""
        self.info(f"❓ {message}")
    
    def user_input(self, prompt: str) -> str:
        """Get user input with logging"""
        self.user_prompt(prompt)
        try:
            response = input("   > ").strip()
            self.debug(f"User input: {response}")
            return response
        except KeyboardInterrupt:
            self.warning("User interrupted input")
            return ""
    
    def banner(self, title: str, subtitle: str = "") -> None:
        """Display a banner with title"""
        banner_width = 60
        
        self.info("=" * banner_width)
        title_padding = (banner_width - len(title) - 4) // 2
        self.info("=" * title_padding + f"  {title}  " + "=" * title_padding)
        
        if subtitle:
            subtitle_padding = (banner_width - len(subtitle) - 2) // 2
            self.info(" " * subtitle_padding + subtitle)
        
        self.info("=" * banner_width)
    
    def set_level(self, level: str) -> None:
        """Set logging level"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.debug(f"Log level set to {level.upper()}")
        else:
            self.warning(f"Unknown log level: {level}")


def main():
    """Test the Logger functionality"""
    logger = Logger("TestLogger")
    
    logger.banner("NGIO Automation Suite", "Logger Test")
    logger.info("Testing different log levels...")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.success("This is a success message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    logger.progress("Processing files", 7, 10)
    logger.step(1, 4, "Initializing system")
    logger.season_start("Winter")
    
    logger.table_header(["Season", "Status", "Duration"])
    logger.table_row(["Winter", "✅ Complete", "45.2 min"])
    logger.table_row(["Spring", "⏳ Running", "12.1 min"])
    
    logger.final_report(["Winter", "Spring"], ["Summer"], 180.5)


if __name__ == "__main__":
    main()
