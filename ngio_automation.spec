# -*- mode: python ; coding: utf-8 -*-
"""
NGIO Automation Suite - PyInstaller Specification
Builds a single-file executable with all dependencies embedded
"""

import sys
from pathlib import Path

# Project paths
project_root = Path(SPECPATH)
src_dir = project_root / 'src'

# Import version info
sys.path.insert(0, str(src_dir))
from __version__ import __version__, __title__

# Analysis: Collect all Python files and dependencies
a = Analysis(
    ['ngio_automation_runner.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include all source modules
        (str(src_dir / 'core'), 'src/core'),
        (str(src_dir / 'utils'), 'src/utils'),
        (str(src_dir / '__version__.py'), 'src'),
        
        # Include documentation (users might need it)
        (str(project_root / 'docs'), 'docs'),
        
        # Include README and LICENSE
        (str(project_root / 'README.md'), '.'),
    ],
    hiddenimports=[
        # Explicit imports that PyInstaller might miss
        'psutil',
        'colorama',
        'colorlog',
        'yaml',
        'win10toast',
        'tqdm',
        'src.core.automation_suite',
        'src.core.game_manager',
        'src.core.config_manager',
        'src.core.file_processor',
        'src.core.progress_monitor',
        'src.core.archive_creator',
        'src.utils.logger',
        'src.utils.config_cache',
        'src.utils.config_loader',
        'src.utils.notifications',
        'src.utils.state_manager',
        'src.utils.system_validator',
        'src.utils.task_scheduler',
        'src.utils.grass_profiles',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'unittest',
        'test',
        # Note: distutils removed - causes conflicts with Python 3.12+ and PyInstaller hooks
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ: Create Python archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE: Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'NGIO_Automation_Suite_v{__version__}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression for smaller file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file if we create one
    version_file=None,  # TODO: Add version info resource
)

# Optional: Create COLLECT for directory-based distribution
# Uncomment if you want both single-file and directory versions
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='NGIO_Automation_Suite',
# )

