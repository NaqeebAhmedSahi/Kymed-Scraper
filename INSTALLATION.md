# Installation & Setup Guide

## Before You Start

### Requirements
- **Windows 10+**, **macOS 10.14+**, or **Linux** (Ubuntu 18.04+)
- **Python 3.8 or higher**
- **Google Chrome** (latest version)
- **3-5 GB disk space**
- **Internet connection** (stable)
- **Administrator/sudo access** (for some operations)

### Check Your Setup

```bash
# Check Python version
python --version
# Should show: Python 3.x.x (where x >= 8)

# Check if Chrome is installed
# Windows: Look in C:\Program Files\Google\Chrome
# macOS: Look in Applications folder
# Linux: Which google-chrome
```

---

## Installation Steps

### Step 1: Extract/Navigate to Project

```bash
# Navigate to the project folder
cd agnthos_scraper
```

### Step 2: Create Virtual Environment

Virtual environments isolate project dependencies from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 3: Install Dependencies

```bash
# Make sure virtual environment is activated (see Step 2)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This installs:
- `selenium` - Browser automation
- `undetected-chromedriver` - Stealth browser driver
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `Pillow` - Image processing

### Step 4: Verify Installation

```bash
python verify_setup.py
```

This checks:
- ✓ All files are present
- ✓ Python version is correct
- ✓ Chrome is installed
- ✓ All modules can be imported
- ✓ All dependencies are installed

**Expected output:**
```
================================================================================
VERIFICATION SUMMARY
================================================================================
  Project Structure: ✓ PASS
  System Environment: ✓ PASS
  Module Imports: ✓ PASS
  Dependencies: ✓ PASS

================================================================================

✓ All checks passed! Ready to start scraping.
```

If you see any failures, see **Troubleshooting** section below.

---

## Configuration (Optional)

Edit `config.py` to customize behavior:

```python
# Show/hide browser window during scraping
HEADLESS = False  # Set to True to hide browser

# Timeouts (in seconds)
IMPLICIT_WAIT = 10  # Wait for elements to appear
PAGE_LOAD_TIMEOUT = 30  # Wait for page to load
SCROLL_PAUSE = 2  # Pause between actions

# Image download settings
IMAGE_TIMEOUT = 10  # Image download timeout
REQUEST_TIMEOUT = 15  # HTTP request timeout
```

---

## First Run

### Quick Start

```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run the scraper
python scraper.py
```

### What Happens

1. **Browser opens** showing https://agnthos.se/
2. **You see a cookie banner** (usually at bottom)
3. **Accept cookies** by clicking the button on the website
4. **Press ENTER** in the terminal
5. **Scraper starts automatically**

### Example Output

```
================================================================================
AGNTHOS SCRAPER INITIALIZED
================================================================================

Setting up undetected Chrome browser...
Browser setup complete

================================================================================
COOKIE ACCEPTANCE REQUIRED
================================================================================
Opening website: https://agnthos.se

Page loaded. Waiting for user to accept cookies...
Press ENTER in the terminal after accepting cookies on the browser

>>> Press ENTER after accepting cookies: [YOU PRESS ENTER HERE]

Proceeding with scraping...

================================================================================
PHASE 1: SCRAPING MAIN CATEGORIES
================================================================================

Found 20 main categories
Added 20 categories to progress tracker

================================================================================
PHASE 2: SCRAPING ALL CATEGORIES AND PRODUCTS
================================================================================

[1/20] Processing category...
Scraping category: Surgical instruments (9)
  ...
```

---

## Troubleshooting Installation

### Issue: "Python not found" or "command not recognized"

**Windows:**
```bash
# Python might not be in PATH
# Try using py instead
py --version

# If that works, use py -m instead of python
py -m pip install -r requirements.txt
py scraper.py
```

**macOS/Linux:**
```bash
# Try python3
python3 --version
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Issue: "Module not found" or "pip: command not found"

**Windows:**
```bash
# Reinstall Python from python.org
# Make sure to check "Add Python to PATH" during installation

# Then run:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Install pip if missing
# macOS:
python3 -m ensurepip --upgrade

# Linux (Ubuntu):
sudo apt-get install python3-pip
```

### Issue: "Virtual environment not activating"

**Windows:**
```bash
# Try PowerShell instead of Command Prompt
# In PowerShell:
venv\Scripts\Activate.ps1

# If you get permission error, run PowerShell as Admin
# Then set execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
```bash
# Make script executable
chmod +x venv/bin/activate
source venv/bin/activate
```

### Issue: "Chrome not found" or WebDriver error

**Windows:**
```bash
# Check if Chrome is installed
dir "C:\Program Files\Google\Chrome\Application\"

