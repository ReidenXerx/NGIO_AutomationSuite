#!/usr/bin/env python3
"""
Archive Creator - Mod Archive Generation
Creates installable mod archives for each season's grass cache
"""

import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time

from ..utils.logger import Logger


@dataclass
class ArchiveInfo:
    """Information about a created archive"""
    season_name: str
    archive_path: str
    file_count: int
    archive_size_mb: float
    creation_time: float


class ArchiveCreator:
    """
    Creates mod archives for seasonal grass cache files
    
    Key features:
    - Creates zip archives with proper mod structure
    - Includes Data/Grass folder with seasonal files
    - Adds mod metadata and installation instructions
    - Validates archive integrity
    - Provides user-friendly naming
    """
    
    def __init__(self, output_directory: str = None):
        self.logger = Logger("ArchiveCreator")
        
        # Set output directory for archives
        if output_directory:
            self.output_directory = output_directory
        else:
            self.output_directory = os.path.join(os.getcwd(), "Generated_Mods")
        
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        
        self.logger.info(f"📦 ArchiveCreator initialized")
        self.logger.info(f"📁 Output directory: {self.output_directory}")
        
        # Archive creation statistics
        self.created_archives: List[ArchiveInfo] = []
    
    def create_season_archive(self, season, grass_files_directory: str, 
                            custom_name: Optional[str] = None) -> Optional[ArchiveInfo]:
        """
        Create a mod archive for a specific season
        
        Args:
            season: Season enum with name and extension info
            grass_files_directory: Directory containing the seasonal .cgid files
            custom_name: Optional custom name for the archive
            
        Returns:
            ArchiveInfo if successful, None if failed
        """
        self.logger.info(f"📦 Creating mod archive for {season.display_name}...")
        
        # Generate archive name
        if custom_name:
            archive_name = f"{custom_name}.zip"
        else:
            archive_name = f"Grass_Cache_{season.display_name}_Season.zip"
        
        archive_path = os.path.join(self.output_directory, archive_name)
        
        # Find seasonal grass files
        seasonal_files = self._find_seasonal_files(grass_files_directory, season.extension)
        
        if not seasonal_files:
            self.logger.error(f"❌ No seasonal files found for {season.display_name} ({season.extension})")
            return None
        
        self.logger.info(f"📁 Found {len(seasonal_files)} files for {season.display_name}")
        
        try:
            # Create temporary directory for archive structure
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create mod structure
                mod_structure = self._create_mod_structure(temp_dir, season, seasonal_files)
                
                if not mod_structure:
                    return None
                
                # Create the zip archive
                archive_info = self._create_zip_archive(mod_structure, archive_path, season)
                
                if archive_info:
                    self.created_archives.append(archive_info)
                    self.logger.success(f"✅ Created archive: {archive_name}")
                    self.logger.info(f"📊 Archive size: {archive_info.archive_size_mb:.1f} MB")
                    self.logger.info(f"📁 Files included: {archive_info.file_count}")
                
                return archive_info
                
        except Exception as e:
            self.logger.error(f"💥 Failed to create archive for {season.display_name}: {e}")
            return None
    
    def _find_seasonal_files(self, directory: str, extension: str) -> List[str]:
        """Find all files with the seasonal extension"""
        seasonal_files = []
        
        if not os.path.exists(directory):
            self.logger.error(f"❌ Directory not found: {directory}")
            return seasonal_files
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(extension):
                        full_path = os.path.join(root, file)
                        seasonal_files.append(full_path)
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        
        return seasonal_files
    
    def _create_mod_structure(self, temp_dir: str, season, seasonal_files: List[str]) -> Optional[str]:
        """
        Create the proper mod directory structure
        
        Args:
            temp_dir: Temporary directory for building the structure
            season: Season enum
            seasonal_files: List of seasonal grass cache files
            
        Returns:
            str: Path to the mod root directory, or None if failed
        """
        try:
            # Create mod root directory
            mod_root = os.path.join(temp_dir, f"Grass_Cache_{season.display_name}")
            data_dir = os.path.join(mod_root, "Data")
            grass_dir = os.path.join(data_dir, "Grass")
            
            os.makedirs(grass_dir, exist_ok=True)
            
            # Copy seasonal files to Grass directory
            copied_files = 0
            for source_file in seasonal_files:
                filename = os.path.basename(source_file)
                target_file = os.path.join(grass_dir, filename)
                
                try:
                    shutil.copy2(source_file, target_file)
                    copied_files += 1
                except Exception as e:
                    self.logger.warning(f"Failed to copy {filename}: {e}")
            
            if copied_files == 0:
                self.logger.error("❌ No files were copied to mod structure")
                return None
            
            # Create mod metadata files
            self._create_mod_metadata_files(mod_root, season, copied_files)
            
            self.logger.info(f"📁 Created mod structure with {copied_files} files")
            return mod_root
            
        except Exception as e:
            self.logger.error(f"💥 Error creating mod structure: {e}")
            return None
    
    def _create_mod_metadata_files(self, mod_root: str, season, file_count: int) -> None:
        """Create metadata files for the mod"""
        try:
            # Create README.txt
            readme_path = os.path.join(mod_root, "README.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_readme_content(season, file_count))
            
            # Create meta.ini for Mod Organizer 2
            meta_path = os.path.join(mod_root, "meta.ini")
            with open(meta_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_meta_ini_content(season))
            
            # Create fomod installer info (optional)
            self._create_fomod_installer(mod_root, season)
            
            self.logger.debug(f"📝 Created metadata files for {season.display_name}")
            
        except Exception as e:
            self.logger.warning(f"Failed to create metadata files: {e}")
    
    def _generate_readme_content(self, season, file_count: int) -> str:
        """Generate README.txt content"""
        return f"""Grass Cache - {season.display_name} Season
{'=' * 50}

Generated by NGIO Automation Suite
Creation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

DESCRIPTION:
This mod contains pre-generated grass cache files for the {season.display_name} season.
These files enable high-performance grass rendering in Skyrim SE/AE/VR.

CONTENTS:
- {file_count} grass cache files ({season.extension})
- Season Type: {season.season_type}

REQUIREMENTS:
- Skyrim SE/AE/VR
- SKSE64
- Grass Cache Helper NG (for seasonal switching)
- Seasons of Skyrim (or compatible seasonal mod)

INSTALLATION:
1. Install this mod using your preferred mod manager (MO2, Vortex, etc.)
2. Ensure Grass Cache Helper NG is installed and enabled
3. Make sure NGIO is DISABLED (important!)
4. Set your seasonal mod to use {season.display_name} season
5. Launch Skyrim and enjoy improved grass performance!

COMPATIBILITY:
- Compatible with all grass mods
- Compatible with ENB and weather mods
- Works with landscape overhauls
- May conflict with other grass cache mods (disable them)

UNINSTALLATION:
Simply disable or remove this mod through your mod manager.

TROUBLESHOOTING:
- If grass doesn't appear: Check that Grass Cache Helper NG is active
- If performance is poor: Ensure NGIO is disabled
- If crashes occur: Check for mod conflicts

CREDITS:
- NGIO Development Team: For the grass cache system
- Grass Cache Helper NG: For seasonal cache loading
- NGIO Automation Suite: For automated generation

For support and updates, visit:
https://github.com/ReidenXerx/ngio-automation-suite

VERSION: 1.0
LICENSE: Mod content follows original mod licenses
"""
    
    def _generate_meta_ini_content(self, season) -> str:
        """Generate meta.ini content for MO2"""
        return f"""[General]
modid=0
version=1.0
newestVersion=1.0
category=23
installationFile=Generated by NGIO Automation Suite

[installedFiles]
size=1

[comments]
Grass Cache for {season.display_name} Season
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Season Type: {season.season_type}
Extension: {season.extension}
"""
    
    def _create_fomod_installer(self, mod_root: str, season) -> None:
        """Create FOMOD installer configuration (optional)"""
        try:
            fomod_dir = os.path.join(mod_root, "fomod")
            os.makedirs(fomod_dir, exist_ok=True)
            
            # Create ModuleConfig.xml
            config_path = os.path.join(fomod_dir, "ModuleConfig.xml")
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_fomod_config(season))
            
            # Create info.xml
            info_path = os.path.join(fomod_dir, "info.xml")
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_fomod_info(season))
            
            self.logger.debug(f"📝 Created FOMOD installer for {season.display_name}")
            
        except Exception as e:
            self.logger.debug(f"Failed to create FOMOD installer: {e}")
    
    def _generate_fomod_config(self, season) -> str:
        """Generate FOMOD ModuleConfig.xml"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
    <moduleName>Grass Cache - {season.display_name} Season</moduleName>
    <installSteps>
        <installStep name="Installation">
            <optionalFileGroups>
                <group name="Grass Cache Files" type="SelectExactlyOne">
                    <plugins>
                        <plugin name="Install {season.display_name} Grass Cache">
                            <description>Installs pre-generated grass cache for {season.display_name} season.</description>
                            <files>
                                <folder source="Data" destination="Data" priority="0" />
                            </files>
                            <typeDescriptor>
                                <type name="Recommended"/>
                            </typeDescriptor>
                        </plugin>
                    </plugins>
                </group>
            </optionalFileGroups>
        </installStep>
    </installSteps>
</config>"""
    
    def _generate_fomod_info(self, season) -> str:
        """Generate FOMOD info.xml"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<fomod>
    <Name>Grass Cache - {season.display_name} Season</Name>
    <Author>NGIO Automation Suite</Author>
    <Version>1.0</Version>
    <Description>Pre-generated grass cache files for {season.display_name} season. Provides optimal grass performance in Skyrim SE/AE/VR.</Description>
    <Website>https://github.com/ReidenXerx/ngio-automation-suite</Website>
</fomod>"""
    
    def _create_zip_archive(self, mod_directory: str, archive_path: str, season) -> Optional[ArchiveInfo]:
        """
        Create the final zip archive
        
        Args:
            mod_directory: Directory containing the mod structure
            archive_path: Path for the output archive
            season: Season enum
            
        Returns:
            ArchiveInfo if successful, None if failed
        """
        try:
            start_time = time.time()
            file_count = 0
            
            # Remove existing archive if it exists
            if os.path.exists(archive_path):
                os.remove(archive_path)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                # Walk through mod directory and add all files
                for root, dirs, files in os.walk(mod_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Calculate relative path within the archive
                        arcname = os.path.relpath(file_path, mod_directory)
                        
                        # Add file to archive
                        zipf.write(file_path, arcname)
                        file_count += 1
            
            # Get archive size
            archive_size_mb = os.path.getsize(archive_path) / (1024 * 1024)
            creation_time = time.time() - start_time
            
            # Validate archive
            if not self._validate_archive(archive_path):
                self.logger.error(f"❌ Archive validation failed: {archive_path}")
                return None
            
            return ArchiveInfo(
                season_name=season.display_name,
                archive_path=archive_path,
                file_count=file_count,
                archive_size_mb=archive_size_mb,
                creation_time=creation_time
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error creating zip archive: {e}")
            return None
    
    def _validate_archive(self, archive_path: str) -> bool:
        """Validate that the archive was created correctly"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                # Test the archive
                bad_file = zipf.testzip()
                if bad_file:
                    self.logger.error(f"❌ Corrupted file in archive: {bad_file}")
                    return False
                
                # Check that it contains expected structure
                file_list = zipf.namelist()
                
                # Should contain Data/Grass/ structure
                has_data_grass = any('Data/Grass/' in name for name in file_list)
                has_readme = any('README.txt' in name for name in file_list)
                
                if not has_data_grass:
                    self.logger.error("❌ Archive missing Data/Grass structure")
                    return False
                
                if not has_readme:
                    self.logger.warning("⚠️ Archive missing README.txt")
                
                return True
                
        except Exception as e:
            self.logger.error(f"💥 Error validating archive: {e}")
            return False
    
    def create_all_season_archives(self, grass_directory: str, seasons: List) -> List[ArchiveInfo]:
        """
        Create archives for all specified seasons
        
        Args:
            grass_directory: Directory containing all seasonal grass files
            seasons: List of Season enums to create archives for
            
        Returns:
            List[ArchiveInfo]: Information about created archives
        """
        self.logger.info(f"📦 Creating archives for {len(seasons)} seasons...")
        
        created_archives = []
        
        for season in seasons:
            self.logger.separator(f"Creating {season.display_name} Archive")
            
            archive_info = self.create_season_archive(season, grass_directory)
            
            if archive_info:
                created_archives.append(archive_info)
                self.logger.success(f"✅ {season.display_name} archive created successfully")
            else:
                self.logger.error(f"❌ Failed to create {season.display_name} archive")
        
        # Summary
        self.logger.separator("Archive Creation Summary")
        self.logger.info(f"📊 Successfully created: {len(created_archives)}/{len(seasons)} archives")
        
        total_size = sum(archive.archive_size_mb for archive in created_archives)
        self.logger.info(f"📁 Total archive size: {total_size:.1f} MB")
        
        if created_archives:
            self.logger.info("📦 Created archives:")
            for archive in created_archives:
                self.logger.info(f"   ✅ {archive.season_name}: {os.path.basename(archive.archive_path)} ({archive.archive_size_mb:.1f} MB)")
        
        return created_archives
    
    def get_created_archives(self) -> List[ArchiveInfo]:
        """Get list of all created archives"""
        return self.created_archives.copy()
    
    def cleanup_output_directory(self, keep_latest: int = 5) -> None:
        """
        Clean up old archives, keeping only the latest ones
        
        Args:
            keep_latest: Number of archive sets to keep
        """
        try:
            if not os.path.exists(self.output_directory):
                return
            
            # Get all archive files
            archive_files = []
            for file in os.listdir(self.output_directory):
                if file.endswith('.zip') and 'Grass_Cache_' in file:
                    file_path = os.path.join(self.output_directory, file)
                    archive_files.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time (newest first)
            archive_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old archives
            removed_count = 0
            for file_path, _ in archive_files[keep_latest:]:
                try:
                    os.remove(file_path)
                    removed_count += 1
                    self.logger.debug(f"🗑️ Removed old archive: {os.path.basename(file_path)}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove archive {file_path}: {e}")
            
            if removed_count > 0:
                self.logger.info(f"🧹 Cleaned up {removed_count} old archives")
                
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def generate_installation_guide(self, output_path: str = None) -> bool:
        """
        Generate a comprehensive installation guide
        
        Args:
            output_path: Path to save the guide (defaults to output directory)
            
        Returns:
            bool: True if successful
        """
        if not output_path:
            output_path = os.path.join(self.output_directory, "INSTALLATION_GUIDE.txt")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_installation_guide_content())
            
            self.logger.info(f"📝 Installation guide created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Failed to create installation guide: {e}")
            return False
    
    def _generate_installation_guide_content(self) -> str:
        """Generate comprehensive installation guide content"""
        return """NGIO Grass Cache - Installation Guide
=====================================

OVERVIEW:
This package contains pre-generated grass cache files for all seasons.
These files dramatically improve grass rendering performance in Skyrim.

WHAT'S INCLUDED:
- Grass_Cache_Winter_Season.zip
- Grass_Cache_Spring_Season.zip  
- Grass_Cache_Summer_Season.zip
- Grass_Cache_Autumn_Season.zip

REQUIREMENTS:
1. Skyrim SE/AE/VR
2. SKSE64 (latest version)
3. Grass Cache Helper NG mod
4. Seasons of Skyrim (or compatible seasonal mod)

INSTALLATION STEPS:

Step 1: Install Required Mods
- Download and install Grass Cache Helper NG from Nexus
- Ensure your seasonal mod (Seasons of Skyrim) is installed
- Make sure SKSE64 is properly installed

Step 2: Install Grass Cache Archives
- Install each seasonal archive as a separate mod in your mod manager
- In Mod Organizer 2: Use "Install from Archive" for each zip file
- In Vortex: Drag and drop each zip file into the mods area

Step 3: Configure Load Order
- Enable all four seasonal grass cache mods
- Ensure Grass Cache Helper NG is loaded after SKSE plugins
- DISABLE the original NGIO mod (very important!)

Step 4: Configure Seasonal Settings
- Set your seasonal mod to the desired season
- The grass cache will automatically match the active season

Step 5: Test In-Game
- Launch Skyrim through SKSE
- Load a save in an outdoor area
- Grass should render with improved performance

TROUBLESHOOTING:

No Grass Visible:
- Check that Grass Cache Helper NG is active
- Verify NGIO is disabled
- Ensure seasonal grass cache mod is enabled

Poor Performance:
- Make sure NGIO is completely disabled
- Check for conflicts with other grass mods
- Verify SKSE is running properly

Crashes:
- Check for mod conflicts
- Ensure all requirements are met
- Try disabling other grass-related mods

Wrong Season:
- Check your seasonal mod settings
- Verify the correct seasonal cache is enabled
- Restart the game after changing seasons

ADVANCED CONFIGURATION:

Multiple Profiles:
- You can create separate MO2 profiles for each season
- Enable only the appropriate seasonal cache in each profile
- Switch profiles when changing seasons

Performance Tuning:
- Grass cache works with all grass density settings
- Compatible with ENB grass modifications
- Works with landscape texture overhauls

UNINSTALLATION:
1. Disable all seasonal grass cache mods
2. Re-enable NGIO if desired
3. Remove the grass cache mod files

SUPPORT:
For issues or questions:
- Check the troubleshooting section above
- Visit the NGIO Automation Suite GitHub page
- Post in the Nexus comments for Grass Cache Helper NG

CREDITS:
- NGIO Development Team: Original grass cache system
- Grass Cache Helper NG: Seasonal cache loading
- NGIO Automation Suite: Automated generation

Generated by NGIO Automation Suite
https://github.com/ReidenXerx/ngio-automation-suite
"""


def main():
    """Test the ArchiveCreator functionality"""
    print("🧪 Testing ArchiveCreator...")
    
    # Create test directory structure
    test_dir = os.path.join(os.getcwd(), "test_archive_creator")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create some dummy grass files
    grass_dir = os.path.join(test_dir, "Grass")
    os.makedirs(grass_dir, exist_ok=True)
    
    # Create test files
    test_files = [
        "test_file_1.WIN.cgid",
        "test_file_2.WIN.cgid",
        "test_file_3.WIN.cgid"
    ]
    
    for filename in test_files:
        with open(os.path.join(grass_dir, filename), 'w') as f:
            f.write(f"Test grass cache content for {filename}\n" * 100)
    
    try:
        # Test archive creation
        from ..core.automation_suite import Season
        
        creator = ArchiveCreator(os.path.join(test_dir, "output"))
        archive_info = creator.create_season_archive(Season.WINTER, grass_dir)
        
        if archive_info:
            print(f"✅ Archive created successfully:")
            print(f"   Path: {archive_info.archive_path}")
            print(f"   Size: {archive_info.archive_size_mb:.1f} MB")
            print(f"   Files: {archive_info.file_count}")
        else:
            print("❌ Archive creation failed")
        
        # Generate installation guide
        creator.generate_installation_guide()
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    main()
