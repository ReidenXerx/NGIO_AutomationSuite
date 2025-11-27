#!/usr/bin/env python3
"""
Config Loader - YAML Configuration System (v1.2.0+)
Provides flexible configuration management with defaults and validation
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from .logger import Logger


@dataclass
class NGIOConfig:
    """
    Complete NGIO Automation Suite configuration
    
    Features (v1.2.0+):
    - YAML file support for persistent configuration
    - Environment variable overrides
    - Sensible defaults
    - Validation and type checking
    """
    
    # === CORE SETTINGS ===
    skyrim_path: str = ""
    output_directory: str = ""
    
    # === SEASONS TO GENERATE ===
    generate_winter: bool = True
    generate_spring: bool = True
    generate_summer: bool = True
    generate_autumn: bool = True
    generate_no_seasons: bool = False
    
    # === CRASH & HANG DETECTION ===
    max_crash_retries: int = 10
    crash_timeout_minutes: int = 5
    no_progress_timeout_minutes: int = 15
    startup_wait_seconds: int = 30
    adaptive_timeouts: bool = True
    
    # === ARCHIVE CREATION ===
    create_archives: bool = True
    generate_checksums: bool = True
    archive_format: str = "zip"  # Future: 7z, rar
    
    # === BACKUP & SAFETY ===
    backup_configs: bool = True
    backup_directory: str = ""  # Auto-detect if empty
    
    # === NOTIFICATIONS (v1.2.0+) ===
    enable_notifications: bool = True
    enable_sounds: bool = True
    notify_on_completion: bool = True
    notify_on_error: bool = True
    
    # === LOGGING & OUTPUT ===
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_to_file: bool = False
    log_file_path: str = ""  # Auto-detect if empty
    
    # === ADVANCED SETTINGS ===
    parallel_file_operations: bool = True
    max_worker_threads: int = 8
    verify_mod_load_order: bool = True
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Validate Skyrim path
        if not self.skyrim_path:
            errors.append("Skyrim path is required")
        elif not Path(self.skyrim_path).exists():
            errors.append(f"Skyrim path does not exist: {self.skyrim_path}")
        
        # Validate numeric ranges
        if self.max_crash_retries < 1:
            errors.append("max_crash_retries must be at least 1")
        if self.crash_timeout_minutes < 1:
            errors.append("crash_timeout_minutes must be at least 1")
        if self.no_progress_timeout_minutes < 1:
            errors.append("no_progress_timeout_minutes must be at least 1")
        if self.startup_wait_seconds < 0:
            errors.append("startup_wait_seconds must be non-negative")
        if self.max_worker_threads < 1:
            errors.append("max_worker_threads must be at least 1")
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if self.log_level.upper() not in valid_levels:
            errors.append(f"log_level must be one of: {', '.join(valid_levels)}")
        
        # Check at least one season selected
        if not any([
            self.generate_winter,
            self.generate_spring,
            self.generate_summer,
            self.generate_autumn,
            self.generate_no_seasons
        ]):
            errors.append("At least one season must be enabled")
        
        return (len(errors) == 0, errors)
    
    def get_enabled_seasons(self) -> list[str]:
        """Get list of enabled season names"""
        seasons = []
        if self.generate_winter:
            seasons.append("Winter")
        if self.generate_spring:
            seasons.append("Spring")
        if self.generate_summer:
            seasons.append("Summer")
        if self.generate_autumn:
            seasons.append("Autumn")
        if self.generate_no_seasons:
            seasons.append("No Seasons")
        return seasons


class ConfigLoader:
    """
    Configuration loader with YAML support
    
    Priority order (highest to lowest):
    1. Environment variables (NGIO_*)
    2. YAML configuration file
    3. Default values
    """
    
    DEFAULT_CONFIG_PATHS = [
        "ngio_config.yaml",
        "config/ngio_config.yaml",
        os.path.expanduser("~/.ngio/config.yaml"),
        os.path.expanduser("~/Documents/NGIO_AutomationSuite/config.yaml")
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = Logger("ConfigLoader")
        self.config_path = config_path
        self.config = NGIOConfig()
    
    def load(self) -> NGIOConfig:
        """
        Load configuration from all sources
        
        Returns:
            NGIOConfig instance with merged settings
        """
        # Start with defaults
        self.config = NGIOConfig()
        
        # Try to load from YAML
        yaml_config = self._load_yaml()
        if yaml_config:
            self._merge_yaml_config(yaml_config)
        
        # Override with environment variables
        self._apply_env_overrides()
        
        # Auto-detect paths if not set
        self._auto_detect_paths()
        
        return self.config
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in default locations"""
        # Check explicit path first
        if self.config_path:
            path = Path(self.config_path)
            if path.exists():
                return path
            else:
                self.logger.warning(f"Config file not found: {self.config_path}")
                return None
        
        # Check default locations
        for path_str in self.DEFAULT_CONFIG_PATHS:
            path = Path(path_str)
            if path.exists():
                self.logger.debug(f"Found config file: {path}")
                return path
        
        return None
    
    def _load_yaml(self) -> Optional[Dict[str, Any]]:
        """Load YAML configuration file"""
        config_file = self._find_config_file()
        
        if not config_file:
            self.logger.debug("No YAML config file found, using defaults")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            self.logger.info(f"📄 Loaded config from: {config_file}")
            return yaml_data
        
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML syntax in {config_file}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_file}: {e}")
            return None
    
    def _merge_yaml_config(self, yaml_data: Dict[str, Any]) -> None:
        """Merge YAML data into config object"""
        for key, value in yaml_data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown config key in YAML: {key}")
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        env_mappings = {
            'NGIO_SKYRIM_PATH': 'skyrim_path',
            'NGIO_OUTPUT_DIR': 'output_directory',
            'NGIO_MAX_RETRIES': ('max_crash_retries', int),
            'NGIO_CRASH_TIMEOUT': ('crash_timeout_minutes', int),
            'NGIO_PROGRESS_TIMEOUT': ('no_progress_timeout_minutes', int),
            'NGIO_STARTUP_WAIT': ('startup_wait_seconds', int),
            'NGIO_LOG_LEVEL': 'log_level',
            'NGIO_NOTIFICATIONS': ('enable_notifications', lambda x: x.lower() in ['true', '1', 'yes']),
            'NGIO_SOUNDS': ('enable_sounds', lambda x: x.lower() in ['true', '1', 'yes']),
        }
        
        for env_var, config_attr in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if isinstance(config_attr, tuple):
                    attr_name, converter = config_attr
                    try:
                        setattr(self.config, attr_name, converter(value))
                        self.logger.debug(f"Applied env override: {env_var} -> {attr_name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to convert {env_var}: {e}")
                else:
                    setattr(self.config, config_attr, value)
                    self.logger.debug(f"Applied env override: {env_var} -> {config_attr}")
    
    def _auto_detect_paths(self) -> None:
        """Auto-detect paths if not explicitly set"""
        # Auto-detect Skyrim path if not set
        if not self.config.skyrim_path:
            detected = self._detect_skyrim_path()
            if detected:
                self.config.skyrim_path = detected
                self.logger.info(f"🔍 Auto-detected Skyrim: {detected}")
        
        # Set default output directory
        if not self.config.output_directory:
            self.config.output_directory = str(Path.cwd() / "output")
        
        # Set default backup directory
        if not self.config.backup_directory:
            self.config.backup_directory = str(Path.cwd() / "backups")
        
        # Set default log file path
        if self.config.log_to_file and not self.config.log_file_path:
            self.config.log_file_path = str(Path.cwd() / "logs" / "ngio_automation.log")
    
    def _detect_skyrim_path(self) -> Optional[str]:
        """Try to auto-detect Skyrim installation"""
        # Common Steam library locations
        possible_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition",
            r"C:\Steam\steamapps\common\Skyrim Special Edition",
            r"D:\Steam\steamapps\common\Skyrim Special Edition",
            r"E:\Steam\steamapps\common\Skyrim Special Edition",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def save_template(self, output_path: str = "ngio_config.yaml") -> bool:
        """
        Save a template configuration file with all options documented
        
        Args:
            output_path: Where to save the template
            
        Returns:
            True if successful
        """
        try:
            template = """# NGIO Automation Suite Configuration (v1.2.0+)
# This file allows you to customize all aspects of grass cache generation

# === CORE SETTINGS ===
skyrim_path: "C:/Steam/steamapps/common/Skyrim Special Edition"
output_directory: "./output"

# === SEASONS TO GENERATE ===
generate_winter: true
generate_spring: true
generate_summer: true
generate_autumn: true
generate_no_seasons: false  # Enable for non-seasonal setups

# === CRASH & HANG DETECTION ===
max_crash_retries: 10            # Max retries per season before giving up
crash_timeout_minutes: 5         # Time to wait for process crash
no_progress_timeout_minutes: 15  # Timeout if no new files generated
startup_wait_seconds: 30         # Wait between retry attempts
adaptive_timeouts: true          # Learn optimal timeouts for your system

# === ARCHIVE CREATION ===
create_archives: true
generate_checksums: true         # SHA256 checksums for verification
archive_format: "zip"            # Archive format (currently only zip)

# === BACKUP & SAFETY ===
backup_configs: true
backup_directory: "./backups"

# === NOTIFICATIONS (v1.2.0+) ===
enable_notifications: true       # Windows toast notifications
enable_sounds: true              # System sound alerts
notify_on_completion: true
notify_on_error: true

# === LOGGING & OUTPUT ===
log_level: "INFO"                # DEBUG, INFO, WARNING, ERROR
log_to_file: false
log_file_path: "./logs/ngio_automation.log"

# === ADVANCED SETTINGS ===
parallel_file_operations: true
max_worker_threads: 8
verify_mod_load_order: true

# === LARGE LOAD ORDER TIPS ===
# For 500+ mods, consider these settings:
# - max_crash_retries: 15
# - no_progress_timeout_minutes: 30
# - startup_wait_seconds: 60
# - adaptive_timeouts: true

# For more information, see docs/LARGE_LOAD_ORDER_GUIDE.md
"""
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template)
            
            self.logger.success(f"✅ Saved config template: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save config template: {e}")
            return False
    
    def validate_and_report(self) -> bool:
        """
        Validate configuration and report any errors
        
        Returns:
            True if valid
        """
        is_valid, errors = self.config.validate()
        
        if not is_valid:
            self.logger.error("❌ Configuration validation failed:")
            for error in errors:
                self.logger.error(f"   - {error}")
            return False
        
        self.logger.success("✅ Configuration validated successfully")
        return True


