#!/usr/bin/env python3
"""
NGIO Automation Suite - Setup Script
Backward compatibility setup.py for older Python environments
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys

# Add src to path to import version
sys.path.insert(0, str(Path(__file__).parent / "src"))
from __version__ import __version__, __title__, __description__, __author__, __license__

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Fully automated grass cache generation suite for Skyrim SE with seasonal support"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract just the package name and version requirement
                if ">=" in line:
                    requirements.append(line.split("#")[0].strip())

setup(
    name="ngio-automation-suite",
    version=__version__,
    author=__author__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ngio-automation-suite",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ngio-automation-suite/issues",
        "Documentation": "https://github.com/yourusername/ngio-automation-suite/blob/main/docs/",
        "Source Code": "https://github.com/yourusername/ngio-automation-suite",
        "Nexus Mods": "https://nexusmods.com/skyrimspecialedition/mods/your-mod-id",
    },
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include additional files
    package_data={
        "": ["*.txt", "*.md", "*.ini", "*.json"],
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=requirements,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points for command-line usage
    entry_points={
        "console_scripts": [
            "ngio-automation=ngio_automation_runner:main",
        ],
    },
    
    # PyPI classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities", 
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ],
    
    keywords="skyrim modding grass cache ngio automation seasonal game modding",
    
    # Additional metadata
    license=__license__,
    platforms=["Windows"],
    
    # Development dependencies (optional)
    extras_require={
        "dev": [
            "build>=0.8.0",
            "wheel>=0.37.0", 
            "twine>=4.0.0",
        ],
    },
)
