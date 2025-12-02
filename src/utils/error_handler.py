#!/usr/bin/env python3
"""
Error Handler - Enhanced Error Messages (v1.4.0+)
Provides contextual error messages with helpful suggestions
"""

from typing import Optional, Dict, List
from enum import Enum

from .logger import Logger


class ErrorCategory(Enum):
    """Error categories for better organization"""
    SKYRIM = "Skyrim Installation"
    NGIO = "NGIO Mod"
    SKSE = "SKSE"
    CONFIGURATION = "Configuration"
    DISK_SPACE = "Disk Space"
    PERMISSIONS = "File Permissions"
    PROCESS = "Process Management"
    CRASH = "Game Crash"
    TIMEOUT = "Timeout"
    UNKNOWN = "Unknown"


class EnhancedError:
    """
    Enhanced error with context and suggestions
    
    Provides user-friendly error messages with:
    - Clear problem description
    - Likely cause
    - Step-by-step solution
    - Related documentation
    """
    
    # Error knowledge base
    ERROR_DATABASE: Dict[str, Dict[str, any]] = {
        "skyrim_not_found": {
            "category": ErrorCategory.SKYRIM,
            "title": "Skyrim Installation Not Found",
            "description": "The specified Skyrim directory does not exist or is inaccessible",
            "causes": [
                "Incorrect path in configuration",
                "Skyrim not installed",
                "Drive letter changed",
                "Network path unavailable"
            ],
            "solutions": [
                "1. Verify Skyrim is installed on your system",
                "2. Check the path in your configuration:",
                "   - Run: ngio-automation (then option 2 to configure)",
                "   - Or edit: ngio_config.yaml",
                "3. Common paths:",
                "   - C:\\Steam\\steamapps\\common\\Skyrim Special Edition",
                "   - C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition",
                "4. Right-click SkyrimSE.exe → Properties → Copy location"
            ],
            "docs": "See: docs/NEXUS_DOCUMENTATION.txt - Section 2"
        },
        
        "skse_not_found": {
            "category": ErrorCategory.SKSE,
            "title": "SKSE64 Not Installed",
            "description": "skse64_loader.exe not found in Skyrim directory",
            "causes": [
                "SKSE64 not installed",
                "Installed to wrong directory",
                "Antivirus deleted files"
            ],
            "solutions": [
                "1. Download SKSE64 from: https://skse.silverlock.org/",
                "2. Download the Anniversary Edition or Special Edition build",
                "3. Extract ALL files to your Skyrim directory (where SkyrimSE.exe is)",
                "4. You should see these files in Skyrim folder:",
                "   - skse64_loader.exe",
                "   - skse64_1_6_640.dll (or similar)",
                "   - Data folder with SKSE scripts",
                "5. Test: Launch Skyrim using skse64_loader.exe"
            ],
            "docs": "See: docs/NEXUS_DOCUMENTATION.txt - Section 2.4"
        },
        
        "ngio_not_found": {
            "category": ErrorCategory.NGIO,
            "title": "NGIO Mod Not Detected",
            "description": "No Grass In Objects mod plugin not found",
            "causes": [
                "NGIO mod not installed",
                "NGIO disabled in mod manager",
                "Wrong mod manager profile active",
                "Plugin in wrong directory"
            ],
            "solutions": [
                "1. Download NGIO from Nexus Mods: 'No Grass In Objects'",
                "2. Install through your mod manager (MO2 or Vortex)",
                "3. Enable the mod in your mod manager",
                "4. Check plugin is in: Data/SKSE/Plugins/NoGrassInObjects.dll",
                "5. If using MO2: Launch this tool through MO2",
                "6. Verify NGIO appears in your plugin list"
            ],
            "docs": "See: docs/NEXUS_DOCUMENTATION.txt - Section 2.3"
        },
        
        "no_disk_space": {
            "category": ErrorCategory.DISK_SPACE,
            "title": "Insufficient Disk Space",
            "description": "Not enough free disk space for grass cache generation",
            "causes": [
                "Disk is nearly full",
                "Large mod list requires more space",
                "Previous generations not cleaned up"
            ],
            "solutions": [
                "1. Free up at least 5 GB of space (10+ GB recommended)",
                "2. Delete temporary files:",
                "   - Windows Temp folder (search %temp%)",
                "   - Skyrim crash logs",
                "   - Old downloads",
                "3. Move Skyrim to drive with more space",
                "4. Clean up old grass cache files if regenerating"
            ],
            "docs": None
        },
        
        "permission_denied": {
            "category": ErrorCategory.PERMISSIONS,
            "title": "File Permission Denied",
            "description": "Cannot write to output directory or Skyrim folder",
            "causes": [
                "Running without admin rights",
                "Antivirus blocking access",
                "Files in use by another program",
                "Read-only folder"
            ],
            "solutions": [
                "1. Run as Administrator:",
                "   - Right-click start_ngio_automation.bat",
                "   - Select 'Run as administrator'",
                "2. Add folder to antivirus exclusions",
                "3. Close Skyrim and mod managers",
                "4. Check folder properties → Remove 'Read-only'",
                "5. Try different output directory"
            ],
            "docs": None
        },
        
        "skyrim_crash_immediate": {
            "category": ErrorCategory.CRASH,
            "title": "Skyrim Crashes Immediately on Launch",
            "description": "Skyrim crashes within 1 minute of starting",
            "causes": [
                "Mod load order issue",
                "Missing master files",
                "Incompatible mods",
                "Corrupted game files",
                "GPU driver issues"
            ],
            "solutions": [
                "1. Run LOOT to sort your load order",
                "2. Check for missing masters in xEdit or Vortex",
                "3. Verify Skyrim files through Steam:",
                "   - Right-click Skyrim SE in Steam",
                "   - Properties → Local Files → Verify Integrity",
                "4. Update GPU drivers",
                "5. Try launching Skyrim manually first to test",
                "6. Disable half your mods to isolate problem mod"
            ],
            "docs": "See: docs/NEXUS_DOCUMENTATION.txt - Section 5"
        },
        
        "skyrim_hang": {
            "category": ErrorCategory.TIMEOUT,
            "title": "Skyrim Appears to Hang/Freeze",
            "description": "Skyrim takes too long to start or generate grass",
            "causes": [
                "Large load order (500+ mods) takes 5-15 min to start",
                "Complex worldspaces with lots of grass",
                "System resource constraints",
                "Timeout settings too aggressive"
            ],
            "solutions": [
                "1. Increase timeout settings in config:",
                "   no_progress_timeout_minutes: 30  (from 15)",
                "   startup_wait_seconds: 120  (from 30)",
                "2. This is NORMAL for large mod lists - be patient!",
                "3. Close background apps to free resources",
                "4. Check Task Manager - Skyrim should show 15-25% CPU",
                "5. Enable verbose mode to see what's happening:",
                "   ngio-automation --season winter --verbose"
            ],
            "docs": "See: docs/LARGE_LOAD_ORDER_GUIDE.md"
        },
        
        "no_files_generated": {
            "category": ErrorCategory.NGIO,
            "title": "No Grass Cache Files Generated",
            "description": "Skyrim runs but creates no .cgid files",
            "causes": [
                "NGIO mod not working",
                "SKSE not loading properly",
                "Wrong game mode/profile",
                "NGIO configuration issue"
            ],
            "solutions": [
                "1. Launch Skyrim manually with SKSE",
                "2. Open console (~ key) and type: 'help ngio'",
                "3. Should see NGIO commands - if not, SKSE isn't loading",
                "4. Check NGIO .ini file for correct settings",
                "5. Ensure PrecacheGrass.txt is in Skyrim folder",
                "6. Run system validation:",
                "   python -m src.utils.system_validator"
            ],
            "docs": "See: docs/NEXUS_DOCUMENTATION.txt - Section 5"
        }
    }
    
    @staticmethod
    def get_error_details(error_code: str) -> Optional[Dict]:
        """Get error details from knowledge base"""
        return EnhancedError.ERROR_DATABASE.get(error_code)
    
    @staticmethod
    def format_error(error_code: str, context: Optional[Dict] = None) -> str:
        """
        Format enhanced error message
        
        Args:
            error_code: Error code from knowledge base
            context: Additional context (paths, values, etc.)
            
        Returns:
            Formatted error message
        """
        error = EnhancedError.get_error_details(error_code)
        if not error:
            return f"Unknown error: {error_code}"
        
        lines = []
        lines.append("=" * 70)
        lines.append(f"❌ ERROR: {error['title']}")
        lines.append("=" * 70)
        
        # Description
        lines.append(f"\n📋 PROBLEM:")
        lines.append(f"   {error['description']}")
        
        # Context if provided
        if context:
            lines.append(f"\n🔍 DETAILS:")
            for key, value in context.items():
                lines.append(f"   {key}: {value}")
        
        # Likely causes
        if error['causes']:
            lines.append(f"\n💡 LIKELY CAUSES:")
            for cause in error['causes']:
                lines.append(f"   • {cause}")
        
        # Solutions
        if error['solutions']:
            lines.append(f"\n✅ HOW TO FIX:")
            for solution in error['solutions']:
                lines.append(f"   {solution}")
        
        # Documentation reference
        if error.get('docs'):
            lines.append(f"\n📚 DOCUMENTATION:")
            lines.append(f"   {error['docs']}")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
    
    @staticmethod
    def print_error(error_code: str, context: Optional[Dict] = None, logger: Optional[Logger] = None):
        """
        Print enhanced error message
        
        Args:
            error_code: Error code from knowledge base
            context: Additional context
            logger: Logger instance (optional)
        """
        message = EnhancedError.format_error(error_code, context)
        
        if logger:
            # Split into lines and log each
            for line in message.split('\n'):
                if line.strip():
                    logger.error(line)
        else:
            print(message)
    
    @staticmethod
    def suggest_next_steps(error_code: str) -> List[str]:
        """
        Get suggested next steps for an error
        
        Args:
            error_code: Error code
            
        Returns:
            List of suggested actions
        """
        error = EnhancedError.get_error_details(error_code)
        if not error or not error.get('solutions'):
            return ["Check logs for more details", "Consult documentation"]
        
        # Return first 3 solutions as quick actions
        return error['solutions'][:3]


# === HELPER FUNCTIONS ===

def show_error(error_code: str, **context):
    """
    Quick helper to show enhanced error
    
    Args:
        error_code: Error code from knowledge base
        **context: Additional context as keyword arguments
    """
    EnhancedError.print_error(error_code, context)


def get_error_suggestions(error_code: str) -> List[str]:
    """
    Quick helper to get error suggestions
    
    Args:
        error_code: Error code
        
    Returns:
        List of suggestions
    """
    return EnhancedError.suggest_next_steps(error_code)


if __name__ == "__main__":
    # Example usage
    print("Enhanced Error Handler - Examples\n")
    
    # Example 1: Skyrim not found
    print("Example 1: Skyrim Not Found")
    show_error("skyrim_not_found", 
               configured_path="C:/Steam/steamapps/common/Skyrim Special Edition")
    
    print("\n" + "="*70 + "\n")
    
    # Example 2: SKSE not found
    print("Example 2: SKSE Not Found")
    show_error("skse_not_found")
    
    print("\n" + "="*70 + "\n")
    
    # Example 3: Get quick suggestions
    print("Example 3: Quick Suggestions")
    suggestions = get_error_suggestions("skyrim_hang")
    print("Quick fixes for hang issues:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")