# If not installed, download from:
# https://www.google.com/chrome/
```

**macOS:**
```bash
# Check if Chrome is installed
ls "/Applications/Google Chrome.app"

# If not installed, download from:
# https://www.google.com/chrome/
```

**Linux:**
```bash
# Install Chrome
sudo apt-get update
sudo apt-get install google-chrome-stable

# Or use Chromium (free alternative)
sudo apt-get install chromium-browser
```

### Issue: "Permission denied" errors

**Windows:**
- Run terminal/PowerShell as Administrator

**macOS/Linux:**
```bash
# Use sudo for installation if needed
sudo pip install -r requirements.txt

# Or fix permissions:
chmod -R 755 ./
```

### Issue: "ModuleNotFoundError" after installation

```bash
# Make sure virtual environment is activated first!
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Then check pip list
pip list

# Should show: selenium, undetected-chromedriver, beautifulsoup4, etc.

# If missing, reinstall:
pip install --upgrade -r requirements.txt
```

### Issue: "SSL certificate error"

```bash
# For pip install:
pip install --trusted-host pypi.python.org -r requirements.txt

# Or upgrade certifi:
pip install --upgrade certifi
pip install -r requirements.txt
```

---

## After Installation

### 1. Verify Everything Works

```bash
python verify_setup.py
```

Should see: ✓ All checks passed!

### 2. Read Documentation

- **Quick start?** → Read `QUICKSTART.md` (5 min)
- **Full details?** → Read `README.md` (15 min)
- **Architecture?** → Read `ARCHITECTURE.md` (10 min)

### 3. Run Scraper

```bash
python scraper.py
```

### 4. Monitor Progress

In another terminal:
```bash
# Windows PowerShell:
Get-Content -Path "logs/scraper.log" -Wait

# Linux/macOS:
tail -f logs/scraper.log
```

### 5. Analyze Results

```bash
# View summary
python analyze_data.py --summary

# View breakdown
python analyze_data.py --breakdown

# Export to CSV
python analyze_data.py --export-csv
```

---

## Deactivating Virtual Environment

When you're done (or want to use system Python):

```bash
# Windows/macOS/Linux:
deactivate
```

The `(venv)` will disappear from your terminal prompt.

---

## Updating/Reinstalling

If you encounter issues and need to start fresh:

```bash
# Remove virtual environment
# Windows:
rmdir venv /s /q

# macOS/Linux:
rm -rf venv

# Create new virtual environment
python -m venv venv

# Activate it
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
python verify_setup.py
```

---

## System-Specific Notes

### Windows 10/11

- **PowerShell vs Command Prompt**: PowerShell recommended
- **Virtual Environment**: Use `venv\Scripts\activate`
- **File Paths**: Use backslashes `\` or forward slashes `/` both work
- **Chrome Path**: Usually `C:\Program Files\Google\Chrome\Application\chrome.exe`

### macOS

- **Terminal**: Use Terminal.app or iTerm2
- **Virtual Environment**: Use `source venv/bin/activate`
- **File Paths**: Use forward slashes `/`
- **Chrome Path**: `/Applications/Google Chrome.app`
- **M1/M2 Macs**: Should work fine, but test Chrome first

### Linux (Ubuntu/Debian)

- **Virtual Environment**: `source venv/bin/activate`
- **Chrome**: May need to install with `apt-get`
- **Permissions**: May need `sudo` for some operations
- **Python**: Usually `python3` command

---

## Getting Help

If installation fails:

1. **Check verify_setup.py output**
   ```bash
   python verify_setup.py
   ```
   This tells you exactly what's wrong

2. **Check logs**
   ```bash
   # After scraper fails:
   type logs/scraper.log  # or tail -f on Linux/Mac
   ```

3. **Read DEBUGGING.md**
   - Common issues and solutions

4. **System check**
   ```bash
   python --version  # Python 3.8+?
   pip --version      # Pip installed?
   # Look for Chrome in Program Files
   ```

---

## Success Checklist

After installation, you should have:

- [ ] Python 3.8+ installed
- [ ] Chrome/Chromium installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` shows them)
- [ ] `verify_setup.py` passes all checks
- [ ] Can run `python scraper.py` without errors
- [ ] Browser opens when running scraper
- [ ] `logs/scraper.log` is being created

Once all checked, you're ready to scrape! 🚀

---

## Next: Running the Scraper

See **QUICKSTART.md** for instructions on:
1. Starting your first scrape
2. Accepting cookies
3. Monitoring progress
4. Using your data

Good luck! 🎉
