#!/usr/bin/env python3
"""
Configuration Cache - Persistent Path Storage
Manages persistent storage of user-provided paths and settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .logger import Logger


@dataclass
class UserPaths:
    """User-provided paths configuration"""
    skyrim_path: str = ""
    output_directory: str = ""
    seasons_config_path: str = ""
    ngio_config_path: str = ""
    last_validated: str = ""
    
    def is_complete(self) -> bool:
        """Check if all required paths are provided"""
        return bool(self.skyrim_path and self.output_directory)
    
    def validate_paths(self) -> List[str]:
        """Validate that all paths exist"""
        issues = []
        
        if self.skyrim_path and not os.path.exists(self.skyrim_path):
            issues.append(f"Skyrim path not found: {self.skyrim_path}")
        
        if self.output_directory and not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create output directory: {self.output_directory} ({e})")
        
        if self.seasons_config_path and not os.path.exists(self.seasons_config_path):
            issues.append(f"Seasons config not found: {self.seasons_config_path}")
        
        if self.ngio_config_path and not os.path.exists(self.ngio_config_path):
            issues.append(f"NGIO config not found: {self.ngio_config_path}")
        
        return issues


@dataclass
class UserPreferences:
    """User preferences and settings"""
    seasons_to_generate: List[str] = None
    use_seasonal_mods: bool = True  # Whether user has seasonal mods installed
    max_crash_retries: int = 5
    crash_timeout_minutes: int = 60
    create_archives: bool = True
    backup_configs: bool = True
    auto_cleanup: bool = True
    
    def __post_init__(self):
        if self.seasons_to_generate is None:
            if self.use_seasonal_mods:
                self.seasons_to_generate = ["Winter", "Spring", "Summer", "Autumn"]
            else:
                self.seasons_to_generate = ["No Seasons"]


class ConfigCache:
    """
    Persistent configuration cache system
    
    Features:
    - Stores user-provided paths and preferences
    - Validates paths on startup
    - Interactive path collection if needed
    - JSON-based storage with backup
    - Automatic path re-validation
    """
    
    def __init__(self, config_file: str = None):
        self.logger = Logger("ConfigCache")
        
        # Set config file location
        if config_file:
            self.config_file = config_file
        else:
            # Store in user's app data directory
            app_data = os.path.expanduser("~")
            config_dir = os.path.join(app_data, ".ngio_automation")
            os.makedirs(config_dir, exist_ok=True)
            self.config_file = os.path.join(config_dir, "config.json")
        
        self.backup_file = f"{self.config_file}.backup"
        
        # Initialize configuration
        self.paths = UserPaths()
        self.preferences = UserPreferences()
        
        self.logger.info(f"📁 Config cache location: {self.config_file}")
    
    def load_config(self) -> bool:
        """
        Load configuration from disk
        
        Returns:
            bool: True if config loaded successfully, False if new config needed
        """
        if not os.path.exists(self.config_file):
            self.logger.info("📝 No existing configuration found")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load paths
            if 'paths' in config_data:
                self.paths = UserPaths(**config_data['paths'])
            
            # Load preferences
            if 'preferences' in config_data:
                self.preferences = UserPreferences(**config_data['preferences'])
            
            self.logger.info("✅ Configuration loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error loading configuration: {e}")
            
            # Try to load backup
            if os.path.exists(self.backup_file):
                self.logger.info("🔄 Attempting to load backup configuration...")
                try:
                    with open(self.backup_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    if 'paths' in config_data:
                        self.paths = UserPaths(**config_data['paths'])
                    if 'preferences' in config_data:
                        self.preferences = UserPreferences(**config_data['preferences'])
                    
                    self.logger.success("✅ Backup configuration loaded")
                    return True
                    
                except Exception as backup_error:
                    self.logger.error(f"💥 Backup loading failed: {backup_error}")
            
            return False
    
    def save_config(self) -> bool:
        """
        Save configuration to disk
        
        Returns:
            bool: True if saved successfully
        """
        try:
            # Create backup of existing config
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        backup_data = f.read()
                    with open(self.backup_file, 'w', encoding='utf-8') as f:
                        f.write(backup_data)
                except Exception:
                    pass  # Backup creation is optional
            
            # Prepare config data
            config_data = {
                'paths': asdict(self.paths),
                'preferences': asdict(self.preferences),
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("💾 Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error saving configuration: {e}")
            return False
    
    def validate_and_update_config(self) -> bool:
        """
        Validate current configuration and update if needed
        
        Returns:
            bool: True if config is valid, False if user input needed
        """
        self.logger.info("🔍 Validating configuration...")
        
        # Check if paths are complete
        if not self.paths.is_complete():
            self.logger.info("📝 Configuration incomplete, user input required")
            return False
        
        # Validate existing paths
        issues = self.paths.validate_paths()
        
        if issues:
            self.logger.warning("⚠️  Configuration validation issues found:")
            for issue in issues:
                self.logger.warning(f"   - {issue}")
            return False
        
        # Update last validated timestamp
        self.paths.last_validated = datetime.now().isoformat()
        self.save_config()
        
        self.logger.success("✅ Configuration is valid")
        return True
    
    def collect_user_paths(self) -> bool:
        """
        Interactively collect paths from user
        
        Returns:
            bool: True if collection successful
        """
        self.logger.separator("Configuration Setup")
        self.logger.info("🎮 NGIO Automation Suite - Initial Setup")
        self.logger.info("Please provide the following paths for grass cache generation:")
        self.logger.info("")
        
        try:
            # Collect Skyrim path
            skyrim_path = self._prompt_for_path(
                "Skyrim Installation Directory",
                "Enter the path to your Skyrim SE/AE/VR installation",
                self.paths.skyrim_path,
                self._validate_skyrim_path
            )
            
            if not skyrim_path:
                return False
            
            self.paths.skyrim_path = skyrim_path
            
            # Auto-detect config paths based on Skyrim path
            self._auto_detect_config_paths()
            
            # Collect output directory
            default_output = os.path.join(skyrim_path, "NGIO_Generated_Mods")
            output_path = self._prompt_for_path(
                "Output Directory",
                "Enter the directory where mod archives will be created",
                default_output,
                self._validate_output_path
            )
            
            if not output_path:
                return False
            
            self.paths.output_directory = output_path
            
            # Collect preferences
            self._collect_user_preferences()
            
            # Save configuration
            if self.save_config():
                self.logger.separator()
                self.logger.success("🎉 Configuration setup complete!")
                self.logger.info("📁 Your settings have been saved and will be remembered")
                self.logger.info("🔧 You can run the automation suite anytime now")
                return True
            else:
                self.logger.error("❌ Failed to save configuration")
                return False
                
        except KeyboardInterrupt:
            self.logger.warning("⚠️  Setup cancelled by user")
            return False
        except Exception as e:
            self.logger.error(f"💥 Error during setup: {e}")
            return False
    
    def _prompt_for_path(self, name: str, description: str, default: str, 
                        validator: callable) -> Optional[str]:
        """Prompt user for a path with validation"""
        self.logger.info(f"📂 {name}:")
        self.logger.info(f"   {description}")
        
        if default:
            self.logger.info(f"   Current/Default: {default}")
        
        while True:
            try:
                if default:
                    user_input = input(f"   Path (press Enter for default): ").strip()
                    if not user_input:
                        user_input = default
                else:
                    user_input = input(f"   Path: ").strip()
                
                if not user_input:
                    self.logger.error("❌ Path cannot be empty")
                    continue
                
                # Validate path
                is_valid, error_msg = validator(user_input)
                
                if is_valid:
                    self.logger.success(f"✅ Valid path: {user_input}")
                    return user_input
                else:
                    self.logger.error(f"❌ {error_msg}")
                    
                    # Ask if user wants to try again
                    retry = input("   Try again? (y/n): ").strip().lower()
                    if retry not in ['y', 'yes']:
                        return None
                        
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.error(f"❌ Input error: {e}")
                continue
    
    def _validate_skyrim_path(self, path: str) -> tuple:
        """Validate Skyrim installation path"""
        if not os.path.exists(path):
            return False, "Directory does not exist"
        
        # Check for Skyrim executables
        executables = ["SkyrimSE.exe", "SkyrimVR.exe", "TESV.exe"]
        found_exe = None
        
        for exe in executables:
            if os.path.exists(os.path.join(path, exe)):
                found_exe = exe
                break
        
        if not found_exe:
            return False, "No Skyrim executable found (SkyrimSE.exe, SkyrimVR.exe, or TESV.exe)"
        
        # Check for Data directory
        data_dir = os.path.join(path, "Data")
        if not os.path.exists(data_dir):
            return False, "Data directory not found"
        
        return True, f"Valid Skyrim installation ({found_exe})"
    
    def _validate_output_path(self, path: str) -> tuple:
        """Validate output directory path"""
        # Try to create directory if it doesn't exist
        try:
            os.makedirs(path, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(path, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            return True, "Valid output directory"
            
        except PermissionError:
            return False, "No write permission to directory"
        except Exception as e:
            return False, f"Cannot create or write to directory: {e}"
    
    def _auto_detect_config_paths(self) -> None:
        """Auto-detect configuration file paths based on Skyrim path"""
        if not self.paths.skyrim_path:
            return
        
        # Look for Seasons of Skyrim config
        seasons_locations = [
            os.path.join(self.paths.skyrim_path, "Data", "SKSE", "Plugins", "po3_SeasonsOfSkyrim.ini"),
            os.path.join(self.paths.skyrim_path, "Data", "po3_SeasonsOfSkyrim.ini")
        ]
        
        for location in seasons_locations:
            if os.path.exists(location):
                self.paths.seasons_config_path = location
                self.logger.info(f"🔍 Found Seasons config: {location}")
                break
        
        # Look for NGIO config
        ngio_locations = [
            os.path.join(self.paths.skyrim_path, "Data", "SKSE", "Plugins", "GrassControl.ini"),
            os.path.join(self.paths.skyrim_path, "Data", "GrassControl.ini")
        ]
        
        for location in ngio_locations:
            if os.path.exists(location):
                self.paths.ngio_config_path = location
                self.logger.info(f"🔍 Found NGIO config: {location}")
                break
    
    def _collect_user_preferences(self) -> None:
        """Collect user preferences"""
        self.logger.info("")
        self.logger.info("⚙️  Preferences (optional - press Enter for defaults):")
        
        try:
            # First, ask about seasonal mod usage
            self.logger.info("🌿 Do you use seasonal mods (like Seasons of Skyrim)?")
            self.logger.info("   This affects how grass cache is generated and named")
            seasonal_choice = input("   Use seasonal mods? (y/n, default y): ").strip().lower()
            
            if seasonal_choice in ['n', 'no']:
                self.preferences.use_seasonal_mods = False
                self.preferences.seasons_to_generate = ["No Seasons"]
                self.logger.info("✅ Configured for non-seasonal grass cache generation")
            else:
                self.preferences.use_seasonal_mods = True
                
                # Seasons to generate
                self.logger.info("")
                self.logger.info("🌱 Which seasons to generate?")
                self.logger.info("   1. All seasons (Winter, Spring, Summer, Autumn)")
                self.logger.info("   2. Custom selection")
                self.logger.info("   3. Specific combinations")
                
                choice = input("   Choice (1-3, default 1): ").strip()
                
                if choice == "2":
                    seasons = []
                    for season in ["Winter", "Spring", "Summer", "Autumn"]:
                        include = input(f"   Include {season}? (y/n, default y): ").strip().lower()
                        if include not in ['n', 'no']:
                            seasons.append(season)
                    
                    if seasons:
                        self.preferences.seasons_to_generate = seasons
                    else:
                        self.logger.warning("⚠️ No seasons selected, using all seasons")
                        
                elif choice == "3":
                    self.logger.info("   Popular combinations:")
                    self.logger.info("   a. Winter + Summer only")
                    self.logger.info("   b. Spring + Autumn only") 
                    self.logger.info("   c. Winter + Spring only")
                    self.logger.info("   d. Summer + Autumn only")
                    self.logger.info("   e. Custom combination")
                    
                    combo_choice = input("   Choose combination (a-e, default a): ").strip().lower()
                    
                    if combo_choice == "b":
                        self.preferences.seasons_to_generate = ["Spring", "Autumn"]
                    elif combo_choice == "c":
                        self.preferences.seasons_to_generate = ["Winter", "Spring"]
                    elif combo_choice == "d":
                        self.preferences.seasons_to_generate = ["Summer", "Autumn"]
                    elif combo_choice == "e":
                        # Custom combination
                        seasons = []
                        for season in ["Winter", "Spring", "Summer", "Autumn"]:
                            include = input(f"   Include {season}? (y/n): ").strip().lower()
                            if include in ['y', 'yes']:
                                seasons.append(season)
                        if seasons:
                            self.preferences.seasons_to_generate = seasons
                    else:  # Default to Winter + Summer
                        self.preferences.seasons_to_generate = ["Winter", "Summer"]
            
            # Crash retries
            retries = input(f"   Max crash retries (default {self.preferences.max_crash_retries}): ").strip()
            if retries.isdigit():
                self.preferences.max_crash_retries = int(retries)
            
            # Timeout (clarify what this means)
            self.logger.info("   ⏰ Inactivity timeout: How long to wait if generation stops progressing")
            self.logger.info("   (Active generation can run longer than this - no hard limit)")
            timeout = input(f"   Inactivity timeout in minutes (default {self.preferences.crash_timeout_minutes}): ").strip()
            if timeout.isdigit():
                self.preferences.crash_timeout_minutes = int(timeout)
            
            # Archive creation
            create_archives = input("   Create mod archives? (y/n, default y): ").strip().lower()
            if create_archives in ['n', 'no']:
                self.preferences.create_archives = False
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.logger.warning(f"Error collecting preferences: {e}")
    
    def get_paths(self) -> UserPaths:
        """Get current paths configuration"""
        return self.paths
    
    def get_preferences(self) -> UserPreferences:
        """Get current preferences"""
        return self.preferences
    
    def update_path(self, path_name: str, new_path: str) -> bool:
        """Update a specific path"""
        if hasattr(self.paths, path_name):
            setattr(self.paths, path_name, new_path)
            return self.save_config()
        return False
    
    def reset_config(self) -> bool:
        """Reset configuration to defaults"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            if os.path.exists(self.backup_file):
                os.remove(self.backup_file)
            
            self.paths = UserPaths()
            self.preferences = UserPreferences()
            
            self.logger.info("🔄 Configuration reset to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error resetting configuration: {e}")
            return False
    
    def show_current_config(self) -> None:
        """Display current configuration"""
        self.logger.separator("Current Configuration")
        
        self.logger.info("📁 Paths:")
        self.logger.info(f"   Skyrim: {self.paths.skyrim_path or 'Not set'}")
        self.logger.info(f"   Output: {self.paths.output_directory or 'Not set'}")
        self.logger.info(f"   Seasons Config: {self.paths.seasons_config_path or 'Auto-detect'}")
        self.logger.info(f"   NGIO Config: {self.paths.ngio_config_path or 'Auto-detect'}")
        
        self.logger.info("")
        self.logger.info("⚙️  Preferences:")
        self.logger.info(f"   Seasonal Mods: {'Yes' if self.preferences.use_seasonal_mods else 'No'}")
        if self.preferences.use_seasonal_mods:
            self.logger.info(f"   Seasons: {', '.join(self.preferences.seasons_to_generate)}")
        else:
            self.logger.info(f"   Mode: Non-seasonal grass cache")
        self.logger.info(f"   Max Retries: {self.preferences.max_crash_retries}")
        self.logger.info(f"   Inactivity Timeout: {self.preferences.crash_timeout_minutes} minutes")
        self.logger.info(f"   Create Archives: {'Yes' if self.preferences.create_archives else 'No'}")
        self.logger.info(f"   Backup Configs: {'Yes' if self.preferences.backup_configs else 'No'}")
        
        if self.paths.last_validated:
            self.logger.info(f"   Last Validated: {self.paths.last_validated}")
        
        self.logger.separator()


def main():
    """Test the ConfigCache functionality"""
    print("🧪 Testing ConfigCache...")
    
    # Create config cache
    config_cache = ConfigCache("test_config.json")
    
    # Try to load existing config
    if config_cache.load_config():
        print("✅ Loaded existing configuration")
        config_cache.show_current_config()
        
        # Validate paths
        if config_cache.validate_and_update_config():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration needs updates")
    else:
        print("📝 No configuration found, would collect from user")
        # In real usage: config_cache.collect_user_paths()
    
    # Cleanup test file
    try:
        os.remove("test_config.json")
        os.remove("test_config.json.backup")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
