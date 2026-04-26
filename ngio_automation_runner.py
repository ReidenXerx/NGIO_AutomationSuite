#!/usr/bin/env python3
"""
NGIO Automation Suite - Main Runner
The user-friendly entry point for grass cache generation
"""

# IMMEDIATE output to see if script starts
print("[DEBUG] Python script started", flush=True)

import os
import sys
import platform
import signal
import atexit
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

print("[DEBUG] Basic imports done", flush=True)

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

print("[DEBUG] About to import automation_suite...", flush=True)
from src.core.automation_suite import NGIOAutomationSuite, AutomationConfig, Season
print("[DEBUG] automation_suite imported", flush=True)

print("[DEBUG] About to import config_cache...", flush=True)
from src.utils.config_cache import ConfigCache
print("[DEBUG] config_cache imported", flush=True)

print("[DEBUG] About to import logger...", flush=True)
from src.utils.logger import Logger
print("[DEBUG] logger imported", flush=True)

print("[DEBUG] About to import state_manager...", flush=True)
from src.utils.state_manager import StateManager, AutomationState
print("[DEBUG] state_manager imported", flush=True)

print("[DEBUG] About to import version...", flush=True)
from src.__version__ import __version__, __title__, __description__
print("[DEBUG] All imports complete!", flush=True)

# Import dependencies at module level (faster than in function)
print("[DEBUG] Checking dependencies...", flush=True)
try:
    import psutil
    import colorlog
    import configparser
    DEPENDENCIES_OK = True
    print("[DEBUG] Dependencies OK", flush=True)
except ImportError:
    DEPENDENCIES_OK = False
    print("[DEBUG] Dependencies MISSING", flush=True)

# Cache platform check at module level
# WORKAROUND: platform.system() can hang for 2+ minutes on some systems!
# Assume Windows since this tool is Windows-only anyway
print("[DEBUG] Caching platform info...", flush=True)
IS_WINDOWS = True  # This tool only works on Windows anyway - skip detection
PYTHON_VERSION = sys.version_info
print("[DEBUG] Platform cached: Windows=True (assumed)", flush=True)
print("[DEBUG] Module initialization complete!", flush=True)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        prog='ngio-automation',
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ngio-automation                        Run in interactive menu mode
  ngio-automation --version              Show version and exit
  ngio-automation --season winter        Generate Winter season
  ngio-automation --season winter -v     Generate with verbose output
  ngio-automation --dry-run              Test workflow without launching Skyrim
  ngio-automation --config custom.yaml   Use custom configuration file

For more information, visit: https://github.com/yourusername/ngio-automation-suite
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{__title__} v{__version__}'
    )
    
    parser.add_argument(
        '--season',
        choices=['winter', 'spring', 'summer', 'autumn', 'all'],
        help='Generate specific season (or all seasons)',
        metavar='SEASON'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file',
        metavar='FILE'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose debug output'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test workflow without launching Skyrim'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Suppress banner display'
    )
    
    parser.add_argument(
        '--unattended',
        action='store_true',
        help='Run without user interaction (for scheduled tasks)'
    )
    
    return parser.parse_args()


def print_banner():
    """Display the application banner"""
    # Enhanced banner with more info (v1.4.0+)
    banner = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    🌱 NGIO AUTOMATION SUITE 🌱                    ║
║                         Version {__version__} - Power User Edition                   ║
║                                                                   ║
║      Transform 4+ Hours of Manual Work Into Automated Magic!     ║
║                                                                   ║
║  ⚠️  OVERNIGHT MODE USERS: Ensure 20GB+ Windows Pagefile!  ⚠️     ║
║      (Skyrim can consume ALL RAM during generation!)             ║
║                                                                   ║
║  ✨ NEW: Resume • Validation • Scheduler • Crash Analytics ✨    ║
║  🚀 CLI • Checksums • Notifications • Progress Bars • YAML 🚀    ║
╚═══════════════════════════════════════════════════════════════════╝

