#!/usr/bin/env python3
"""
NGIO Automation Suite - Main Controller
Orchestrates the complete grass cache generation workflow
"""

import os
import sys
import time
import logging
import shutil
import zipfile
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
from ..utils.notifications import Notifier
from ..utils.state_manager import StateManager, AutomationState


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
    max_crash_retries: int = 10  # Increased from 5 for complex worldspaces
    crash_timeout_minutes: int = 5  # Process crash detection
    no_progress_timeout_minutes: int = 15  # File inactivity detection (increased from 10)
    startup_wait_seconds: int = 30  # Wait between retry attempts
    create_archives: bool = True
    backup_configs: bool = True
    adaptive_timeouts: bool = True  # Use intelligent timeout adjustment
    enable_notifications: bool = True  # Windows toast notifications (v1.2.0+)
    enable_sounds: bool = True  # System sound alerts (v1.2.0+)
    
    # v1.5.0: NEW - NGIO Grass Generation Settings
    extend_grass_distance: bool = True  # Required for LOD compatibility
    extend_grass_count: bool = False  # WARNING: Dramatically increases generation time
    super_dense_grass: bool = False  # WARNING: Can take MANY hours
    overwrite_min_grass_size: int = 67  # Grass density (20-100, higher = less dense)
    global_grass_scale: float = 1.0  # Grass height multiplier (0.5-2.0)
    ensure_max_grass_types: int = 15  # Max grass types per texture (grass mod specific)
    only_pregenerate_worldspaces: str = ""  # Comma-separated worldspace filter (optional)
    
    # v1.6.0: LOD Grass Generation for DynDOLOD
    generate_lod_grass: bool = False  # Generate LOD grass cache (no seasonal suffix)
    lod_grass_source_season: str = ""  # Which season to use as source (empty = first season)
    
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
        
        # Initialize notifications (v1.2.0+)
        self.notifier = Notifier(
            enable_toast=config.enable_notifications,
            enable_sound=config.enable_sounds
        )
        
        # Initialize state manager (v1.3.0+)
        self.state_manager = StateManager(config.output_directory)
        
        # State tracking
        self.current_season: Optional[Season] = None
        self.completed_seasons: List[Season] = []
        self.failed_seasons: List[Season] = []
        self.start_time: Optional[float] = None
        self.season_start_time: Optional[float] = None  # Track per-season time
        self.automation_state: Optional[AutomationState] = None
        
    def run_full_automation(self) -> bool:
        """
        Run the complete automation workflow
        
        Returns:
            bool: True if successful, False if failed
        """
        self.logger.info("🌱 Starting NGIO Automation Suite")
        self.start_time = time.time()
        
        try:
            # Check for resumable state (v1.3.0+)
            interrupted_state = self.state_manager.check_for_interruption()
            if interrupted_state:
                self.logger.warning("=" * 60)
                self.logger.warning("⚠️ PREVIOUS SESSION WAS INTERRUPTED")
                self.logger.warning("=" * 60)
                print(self.state_manager.format_state_summary(interrupted_state))
                
                if self._should_resume_from_state(interrupted_state):
                    return self._resume_from_state(interrupted_state)
                else:
                    self.logger.info("Starting fresh generation...")
                    self.state_manager.clear_state()
            
            # Create new state
            self.automation_state = self.state_manager.create_state_from_config(self.config)
            self.state_manager.save_state(self.automation_state)
            
            # Phase 1: Setup and Validation
            if not self._setup_and_validate():
                self.automation_state.is_running = False
                self.state_manager.save_state(self.automation_state)
                return False
                
            # Phase 2: Backup configurations
            if not self._backup_configurations():
                return False
                
            # Phase 3: Generate grass cache for each season
            total_seasons = len(self.config.seasons_to_generate)
            
            for idx, season in enumerate(self.config.seasons_to_generate, 1):
                # v1.5.1: Show progress for multi-season
                if total_seasons > 1:
                    self.logger.separator()
                    self.logger.info(f"🌱 SEASON {idx}/{total_seasons}: {season.display_name}")
                    self.logger.separator()
                
                # Update state before starting season (v1.3.0+)
                if self.automation_state:
                    self.automation_state.current_season = season.display_name
                    self.automation_state.season_start_time = time.time()
                    self.state_manager.save_state(self.automation_state)
                
                # Generate season
                success = self._generate_season_cache(season)
                
                # Update state after season (v1.3.0+)
                if self.automation_state:
                    self._update_state_after_season(season, success)
                
                if not success:
                    self.failed_seasons.append(season)
                    self.logger.error(f"❌ Failed to generate cache for {season.display_name}")
                else:
                    self.completed_seasons.append(season)
                    
                    # v1.5.1: Multi-season progress update
                    if total_seasons > 1:
                        remaining = total_seasons - idx
                        self.logger.success(f"✅ Completed: {season.display_name} (Season {idx}/{total_seasons})")
                        if remaining > 0:
                            self.logger.info(f"📊 Progress: {idx}/{total_seasons} seasons complete, {remaining} remaining")
                    else:
                        self.logger.info(f"✅ Successfully completed {season.display_name}")
                    
            # Phase 4: Archive creation handled per-season
            # (Archives created individually after each season)
            
            # Phase 4.5: LOD Grass Cache Generation (v1.6.0)
            # Only generate LOD grass for seasonal mods (NO_SEASONS already has plain .cgid files)
            if self.config.generate_lod_grass and self.completed_seasons:
                # Check if we have seasonal seasons (not NO_SEASONS)
                has_seasonal = any(s != Season.NO_SEASONS for s in self.completed_seasons)
                if has_seasonal:
                    self._generate_lod_grass_for_dyndolod()
                else:
                    self.logger.info("ℹ️ Skipping LOD grass generation - NO_SEASONS mode already uses plain .cgid files")
            
            # Phase 5: Cleanup and restoration
            self._restore_configurations()
            
            # Phase 6: Generate final report
            self._generate_completion_report()
            
            # Clear state on successful completion (v1.3.0+)
            if self.automation_state:
                self.automation_state.is_running = False
                self.state_manager.clear_state()
                self.logger.debug("✅ State cleared - generation complete")
            
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
        self.season_start_time = time.time()
        self.logger.info(f"🌱 Starting {season.display_name} grass cache generation...")
        
        # Notify generation start
        self.notifier.notify_progress(
            f"Starting {season.display_name} grass cache generation...",
            season.display_name
        )
        
        try:
            # Step 1: Configure season settings
            if not self.config_manager.set_season(season.season_type):
                self.notifier.notify_error(f"Failed to configure {season.display_name} settings")
                return False
            
            # v1.5.0: NEW - Configure NGIO settings for generation
            if not self.config_manager.configure_ngio_for_generation(
                extend_grass_distance=self.config.extend_grass_distance,
                extend_grass_count=self.config.extend_grass_count,
                super_dense_grass=self.config.super_dense_grass,
                overwrite_min_grass_size=self.config.overwrite_min_grass_size,
                global_grass_scale=self.config.global_grass_scale,
                ensure_max_grass_types=self.config.ensure_max_grass_types,
                only_pregenerate_worldspaces=self.config.only_pregenerate_worldspaces
            ):
                self.notifier.notify_error(f"Failed to configure NGIO for {season.display_name}")
                return False
                
            # Step 2: Launch Skyrim and monitor generation
            if not self._run_generation_with_monitoring(season):
                self.notifier.notify_error(f"{season.display_name} generation failed")
                return False
                
            # Step 3: Process and rename generated files
            if not self._process_generated_files(season):
                self.notifier.notify_error(f"Failed to process {season.display_name} files")
                return False
                
            # Step 4: Create archive for this season
            if self.config.create_archives:
                if not self._create_single_season_archive(season):
                    self.notifier.notify_error(f"Failed to create {season.display_name} archive")
                    return False
                    
                # Step 5: Clean up seasonal files after successful archive creation
                if not self._cleanup_season_files(season):
                    self.logger.warning(f"⚠️ Failed to clean up {season.display_name} files, but continuing...")
            
            # Calculate duration and notify success
            duration_minutes = (time.time() - self.season_start_time) / 60
            self.notifier.notify_completion(season.display_name, duration_minutes)
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error generating {season.display_name}: {e}")
            self.notifier.notify_error(f"Unexpected error in {season.display_name} generation")
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
            
            # Display retry information
            if retry_count == 0:
                self.logger.info(f"🎮 Launching Skyrim for {season.display_name}")
            else:
                remaining = max_retries - retry_count
                self.logger.info(f"🔄 Retry {retry_count}/{max_retries} for {season.display_name}")
                self.logger.info(f"💡 {remaining} attempts remaining")
                
                # Intelligent wait time between retries (prevents death loop)
                wait_time = min(self.config.startup_wait_seconds * retry_count, 120)
                if wait_time > 0:
                    self.logger.info(f"⏳ Waiting {wait_time}s before retry (allows system to stabilize)...")
                    time.sleep(wait_time)
            
            # Launch Skyrim with grass generation enabled
            # On retry: preserves existing PrecacheGrass.txt for resume
            # On first attempt: creates fresh PrecacheGrass.txt
            launch_start_time = time.time()
            process = self.game_manager.launch_for_generation(is_retry=is_retry)
            if not process:
                return False
            
            # Track startup duration for adaptive timeouts
            launch_duration = time.time() - launch_start_time
            if self.config.adaptive_timeouts:
                recommended_timeout = self.game_manager.track_startup_duration(launch_duration)
                self.logger.debug(f"📊 Startup took {launch_duration:.1f}s, recommended timeout: {recommended_timeout:.1f}s")
            
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
                    remaining = max_retries - retry_count
                    self.logger.info(f"🔄 Will retry generation ({remaining} attempts remaining)")
                    # Wait time is handled at the top of the loop
                else:
                    self.logger.error(f"❌ Max retries ({max_retries}) exceeded for {season.display_name}")
                    self.logger.error(f"💡 Possible solutions:")
                    self.logger.error(f"   • Increase max_crash_retries in config (currently {max_retries})")
                    self.logger.error(f"   • Check Skyrim stability (try generating manually)")
                    self.logger.error(f"   • This worldspace may be particularly crash-prone")
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
        
        # v1.5.0: NEW - Configure NGIO to use cache (set OnlyLoadFromCache=True)
        self.logger.info("⚙️ Configuring NGIO for cache usage...")
        if not self.config_manager.configure_ngio_for_cache_use():
            self.logger.warning("⚠️ Failed to configure NGIO for cache usage")
        
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
                
                # Send final completion notification
                self.notifier.notify_completion(season_name, total_time / 60)
        else:
            season_name = self.failed_seasons[0].display_name
            self.logger.warning(f"⚠️  {season_name} generation failed. Check logs for details.")
            
            # Send failure notification
            self.notifier.notify_error(f"{season_name} generation failed after {total_time/60:.1f} minutes")
    
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
    
    def _should_resume_from_state(self, state: AutomationState) -> bool:
        """
        Ask user if they want to resume from interrupted state (v1.3.0+)
        
        Args:
            state: The interrupted automation state
            
        Returns:
            True if should resume, False to start fresh
        """
        remaining = self.state_manager.get_resumable_seasons(state)
        
        if not remaining:
            self.logger.info("No remaining seasons to generate - starting fresh")
            return False
        
        self.logger.info(f"\nRemaining seasons: {', '.join(remaining)}")
        response = input("\n🔄 Resume from where it left off? (y/n): ").strip().lower()
        
        return response in ['y', 'yes']
    
    def _resume_from_state(self, state: AutomationState) -> bool:
        """
        Resume automation from saved state (v1.3.0+)
        
        Args:
            state: The state to resume from
            
        Returns:
            True if successful
        """
        self.logger.info("🔄 Resuming from saved state...")
        
        # Restore completed/failed seasons
        for season_name in state.completed_seasons:
            season = self._get_season_by_name(season_name)
            if season:
                self.completed_seasons.append(season)
        
        for season_name in state.failed_seasons:
            season = self._get_season_by_name(season_name)
            if season:
                self.failed_seasons.append(season)
        
        # Get remaining seasons
        remaining_names = self.state_manager.get_resumable_seasons(state)
        remaining_seasons = [self._get_season_by_name(name) for name in remaining_names if self._get_season_by_name(name)]
        
        # Update config with remaining seasons
        self.config.seasons_to_generate = remaining_seasons
        
        # Update state and continue
        self.automation_state = state
        self.automation_state.is_running = True
        self.automation_state.interrupted = False
        self.state_manager.save_state(self.automation_state)
        
        # Run automation with remaining seasons
        return self.run_full_automation()
    
    def _get_season_by_name(self, season_name: str) -> Optional[Season]:
        """
        Get Season enum by display name
        
        Args:
            season_name: Display name like "Winter", "Spring"
            
        Returns:
            Season enum or None
        """
        for season in Season:
            if season.display_name == season_name:
                return season
        return None
    
    def _update_state_after_season(self, season: Season, success: bool):
        """
        Update state after completing/failing a season (v1.3.0+)
        
        Args:
            season: The season that was processed
            success: Whether it succeeded or failed
        """
        if not self.automation_state:
            return
        
        if success:
            if season.display_name not in self.automation_state.completed_seasons:
                self.automation_state.completed_seasons.append(season.display_name)
        else:
            if season.display_name not in self.automation_state.failed_seasons:
                self.automation_state.failed_seasons.append(season.display_name)
        
        self.automation_state.current_season = None
        self.state_manager.save_state(self.automation_state)
    
    def _generate_lod_grass_cache(self, source_season: Season) -> bool:
        """
        Generate LOD grass cache from a completed seasonal grass cache.
        
        This creates grass files without seasonal postfixes, required for
        DynDOLOD grass LOD generation.
        
        Args:
            source_season: The season to use as source for LOD grass
            
        Returns:
            bool: True if successful, False if failed
        """
        self.logger.separator("LOD Grass Cache Generation")
        self.logger.info(f"🏔️ Creating LOD grass cache from {source_season.display_name}...")
        self.logger.info("   This is required for DynDOLOD grass LOD generation")
        
        try:
            # Source: seasonal grass files in Data/Grass
            grass_directory = os.path.join(self.config.skyrim_path, "Data", "Grass")
            
            if not os.path.exists(grass_directory):
                self.logger.error("❌ Grass directory not found")
                return False
            
            # Target: temporary LOD grass directory
            lod_grass_directory = os.path.join(self.config.output_directory, "_LOD_Grass_Temp")
            
            # Use file processor to create LOD grass files (strip seasonal extension)
            result = self.file_processor.create_lod_grass_files(
                source_directory=grass_directory,
                target_directory=lod_grass_directory,
                season_extension=source_season.extension
            )
            
            if not result.success:
                self.logger.error(f"❌ Failed to create LOD grass files: {result.errors}")
                return False
            
            self.logger.info(f"✅ Created {result.processed_files} LOD grass files")
            
            # Create LOD grass archive
            self.logger.info("📦 Creating LOD grass archive...")
            archive_info = self.archive_creator.create_lod_grass_archive(
                lod_grass_directory=lod_grass_directory,
                source_season_name=source_season.display_name
            )
            
            if not archive_info:
                self.logger.error("❌ Failed to create LOD grass archive")
                return False
            
            self.logger.success(f"✅ LOD grass archive created: {archive_info.archive_path}")
            self.logger.info(f"📊 Archive size: {archive_info.archive_size_mb:.1f} MB")
            self.logger.info(f"📁 Files included: {archive_info.file_count}")
            
            # Clean up temporary LOD grass directory
            try:
                shutil.rmtree(lod_grass_directory)
                self.logger.debug("🧹 Cleaned up temporary LOD grass files")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to clean up temp directory: {e}")
            
            # Notify user about LOD grass
            self.notifier.notify_progress(
                "LOD grass cache created for DynDOLOD!",
                "LOD Grass"
            )
            
            self.logger.separator()
            self.logger.info("📝 LOD GRASS USAGE INSTRUCTIONS:")
            self.logger.info("   1. Keep 'Grass Cache - Default' DISABLED normally")
            self.logger.info("   2. Enable it ONLY when generating LOD with DynDOLOD")
            self.logger.info("   3. Disable seasonal grass caches during DynDOLOD")
            self.logger.info("   4. After DynDOLOD completes, disable LOD grass")
            self.logger.info("   5. Re-enable your seasonal grass caches")
            self.logger.separator()
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error generating LOD grass cache: {e}")
            return False
    
    def _generate_lod_grass_for_dyndolod(self) -> bool:
        """
        Generate LOD grass cache for DynDOLOD using the specified source season.
        
        v1.6.0: This is called after all seasons are generated to create
        the "Grass Cache - Default" archive for DynDOLOD LOD generation.
        
        Returns:
            bool: True if successful, False if failed
        """
        # Safety check: ensure we have completed seasons
        if not self.completed_seasons:
            self.logger.error("❌ No completed seasons available for LOD grass generation")
            return False
        
        # Determine source season
        source_season = None
        
        # Check if user specified a source season
        if self.config.lod_grass_source_season:
            # Find the season by name
            for season in self.completed_seasons:
                if season.display_name == self.config.lod_grass_source_season:
                    source_season = season
                    break
            
            if not source_season:
                self.logger.warning(f"⚠️ Specified LOD source season '{self.config.lod_grass_source_season}' was not completed")
                self.logger.info(f"   Using first completed season instead")
        
        # Default to first completed season
        if not source_season:
            source_season = self.completed_seasons[0]
        
        self.logger.info(f"🏔️ Using {source_season.display_name} as source for LOD grass cache")
        
        # We need to check if seasonal files still exist for the source season
        # They should still be in the archive, but we need the files on disk
        # The files may have been cleaned up after archive creation
        
        # Check if seasonal files exist in Data/Grass
        grass_directory = os.path.join(self.config.skyrim_path, "Data", "Grass")
        seasonal_files_exist = False
        
        if os.path.exists(grass_directory):
            for root, dirs, files in os.walk(grass_directory):
                for file in files:
                    if file.endswith(source_season.extension):
                        seasonal_files_exist = True
                        break
                if seasonal_files_exist:
                    break
        
        if not seasonal_files_exist:
            # Need to extract files from the archive
            self.logger.info(f"📂 Seasonal files not found in Data/Grass")
            self.logger.info(f"📦 Extracting from {source_season.display_name} archive...")
            
            archive_path = os.path.join(
                self.config.output_directory, 
                f"Grass_Cache_{source_season.display_name}_Season.zip"
            )
            
            if not os.path.exists(archive_path):
                self.logger.error(f"❌ Archive not found: {archive_path}")
                self.logger.error("   Cannot create LOD grass without source files")
                return False
            
            # Extract archive to temporary location
            temp_extract_dir = os.path.join(self.config.output_directory, "_LOD_Extract_Temp")
            
            try:
                os.makedirs(temp_extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(temp_extract_dir)
                
                # Find the Grass directory in extracted content
                extracted_grass_dir = None
                for root, dirs, files in os.walk(temp_extract_dir):
                    if os.path.basename(root) == "Grass" and files:
                        extracted_grass_dir = root
                        break
                
                if not extracted_grass_dir:
                    self.logger.error("❌ Could not find Grass directory in archive")
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                    return False
                
                # Generate LOD grass from extracted files
                success = self._generate_lod_grass_cache_from_dir(source_season, extracted_grass_dir)
                
                # Clean up extracted files
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                
                return success
                
            except Exception as e:
                self.logger.error(f"💥 Error extracting archive: {e}")
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                return False
        else:
            # Generate directly from existing files
            return self._generate_lod_grass_cache(source_season)
    
    def _generate_lod_grass_cache_from_dir(self, source_season: Season, source_dir: str) -> bool:
        """
        Generate LOD grass cache from a specific directory.
        
        Args:
            source_season: The season the files came from
            source_dir: Directory containing the seasonal grass files
            
        Returns:
            bool: True if successful
        """
        self.logger.separator("LOD Grass Cache Generation")
        self.logger.info(f"🏔️ Creating LOD grass cache from {source_season.display_name}...")
        
        try:
            # Target: temporary LOD grass directory
            lod_grass_directory = os.path.join(self.config.output_directory, "_LOD_Grass_Temp")
            
            # Use file processor to create LOD grass files
            result = self.file_processor.create_lod_grass_files(
                source_directory=source_dir,
                target_directory=lod_grass_directory,
                season_extension=source_season.extension
            )
            
            if not result.success:
                self.logger.error(f"❌ Failed to create LOD grass files")
                return False
            
            self.logger.info(f"✅ Created {result.processed_files} LOD grass files")
            
            # Create LOD grass archive
            archive_info = self.archive_creator.create_lod_grass_archive(
                lod_grass_directory=lod_grass_directory,
                source_season_name=source_season.display_name
            )
            
            if not archive_info:
                self.logger.error("❌ Failed to create LOD grass archive")
                return False
            
            self.logger.success(f"✅ LOD grass archive created!")
            self.logger.info(f"📊 Archive size: {archive_info.archive_size_mb:.1f} MB")
            
            # Clean up
            shutil.rmtree(lod_grass_directory, ignore_errors=True)
            
            # Show instructions
            self.logger.separator()
            self.logger.info("📝 LOD GRASS USAGE INSTRUCTIONS:")
            self.logger.info("   1. Keep 'Grass Cache - Default' DISABLED normally")
            self.logger.info("   2. Enable ONLY when generating LOD with DynDOLOD")
            self.logger.info("   3. After DynDOLOD, disable and re-enable seasonal caches")
            self.logger.separator()
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error generating LOD grass: {e}")
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
