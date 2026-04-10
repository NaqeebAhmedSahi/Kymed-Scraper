"""
Verification Script - Check if everything is set up correctly
"""
import sys
from pathlib import Path


def check_structure():
    """Verify project structure is complete"""
    print("\n" + "=" * 80)
    print("AGNTHOS SCRAPER - PROJECT VERIFICATION")
    print("=" * 80 + "\n")
    
    base_dir = Path(__file__).parent
    
    required_files = {
        'Config Files': [
            'config.py',
            'requirements.txt',
        ],
        'Main Scripts': [
            'scraper.py',
            'analyze_data.py',
        ],
        'Source Code': [
            'src/__init__.py',
            'src/json_manager.py',
            'src/parser.py',
            'src/image_downloader.py',
        ],
        'Documentation': [
            'README.md',
            'QUICKSTART.md',
            'DEBUGGING.md',
            'ARCHITECTURE.md',
            'PROJECT_SUMMARY.md',
        ],
    }
    
    required_dirs = [
        'data',
        'images',
        'logs',
        'src',
    ]
    
    print("📁 Checking Directory Structure...")
    print("-" * 80)
    
    all_ok = True
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ - MISSING!")
            all_ok = False
    
    print("\n📄 Checking Files...")
    print("-" * 80)
    
    # Check files
    for category, files in required_files.items():
        print(f"\n  {category}:")
        for filename in files:
            filepath = base_dir / filename
            if filepath.exists() and filepath.is_file():
                size = filepath.stat().st_size
                if size > 0:
                    print(f"    ✓ {filename} ({size:,} bytes)")
                else:
                    print(f"    ⚠ {filename} (empty file!)")
                    all_ok = False
            else:
                print(f"    ✗ {filename} - MISSING!")
                all_ok = False
    
    return all_ok


def check_dependencies():
    """Check if required packages are installed"""
    print("\n\n🔧 Checking Python Dependencies...")
    print("-" * 80)
    
    required_packages = {
        'selenium': 'selenium',
        'undetected-chromedriver': 'undetected_chromedriver',
        'beautifulsoup4': 'bs4',
        'requests': 'requests',
        'Pillow': 'PIL',
    }
    
    all_ok = True
    
    for package, module_name in required_packages.items():
        try:
            module = __import__(module_name)
            print(f"  ✓ {package} (installed)")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED!")
            print(f"     Run: pip install {package}")
            all_ok = False
    
    return all_ok


def check_environment():
    """Check system environment"""
    print("\n\n💻 Checking System Environment...")
    print("-" * 80)
    
    import platform
    
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.architecture()[0]}")
    
    # Check if Python version is 3.8+
    version_ok = sys.version_info >= (3, 8)
    if version_ok:
        print(f"  ✓ Python version OK")
    else:
        print(f"  ✗ Python 3.8+ required!")
        return False
    
    # Check for Chrome/Chromium
    import subprocess
    
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    
    chrome_found = False
    for path in chrome_paths:
        try:
            if Path(path).exists():
                print(f"  ✓ Chrome/Chromium found: {path}")
                chrome_found = True
                break
        except:
            pass
    
    if not chrome_found:
        print(f"  ⚠ Chrome/Chromium not found (will try to auto-download)")
    
    return True


def test_imports():
    """Test if all modules can be imported"""
    print("\n\n📚 Testing Module Imports...")
    print("-" * 80)
    
    base_dir = Path(__file__).parent
    sys.path.insert(0, str(base_dir))
    
    modules = {
        'config': 'Configuration module',
        'src.json_manager': 'JSON Manager',
        'src.parser': 'HTML Parser',
        'src.image_downloader': 'Image Downloader',
    }
    
    all_ok = True
    
    for module_name, description in modules.items():
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}: {description}")
        except Exception as e:
            print(f"  ✗ {module_name}: {description}")
            print(f"     Error: {str(e)}")
            all_ok = False
    
    return all_ok


def main():
    """Run all checks"""
    print("\n")
    
    checks = [
        ("Project Structure", check_structure()),
        ("System Environment", check_environment()),
        ("Module Imports", test_imports()),
        ("Dependencies", check_dependencies()),
    ]
    
    print("\n\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("\n✓ All checks passed! Ready to start scraping.\n")
        print("Next steps:")
        print("  1. Read QUICKSTART.md")
        print("  2. Run: python scraper.py")
        print("  3. Accept cookies when browser opens")
        print("  4. Press ENTER in terminal to continue\n")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.\n")
        print("Troubleshooting:")
        print("  1. Run: pip install -r requirements.txt")
        print("  2. Ensure Chrome is installed")
        print("  3. Check Python version (3.8+ required)")
        print("  4. Read DEBUGGING.md for more help\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
