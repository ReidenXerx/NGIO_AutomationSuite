#!/usr/bin/env python3
"""
NGIO Automation Suite - Main Runner
The user-friendly entry point for grass cache generation
"""

import os
import sys
import platform
import signal
import atexit
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.core.automation_suite import NGIOAutomationSuite, AutomationConfig, Season
from src.utils.config_cache import ConfigCache
from src.utils.logger import Logger


def print_banner():
    """Display the application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                    🌱 NGIO AUTOMATION SUITE 🌱                    ║
║                                                                   ║
║              Transform 4+ Hours of Manual Work Into              ║
║                   5 Minutes of Automated Bliss!                  ║
║                                                                   ║
║  ✨ Fully Automated Grass Cache Generation for All Seasons ✨   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_system_requirements() -> bool:
    """Check if system meets requirements"""
    logger = Logger("SystemCheck")
    logger.info("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        logger.error("❌ Python 3.7+ required")
        return False
    
    # Check OS
    if platform.system() != "Windows":
        logger.error("❌ Windows is required for Skyrim modding")
        return False
    
    # Check dependencies
    try:
        import psutil
        import colorlog
        import configparser
        logger.info("✅ All dependencies available")
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("💡 Run: pip install -r requirements.txt")
        return False
    
    logger.success("✅ System requirements met")
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
        backup_configs=preferences.backup_configs
    )
    
    # Show generation summary
    logger.separator("Generation Summary")
    logger.info("🎯 About to generate grass cache with these settings:")
    logger.info(f"   📁 Skyrim: {paths.skyrim_path}")
    logger.info(f"   📦 Output: {paths.output_directory}")
    
    # Show mode and seasons
    if preferences.use_seasonal_mods:
        logger.info(f"   🌿 Mode: Seasonal (with seasonal mods)")
        logger.info(f"   🌱 Season: {preferences.seasons_to_generate[0]}")
    else:
        logger.info(f"   🌿 Mode: Non-seasonal (no seasonal mods)")
        logger.info(f"   🌱 Generation: Single grass cache")
    
    logger.info(f"   🔄 Max retries: {preferences.max_crash_retries}")
    logger.info(f"   ⚡ Crash timeout: {preferences.crash_timeout_minutes} minutes (process not running)")
    logger.info(f"   ⏰ No progress timeout: {preferences.no_progress_timeout_minutes} minutes (file not updating)")
    logger.info(f"   📦 Create archives: {'Yes' if preferences.create_archives else 'No'}")
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

def main():
    """Main entry point"""
    global automation_suite
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, emergency_shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, emergency_shutdown)  # Termination signal
    atexit.register(emergency_shutdown)  # Normal exit
    
    print_banner()
    
    # Check system requirements
    if not check_system_requirements():
        input("Press Enter to exit...")
        return 1
    
    # Initialize config cache
    config_cache = ConfigCache()
    logger = Logger("Main")
    
    # Load existing configuration
    config_loaded = config_cache.load_config()
    
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
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
