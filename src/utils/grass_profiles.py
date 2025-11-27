#!/usr/bin/env python3
"""
Grass Generation Profiles (v1.5.0+)
Provides preset configurations for different grass generation scenarios
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum


class ProfileType(Enum):
    """Grass generation profile types"""
    FAST = "fast"
    LOD_COMPATIBLE = "lod_compatible"
    MAXIMUM_QUALITY = "maximum_quality"
    CUSTOM = "custom"


@dataclass
class GrassProfile:
    """Grass generation profile configuration"""
    name: str
    description: str
    estimated_time: str
    extend_grass_distance: bool
    extend_grass_count: bool
    super_dense_grass: bool
    overwrite_min_grass_size: int
    global_grass_scale: float
    ensure_max_grass_types: int
    
    def get_summary(self) -> str:
        """Get formatted summary of profile settings"""
        return f"""
Profile: {self.name}
{self.description}

⏱️  Estimated Time: {self.estimated_time}

Settings (BAKED into cache):
  • Grass Density: {self.overwrite_min_grass_size} (20-100, higher = less dense)
  • Grass Height: {self.global_grass_scale}x
  • Extended Distance: {'Yes' if self.extend_grass_distance else 'No'} {'(LOD Compatible)' if self.extend_grass_distance else ''}
  • Extended Count: {'Yes ⚠️ SLOW!' if self.extend_grass_count else 'No'}
  • Super Dense: {'Yes ⚠️ VERY SLOW!' if self.super_dense_grass else 'No'}
  • Max Grass Types: {self.ensure_max_grass_types}
"""


# Predefined Profiles
PROFILES: Dict[ProfileType, GrassProfile] = {
    ProfileType.FAST: GrassProfile(
        name="Fast Generation",
        description="Quick generation for testing. Normal density, no extended features.",
        estimated_time="30-45 minutes (varies by load order)",
        extend_grass_distance=False,
        extend_grass_count=False,
        super_dense_grass=False,
        overwrite_min_grass_size=80,  # Lower density for speed
        global_grass_scale=1.0,
        ensure_max_grass_types=7
    ),
    
    ProfileType.LOD_COMPATIBLE: GrassProfile(
        name="LOD Compatible",
        description="Recommended for most users. Compatible with DynDOLOD grass LOD.",
        estimated_time="60-90 minutes (varies by load order)",
        extend_grass_distance=True,  # Required for LOD
        extend_grass_count=False,
        super_dense_grass=False,
        overwrite_min_grass_size=67,  # Medium density (Cathedral Landscapes default)
        global_grass_scale=1.0,
        ensure_max_grass_types=15  # Cathedral Landscapes default
    ),
    
    ProfileType.MAXIMUM_QUALITY: GrassProfile(
        name="Maximum Quality",
        description="Highest quality settings. WARNING: Can take 2-6 hours!",
        estimated_time="2-6 hours (WARNING: ExtendGrassCount adds significant time!)",
        extend_grass_distance=True,
        extend_grass_count=True,  # WARNING: Very slow!
        super_dense_grass=False,  # Still disabled - would make it take MANY hours
        overwrite_min_grass_size=40,  # High density
        global_grass_scale=1.15,  # Slightly taller grass
        ensure_max_grass_types=15
    ),
}


def get_profile(profile_type: ProfileType) -> GrassProfile:
    """Get a profile by type"""
    return PROFILES[profile_type]


def get_all_profiles() -> Dict[ProfileType, GrassProfile]:
    """Get all available profiles"""
    return PROFILES


def display_profile_menu() -> str:
    """Display profile selection menu"""
    menu = """
┌──────────────────────────────────────────────────────────────┐
│             🌱 Grass Generation Profile Selection            │
└──────────────────────────────────────────────────────────────┘

⚠️  IMPORTANT: These settings are PERMANENTLY BAKED into cache!
   Once generated, you must regenerate everything to change them.

