#!/usr/bin/env python3
"""
System Validator - Configuration Validation Tool (v1.3.0+)
Pre-flight checks before starting automation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from .logger import Logger


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    passed: bool
    category: str
    check_name: str
    message: str
    severity: str  # 'critical', 'warning', 'info'
    suggestion: Optional[str] = None


class SystemValidator:
    """
    Validates system configuration before running automation
    
    Checks:
    - Skyrim installation
    - Required mods (NGIO, SKSE)
    - Disk space
    - System RAM and pagefile (critical for overnight mode!)
    - Python environment
    - File permissions
    - Optional dependencies
    """
    
    def __init__(self, skyrim_path: str, output_directory: str):
        self.logger = Logger("SystemValidator")
        self.skyrim_path = Path(skyrim_path) if skyrim_path else None
        self.output_directory = Path(output_directory) if output_directory else None
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> Tuple[bool, List[ValidationResult]]:
        """
        Run all validation checks
        
        Returns:
            (all_passed, results_list)
        """
        self.results = []
        
        # Critical checks
        self._check_skyrim_installation()
        self._check_skyrim_executable()
        self._check_skse_installation()
        self._check_ngio_mod()
        self._check_disk_space()
        self._check_write_permissions()
        
        # Warning checks (RAM/Pagefile are WARNING, not CRITICAL)
        self._check_system_memory()
        self._check_pagefile_settings()
        self._check_python_version()
        self._check_dependencies()
        self._check_mod_manager()
        
        # Info checks
        self._check_optional_features()
        
        # Determine if all critical checks passed
        critical_failures = [r for r in self.results if not r.passed and r.severity == 'critical']
        all_passed = len(critical_failures) == 0
        
        return all_passed, self.results
    
    def _check_skyrim_installation(self):
        """Check if Skyrim path exists and is valid"""
        if not self.skyrim_path:
            self.results.append(ValidationResult(
                passed=False,
                category="Skyrim",
                check_name="Installation Path",
                message="Skyrim path not configured",
                severity="critical",
                suggestion="Configure Skyrim path in settings"
            ))
            return
        
        if not self.skyrim_path.exists():
            self.results.append(ValidationResult(
                passed=False,
                category="Skyrim",
                check_name="Installation Path",
                message=f"Skyrim directory not found: {self.skyrim_path}",
                severity="critical",
                suggestion="Verify Skyrim installation path is correct"
            ))
            return
        
        self.results.append(ValidationResult(
            passed=True,
            category="Skyrim",
            check_name="Installation Path",
            message=f"Found Skyrim at: {self.skyrim_path}",
            severity="info"
        ))
    
    def _check_skyrim_executable(self):
        """Check if SkyrimSE.exe exists"""
        if not self.skyrim_path or not self.skyrim_path.exists():
            return
        
        skyrim_exe = self.skyrim_path / "SkyrimSE.exe"
        
        if not skyrim_exe.exists():
            self.results.append(ValidationResult(
                passed=False,
                category="Skyrim",
                check_name="Game Executable",
                message="SkyrimSE.exe not found",
                severity="critical",
                suggestion="Ensure Skyrim SE (not LE) is installed"
            ))
            return
        
        self.results.append(ValidationResult(
            passed=True,
            category="Skyrim",
            check_name="Game Executable",
            message=f"SkyrimSE.exe found ({skyrim_exe.stat().st_size / 1024 / 1024:.1f} MB)",
            severity="info"
        ))
    
    def _check_skse_installation(self):
        """Check if SKSE64 is installed"""
        if not self.skyrim_path or not self.skyrim_path.exists():
            return
        
        skse_loader = self.skyrim_path / "skse64_loader.exe"
        
        if not skse_loader.exists():
            self.results.append(ValidationResult(
                passed=False,
                category="Requirements",
                check_name="SKSE64",
                message="SKSE64 not found",
                severity="critical",
                suggestion="Download and install SKSE64 from https://skse.silverlock.org/"
            ))
            return
        
        self.results.append(ValidationResult(
            passed=True,
            category="Requirements",
            check_name="SKSE64",
            message="SKSE64 installed",
            severity="info"
        ))
    
    def _check_ngio_mod(self):
        """Check if NGIO mod is present"""
        if not self.skyrim_path or not self.skyrim_path.exists():
            return
        
        # Check Data/SKSE/Plugins for NGIO
        ngio_plugin = self.skyrim_path / "Data" / "SKSE" / "Plugins" / "NoGrassInObjects.dll"
        
        if not ngio_plugin.exists():
            self.results.append(ValidationResult(
                passed=False,
                category="Requirements",
                check_name="NGIO Mod",
                message="NGIO mod not detected",
                severity="critical",
                suggestion="Install 'No Grass In Objects' mod from Nexus Mods"
            ))
            return
        
        self.results.append(ValidationResult(
            passed=True,
            category="Requirements",
            check_name="NGIO Mod",
            message="NGIO mod installed",
            severity="info"
        ))
    
    def _check_disk_space(self):
        """Check available disk space"""
        if not self.skyrim_path or not self.skyrim_path.exists():
            return
        
        try:
            self.logger.debug("Checking disk space...")
            stat = shutil.disk_usage(self.skyrim_path)
            free_gb = stat.free / (1024 ** 3)
            
            if free_gb < 5:
                self.results.append(ValidationResult(
                    passed=False,
                    category="System",
                    check_name="Disk Space",
                    message=f"Low disk space: {free_gb:.1f} GB free",
                    severity="critical",
                    suggestion="At least 5 GB free space required"
                ))
            elif free_gb < 10:
                self.results.append(ValidationResult(
                    passed=True,
                    category="System",
                    check_name="Disk Space",
                    message=f"Limited disk space: {free_gb:.1f} GB free",
                    severity="warning",
                    suggestion="10+ GB recommended for safety"
                ))
            else:
                self.results.append(ValidationResult(
                    passed=True,
                    category="System",
                    check_name="Disk Space",
                    message=f"{free_gb:.1f} GB free",
                    severity="info"
                ))
        except Exception as e:
            self.logger.warning(f"Failed to check disk space: {e}")
    
    def _check_system_memory(self):
        """Check system RAM - Critical for overnight generation"""
        try:
            import psutil
            
            self.logger.debug("Checking system RAM...")
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024 ** 3)
            available_gb = memory.available / (1024 ** 3)
            
            # Check if system has enough RAM
            if total_gb < 12:
                self.results.append(ValidationResult(
                    passed=True,
                    category="Memory",
                    check_name="System RAM",
                    message=f"⚠️  Low RAM: {total_gb:.1f} GB total (Skyrim can crash during generation!)",
                    severity="warning",
                    suggestion="🔥 CRITICAL: With <16GB RAM, you MUST configure Windows pagefile to 20GB+ to prevent crashes during overnight generation!"
                ))
            elif total_gb < 16:
                self.results.append(ValidationResult(
                    passed=True,
                    category="Memory",
                    check_name="System RAM",
                    message=f"⚠️  Limited RAM: {total_gb:.1f} GB total (Configure 20GB+ pagefile recommended)",
                    severity="warning",
                    suggestion="Skyrim can consume ALL available RAM during grass generation. Set Windows pagefile to 20GB+ to prevent crashes!"
                ))
            else:
                self.results.append(ValidationResult(
                    passed=True,
                    category="Memory",
                    check_name="System RAM",
                    message=f"{total_gb:.1f} GB total, {available_gb:.1f} GB available",
                    severity="info"
                ))
        except ImportError:
            self.logger.warning("psutil not available - cannot check system memory")
        except Exception as e:
            self.logger.warning(f"Failed to check system memory: {e}")
    
    def _check_pagefile_settings(self):
        """Check Windows pagefile (virtual memory) configuration"""
        try:
            import psutil
            
            self.logger.debug("Checking Windows pagefile...")
            swap = psutil.swap_memory()
            pagefile_gb = swap.total / (1024 ** 3)
            
            if pagefile_gb < 10:
                self.results.append(ValidationResult(
                    passed=False,
                    category="Memory",
                    check_name="Windows Pagefile",
                    message=f"🚨 CRITICAL: Pagefile too small: {pagefile_gb:.1f} GB",
                    severity="warning",  # Warning not critical - user can still try
                    suggestion="⚠️  SET PAGEFILE TO 20GB+ IMMEDIATELY! Skyrim WILL crash during overnight generation otherwise. Go to: System Properties → Advanced → Performance Settings → Advanced → Virtual Memory → Custom size: 20480 MB"
                ))
            elif pagefile_gb < 20:
                self.results.append(ValidationResult(
                    passed=True,
                    category="Memory",
                    check_name="Windows Pagefile",
                    message=f"⚠️  Pagefile: {pagefile_gb:.1f} GB (Minimum, 20GB+ recommended)",
                    severity="warning",
                    suggestion="Increase pagefile to 20GB+ for safer overnight generation (especially with <16GB RAM)"
                ))
            else:
                self.results.append(ValidationResult(
                    passed=True,
                    category="Memory",
                    check_name="Windows Pagefile",
                    message=f"✅ Pagefile: {pagefile_gb:.1f} GB (Good for overnight generation!)",
                    severity="info"
                ))
        except ImportError:
            self.logger.warning("psutil not available - cannot check pagefile")
        except Exception as e:
            self.logger.warning(f"Failed to check pagefile: {e}")
    
    def _check_write_permissions(self):
        """Check write permissions for output directory"""
        if not self.output_directory:
            return
        
        try:
            # Try creating output directory
            self.output_directory.mkdir(parents=True, exist_ok=True)
            
            # Try writing a test file
            test_file = self.output_directory / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            self.results.append(ValidationResult(
                passed=True,
                category="System",
                check_name="Write Permissions",
                message="Output directory writable",
                severity="info"
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                passed=False,
                category="System",
                check_name="Write Permissions",
                message=f"Cannot write to output directory: {e}",
                severity="critical",
                suggestion="Check folder permissions or choose different output directory"
            ))
    
    def _check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.results.append(ValidationResult(
                passed=False,
                category="Python",
                check_name="Version",
                message=f"Python {version.major}.{version.minor} detected",
                severity="warning",
                suggestion="Python 3.8+ recommended"
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                category="Python",
                check_name="Version",
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                severity="info"
            ))
    
    def _check_dependencies(self):
        """Check required Python dependencies"""
        required_modules = ['colorlog', 'psutil']
        optional_modules = ['yaml', 'tqdm', 'winotify']
        
        missing_required = []
        missing_optional = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_required.append(module)
        
        for module in optional_modules:
            try:
                __import__(module)
            except ImportError:
                missing_optional.append(module)
        
        if missing_required:
            self.results.append(ValidationResult(
                passed=False,
                category="Python",
                check_name="Dependencies",
                message=f"Missing required modules: {', '.join(missing_required)}",
                severity="critical",
                suggestion="Run: pip install -r requirements.txt"
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                category="Python",
                check_name="Dependencies",
                message="All required dependencies installed",
                severity="info"
            ))
        
        if missing_optional:
            self.results.append(ValidationResult(
                passed=True,
                category="Python",
                check_name="Optional Features",
                message=f"Optional modules not installed: {', '.join(missing_optional)}",
                severity="warning",
                suggestion="Some features may be unavailable (progress bars, notifications, etc.)"
            ))
    
    def _check_mod_manager(self):
        """Check if mod manager might interfere"""
        if not self.skyrim_path or not self.skyrim_path.exists():
            return
        
        # Check for common mod manager indicators
        mo2_indicator = self.skyrim_path / "ModOrganizer.exe"
        vortex_indicator = Path.home() / "AppData" / "Roaming" / "Vortex"
        
        if mo2_indicator.exists():
            self.results.append(ValidationResult(
                passed=True,
                category="Mods",
                check_name="Mod Manager",
                message="Mod Organizer 2 detected",
                severity="info",
                suggestion="Launch tool through MO2 or configure virtual filesystem"
            ))
        elif vortex_indicator.exists():
            self.results.append(ValidationResult(
                passed=True,
                category="Mods",
                check_name="Mod Manager",
                message="Vortex detected",
                severity="info"
            ))
    
    def _check_optional_features(self):
        """Check for optional features availability"""
        # Check for seasonal mods
        if self.skyrim_path and self.skyrim_path.exists():
            seasons_ini = self.skyrim_path / "Data" / "SKSE" / "Plugins" / "po3_SeasonsOfSkyrim.ini"
            if seasons_ini.exists():
                self.results.append(ValidationResult(
                    passed=True,
                    category="Optional",
                    check_name="Seasons of Skyrim",
                    message="Seasonal mod detected",
                    severity="info"
                ))
    
    def print_results(self, show_all: bool = True):
        """
        Print validation results to console
        
        Args:
            show_all: Show all checks, or only failures/warnings
        """
        critical_failures = [r for r in self.results if not r.passed and r.severity == 'critical']
        warnings = [r for r in self.results if r.severity == 'warning' or (not r.passed and r.severity != 'critical')]
        passed = [r for r in self.results if r.passed and r.severity == 'info']
        
        self.logger.info("=" * 60)
        self.logger.info("🔍 SYSTEM VALIDATION RESULTS")
        self.logger.info("=" * 60)
        
        if critical_failures:
            self.logger.error("\n❌ CRITICAL ISSUES:")
            for result in critical_failures:
                self.logger.error(f"   [{result.category}] {result.check_name}: {result.message}")
                if result.suggestion:
                    self.logger.error(f"      → {result.suggestion}")
        
        if warnings:
            self.logger.warning("\n⚠️  WARNINGS:")
            for result in warnings:
                self.logger.warning(f"   [{result.category}] {result.check_name}: {result.message}")
                if result.suggestion:
                    self.logger.warning(f"      → {result.suggestion}")
        
        if show_all and passed:
            self.logger.info("\n✅ PASSED CHECKS:")
            for result in passed:
                self.logger.info(f"   [{result.category}] {result.check_name}: {result.message}")
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"Summary: {len(passed)} passed, {len(warnings)} warnings, {len(critical_failures)} critical")
        self.logger.info("=" * 60)
        
        return len(critical_failures) == 0


# === HELPER FUNCTIONS ===

def validate_system(skyrim_path: str, output_directory: str) -> bool:
    """
    Quick validation helper
    
    Args:
        skyrim_path: Path to Skyrim installation
        output_directory: Output directory for archives
        
    Returns:
        True if all critical checks passed
    """
    validator = SystemValidator(skyrim_path, output_directory)
    passed, results = validator.validate_all()
    validator.print_results(show_all=False)
    return passed


if __name__ == "__main__":
    # Example usage
    print("System Validator - Testing")
    print("=" * 60)
    
    skyrim_path = r"C:\Steam\steamapps\common\Skyrim Special Edition"
    output_dir = "./output"
    
    validator = SystemValidator(skyrim_path, output_dir)
    all_passed, results = validator.validate_all()
    validator.print_results(show_all=True)
    
    if all_passed:
        print("\n✅ System validation PASSED - ready to run!")
    else:
        print("\n❌ System validation FAILED - please fix issues above")

