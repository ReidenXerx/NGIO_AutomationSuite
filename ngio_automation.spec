# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for NGIO Automation Suite
# Creates a standalone executable with embedded Python interpreter

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'src'))

block_cipher = None

a = Analysis(
    ['ngio_automation_runner.py'],
    pathex=[
        os.path.dirname(os.path.abspath(SPEC)),
        os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'src')
    ],
    binaries=[],
    datas=[
        # Include documentation files
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        # Explicitly include all our modules
        'core.automation_suite',
        'core.game_manager', 
        'core.config_manager',
        'core.file_processor',
        'core.archive_creator',
        'core.progress_monitor',
        'utils.logger',
        'utils.config_cache',
        'utils.skyrim_detector',
        # System modules that might be missed
        'psutil',
        'colorama',
        'json',
        'configparser',
        'zipfile',
        'threading',
        'subprocess',
        'signal',
        'atexit',
        'time',
        'os',
        'sys',
        'pathlib',
        'shutil',
        'glob',
        'enum',
        'dataclasses',
        'typing',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
        'django',
        'flask',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NGIO_Automation_Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable (optional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window for user interaction
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Could add an icon file here
    version_file=None,  # Could add version info here
)

# Optional: Create a directory distribution instead of single file
# This can be faster to start and easier to debug
# Uncomment the following lines to create directory distribution:

# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='NGIO_Automation_Suite'
# )