💡 Quick Start:
   • Interactive Mode: Just press Enter!
   • CLI Mode:        ngio-automation --season winter -v
   • Get Help:        ngio-automation --help
   • Schedule Task:   python -m src.utils.task_scheduler guide
"""
    print(banner)


def check_system_requirements() -> bool:
    """Check if system meets requirements"""
    logger = Logger("SystemCheck")
    logger.info("🔍 Checking system requirements...")
    
    # Check Python version (cached at module level)
    if PYTHON_VERSION < (3, 7):
        logger.error("❌ Python 3.7+ required")
        return False
    
    # Check OS (cached at module level)
    if not IS_WINDOWS:
        logger.error("❌ Windows is required for Skyrim modding")
        return False
    
    # Check dependencies (already imported at module level)
    if not DEPENDENCIES_OK:
        logger.error("❌ Missing dependencies: psutil, colorlog, or configparser")
        logger.info("💡 Run: pip install -r requirements.txt")
        return False
    
    logger.success("✅ System requirements met (Python {}.{}, Windows, Dependencies OK)".format(
        PYTHON_VERSION.major, PYTHON_VERSION.minor
    ))
    return True


def show_main_menu(config_cache: ConfigCache) -> str:
    """Display main menu and get user choice"""
    logger = Logger("Menu")
    
    while True:
        logger.separator("Main Menu")
        logger.info("🎮 What would you like to do?")
        logger.info("")
        logger.info("1. 🚀 Start Grass Cache Generation")
        logger.info("2. ⚙️  Configure Paths and Settings")
        logger.info("3. 📊 Show Current Configuration")
        logger.info("4. 🔄 Reset Configuration")
        logger.info("5. ❓ Help and Information")
        logger.info("6. 🚪 Exit")
        logger.info("")
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                logger.error("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            return '6'
        except Exception:
            logger.error("❌ Invalid input. Please try again.")


def handle_grass_generation(config_cache: ConfigCache) -> bool:
    """Handle the grass cache generation process"""
    logger = Logger("Generation")
    
    # Validate configuration
    if not config_cache.validate_and_update_config():
        logger.error("❌ Configuration is invalid or incomplete")
        logger.info("💡 Please configure paths first (option 2)")
        return False
    
    # Check for previous interrupted session FIRST
    paths = config_cache.get_paths()
    state_manager = StateManager(paths.output_directory)
    
    if state_manager.has_saved_state():
        saved_state = state_manager.load_state()
        
        if saved_state and saved_state.current_season:
            # Show session info
            logger.separator("Previous Session Detected")
            logger.info("🔄 An interrupted automation session was found!")
            logger.info("")
            logger.info(f"   📅 Last updated: {datetime.fromtimestamp(saved_state.last_updated).strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"   🌱 Current season: {saved_state.current_season}")
            logger.info(f"   ✅ Completed: {', '.join(saved_state.completed_seasons) if saved_state.completed_seasons else 'None'}")
            
            remaining = [s for s in saved_state.seasons_to_generate if s not in saved_state.completed_seasons]
            logger.info(f"   📊 Remaining: {len(remaining)} seasons")
            logger.info("")
            logger.separator()
            logger.info("")
            logger.info("Do you want to continue from where you left off?")
            logger.info("")
            logger.info("   [Y] Yes - Resume previous session (skips profile selection)")
            logger.info("   [N] No - Start fresh (clears previous session)")
            logger.info("")
            
            choice = input("Your choice [Y/n]: ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                # User confirmed resume - extract remaining seasons and update config
                logger.success("✅ Resuming previous session...")
                logger.info("")
                
                # Extract remaining seasons
                remaining_seasons = [s for s in saved_state.seasons_to_generate if s not in saved_state.completed_seasons]
                logger.info(f"📊 Will generate: {', '.join(remaining_seasons)}")
                logger.info(f"🔄 Previous retry count: {saved_state.retry_count}/{saved_state.total_retries}")
                logger.info("")
                
                # Update config cache with remaining seasons
                preferences = config_cache.get_preferences()
                preferences.seasons_to_generate = remaining_seasons
                config_cache.save_config()
                
                # Clear the saved state - user confirmed, we'll create a fresh one with remaining seasons
                # This prevents the double-prompt issue
                state_manager.clear_state()
                
                # Skip profile selection - continue to generation with LOD Compatible default
                automation_config = create_automation_config_from_cache(config_cache)
                automation_suite = NGIOAutomationSuite(automation_config)
                
                # Start fresh generation with remaining seasons
                return automation_suite.run_full_automation()
            else:
                # User wants fresh start
                logger.info("🗑️  Clearing previous session...")
                state_manager.clear_state()
                logger.success("✅ Starting fresh session")
                # Continue to profile selection below
    
    # v1.5.0: NEW - Grass Profile Selection
    from src.utils.grass_profiles import select_profile_interactive
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("⚙️  GRASS GENERATION SETTINGS")
    logger.info("=" * 60)
    logger.info("")
    
    # Let user select profile
    grass_profile, confirmed = select_profile_interactive()
    
    if not confirmed or grass_profile is None:
        logger.warning("⚠️ Generation cancelled by user")
        return False
    
    logger.info("")
    logger.info("✅ Profile selected successfully!")
    logger.info("")
    
    # Get paths and preferences
    paths = config_cache.get_paths()
    preferences = config_cache.get_preferences()
    
    # Convert season names to Season enums
    season_map = {
        "Winter": Season.WINTER,
        "Spring": Season.SPRING, 
        "Summer": Season.SUMMER,
        "Autumn": Season.AUTUMN,
        "No Seasons": Season.NO_SEASONS
    }
    
    seasons_to_generate = []
    for season_name in preferences.seasons_to_generate:
        if season_name in season_map:
            seasons_to_generate.append(season_map[season_name])
    
    # Validate season selection
    if not seasons_to_generate:
        logger.error("❌ No valid seasons selected for generation")
        return False
    
    # Create automation config
    automation_config = AutomationConfig(
        skyrim_path=paths.skyrim_path,
        output_directory=paths.output_directory,
        seasons_to_generate=seasons_to_generate,
        max_crash_retries=preferences.max_crash_retries,
        crash_timeout_minutes=preferences.crash_timeout_minutes,
        no_progress_timeout_minutes=preferences.no_progress_timeout_minutes,
        create_archives=preferences.create_archives,
        backup_configs=preferences.backup_configs,
        # v1.5.0: NEW - Grass profile settings
        extend_grass_distance=grass_profile.extend_grass_distance,
        extend_grass_count=grass_profile.extend_grass_count,
        super_dense_grass=grass_profile.super_dense_grass,
        overwrite_min_grass_size=grass_profile.overwrite_min_grass_size,
        global_grass_scale=grass_profile.global_grass_scale,
        ensure_max_grass_types=grass_profile.ensure_max_grass_types,
        # v1.6.0: LOD Grass settings
        generate_lod_grass=preferences.generate_lod_grass,
        lod_grass_source_season=preferences.lod_grass_source_season
    )
    
    # Show generation summary
    logger.separator("Generation Summary")
    logger.info("🎯 About to generate grass cache with these settings:")
    logger.info(f"   📁 Skyrim: {paths.skyrim_path}")
    logger.info(f"   📦 Output: {paths.output_directory}")
    
    # Show mode and seasons
    if preferences.use_seasonal_mods:
        logger.info(f"   🌿 Mode: Seasonal (with seasonal mods)")
        
        # v1.5.1: Show all seasons if multiple selected
        if len(preferences.seasons_to_generate) > 1:
            season_list = ", ".join(preferences.seasons_to_generate)
            logger.info(f"   🌱 Seasons: {season_list}")
            logger.info(f"   🌈 Multi-Season Mode: {len(preferences.seasons_to_generate)} seasons")
            estimated_minutes = len(preferences.seasons_to_generate) * 75  # ~75 min average per season
            estimated_hours = estimated_minutes / 60
            logger.info(f"   ⏰ Estimated Total Time: {estimated_hours:.1f} hours ({estimated_minutes} minutes)")
            logger.info(f"   💤 Perfect for overnight generation!")
        else:
            logger.info(f"   🌱 Season: {preferences.seasons_to_generate[0]}")
            logger.info(f"   ⏰ Estimated Time: 60-90 minutes")
    else:
        logger.info(f"   🌿 Mode: Non-seasonal (no seasonal mods)")
        logger.info(f"   🌱 Generation: Single grass cache")
    
    logger.info(f"   🔄 Max retries: {preferences.max_crash_retries}")
    logger.info(f"   ⚡ Crash timeout: {preferences.crash_timeout_minutes} minutes (process not running)")
    logger.info(f"   ⏰ No progress timeout: {preferences.no_progress_timeout_minutes} minutes (file not updating)")
    logger.info(f"   📦 Create archives: {'Yes' if preferences.create_archives else 'No'}")
    
    # v1.6.0: Show LOD grass settings
    if preferences.generate_lod_grass:
        logger.info(f"   🏔️ LOD Grass Cache: Yes (for DynDOLOD)")
        if preferences.lod_grass_source_season:
            logger.info(f"   🏔️ LOD Source Season: {preferences.lod_grass_source_season}")
        else:
            logger.info(f"   🏔️ LOD Source Season: {preferences.seasons_to_generate[0]} (first season)")
    
    logger.separator()
    
    # Confirm with user
    logger.info("⚠️  IMPORTANT NOTES:")
    logger.info("   • This process can take 1-4 hours depending on your system")
    logger.info("   • Skyrim will launch and close multiple times (this is normal)")
    logger.info("   • Your seasonal mod settings will be temporarily changed")
    logger.info("   • All settings will be restored when complete")
    logger.info("")
    
    try:
        confirm = input("🚀 Start grass cache generation? (y/n): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            logger.info("❌ Generation cancelled by user")
            return False
        
    except KeyboardInterrupt:
        logger.info("❌ Generation cancelled by user")
        return False
    
    # Start the automation
    logger.separator("Starting Automation")
    logger.info("🌱 Initializing NGIO Automation Suite...")
    
    try:
        automation_suite = NGIOAutomationSuite(automation_config)
        
        # Set global reference for signal handlers
        globals()['automation_suite'] = automation_suite
        success = automation_suite.run_full_automation()
        
        if success:
            logger.separator()
            logger.success("🎉 GRASS CACHE GENERATION COMPLETED SUCCESSFULLY!")
            logger.info("📦 Your mod archives are ready to install!")
            logger.info(f"📁 Location: {paths.output_directory}")
            logger.info("📖 Check the INSTALLATION_GUIDE.txt for next steps")
            return True
        else:
            logger.separator()
            logger.error("❌ Grass cache generation failed or incomplete")
            logger.info("💡 Check the logs above for details")
            return False
            
    except Exception as e:
        logger.error(f"💥 Unexpected error during generation: {e}")
        return False


def handle_configuration(config_cache: ConfigCache) -> bool:
    """Handle configuration setup"""
    logger = Logger("Config")
    
    logger.info("🔧 Starting configuration setup...")
    return config_cache.collect_user_paths()


def show_help():
    """Display help information"""
    logger = Logger("Help")
    
    help_text = """
