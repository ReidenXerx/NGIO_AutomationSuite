#!/usr/bin/env python3
"""
Archive Creator - Mod Archive Generation
Creates installable mod archives for each season's grass cache
"""

import os
import shutil
import zipfile
import tempfile
import hashlib
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
    sha256_checksum: Optional[str] = None  # Added for integrity verification


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
            
            # Generate checksum for integrity verification
            checksum = self._generate_checksum(archive_path)
            if checksum:
                # Save checksum to file
                self._save_checksum_file(archive_path, checksum)
            
            return ArchiveInfo(
                season_name=season.display_name,
                archive_path=archive_path,
                file_count=file_count,
                archive_size_mb=archive_size_mb,
                creation_time=creation_time,
                sha256_checksum=checksum
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
    
    def _generate_checksum(self, file_path: str) -> Optional[str]:
        """
        Generate SHA256 checksum for file
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash string, or None if failed
        """
        try:
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large archives
                for byte_block in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(byte_block)
            
            checksum = sha256_hash.hexdigest()
            self.logger.debug(f"🔐 Generated checksum: {checksum[:16]}...")
            return checksum
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to generate checksum: {e}")
            return None
    
    def _save_checksum_file(self, archive_path: str, checksum: str) -> bool:
        """
        Save checksum to .sha256 file
        
        Args:
            archive_path: Path to archive
            checksum: SHA256 checksum string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            checksum_path = archive_path + '.sha256'
            archive_name = os.path.basename(archive_path)
            
            with open(checksum_path, 'w') as f:
                # Standard format: <checksum>  <filename>
                f.write(f"{checksum}  {archive_name}\n")
            
            self.logger.info(f"🔐 Checksum saved: {os.path.basename(checksum_path)}")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save checksum file: {e}")
            return False
    
    def verify_archive_checksum(self, archive_path: str) -> bool:
        """
        Verify archive integrity using checksum file
        
        Args:
            archive_path: Path to archive
            
        Returns:
            True if checksum matches, False otherwise
        """
        checksum_path = archive_path + '.sha256'
        
        if not os.path.exists(checksum_path):
            self.logger.warning("⚠️ No checksum file found for verification")
            return False
        
        try:
            # Read expected checksum
            with open(checksum_path, 'r') as f:
                expected_checksum = f.read().strip().split()[0]
            
            # Calculate actual checksum
            actual_checksum = self._generate_checksum(archive_path)
            
            if not actual_checksum:
                return False
            
            # Compare
            if expected_checksum == actual_checksum:
                self.logger.success("✅ Archive checksum verified")
                return True
            else:
                self.logger.error("❌ Checksum mismatch! Archive may be corrupted")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Error verifying checksum: {e}")
            return False
    
    def create_lod_grass_archive(self, lod_grass_directory: str, 
                                  source_season_name: str = "Default") -> Optional[ArchiveInfo]:
        """
        Create a mod archive for LOD grass (DynDOLOD compatible).
        
        This creates "Grass Cache - Default" archive containing grass files
        without seasonal postfixes, required for DynDOLOD LOD generation.
        
        Args:
            lod_grass_directory: Directory containing the plain .cgid files (no seasonal suffix)
            source_season_name: Name of the season used as source (for documentation)
            
        Returns:
            ArchiveInfo if successful, None if failed
        """
        self.logger.info(f"🏔️ Creating LOD grass archive (Grass Cache - Default)...")
        
        archive_name = "Grass_Cache_Default_LOD.zip"
        archive_path = os.path.join(self.output_directory, archive_name)
        
        # Find plain .cgid files (without seasonal suffixes)
        lod_files = self._find_lod_grass_files(lod_grass_directory)
        
        if not lod_files:
            self.logger.error("❌ No LOD grass files found (.cgid without seasonal suffix)")
            return None
        
        self.logger.info(f"📁 Found {len(lod_files)} LOD grass files")
        
        try:
            # Create temporary directory for archive structure
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create mod structure for LOD grass
                mod_structure = self._create_lod_mod_structure(temp_dir, lod_files, source_season_name)
                
                if not mod_structure:
                    return None
                
                # Create the zip archive
                archive_info = self._create_lod_zip_archive(mod_structure, archive_path, source_season_name, len(lod_files))
                
                if archive_info:
                    self.created_archives.append(archive_info)
                    self.logger.success(f"✅ Created LOD archive: {archive_name}")
                    self.logger.info(f"📊 Archive size: {archive_info.archive_size_mb:.1f} MB")
                    self.logger.info(f"📁 Files included: {archive_info.file_count}")
                
                return archive_info
                
        except Exception as e:
            self.logger.error(f"💥 Failed to create LOD grass archive: {e}")
            return None
    
    def _find_lod_grass_files(self, directory: str) -> List[str]:
        """Find all plain .cgid files (without seasonal suffixes)"""
        lod_files = []
        seasonal_suffixes = ['.WIN.cgid', '.SPR.cgid', '.SUM.cgid', '.AUT.cgid']
        
        if not os.path.exists(directory):
            self.logger.error(f"❌ Directory not found: {directory}")
            return lod_files
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # Only include .cgid files that DON'T have seasonal suffixes
                    if file.endswith('.cgid'):
                        is_seasonal = any(file.endswith(suffix) for suffix in seasonal_suffixes)
                        if not is_seasonal:
                            full_path = os.path.join(root, file)
                            lod_files.append(full_path)
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        
        return lod_files
    
    def _create_lod_mod_structure(self, temp_dir: str, lod_files: List[str], 
                                   source_season_name: str) -> Optional[str]:
        """
        Create the proper mod directory structure for LOD grass
        
        Args:
            temp_dir: Temporary directory for building the structure
            lod_files: List of LOD grass cache files
            source_season_name: Season used as source
            
        Returns:
            str: Path to the mod root directory, or None if failed
        """
        try:
            # Create mod root directory
            mod_root = os.path.join(temp_dir, "Grass_Cache_Default")
            data_dir = os.path.join(mod_root, "Data")
            grass_dir = os.path.join(data_dir, "Grass")
            
            os.makedirs(grass_dir, exist_ok=True)
            
            # Copy LOD files to Grass directory
            copied_files = 0
            for source_file in lod_files:
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
            
            # Create LOD-specific metadata files
            self._create_lod_metadata_files(mod_root, source_season_name, copied_files)
            
            self.logger.info(f"📁 Created LOD mod structure with {copied_files} files")
            return mod_root
            
        except Exception as e:
            self.logger.error(f"💥 Error creating LOD mod structure: {e}")
            return None
    
    def _create_lod_metadata_files(self, mod_root: str, source_season_name: str, file_count: int) -> None:
        """Create metadata files for the LOD grass mod"""
        try:
            # Create README.txt with LOD-specific instructions
            readme_path = os.path.join(mod_root, "README.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_lod_readme_content(source_season_name, file_count))
            
            # Create meta.ini for Mod Organizer 2
            meta_path = os.path.join(mod_root, "meta.ini")
            with open(meta_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_lod_meta_ini_content(source_season_name))
            
            self.logger.debug(f"📝 Created LOD metadata files")
            
        except Exception as e:
            self.logger.warning(f"Failed to create LOD metadata files: {e}")
    
    def _generate_lod_readme_content(self, source_season_name: str, file_count: int) -> str:
        """Generate README.txt content for LOD grass mod"""
        return f"""Grass Cache - Default (LOD Generation)
{'=' * 50}

Generated by NGIO Automation Suite
Source Season: {source_season_name}
Creation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

⚠️  IMPORTANT: This mod is ONLY for DynDOLOD LOD generation!

DESCRIPTION:
This mod contains grass cache files WITHOUT seasonal postfixes.
These files are required when generating grass LOD with DynDOLOD.

CONTENTS:
- {file_count} grass cache files (.cgid - no seasonal suffix)

WHEN TO USE THIS MOD:
✅ Enable ONLY when running DynDOLOD for grass LOD generation
❌ Keep DISABLED during normal gameplay

HOW TO USE:
1. Install this mod in your mod manager
2. Keep it DISABLED by default
3. When you want to generate grass LOD with DynDOLOD:
   a. Enable this mod (Grass Cache - Default)
   b. Disable your seasonal grass cache mods temporarily
   c. Run DynDOLOD with grass LOD options
   d. After DynDOLOD completes, DISABLE this mod again
   e. Re-enable your seasonal grass cache mods
4. Your grass LOD is now generated!

WHY IS THIS NEEDED:
DynDOLOD requires grass cache files without seasonal extensions
to properly generate grass LOD. Seasonal files (.WIN.cgid, .SPR.cgid,
etc.) are not recognized by DynDOLOD's grass LOD system.

INSTALLATION:
- Mod Organizer 2: Install as a mod, keep disabled by default
- Vortex: Install as a mod, set to disabled

SOURCE INFORMATION:
This LOD grass cache was generated from: {source_season_name} season
The grass density and settings match your {source_season_name} grass cache.

CREDITS:
- NGIO Development Team: Original grass cache system
- DynDOLOD: LOD generation system
- NGIO Automation Suite: Automated generation

Generated by NGIO Automation Suite
https://github.com/ReidenXerx/ngio-automation-suite
"""
    
    def _generate_lod_meta_ini_content(self, source_season_name: str) -> str:
        """Generate meta.ini content for LOD grass MO2"""
        return f"""[General]
modid=0
version=1.0
newestVersion=1.0
category=23
installationFile=Generated by NGIO Automation Suite

[installedFiles]
size=1

[comments]
Grass Cache - Default (for DynDOLOD LOD generation)
Generated from: {source_season_name} season
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
NOTE: Enable ONLY when generating grass LOD with DynDOLOD!
"""
    
    def _create_lod_zip_archive(self, mod_directory: str, archive_path: str, 
                                 source_season_name: str, file_count: int) -> Optional[ArchiveInfo]:
        """
        Create the final LOD zip archive
        
        Args:
            mod_directory: Directory containing the mod structure
            archive_path: Path for the output archive
            source_season_name: Season used as source
            file_count: Number of grass files
            
        Returns:
            ArchiveInfo if successful, None if failed
        """
        try:
            start_time = time.time()
            actual_file_count = 0
            
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
                        actual_file_count += 1
            
            # Get archive size
            archive_size_mb = os.path.getsize(archive_path) / (1024 * 1024)
            creation_time = time.time() - start_time
            
            # Validate archive
            if not self._validate_archive(archive_path):
                self.logger.error(f"❌ LOD archive validation failed: {archive_path}")
                return None
            
            # Generate checksum for integrity verification
            checksum = self._generate_checksum(archive_path)
            if checksum:
                self._save_checksum_file(archive_path, checksum)
            
            return ArchiveInfo(
                season_name=f"Default (LOD - from {source_season_name})",
                archive_path=archive_path,
                file_count=actual_file_count,
                archive_size_mb=archive_size_mb,
                creation_time=creation_time,
                sha256_checksum=checksum
            )
            
        except Exception as e:
            self.logger.error(f"💥 Error creating LOD zip archive: {e}")
            return None

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