# === HELPER FUNCTIONS ===

def load_config(config_path: Optional[str] = None) -> NGIOConfig:
    """
    Convenience function to load configuration
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        NGIOConfig instance
    """
    loader = ConfigLoader(config_path)
    config = loader.load()
    loader.validate_and_report()
    return config


def create_config_template(output_path: str = "ngio_config.yaml") -> bool:
    """
    Create a configuration template file
    
    Args:
        output_path: Where to save the template
        
    Returns:
        True if successful
    """
    loader = ConfigLoader()
    return loader.save_template(output_path)


if __name__ == "__main__":
    # Example usage and testing
    print("NGIO Configuration Loader - Testing")
    print("=" * 60)
    
    # Create a template
    print("\n1. Creating config template...")
    if create_config_template("example_config.yaml"):
        print("   ✅ Template created: example_config.yaml")
    
    # Load configuration
    print("\n2. Loading configuration...")
    config = load_config()
    
    print(f"\n3. Current configuration:")
    print(f"   Skyrim Path: {config.skyrim_path}")
    print(f"   Output Dir: {config.output_directory}")
    print(f"   Enabled Seasons: {', '.join(config.get_enabled_seasons())}")
    print(f"   Max Retries: {config.max_crash_retries}")
    print(f"   Notifications: {'ON' if config.enable_notifications else 'OFF'}")
    print(f"   Log Level: {config.log_level}")
    
    print("\n4. Validation:")
    is_valid, errors = config.validate()
    if is_valid:
        print("   ✅ Configuration is valid!")
    else:
        print("   ❌ Configuration errors:")
        for error in errors:
            print(f"      - {error}")

