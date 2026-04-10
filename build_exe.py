import os
import sys
import shutil
import subprocess

def build():
    print("🚀 Starting Agnthos Scraper Build Process...")
    
    # 1. Clean previous builds
    print("🧹 Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # 2. Define the main script and project name
    main_script = "scraper.py"
    app_name = "KymedScraper"
    
    # 3. Build the PyInstaller command
    # We use --onedir for better compatibility with browser automation
    # We include src/ as a data folder
    # We include config.py
    cmd = [
        "pyinstaller",
        "--name", app_name,
        "--onedir",
        "--clean",
        "--add-data", f"src{os.pathsep}src",
        "--add-data", f"config.py{os.pathsep}.",
        "--add-data", f".env{os.pathsep}.",
        "--collect-all", "undetected_chromedriver",
        "--hidden-import", "src.parser",
        "--hidden-import", "src.json_manager",
        "--hidden-import", "src.image_downloader",
        main_script
    ]
    
    print(f"📦 Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n\n✅ BUILD COMPLETED SUCCESSFULLY!")
        print(f"📍 Executable folder: dist/{app_name}")
        print("-" * 50)
        print("Note for Multi-PC support:")
        print("1. Your Chrome fallback logic in scraper.py will handle different versions.")
        print("2. Ensure Google Chrome is installed on the target PC.")
        print("-" * 50)
    else:
        print("\n\n❌ BUILD FAILED!")

if __name__ == "__main__":
    build()