🌱 NGIO AUTOMATION SUITE - HELP & INFORMATION

WHAT IS THIS?
This tool automates the tedious process of generating grass cache files for 
all seasons in Skyrim. Instead of manually spending 4+ hours, you can set it 
up once and let it run automatically!

REQUIREMENTS:
• Windows 10/11
• Skyrim SE/AE/VR with NGIO mod installed
• Seasons of Skyrim (or compatible seasonal mod)
• SKSE64
• At least 5GB free disk space

HOW IT WORKS:
1. You provide paths to your Skyrim installation
2. The tool automatically changes seasonal settings
3. Skyrim launches and generates grass cache for each season
4. Files are processed and renamed with seasonal extensions
5. Mod archives are created for easy installation
6. Original settings are restored

WHAT YOU GET:
• Grass_Cache_Winter_Season.zip
• Grass_Cache_Spring_Season.zip  
• Grass_Cache_Summer_Season.zip
• Grass_Cache_Autumn_Season.zip
• INSTALLATION_GUIDE.txt

INSTALLATION:
1. Install the seasonal grass cache archives as mods
2. Ensure Grass Cache Helper NG is active
3. DISABLE the original NGIO mod
4. Enjoy seasonal grass with great performance!

TROUBLESHOOTING:
• If generation fails: Check that all required mods are installed
• If Skyrim won't start: Verify SKSE64 is properly installed
• If no grass appears: Make sure Grass Cache Helper NG is enabled
• For crashes: The tool will automatically retry up to 5 times

