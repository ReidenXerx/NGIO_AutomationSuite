#!/usr/bin/env python3
"""
Configuration Manager - INI File Management
Handles backup, modification, and restoration of game configuration files
"""

import os
import shutil
import configparser
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ..utils.logger import Logger


class ConfigManager:
    """
    Manages configuration files for NGIO grass cache generation
    
    Key responsibilities:
    - Backup original configuration files before modification
    - Modify season settings in po3_SeasonsOfSkyrim.ini
    - Restore original configurations after completion
    - Handle NGIO GrassControl.ini settings
    - Validate configuration integrity
    """
    
    def __init__(self, skyrim_path: Optional[str] = None):
        self.logger = Logger("ConfigManager")
        
        # Configuration file paths
        self.skyrim_path = skyrim_path
        self.config_files = {}
        self.backup_directory = None
        self.original_configs = {}
        
        # Initialize configuration file locations
        self._initialize_config_paths()
    
    def _initialize_config_paths(self) -> None:
        """Initialize paths to all configuration files"""
        if not self.skyrim_path:
            # Try to auto-detect Skyrim path
            self.skyrim_path = self._detect_skyrim_path()
            
        if not self.skyrim_path:
            self.logger.error("❌ Skyrim path not provided and auto-detection failed")
            return
            
        # Define configuration file locations
        data_path = os.path.join(self.skyrim_path, "Data")
        skse_plugins_path = os.path.join(data_path, "SKSE", "Plugins")
        
        self.config_files = {
            "seasons_config": os.path.join(skse_plugins_path, "po3_SeasonsOfSkyrim.ini"),
            "ngio_config": os.path.join(skse_plugins_path, "GrassControl.ini"),
            "dyndolod_config": os.path.join(data_path, "DynDOLOD", "DynDOLOD_SSE.ini")
        }
        
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_directory = os.path.join(
            self.skyrim_path, "NGIO_Backups", f"backup_{timestamp}"
        )
        
        self.logger.info(f"📁 Initialized config paths for: {self.skyrim_path}")
        self.logger.info(f"💾 Backup directory: {self.backup_directory}")
    
    def _detect_skyrim_path(self) -> Optional[str]:
        """Auto-detect Skyrim installation path"""
        common_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition",
            r"C:\Program Files\Steam\steamapps\common\Skyrim Special Edition",
            r"C:\Games\Steam\steamapps\common\Skyrim Special Edition",
            r"D:\Steam\steamapps\common\Skyrim Special Edition",
            r"E:\Steam\steamapps\common\Skyrim Special Edition"
        ]
        
        for path in common_paths:
            if os.path.exists(os.path.join(path, "SkyrimSE.exe")):
                self.logger.info(f"🔍 Auto-detected Skyrim at: {path}")
                return path
                
        return None
    
    def _read_config_with_bom_handling(self, config: configparser.ConfigParser, file_path: str) -> None:
        """
        Read INI file with BOM (Byte Order Mark) handling
        
        Some text editors add BOM to UTF-8 files, which breaks ConfigParser.
        This method strips BOM before parsing.
        
        Args:
            config: ConfigParser instance to read into
            file_path: Path to the INI file
        """
        try:
            # Read file content and strip BOM if present
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Parse the content directly
            config.read_string(content)
            
        except (UnicodeDecodeError, configparser.Error):
            # Fallback: try with different encodings
            for encoding in ['utf-8', 'utf-16', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    config.read_string(content)
                    self.logger.debug(f"🔧 Successfully read INI with {encoding} encoding")
                    return
                except (UnicodeDecodeError, configparser.Error):
                    continue
            
            # If all encodings fail, raise the original error
            raise
    
    def _modify_ini_value(self, file_path: str, section: str, key: str, new_value: str) -> None:
        """
        Modify a single INI value while preserving formatting, comments, and case
        
        This method reads the file line by line, finds the target key, and replaces
        only the value part, preserving everything else.
        
        Args:
            file_path: Path to the INI file
            section: Section name to modify
            key: Key name to modify (case insensitive search)
            new_value: New value to set
        """
        try:
            # Read the file with BOM handling
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            # Find the section and key
            in_target_section = False
            modified = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Check for section headers
                if stripped.startswith('[') and stripped.endswith(']'):
                    current_section = stripped[1:-1].strip()
                    in_target_section = (current_section.lower() == section.lower())
                    continue
                
                # Skip if not in target section
                if not in_target_section:
                    continue
                
                # Skip comments and empty lines
                if not stripped or stripped.startswith(';') or stripped.startswith('#'):
                    continue
                
                # Check if this line contains our key
                if '=' in stripped:
                    line_key, line_value = stripped.split('=', 1)
                    line_key = line_key.strip()
                    
                    if line_key.lower() == key.lower():
                        # Preserve the original key case and spacing
                        # Find the '=' position in the original line
                        equals_pos = line.find('=')
                        if equals_pos != -1:
                            # Reconstruct the line with new value
                            prefix = line[:equals_pos + 1]  # Keep everything up to and including '='
                            # Add a space after '=' if there wasn't one, preserve if there was
                            if len(line) > equals_pos + 1 and line[equals_pos + 1] == ' ':
                                lines[i] = f"{prefix} {new_value}\n"
                            else:
                                lines[i] = f"{prefix}{new_value}\n"
                            modified = True
                            break
            
            if not modified:
                self.logger.warning(f"⚠️ Key '{key}' not found in section '{section}' of {file_path}")
                return
            
            # Write the file back with preserved formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            self.logger.debug(f"🔧 Modified {key} = {new_value} in [{section}]")
            
        except Exception as e:
            self.logger.error(f"💥 Failed to modify INI value: {e}")
            raise
    
    def backup_all_configs(self) -> bool:
        """
        Create backups of all configuration files
        
        Returns:
            bool: True if successful, False if any backup failed
        """
        self.logger.info("💾 Creating configuration backups...")
        
        try:
            # Create backup directory
            os.makedirs(self.backup_directory, exist_ok=True)
            
            backup_success = True
            for config_name, config_path in self.config_files.items():
                if os.path.exists(config_path):
                    backup_path = os.path.join(
                        self.backup_directory, 
                        f"{config_name}_{os.path.basename(config_path)}"
                    )
                    
                    try:
                        shutil.copy2(config_path, backup_path)
                        self.logger.info(f"✅ Backed up {config_name}")
                        
                        # Store original content for quick restore
                        with open(config_path, 'r', encoding='utf-8') as f:
                            self.original_configs[config_name] = f.read()
                            
                    except Exception as e:
                        self.logger.error(f"❌ Failed to backup {config_name}: {e}")
                        backup_success = False
                else:
                    self.logger.warning(f"⚠️ Config file not found: {config_name} ({config_path})")
            
            if backup_success:
                self.logger.info("✅ All configuration files backed up successfully")
            
            return backup_success
            
        except Exception as e:
            self.logger.error(f"💥 Error creating backups: {e}")
            return False
    
    def set_season(self, season_type: int) -> bool:
        """
        Set the season type in po3_SeasonsOfSkyrim.ini
        
        Args:
            season_type: Season type (0=No Seasons, 1=Winter, 2=Spring, 3=Summer, 4=Autumn, 5=Seasonal)
            
        Returns:
            bool: True if successful, False if failed
        """
        season_names = {0: "No Seasons", 1: "Winter", 2: "Spring", 3: "Summer", 4: "Autumn", 5: "Seasonal"}
        season_name = season_names.get(season_type, f"Unknown({season_type})")
        
        # Special handling for non-seasonal mode
        if season_type == 0:
            self.logger.info(f"🌱 Non-seasonal mode: Skipping season configuration")
            return True  # No need to modify seasonal config for non-seasonal users
        
        self.logger.info(f"🌱 Setting season to: {season_name} (type {season_type})")
        
        seasons_config_path = self.config_files.get("seasons_config")
        if not seasons_config_path or not os.path.exists(seasons_config_path):
            if season_type == 5:  # Restoration to seasonal mode
                self.logger.warning("⚠️ Seasons of Skyrim config file not found - cannot restore seasonal mode")
                return True  # Don't fail restoration for this
            else:
                self.logger.error("❌ Seasons of Skyrim config file not found")
                self.logger.error("   This is required for seasonal grass generation")
                self.logger.error("   Install Seasons of Skyrim mod or use non-seasonal mode")
                return False
        
        try:
            # Read current configuration with BOM handling
            config = configparser.ConfigParser()
            self._read_config_with_bom_handling(config, seasons_config_path)
            
            # Find the correct section (usually [Settings] or [General])
            target_section = None
            for section_name in config.sections():
                if 'season type' in [key.lower() for key in config[section_name].keys()]:
                    target_section = section_name
                    break
            
            if not target_section:
                # Create Settings section if it doesn't exist
                target_section = "Settings"
                if target_section not in config:
                    config.add_section(target_section)
            
            # Set the season type
            # Handle different possible key names
            season_key = None
            for key in config[target_section].keys():
                if key.lower() in ['season type', 'seasontype', 'season']:
                    season_key = key
                    break
            
            if not season_key:
                season_key = "Season Type"
            
            # Use careful modification to preserve formatting
            self._modify_ini_value(seasons_config_path, target_section, season_key, str(season_type))
            
            self.logger.info(f"✅ Successfully set season to {season_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Failed to set season: {e}")
            return False
    
    def configure_ngio_for_generation(self) -> bool:
        """
        Configure NGIO settings for grass cache generation
        
        Returns:
            bool: True if successful, False if failed
        """
        self.logger.info("⚙️ Configuring NGIO for grass generation...")
        
        ngio_config_path = self.config_files.get("ngio_config")
        if not ngio_config_path or not os.path.exists(ngio_config_path):
            self.logger.error("❌ NGIO GrassControl.ini not found")
            return False
        
        try:
            config = configparser.ConfigParser()
            self._read_config_with_bom_handling(config, ngio_config_path)
            
            # Ensure [Settings] section exists
            if "Settings" not in config:
                config.add_section("Settings")
            
            # Configure NGIO for cache generation
            ngio_settings = {
                "UseGrassCache": "1",
                "OnlyLoadFromCache": "0",  # Allow generation
                "DynDOLODGrassMode": "1",
                "EnableGrassGeneration": "1"
            }
            
            for key, value in ngio_settings.items():
                config["Settings"][key] = value
            
            # Write updated configuration
            with open(ngio_config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.logger.info("✅ NGIO configured for grass generation")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Failed to configure NGIO: {e}")
            return False
    
    def configure_ngio_for_cache_use(self) -> bool:
        """
        Configure NGIO settings for using generated cache (post-generation)
        
        Returns:
            bool: True if successful, False if failed
        """
        self.logger.info("⚙️ Configuring NGIO for cache usage...")
        
        ngio_config_path = self.config_files.get("ngio_config")
        if not ngio_config_path or not os.path.exists(ngio_config_path):
            self.logger.error("❌ NGIO GrassControl.ini not found")
            return False
        
        try:
            config = configparser.ConfigParser()
            self._read_config_with_bom_handling(config, ngio_config_path)
            
            # Ensure [Settings] section exists
            if "Settings" not in config:
                config.add_section("Settings")
            
            # Configure NGIO for cache usage only
            ngio_settings = {
                "UseGrassCache": "1",
                "OnlyLoadFromCache": "1",  # Only use cache, don't generate
                "DynDOLODGrassMode": "1",
                "EnableGrassGeneration": "0"
            }
            
            for key, value in ngio_settings.items():
                config["Settings"][key] = value
            
            # Write updated configuration
            with open(ngio_config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.logger.info("✅ NGIO configured for cache usage")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Failed to configure NGIO for cache usage: {e}")
            return False
    
    def validate_configurations(self) -> Tuple[bool, List[str]]:
        """
        Validate that all required configurations are present and correct
        
        Returns:
            Tuple[bool, List[str]]: (success, list of issues)
        """
        self.logger.info("🔍 Validating configurations...")
        
        issues = []
        
        # Check if all config files exist
        for config_name, config_path in self.config_files.items():
            if not os.path.exists(config_path):
                issues.append(f"Missing config file: {config_name} ({config_path})")
        
        # Validate Seasons of Skyrim configuration
        seasons_config_path = self.config_files.get("seasons_config")
        if seasons_config_path and os.path.exists(seasons_config_path):
            try:
                config = configparser.ConfigParser()
                self._read_config_with_bom_handling(config, seasons_config_path)
                
                # Check if season type setting exists
                season_type_found = False
                for section in config.sections():
                    for key in config[section].keys():
                        if key.lower() in ['season type', 'seasontype', 'season']:
                            season_type_found = True
                            break
                    if season_type_found:
                        break
                
                if not season_type_found:
                    issues.append("Season Type setting not found in po3_SeasonsOfSkyrim.ini")
                    
            except Exception as e:
                issues.append(f"Error reading seasons config: {e}")
        
        # Validate NGIO configuration
        ngio_config_path = self.config_files.get("ngio_config")
        if ngio_config_path and os.path.exists(ngio_config_path):
            try:
                config = configparser.ConfigParser()
                self._read_config_with_bom_handling(config, ngio_config_path)
                
                required_settings = ["UseGrassCache", "DynDOLODGrassMode"]
                for setting in required_settings:
                    found = False
                    for section in config.sections():
                        if setting in config[section]:
                            found = True
                            break
                    if not found:
                        issues.append(f"Missing NGIO setting: {setting}")
                        
            except Exception as e:
                issues.append(f"Error reading NGIO config: {e}")
        
        success = len(issues) == 0
        
        if success:
            self.logger.info("✅ All configurations validated successfully")
        else:
            self.logger.warning(f"⚠️ Found {len(issues)} configuration issues")
            for issue in issues:
                self.logger.warning(f"   - {issue}")
        
        return success, issues
    
    def restore_all_configs(self) -> bool:
        """
        Restore all configuration files from backups
        
        Returns:
            bool: True if successful, False if any restore failed
        """
        self.logger.info("🔄 Restoring original configurations...")
        
        if not self.backup_directory or not os.path.exists(self.backup_directory):
            self.logger.error("❌ No backup directory found")
            return False
        
        restore_success = True
        
        try:
            for config_name, config_path in self.config_files.items():
                backup_path = os.path.join(
                    self.backup_directory, 
                    f"{config_name}_{os.path.basename(config_path)}"
                )
                
                if os.path.exists(backup_path):
                    try:
                        shutil.copy2(backup_path, config_path)
                        self.logger.info(f"✅ Restored {config_name}")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to restore {config_name}: {e}")
                        restore_success = False
                else:
                    # Try to restore from memory if backup file missing
                    if config_name in self.original_configs:
                        try:
                            with open(config_path, 'w', encoding='utf-8') as f:
                                f.write(self.original_configs[config_name])
                            self.logger.info(f"✅ Restored {config_name} from memory")
                        except Exception as e:
                            self.logger.error(f"❌ Failed to restore {config_name} from memory: {e}")
                            restore_success = False
                    else:
                        self.logger.warning(f"⚠️ No backup found for {config_name}")
            
            if restore_success:
                self.logger.info("✅ All configurations restored successfully")
            
            return restore_success
            
        except Exception as e:
            self.logger.error(f"💥 Error during configuration restore: {e}")
            return False
    
    def get_current_season(self) -> Optional[int]:
        """
        Get the current season type from configuration
        
        Returns:
            Optional[int]: Current season type, or None if not found
        """
        seasons_config_path = self.config_files.get("seasons_config")
        if not seasons_config_path or not os.path.exists(seasons_config_path):
            return None
        
        try:
            config = configparser.ConfigParser()
            self._read_config_with_bom_handling(config, seasons_config_path)
            
            # Find season type setting
            for section in config.sections():
                for key, value in config[section].items():
                    if key.lower() in ['season type', 'seasontype', 'season']:
                        return int(value)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error reading current season: {e}")
            return None
    
    def cleanup_backups(self, keep_latest: int = 3) -> None:
        """
        Clean up old backup directories, keeping only the latest ones
        
        Args:
            keep_latest: Number of backup directories to keep
        """
        if not self.skyrim_path:
            return
            
        backup_root = os.path.join(self.skyrim_path, "NGIO_Backups")
        if not os.path.exists(backup_root):
            return
        
        try:
            # Get all backup directories
            backup_dirs = []
            for item in os.listdir(backup_root):
                item_path = os.path.join(backup_root, item)
                if os.path.isdir(item_path) and item.startswith("backup_"):
                    backup_dirs.append((item_path, os.path.getctime(item_path)))
            
            # Sort by creation time (newest first)
            backup_dirs.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for backup_path, _ in backup_dirs[keep_latest:]:
                try:
                    shutil.rmtree(backup_path)
                    self.logger.info(f"🗑️ Removed old backup: {os.path.basename(backup_path)}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove backup {backup_path}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Error during backup cleanup: {e}")


def main():
    """Test the ConfigManager functionality"""
    print("🧪 Testing ConfigManager...")
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Test validation
    success, issues = config_manager.validate_configurations()
    print(f"Validation: {'✅ Success' if success else '❌ Failed'}")
    
    if issues:
        for issue in issues:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
