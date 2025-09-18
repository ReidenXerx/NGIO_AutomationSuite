#!/usr/bin/env python3
"""
Skyrim Detector - Game Installation and Mod Validation
Detects Skyrim installations and validates required mods
"""

import os
import sys
import winreg
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass

from .logger import Logger


@dataclass
class SkyrimInstallation:
    """Information about a Skyrim installation"""
    path: str
    version: str  # "SE", "AE", "VR", "LE"
    executable: str
    data_directory: str
    plugins_directory: str
    valid: bool


@dataclass
class ModInfo:
    """Information about an installed mod"""
    name: str
    found: bool
    path: Optional[str] = None
    version: Optional[str] = None
    files: List[str] = None


class SkyrimDetector:
    """
    Detects Skyrim installations and validates mod requirements
    
    Key features:
    - Auto-detect Skyrim SE/AE/VR installations
    - Validate game installation integrity
    - Check for required mods (NGIO, Seasons of Skyrim, SKSE)
    - Detect mod manager installations
    - Verify file permissions and access
    """
    
    def __init__(self):
        self.logger = Logger("SkyrimDetector")
        
        # Common installation paths to check
        self.common_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition",
            r"C:\Program Files\Steam\steamapps\common\Skyrim Special Edition",
            r"C:\Games\Steam\steamapps\common\Skyrim Special Edition",
            r"D:\Steam\steamapps\common\Skyrim Special Edition",
            r"E:\Steam\steamapps\common\Skyrim Special Edition",
            r"C:\Program Files (x86)\Steam\steamapps\common\SkyrimVR",
            r"C:\Program Files\Steam\steamapps\common\SkyrimVR",
            r"D:\Steam\steamapps\common\SkyrimVR",
            r"E:\Steam\steamapps\common\SkyrimVR"
        ]
        
        # Required files for validation
        self.required_files = {
            "SE": ["SkyrimSE.exe", "Data"],
            "AE": ["SkyrimSE.exe", "Data"],  # AE uses same exe as SE
            "VR": ["SkyrimVR.exe", "Data"],
            "LE": ["TESV.exe", "Data"]
        }
        
        # Required mod files
        self.required_mods = {
            "NGIO": {
                "files": ["GrassControl.ini", "skse64_loader.exe"],
                "directories": ["SKSE/Plugins"]
            },
            "Seasons of Skyrim": {
                "files": ["po3_SeasonsOfSkyrim.ini"],
                "directories": ["SKSE/Plugins"]
            },
            "SKSE": {
                "files": ["skse64_loader.exe", "skse64_steam_loader.dll"],
                "directories": ["Data/SKSE"]
            }
        }
    
    def detect_skyrim_installations(self) -> List[SkyrimInstallation]:
        """
        Detect all Skyrim installations on the system
        
        Returns:
            List[SkyrimInstallation]: Found installations
        """
        self.logger.info("🔍 Detecting Skyrim installations...")
        
        installations = []
        
        # Method 1: Check registry
        registry_paths = self._check_registry()
        for path in registry_paths:
            installation = self._validate_installation_path(path)
            if installation and installation not in installations:
                installations.append(installation)
        
        # Method 2: Check common paths
        for path in self.common_paths:
            if os.path.exists(path):
                installation = self._validate_installation_path(path)
                if installation and installation not in installations:
                    installations.append(installation)
        
        # Method 3: Check environment variables
        env_paths = self._check_environment_variables()
        for path in env_paths:
            installation = self._validate_installation_path(path)
            if installation and installation not in installations:
                installations.append(installation)
        
        self.logger.info(f"📊 Found {len(installations)} Skyrim installations")
        
        for installation in installations:
            self.logger.info(f"   ✅ {installation.version}: {installation.path}")
        
        return installations
    
    def _check_registry(self) -> List[str]:
        """Check Windows registry for Skyrim installations"""
        registry_paths = []
        
        try:
            # Steam registry keys
            steam_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 489830"),  # Skyrim SE
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 611670"),  # Skyrim VR
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 489830"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 611670")
            ]
            
            for hkey, key_path in steam_keys:
                try:
                    with winreg.OpenKey(hkey, key_path) as key:
                        install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
                        if install_location and os.path.exists(install_location):
                            registry_paths.append(install_location)
                except (WindowsError, FileNotFoundError):
                    continue
            
            # Check Steam installation path
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                    steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    
                    # Check common Steam library locations
                    steamapps_common = os.path.join(steam_path, "steamapps", "common")
                    if os.path.exists(steamapps_common):
                        for folder in os.listdir(steamapps_common):
                            if "skyrim" in folder.lower():
                                folder_path = os.path.join(steamapps_common, folder)
                                if os.path.isdir(folder_path):
                                    registry_paths.append(folder_path)
            except (WindowsError, FileNotFoundError):
                pass
                
        except Exception as e:
            self.logger.debug(f"Error checking registry: {e}")
        
        return registry_paths
    
    def _check_environment_variables(self) -> List[str]:
        """Check environment variables for Skyrim paths"""
        env_paths = []
        
        # Check common environment variables
        env_vars = ["SKYRIM_PATH", "SKYRIMSE_PATH", "SKYRIMVR_PATH"]
        
        for var in env_vars:
            path = os.environ.get(var)
            if path and os.path.exists(path):
                env_paths.append(path)
        
        return env_paths
    
    def _validate_installation_path(self, path: str) -> Optional[SkyrimInstallation]:
        """
        Validate a potential Skyrim installation path
        
        Args:
            path: Path to check
            
        Returns:
            SkyrimInstallation if valid, None otherwise
        """
        if not os.path.exists(path):
            return None
        
        # Determine Skyrim version
        version = self._determine_skyrim_version(path)
        if not version:
            return None
        
        # Find executable
        executable = self._find_executable(path, version)
        if not executable:
            return None
        
        # Check required files
        valid = self._check_required_files(path, version)
        
        # Set up directories
        data_directory = os.path.join(path, "Data")
        plugins_directory = os.path.join(data_directory, "SKSE", "Plugins")
        
        return SkyrimInstallation(
            path=path,
            version=version,
            executable=executable,
            data_directory=data_directory,
            plugins_directory=plugins_directory,
            valid=valid
        )
    
    def _determine_skyrim_version(self, path: str) -> Optional[str]:
        """Determine which version of Skyrim is installed"""
        if os.path.exists(os.path.join(path, "SkyrimSE.exe")):
            # Check if it's AE or SE by looking for AE-specific files
            if os.path.exists(os.path.join(path, "creationclub.exe")):
                return "AE"
            else:
                return "SE"
        elif os.path.exists(os.path.join(path, "SkyrimVR.exe")):
            return "VR"
        elif os.path.exists(os.path.join(path, "TESV.exe")):
            return "LE"
        
        return None
    
    def _find_executable(self, path: str, version: str) -> Optional[str]:
        """Find the main executable for the Skyrim version"""
        executables = {
            "SE": "SkyrimSE.exe",
            "AE": "SkyrimSE.exe",
            "VR": "SkyrimVR.exe",
            "LE": "TESV.exe"
        }
        
        exe_name = executables.get(version)
        if exe_name:
            exe_path = os.path.join(path, exe_name)
            if os.path.exists(exe_path):
                return exe_path
        
        return None
    
    def _check_required_files(self, path: str, version: str) -> bool:
        """Check if all required files are present"""
        required = self.required_files.get(version, [])
        
        for file_or_dir in required:
            full_path = os.path.join(path, file_or_dir)
            if not os.path.exists(full_path):
                return False
        
        return True
    
    def validate_installation(self, skyrim_path: str) -> bool:
        """
        Validate a specific Skyrim installation
        
        Args:
            skyrim_path: Path to Skyrim installation
            
        Returns:
            bool: True if valid, False otherwise
        """
        self.logger.info(f"🔍 Validating Skyrim installation: {skyrim_path}")
        
        installation = self._validate_installation_path(skyrim_path)
        
        if installation and installation.valid:
            self.logger.success(f"✅ Valid {installation.version} installation")
            return True
        else:
            self.logger.error(f"❌ Invalid Skyrim installation")
            return False
    
    def check_mod_installed(self, mod_name: str, skyrim_path: str = None) -> bool:
        """
        Check if a specific mod is installed
        
        Args:
            mod_name: Name of the mod to check
            skyrim_path: Path to Skyrim installation
            
        Returns:
            bool: True if mod is installed, False otherwise
        """
        if not skyrim_path:
            # Try to find any Skyrim installation
            installations = self.detect_skyrim_installations()
            if not installations:
                return False
            skyrim_path = installations[0].path
        
        mod_info = self.get_mod_info(mod_name, skyrim_path)
        return mod_info.found
    
    def get_mod_info(self, mod_name: str, skyrim_path: str) -> ModInfo:
        """
        Get detailed information about a mod
        
        Args:
            mod_name: Name of the mod
            skyrim_path: Path to Skyrim installation
            
        Returns:
            ModInfo: Detailed mod information
        """
        mod_requirements = self.required_mods.get(mod_name)
        if not mod_requirements:
            return ModInfo(name=mod_name, found=False)
        
        found_files = []
        all_found = True
        
        # Check required files
        for filename in mod_requirements.get("files", []):
            file_locations = [
                os.path.join(skyrim_path, filename),
                os.path.join(skyrim_path, "Data", filename),
                os.path.join(skyrim_path, "Data", "SKSE", "Plugins", filename)
            ]
            
            file_found = False
            for location in file_locations:
                if os.path.exists(location):
                    found_files.append(location)
                    file_found = True
                    break
            
            if not file_found:
                all_found = False
        
        # Check required directories
        for dirname in mod_requirements.get("directories", []):
            dir_path = os.path.join(skyrim_path, "Data", dirname)
            if not os.path.exists(dir_path):
                all_found = False
        
        return ModInfo(
            name=mod_name,
            found=all_found,
            path=skyrim_path if all_found else None,
            files=found_files
        )
    
    def validate_all_requirements(self, skyrim_path: str) -> Tuple[bool, List[str]]:
        """
        Validate all mod requirements for grass cache generation
        
        Args:
            skyrim_path: Path to Skyrim installation
            
        Returns:
            Tuple[bool, List[str]]: (all_valid, list_of_issues)
        """
        self.logger.info("🔍 Validating mod requirements...")
        
        issues = []
        
        # Validate Skyrim installation
        if not self.validate_installation(skyrim_path):
            issues.append("Invalid Skyrim installation")
        
        # Check each required mod
        for mod_name in self.required_mods.keys():
            mod_info = self.get_mod_info(mod_name, skyrim_path)
            
            if mod_info.found:
                self.logger.success(f"✅ {mod_name}: Found")
            else:
                self.logger.error(f"❌ {mod_name}: Not found")
                issues.append(f"Missing required mod: {mod_name}")
        
        # Additional checks
        additional_issues = self._perform_additional_checks(skyrim_path)
        issues.extend(additional_issues)
        
        all_valid = len(issues) == 0
        
        if all_valid:
            self.logger.success("✅ All requirements validated successfully")
        else:
            self.logger.warning(f"⚠️ Found {len(issues)} issues:")
            for issue in issues:
                self.logger.warning(f"   - {issue}")
        
        return all_valid, issues
    
    def _perform_additional_checks(self, skyrim_path: str) -> List[str]:
        """Perform additional validation checks"""
        issues = []
        
        try:
            # Check write permissions
            data_path = os.path.join(skyrim_path, "Data")
            if not os.access(data_path, os.W_OK):
                issues.append("No write permission to Data directory")
            
            # Check for conflicting mods
            conflicting_mods = self._check_for_conflicts(skyrim_path)
            if conflicting_mods:
                issues.extend([f"Potential conflict: {mod}" for mod in conflicting_mods])
            
            # Check available disk space
            free_space = self._get_free_disk_space(skyrim_path)
            if free_space < 5 * 1024 * 1024 * 1024:  # 5GB minimum
                issues.append(f"Low disk space: {free_space / (1024**3):.1f}GB available")
            
        except Exception as e:
            self.logger.debug(f"Error in additional checks: {e}")
        
        return issues
    
    def _check_for_conflicts(self, skyrim_path: str) -> List[str]:
        """Check for potentially conflicting mods"""
        conflicts = []
        
        try:
            plugins_dir = os.path.join(skyrim_path, "Data", "SKSE", "Plugins")
            if os.path.exists(plugins_dir):
                for file in os.listdir(plugins_dir):
                    # Check for known conflicting mods
                    if "grasscontrol" in file.lower() and "backup" not in file.lower():
                        # Multiple grass control mods
                        conflicts.append(f"Multiple grass control files: {file}")
        
        except Exception as e:
            self.logger.debug(f"Error checking conflicts: {e}")
        
        return conflicts
    
    def _get_free_disk_space(self, path: str) -> int:
        """Get free disk space for the given path"""
        try:
            if sys.platform == "win32":
                import shutil
                return shutil.disk_usage(path).free
            else:
                statvfs = os.statvfs(path)
                return statvfs.f_frsize * statvfs.f_bavail
        except Exception:
            return 0
    
    def get_best_installation(self) -> Optional[SkyrimInstallation]:
        """
        Get the best Skyrim installation for grass cache generation
        
        Returns:
            SkyrimInstallation: Best installation, or None if none found
        """
        installations = self.detect_skyrim_installations()
        
        if not installations:
            return None
        
        # Prefer SE/AE over VR, and valid over invalid
        valid_installations = [inst for inst in installations if inst.valid]
        
        if valid_installations:
            # Prefer SE/AE
            for inst in valid_installations:
                if inst.version in ["SE", "AE"]:
                    return inst
            
            # Fall back to any valid installation
            return valid_installations[0]
        
        # Return any installation if no valid ones
        return installations[0]
    
    def create_diagnostic_report(self, output_path: str = None) -> str:
        """
        Create a diagnostic report of the system
        
        Args:
            output_path: Path to save the report
            
        Returns:
            str: Report content
        """
        report_lines = [
            "NGIO Automation Suite - System Diagnostic Report",
            "=" * 60,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SKYRIM INSTALLATIONS:",
            "-" * 30
        ]
        
        installations = self.detect_skyrim_installations()
        
        if not installations:
            report_lines.append("❌ No Skyrim installations found")
        else:
            for i, inst in enumerate(installations, 1):
                report_lines.extend([
                    f"{i}. {inst.version} - {'✅ Valid' if inst.valid else '❌ Invalid'}",
                    f"   Path: {inst.path}",
                    f"   Executable: {inst.executable}",
                    ""
                ])
        
        # Check mods for each installation
        for inst in installations:
            if inst.valid:
                report_lines.extend([
                    f"MOD STATUS FOR {inst.version} ({inst.path}):",
                    "-" * 40
                ])
                
                for mod_name in self.required_mods.keys():
                    mod_info = self.get_mod_info(mod_name, inst.path)
                    status = "✅ Found" if mod_info.found else "❌ Missing"
                    report_lines.append(f"{mod_name}: {status}")
                
                report_lines.append("")
        
        # System information
        report_lines.extend([
            "SYSTEM INFORMATION:",
            "-" * 30,
            f"OS: {sys.platform}",
            f"Python: {sys.version}",
            f"Working Directory: {os.getcwd()}",
            ""
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"📝 Diagnostic report saved: {output_path}")
            except Exception as e:
                self.logger.error(f"💥 Failed to save diagnostic report: {e}")
        
        return report_content


def main():
    """Test the SkyrimDetector functionality"""
    print("🧪 Testing SkyrimDetector...")
    
    detector = SkyrimDetector()
    
    # Detect installations
    installations = detector.detect_skyrim_installations()
    print(f"Found {len(installations)} installations")
    
    # Get best installation
    best = detector.get_best_installation()
    if best:
        print(f"Best installation: {best.version} at {best.path}")
        
        # Validate requirements
        valid, issues = detector.validate_all_requirements(best.path)
        print(f"Requirements valid: {valid}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")
    
    # Create diagnostic report
    report = detector.create_diagnostic_report()
    print("\nDiagnostic Report:")
    print(report)


if __name__ == "__main__":
    import time
    main()