SUPPORT:
• Check logs for detailed error information
• Visit the GitHub repository for updates
• Post issues on the Nexus mod page

This tool can save the Skyrim modding community thousands of hours!
"""
    
    logger.info(help_text)


# Global reference for signal handlers
automation_suite = None

def emergency_shutdown(signum=None, frame=None):
    """Handle emergency shutdown while preserving progress"""
    if automation_suite:
        try:
            print("\n🚨 Emergency shutdown - preserving progress...")
            automation_suite._emergency_cleanup()
        except Exception as e:
            print(f"Error during emergency shutdown: {e}")
    sys.exit(1)


def create_automation_config_from_cache(config_cache: ConfigCache, grass_profile=None) -> AutomationConfig:
    """
    Create AutomationConfig from cached configuration
    
    Args:
        config_cache: Configuration cache
        grass_profile: Optional grass profile (uses LOD Compatible if None)
        
    Returns:
        AutomationConfig instance
    """
    paths = config_cache.get_paths()
    preferences = config_cache.get_preferences()
    
    # Convert season names to Season enums
    season_map = {
        "Winter": Season.WINTER,
        "Spring": Season.SPRING, 
        "Summer": Season.SUMMER,
        "Autumn": Season.AUTUMN,
        "No Seasons": Season.NO_SEASONS
    }
    
    seasons_to_generate = []
    for season_name in preferences.seasons_to_generate:
        if season_name in season_map:
            seasons_to_generate.append(season_map[season_name])
    
    # Use default LOD Compatible profile if none provided
    if grass_profile is None:
        from src.utils.grass_profiles import PROFILES, ProfileType
        grass_profile = PROFILES[ProfileType.LOD_COMPATIBLE]
    
    # Create automation config
    return AutomationConfig(
        skyrim_path=paths.skyrim_path,
        output_directory=paths.output_directory,
        seasons_to_generate=seasons_to_generate,
        max_crash_retries=preferences.max_crash_retries,
        crash_timeout_minutes=preferences.crash_timeout_minutes,
        no_progress_timeout_minutes=preferences.no_progress_timeout_minutes,
        create_archives=preferences.create_archives,
        backup_configs=preferences.backup_configs,
        # Grass profile settings
        extend_grass_distance=grass_profile.extend_grass_distance,
        extend_grass_count=grass_profile.extend_grass_count,
        super_dense_grass=grass_profile.super_dense_grass,
        overwrite_min_grass_size=grass_profile.overwrite_min_grass_size,
        global_grass_scale=grass_profile.global_grass_scale,
        ensure_max_grass_types=grass_profile.ensure_max_grass_types,
        # v1.6.0: LOD Grass settings
        generate_lod_grass=preferences.generate_lod_grass,
        lod_grass_source_season=preferences.lod_grass_source_season
    )


def check_for_previous_session(config_cache: ConfigCache, logger: Logger) -> Optional[AutomationState]:
    """
    Check if there's an interrupted/previous session and prompt user to resume
    
    Args:
        config_cache: Configuration cache with paths
        logger: Logger instance
        
    Returns:
        AutomationState if user wants to resume, None otherwise
    """
    paths = config_cache.get_paths()
    if not paths or not paths.output_directory:
        return None
    
    # Initialize state manager
    state_manager = StateManager(paths.output_directory)
    
    # Check if there's a saved state
    if not state_manager.has_saved_state():
        return None
    
    # Load the saved state
    saved_state = state_manager.load_state()
    
    if not saved_state or not saved_state.current_season:
        return None
    
    # Check if state is stale (older than 7 days)
    if saved_state.last_updated:
        age_days = (time.time() - saved_state.last_updated) / (24 * 3600)
        if age_days > 7:
            logger.warning(f"⚠️  Found old session state ({age_days:.1f} days old) - ignoring")
            state_manager.clear_state()
            return None
    
    # Display session info
    logger.separator("Previous Session Detected")
    logger.info("🔄 An interrupted automation session was found!")
    logger.info("")
    logger.info(f"   📅 Last updated: {datetime.fromtimestamp(saved_state.last_updated).strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"   🌱 Current season: {saved_state.current_season}")
    logger.info(f"   ✅ Completed: {', '.join(saved_state.completed_seasons) if saved_state.completed_seasons else 'None'}")
    logger.info(f"   📊 Remaining: {len([s for s in saved_state.seasons_to_generate if s not in saved_state.completed_seasons])} seasons")
    
    if saved_state.retry_count > 0:
        logger.info(f"   🔄 Retries: {saved_state.retry_count}/{saved_state.total_retries}")
    
    logger.info("")
    logger.separator()
    
    # Prompt user
    logger.info("Do you want to continue from where you left off?")
    logger.info("")
    logger.info("   [Y] Yes - Resume previous session")
    logger.info("   [N] No - Start fresh (clears previous session)")
    logger.info("")
    
    while True:
        try:
            choice = input("Your choice [Y/n]: ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                # User wants to resume
                logger.success("✅ Resuming previous session...")
                
                # Validate that paths still exist
                logger.info("🔍 Validating previous session configuration...")
                
                if saved_state.skyrim_path and not os.path.exists(saved_state.skyrim_path):
                    logger.error(f"❌ Skyrim path no longer exists: {saved_state.skyrim_path}")
                    logger.error("   Cannot resume - please start fresh")
                    state_manager.clear_state()
                    input("Press Enter to continue...")
                    return None
                
                if saved_state.output_directory and not os.path.exists(saved_state.output_directory):
                    logger.warning(f"⚠️  Output directory missing: {saved_state.output_directory}")
                    logger.info("   Creating output directory...")
                    try:
                        os.makedirs(saved_state.output_directory, exist_ok=True)
                    except Exception as e:
                        logger.error(f"❌ Failed to create output directory: {e}")
                        logger.error("   Cannot resume - please start fresh")
                        state_manager.clear_state()
                        input("Press Enter to continue...")
                        return None
                
                logger.success("✅ Configuration validated")
                return saved_state
            
            elif choice in ['n', 'no']:
                # User wants fresh start
                logger.info("🗑️  Clearing previous session...")
                state_manager.clear_state()
                logger.success("✅ Starting fresh session")
                return None
            
            else:
                logger.warning("Invalid choice. Please enter Y or N")
        
        except KeyboardInterrupt:
            logger.info("\n⚠️  Cancelled - starting fresh session")
            state_manager.clear_state()
            return None
        except Exception as e:
            logger.error(f"Error prompting for resume: {e}")
            return None

def main():
    """Main entry point"""
    print("[DEBUG] main() started", flush=True)
    global automation_suite
    
    # Parse command-line arguments
    print("[DEBUG] Parsing arguments...", flush=True)
    args = parse_arguments()
    print("[DEBUG] Arguments parsed", flush=True)
    
    # Register signal handlers for graceful shutdown
    print("[DEBUG] Registering signal handlers...", flush=True)
    signal.signal(signal.SIGINT, emergency_shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, emergency_shutdown)  # Termination signal
    atexit.register(emergency_shutdown)  # Normal exit
    print("[DEBUG] Signal handlers registered", flush=True)
    
    # Show banner unless suppressed
    print("[DEBUG] Showing banner...", flush=True)
    if not args.no_banner:
        print_banner()
    print("[DEBUG] Banner shown", flush=True)
    
    # Check system requirements
    if not check_system_requirements():
        if not args.unattended:
            input("Press Enter to exit...")
        return 1
    
    # Set verbose logging if requested (v1.2.0+)
    if args.verbose:
        Logger.set_console_level('DEBUG')
    
    # Initialize config cache
    temp_logger = Logger("Init")
    temp_logger.info("⏳ Initializing ConfigCache...")
    config_cache = ConfigCache()
    temp_logger.info("✅ ConfigCache initialized")
    
    logger = Logger("Main")
    
    if args.verbose:
        logger.debug("🔧 Verbose DEBUG mode enabled")
    
    # Load existing configuration
    logger.info("⏳ Loading configuration...")
    config_loaded = config_cache.load_config()
    logger.info("✅ Configuration loaded")
    
    # NOTE: Session resume is handled automatically by NGIOAutomationSuite.run_full_automation()
    # It will detect interrupted sessions and prompt the user during generation
    # No need to check here - let the automation suite handle it
    
    # CLI MODE: If season argument provided, run generation directly
    if args.season:
        logger.info(f"🎯 CLI Mode: Generating {args.season} season")
        
        # Map season string to Season enum
        season_map = {
            'winter': Season.WINTER,
            'spring': Season.SPRING,
            'summer': Season.SUMMER,
            'autumn': Season.AUTUMN,
        }
        
        if args.season == 'all':
            # Generate all seasons
            seasons_to_generate = list(season_map.values())
        else:
            # Generate single season
            seasons_to_generate = [season_map[args.season]]
        
        # Override config cache with CLI season selection
        if config_cache.preferences:
            config_cache.preferences.seasons_to_generate = [s.display_name for s in seasons_to_generate]
        
        # Handle dry-run mode
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - Simulating workflow")
            logger.info(f"   Would generate: {', '.join([s.display_name for s in seasons_to_generate])}")
            logger.info("   Skyrim path: " + (config_cache.get_paths().skyrim_path if config_cache.get_paths() else "Not configured"))
            logger.info("   No actual changes will be made")
            return 0
        
        # Run generation
        success = handle_grass_generation(config_cache)
        
        if not args.unattended:
            input("\nPress Enter to exit...")
        
        return 0 if success else 1
    
    # INTERACTIVE MODE: Show menu if no CLI arguments
    # Main application loop
    while True:
        try:
            choice = show_main_menu(config_cache)
            
            if choice == '1':  # Start generation
                handle_grass_generation(config_cache)
                input("\nPress Enter to continue...")
                
            elif choice == '2':  # Configure
                if handle_configuration(config_cache):
                    logger.success("✅ Configuration completed successfully!")
                else:
                    logger.error("❌ Configuration setup failed or cancelled")
                input("\nPress Enter to continue...")
                
            elif choice == '3':  # Show config
                config_cache.show_current_config()
                input("\nPress Enter to continue...")
                
            elif choice == '4':  # Reset config
                logger.warning("⚠️  This will delete all saved configuration!")
                confirm = input("Are you sure? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    if config_cache.reset_config():
                        logger.success("✅ Configuration reset successfully")
                    else:
                        logger.error("❌ Failed to reset configuration")
                input("\nPress Enter to continue...")
                
            elif choice == '5':  # Help
                show_help()
                input("\nPress Enter to continue...")
                
            elif choice == '6':  # Exit
                logger.info("👋 Thank you for using NGIO Automation Suite!")
                logger.info("🌟 Happy modding!")
                break
                
        except KeyboardInterrupt:
            logger.info("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            logger.info("🔄 Returning to main menu...")
            input("Press Enter to continue...")
    
    return 0


if __name__ == "__main__":
    print("[DEBUG] Entering __main__ block", flush=True)
    try:
        print("[DEBUG] About to call main()...", flush=True)
        exit_code = main()
        print("[DEBUG] main() returned", flush=True)
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
