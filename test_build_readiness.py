#!/usr/bin/env python3
"""
Quick test to verify build system readiness
Run this before building to catch issues early
"""

import sys
import subprocess
from pathlib import Path

def test_python_version():
    """Check Python version."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def test_dependencies():
    """Check if all required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    dependencies = {
        'PyInstaller': 'PyInstaller',
        'psutil': 'psutil',
        'colorama': 'colorama',
        'colorlog': 'colorlog',
        'PyYAML': 'yaml',
        'winotify': 'winotify',
        'tqdm': 'tqdm',
    }
    
    all_ok = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """Verify project structure is intact."""
    print("\n🔍 Checking project structure...")
    
    root = Path(__file__).parent
    required = [
        'ngio_automation_runner.py',
        'ngio_automation.spec',
        'build_release.py',
        'requirements.txt',
        'src/__version__.py',
        'src/core',
        'src/utils',
        'docs',
    ]
    
    all_ok = True
    for item in required:
        path = root / item
        if path.exists():
            print(f"   ✅ {item}")
        else:
            print(f"   ❌ {item} - MISSING")
            all_ok = False
    
    return all_ok

def test_spec_file():
    """Verify .spec file is valid Python."""
    print("\n🔍 Checking PyInstaller spec file...")
    
    spec_file = Path(__file__).parent / 'ngio_automation.spec'
    if not spec_file.exists():
        print("   ❌ ngio_automation.spec not found")
        return False
    
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Basic syntax check
        compile(code, str(spec_file), 'exec')
        print("   ✅ Spec file syntax valid")
        return True
    except SyntaxError as e:
        print(f"   ❌ Spec file has syntax error: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  Could not validate spec file: {e}")
        return True  # Don't fail on this

def test_version_import():
    """Test if version can be imported."""
    print("\n🔍 Checking version info...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from __version__ import __version__, __title__
        print(f"   ✅ Version: {__version__}")
        print(f"   ✅ Title: {__title__}")
        return True
    except Exception as e:
        print(f"   ❌ Cannot import version: {e}")
        return False

def test_pyinstaller():
    """Test if PyInstaller is working."""
    print("\n🔍 Testing PyInstaller...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ PyInstaller {version}")
            return True
        else:
            print(f"   ❌ PyInstaller failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ PyInstaller check timed out")
        return False
    except Exception as e:
        print(f"   ❌ PyInstaller error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 80)
    print("NGIO Automation Suite - Build Readiness Test")
    print("=" * 80)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("Spec File", test_spec_file),
        ("Version Import", test_version_import),
        ("PyInstaller", test_pyinstaller),
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to build!")
        print("\nRun: build.bat")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before building.")
        print("\nTo fix missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