"""
    
    profiles = [
        (1, ProfileType.FAST, "Fast"),
        (2, ProfileType.LOD_COMPATIBLE, "LOD Compatible [Recommended]"),
        (3, ProfileType.MAXIMUM_QUALITY, "Maximum Quality"),
        (4, ProfileType.CUSTOM, "Custom Settings")
    ]
    
    for num, ptype, label in profiles:
        if ptype == ProfileType.CUSTOM:
            menu += f"{num}. {label}\n"
            menu += "   • Manually configure all settings\n\n"
        else:
            profile = PROFILES[ptype]
            menu += f"{num}. {label}\n"
            menu += f"   • Time: {profile.estimated_time}\n"
            menu += f"   • {profile.description}\n\n"
    
    return menu


def create_custom_profile_interactive() -> GrassProfile:
    """
    Interactive profile creation
    Returns a custom GrassProfile based on user input
    """
    from .logger import Logger
    logger = Logger("ProfileCreator")
    
    logger.info("🎨 Creating custom profile...")
    logger.info("")
    
    # Default values
    profile = GrassProfile(
        name="Custom",
        description="User-configured settings",
        estimated_time="Varies",
        extend_grass_distance=True,
        extend_grass_count=False,
        super_dense_grass=False,
        overwrite_min_grass_size=67,
        global_grass_scale=1.0,
        ensure_max_grass_types=15
    )
    
    return profile


def confirm_profile(profile: GrassProfile) -> bool:
    """
    Display profile summary and ask for confirmation
    
    Returns:
        bool: True if user confirms, False if they want to modify
    """
    print(profile.get_summary())
    print("─" * 60)
    print("\nOptions:")
    print("  [C]ontinue with these settings")
    print("  [M]odify settings")
    print("  [B]ack to profile menu")
    print("")
    
    while True:
        choice = input("Your choice [C/M/B]: ").strip().upper()
        
        if choice == 'C':
            return True
        elif choice == 'M':
            return False
        elif choice == 'B':
            return None  # Special case: go back to menu
        else:
            print("Invalid choice. Please enter C, M, or B.")


def modify_profile_interactive(profile: GrassProfile) -> GrassProfile:
    """
    Allow user to modify individual profile settings
    
    Returns:
        Modified GrassProfile
    """
    from .logger import Logger
    logger = Logger("ProfileModifier")
    
    logger.info("🔧 Modify Profile Settings")
    logger.info("")
    
    while True:
        print("┌──────────────────────────────────────────────────────────────┐")
        print("│                    Modify Settings                           │")
        print("└──────────────────────────────────────────────────────────────┘")
        print("")
        print(f"1. Grass Density (OverwriteMinGrassSize): {profile.overwrite_min_grass_size}")
        print("   Range: 20-100 (higher = less grass, better performance)")
        print("")
        print(f"2. Grass Height (GlobalGrassScale): {profile.global_grass_scale}x")
        print("   Range: 0.5-2.0 (multiplier)")
        print("")
        print(f"3. Extended Distance: {'Yes' if profile.extend_grass_distance else 'No'}")
        print("   Required for DynDOLOD grass LOD")
        print("")
        print(f"4. Extended Count: {'Yes' if profile.extend_grass_count else 'No'}")
        print("   ⚠️  WARNING: Dramatically increases generation time!")
        print("")
        print(f"5. Super Dense Grass: {'Yes' if profile.super_dense_grass else 'No'}")
        print("   ⚠️  WARNING: Can take MANY hours!")
        print("")
        print(f"6. Max Grass Types: {profile.ensure_max_grass_types}")
        print("   Grass mod specific (7=Vanilla, 15=Cathedral)")
        print("")
        print("0. Done - Return to confirmation")
        print("")
        
        try:
            choice = int(input("Enter setting number to change: ").strip())
            
            if choice == 0:
                return profile
            elif choice == 1:
                val = int(input(f"Enter grass density [20-100] (current: {profile.overwrite_min_grass_size}): "))
                if 20 <= val <= 100:
                    profile.overwrite_min_grass_size = val
                else:
                    print("❌ Value must be between 20 and 100")
            elif choice == 2:
                val = float(input(f"Enter grass scale [0.5-2.0] (current: {profile.global_grass_scale}): "))
                if 0.5 <= val <= 2.0:
                    profile.global_grass_scale = val
                else:
                    print("❌ Value must be between 0.5 and 2.0")
            elif choice == 3:
                val = input(f"Extended Distance? [y/n] (current: {'y' if profile.extend_grass_distance else 'n'}): ")
                profile.extend_grass_distance = val.lower() == 'y'
            elif choice == 4:
                val = input(f"Extended Count? ⚠️  [y/n] (current: {'y' if profile.extend_grass_count else 'n'}): ")
                if val.lower() == 'y':
                    confirm = input("Are you sure? This can add HOURS to generation time [y/n]: ")
                    profile.extend_grass_count = confirm.lower() == 'y'
                else:
                    profile.extend_grass_count = False
            elif choice == 5:
                val = input(f"Super Dense Grass? ⚠️  [y/n] (current: {'y' if profile.super_dense_grass else 'n'}): ")
                if val.lower() == 'y':
                    confirm = input("Are you sure? This can take MANY HOURS [y/n]: ")
                    profile.super_dense_grass = confirm.lower() == 'y'
                else:
                    profile.super_dense_grass = False
            elif choice == 6:
                val = int(input(f"Enter max grass types [1-20] (current: {profile.ensure_max_grass_types}): "))
                if 1 <= val <= 20:
                    profile.ensure_max_grass_types = val
                else:
                    print("❌ Value must be between 1 and 20")
            else:
                print("❌ Invalid choice")
            
            print("")
            
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled")
            return profile


def select_profile_interactive() -> Tuple[GrassProfile, bool]:
    """
    Interactive profile selection with confirmation
    
    Returns:
        Tuple[GrassProfile, bool]: (selected_profile, user_confirmed)
    """
    from .logger import Logger
    logger = Logger("ProfileSelector")
    
    while True:
        # Show menu
        print(display_profile_menu())
        
        try:
            choice = int(input("Select profile [1-4]: ").strip())
            
            if choice == 1:
                profile = get_profile(ProfileType.FAST)
            elif choice == 2:
                profile = get_profile(ProfileType.LOD_COMPATIBLE)
            elif choice == 3:
                profile = get_profile(ProfileType.MAXIMUM_QUALITY)
            elif choice == 4:
                # Start with LOD compatible as base for custom
                profile = GrassProfile(**PROFILES[ProfileType.LOD_COMPATIBLE].__dict__)
                profile.name = "Custom"
                profile.description = "User-configured settings"
                # Skip confirmation, go straight to modification
                profile = modify_profile_interactive(profile)
                confirmation = confirm_profile(profile)
                if confirmation is True:
                    return profile, True
                elif confirmation is False:
                    profile = modify_profile_interactive(profile)
                    continue
                else:  # None = back to menu
                    continue
            else:
                print("❌ Invalid choice. Please select 1-4.")
                continue
            
            # Confirm profile
            confirmation = confirm_profile(profile)
            
            if confirmation is True:
                return profile, True
            elif confirmation is False:
                # Modify settings
                profile = modify_profile_interactive(profile)
                # Re-confirm after modification
                confirmation = confirm_profile(profile)
                if confirmation is True:
                    return profile, True
                elif confirmation is None:
                    continue  # Back to menu
                else:
                    # User wants to modify again
                    profile = modify_profile_interactive(profile)
                    continue
            else:  # None = back to menu
                continue
                
        except ValueError:
            print("❌ Invalid input. Please enter a number 1-4.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Selection cancelled")
            return None, False


if __name__ == "__main__":
    # Test profile selection
    profile, confirmed = select_profile_interactive()
    if confirmed:
        print("\n✅ Profile selected!")
        print(profile.get_summary())

