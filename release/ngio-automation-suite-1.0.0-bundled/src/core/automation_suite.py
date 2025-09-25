#!/usr/bin/env python3
"""
NGIO Automation Suite - Main Controller
Orchestrates the complete grass cache generation workflow
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .game_manager import GameManager
from .config_manager import ConfigManager
from .file_processor import FileProcessor
from .progress_monitor import ProgressMonitor
from .archive_creator import ArchiveCreator
from ..utils.logger import Logger
from ..utils.config_cache import ConfigCache


class Season(Enum):
    """Enumeration for different seasons and non-seasonal mode"""
    WINTER = (1, "Winter", ".WIN.cgid")
    SPRING = (2, "Spring", ".SPR.cgid")
    SUMMER = (3, "Summer", ".SUM.cgid")
    AUTUMN = (4, "Autumn", ".AUT.cgid")
    NO_SEASONS = (0, "No Seasons", ".cgid")  # For users without seasonal mods
    
    def __init__(self, season_type: int, display_name: str, extension: str):
        self.season_type = season_type
        self.display_name = display_name
        self.extension = extension
    
    @classmethod
    def get_seasonal_seasons(cls):
        """Get only seasonal seasons (excludes NO_SEASONS)"""
        return [cls.WINTER, cls.SPRING, cls.SUMMER, cls.AUTUMN]
    
    @classmethod
    def get_all_seasons(cls):
        """Get all seasons including NO_SEASONS"""
        return list(cls)


@dataclass
class AutomationConfig:
    """Configuration for the automation process"""
    skyrim_path: str
    output_directory: str = ""
    seasons_to_generate: List[Season] = None
    max_crash_retries: int = 5
    crash_timeout_minutes: int = 5  # Process crash detection
    no_progress_timeout_minutes: int = 10  # File inactivity detection
    create_archives: bool = True
    backup_configs: bool = True
    
    def __post_init__(self):
        if self.seasons_to_generate is None:
            self.seasons_to_generate = list(Season)


class NGIOAutomationSuite:
    """
    Main automation controller for NGIO grass cache generation
    
    Orchestrates the entire workflow:
    1. Setup and validation
    2. Season-by-season generation
    3. File processing and organization
    4. Cleanup and restoration
    """
    
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.logger = Logger("NGIOAutomationSuite")
        
        # Initialize managers
        self.game_manager = GameManager(config.skyrim_path)
        self.config_manager = ConfigManager(config.skyrim_path)
        self.file_processor = FileProcessor()
        self.progress_monitor = ProgressMonitor()
        self.archive_creator = ArchiveCreator(config.output_directory)
        
        # State tracking
        self.current_season: Optional[Season] = None
        self.completed_seasons: List[Season] = []
        self.failed_seasons: List[Season] = []
        self.start_time: Optional[float] = None
        
    def run_full_automation(self) -> bool:
        """
        Run the complete automation workflow
        
        Returns:
            bool: True if successful, False if failed
        """
        self.logger.info("🌱 Starting NGIO Automation Suite")
        self.start_time = time.time()
        
        try:
            # Phase 1: Setup and Validation
            if not self._setup_and_validate():
                return False
                
            # Phase 2: Backup configurations
            if not self._backup_configurations():
                return False
                
            # Phase 3: Generate grass cache for each season
            for season in self.config.seasons_to_generate:
                if not self._generate_season_cache(season):
                    self.failed_seasons.append(season)
                    self.logger.error(f"❌ Failed to generate cache for {season.display_name}")
                else:
                    self.completed_seasons.append(season)
                    self.logger.info(f"✅ Successfully completed {season.display_name}")
                    
            # Phase 4: Archive creation handled per-season
            # (Archives created individually after each season)
            
            # Phase 5: Cleanup and restoration
            self._restore_configurations()
            
            # Phase 6: Generate final report
            self._generate_completion_report()
            
            return len(self.failed_seasons) == 0
            
        except KeyboardInterrupt:
            self.logger.warning("⚠️ Process interrupted by user")
            self._emergency_cleanup()
            return False
        except Exception as e:
            self.logger.error(f"💥 Unexpected error: {e}")
            self._emergency_cleanup()
            return False
    
    def _setup_and_validate(self) -> bool:
        """Setup and validate the environment"""
        self.logger.info("🔍 Validating environment...")
        
        # Validate Skyrim installation
        if not os.path.exists(self.config.skyrim_path):
            self.logger.error("❌ Skyrim path does not exist")
            return False
            
        # Check for Skyrim executable
        executables = ["SkyrimSE.exe", "SkyrimVR.exe", "TESV.exe"]
        found_exe = None
        for exe in executables:
            if os.path.exists(os.path.join(self.config.skyrim_path, exe)):
                found_exe = exe
                break
        
        if not found_exe:
            self.logger.error("❌ No Skyrim executable found")
            return False
        
        self.logger.info(f"✅ Found Skyrim executable: {found_exe}")
        
        # Validate Data directory
        data_dir = os.path.join(self.config.skyrim_path, "Data")
        if not os.path.exists(data_dir):
            self.logger.error("❌ Skyrim Data directory not found")
            return False
            
        # Ensure output directory exists
        if not self.config.output_directory:
            self.config.output_directory = os.path.join(self.config.skyrim_path, "NGIO_Generated_Mods")
        
        os.makedirs(self.config.output_directory, exist_ok=True)
            
        self.logger.info("✅ Environment validation complete")
        return True
    
    def _backup_configurations(self) -> bool:
        """Backup original configuration files"""
        if not self.config.backup_configs:
            return True
            
        self.logger.info("💾 Backing up configuration files...")
        return self.config_manager.backup_all_configs()
    
    def _generate_season_cache(self, season: Season) -> bool:
        """
        Generate grass cache for a specific season
        
        Args:
            season: The season to generate cache for
            
        Returns:
            bool: True if successful, False if failed
        """
        self.current_season = season
        self.logger.info(f"🌱 Starting {season.display_name} grass cache generation...")
        
        try:
            # Step 1: Configure season settings
            if not self.config_manager.set_season(season.season_type):
                return False
                
            # Step 2: Launch Skyrim and monitor generation
            if not self._run_generation_with_monitoring(season):
                return False
                
            # Step 3: Process and rename generated files
            if not self._process_generated_files(season):
                return False
                
            # Step 4: Create archive for this season
            if self.config.create_archives:
                if not self._create_single_season_archive(season):
                    return False
                    
                # Step 5: Clean up seasonal files after successful archive creation
                if not self._cleanup_season_files(season):
                    self.logger.warning(f"⚠️ Failed to clean up {season.display_name} files, but continuing...")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error generating {season.display_name}: {e}")
            return False
    
    def _run_generation_with_monitoring(self, season: Season) -> bool:
        """Run grass generation with intelligent crash monitoring"""
        # First check if this season is already completed
        if self._is_season_completed(season):
            self.logger.info(f"🏁 {season.display_name} already completed - skipping Skyrim launch")
            self.logger.info(f"📁 Grass cache files exist, proceeding to post-processing...")
            return True
            
        max_retries = self.config.max_crash_retries
        retry_count = 0
        
        while retry_count < max_retries:
            is_retry = retry_count > 0
            self.logger.info(f"🎮 Launching Skyrim for {season.display_name} (attempt {retry_count + 1})")
            
            # Launch Skyrim with grass generation enabled
            # On retry: preserves existing PrecacheGrass.txt for resume
            # On first attempt: creates fresh PrecacheGrass.txt
            process = self.game_manager.launch_for_generation(is_retry=is_retry)
            if not process:
                return False
            
            # Wait for generation to start (file should appear and grow)
            self.logger.info("⏳ Waiting for grass generation to begin...")
            time.sleep(10)  # Give Skyrim time to start
            
            # Check if PrecacheGrass.txt exists and is being written to
            precache_status = self.game_manager.check_precache_file_status()
            if not precache_status["exists"]:
                self.logger.warning("⚠️ PrecacheGrass.txt not found - generation may not have started")
            else:
                self.logger.info("✅ PrecacheGrass.txt found - generation active")
            
            # Primary monitoring: Wait for PrecacheGrass.txt to be deleted (completion signal)
            generation_completed = self.game_manager.wait_for_precache_completion(
                timeout_minutes=self.config.no_progress_timeout_minutes
            )
            
            if generation_completed:
                self.logger.success(f"🎉 {season.display_name} generation completed successfully!")
                
                # Verify that Skyrim process has closed (should happen automatically)
                if self.game_manager.is_process_running():
                    self.logger.info("🔄 Waiting for Skyrim to close...")
                    time.sleep(5)
                    
                    if self.game_manager.is_process_running():
                        self.logger.warning("⚠️ Skyrim still running, forcing close...")
                        self.game_manager.force_terminate()
                
                return True
            else:
                # Generation failed - check why
                if self.game_manager.is_process_running():
                    # Process still running but no progress - likely hung
                    self.logger.warning("🔒 Skyrim appears to be hung, forcing restart...")
                    self.game_manager.force_terminate()
                else:
                    # Process crashed
                    self.logger.warning("💥 Skyrim crashed during generation")
                
                retry_count += 1
                
                if retry_count < max_retries:
                    self.logger.info(f"🔄 Retrying generation (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(5)  # Brief pause before retry
                else:
                    self.logger.error(f"❌ Max retries exceeded for {season.display_name}")
                    return False
                
        return False
    
    def _process_generated_files(self, season: Season) -> bool:
        """Process and rename generated grass cache files"""
        self.logger.info(f"⚡ Processing {season.display_name} files...")
        
        # Grass files are generated in Skyrim's Data/Grass directory
        grass_directory = os.path.join(self.config.skyrim_path, "Data", "Grass")
        if not os.path.exists(grass_directory):
            self.logger.error("❌ No Grass directory found after generation")
            return False
            
        # Use high-speed file processor to rename files
        return self.file_processor.process_season_files(grass_directory, season)
    
    def _create_single_season_archive(self, season: Season) -> bool:
        """Create mod archive for a single season immediately after generation"""
        self.logger.info(f"📦 Creating archive for {season.display_name}...")
        
        grass_directory = os.path.join(self.config.skyrim_path, "Data", "Grass")
        
        if not os.path.exists(grass_directory):
            self.logger.error("❌ No Grass directory found")
            return False
        
        # Create archive for this specific season
        archive_info = self.archive_creator.create_season_archive(season, grass_directory)
        
        if archive_info:
            self.logger.success(f"✅ Created archive: {archive_info.archive_path}")
            self.logger.info(f"📊 Archive size: {archive_info.archive_size_mb:.1f} MB")
            self.logger.info(f"📁 Files included: {archive_info.file_count}")
            
            # Generate/update installation guide
            guide_path = os.path.join(self.config.output_directory, "INSTALLATION_GUIDE.txt")
            self.archive_creator.generate_installation_guide(guide_path)
            
            return True
        else:
            self.logger.error(f"❌ Failed to create archive for {season.display_name}")
            return False
    
    def _cleanup_season_files(self, season: Season) -> bool:
        """
        Clean up seasonal grass cache files after successful archive creation
        
        This removes the season-specific files from Data/Grass to prevent
        accumulation of thousands of files from multiple seasons.
        
        Args:
            season: The season whose files should be cleaned up
            
        Returns:
            bool: True if cleanup successful, False if failed
        """
        self.logger.info(f"🧹 Cleaning up {season.display_name} files from Grass directory...")
        
        grass_directory = os.path.join(self.config.skyrim_path, "Data", "Grass")
        
        if not os.path.exists(grass_directory):
            self.logger.warning("⚠️ Grass directory not found, nothing to clean")
            return True
        
        try:
            # Find all files with this season's extension
            seasonal_files = []
            for root, dirs, files in os.walk(grass_directory):
                for file in files:
                    if file.endswith(season.extension):
                        full_path = os.path.join(root, file)
                        seasonal_files.append(full_path)
            
            if not seasonal_files:
                self.logger.info(f"✅ No {season.display_name} files found to clean up")
                return True
            
            self.logger.info(f"🗑️ Removing {len(seasonal_files)} {season.display_name} files...")
            
            # Remove all seasonal files
            removed_count = 0
            failed_count = 0
            
            for file_path in seasonal_files:
                try:
                    os.remove(file_path)
                    removed_count += 1
                except Exception as e:
                    self.logger.debug(f"Failed to remove {file_path}: {e}")
                    failed_count += 1
            
            if failed_count > 0:
                self.logger.warning(f"⚠️ Failed to remove {failed_count} files, but {removed_count} removed successfully")
            else:
                self.logger.success(f"✅ Successfully removed {removed_count} {season.display_name} files")
            
            return failed_count == 0
            
        except Exception as e:
            self.logger.error(f"💥 Error during {season.display_name} file cleanup: {e}")
            return False
    
    def _restore_configurations(self) -> bool:
        """Restore original configuration files"""
        if not self.config.backup_configs:
            return True
            
        self.logger.info("🔄 Restoring original configurations...")
        
        # Restore to seasonal mode (type 5)
        self.config_manager.set_season(5)  # Seasonal mode
        return self.config_manager.restore_all_configs()
    
    def _generate_completion_report(self) -> None:
        """Generate and display completion report"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        self.logger.info("=" * 60)
        self.logger.info("🎉 NGIO AUTOMATION SUITE - COMPLETION REPORT")
        self.logger.info("=" * 60)
        self.logger.info(f"⏱️  Total processing time: {total_time/60:.1f} minutes")
        
        if len(self.completed_seasons) > 0:
            season_name = self.completed_seasons[0].display_name
            self.logger.info(f"✅ Successfully completed: {season_name}")
        
        if len(self.failed_seasons) > 0:
            season_name = self.failed_seasons[0].display_name
            self.logger.info(f"❌ Failed: {season_name}")
        
        if self.completed_seasons:
            self.logger.info("📝 Completed seasons:")
            for season in self.completed_seasons:
                self.logger.info(f"   ✅ {season.display_name}")
                
        if self.failed_seasons:
            self.logger.info("📝 Failed seasons:")
            for season in self.failed_seasons:
                self.logger.info(f"   ❌ {season.display_name}")
                
        self.logger.info("=" * 60)
        
        if len(self.failed_seasons) == 0:
            if len(self.completed_seasons) > 0:
                season_name = self.completed_seasons[0].display_name
                self.logger.info(f"🎊 {season_name.upper()} COMPLETED SUCCESSFULLY!")
                self.logger.info("🎯 Next steps:")
                self.logger.info("   1. Install the generated archive in your mod manager")
                self.logger.info("   2. Keep NGIO mod ENABLED (for future grass generation)")
                self.logger.info("   3. Ensure Grass Cache Helper NG is enabled")
                self.logger.info("   4. Run this script again for other seasons!")
                self.logger.info("   5. Enjoy your automated seasonal grass cache!")
        else:
            season_name = self.failed_seasons[0].display_name
            self.logger.warning(f"⚠️  {season_name} generation failed. Check logs for details.")
    
    def _emergency_cleanup(self) -> None:
        """Emergency cleanup in case of unexpected failure"""
        self.logger.warning("🚨 Performing emergency cleanup...")
        try:
            # Kill any running Skyrim processes
            self.game_manager.cleanup_processes()
            
            # Restore configurations if possible
            if self.config.backup_configs:
                self.config_manager.restore_all_configs()
                
        except Exception as e:
            self.logger.error(f"💥 Error during emergency cleanup: {e}")

    def _is_season_completed(self, season: Season) -> bool:
        """
        Check if a season's grass cache generation is already completed
        
        A season is considered completed if:
        1. No PrecacheGrass.txt exists (plugin deleted it after completion)
        2. Season-specific grass cache files exist in Data/Grass/
        
        Args:
            season: The season to check
            
        Returns:
            bool: True if season is already completed, False otherwise
        """
        try:
            # Check if PrecacheGrass.txt exists
            precache_file = os.path.join(self.config.skyrim_path, "PrecacheGrass.txt")
            if os.path.exists(precache_file):
                # If PrecacheGrass.txt exists, generation is not completed
                return False
            
            # Check for season-specific grass cache files
            grass_dir = os.path.join(self.config.skyrim_path, "Data", "Grass")
            if not os.path.exists(grass_dir):
                return False
            
            # Look for files with the season's extension
            season_files = []
            for root, dirs, files in os.walk(grass_dir):
                for file in files:
                    if file.endswith(season.extension):
                        season_files.append(file)
            
            if season_files:
                self.logger.debug(f"🌱 Found {len(season_files)} {season.display_name} grass cache files")
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Failed to check {season.display_name} completion status: {e}")
            return False


def main():
    """Main entry point for CLI usage"""
    # This would parse command line arguments and create config
    # For now, just a placeholder
    print("🌱 NGIO Automation Suite")
    print("This is the core automation engine.")
    print("Use run_automation.bat to start the full workflow.")


if __name__ == "__main__":
    main()
