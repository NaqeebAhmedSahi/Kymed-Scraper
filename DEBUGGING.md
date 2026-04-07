# Debugging & Troubleshooting Guide

## Common Issues & Solutions

### 1. Chrome Browser Not Opening

**Problem**: Script runs but browser window doesn't appear

**Solutions**:
```python
# In config.py, change HEADLESS setting
HEADLESS = False  # Show browser window
```

**Or run with flag**:
```bash
python scraper.py  # Browser will be visible
```

**Check Chrome Installation**:
```bash
# Windows - Check if Chrome is installed
wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version
```

---

### 2. "Cookie Acceptance" Stuck

**Problem**: Script says "Waiting for cookie acceptance" but nothing happens

**Checklist**:
1. ✅ Is the browser window visible? (Check HEADLESS = False)
2. ✅ Look for cookie banner (usually at bottom of page)
3. ✅ Click "Accept" or similar button on cookie banner
4. ✅ After clicking, press ENTER in terminal

**Example**:
```
>>> Press ENTER after accepting cookies: [CLICK "ACCEPT" BUTTON ON BROWSER FIRST]
```

**If still stuck after 30 seconds**:
```bash
# Cancel with Ctrl+C and check logs
python scraper.py
# Press Ctrl+C
# Then check logs/scraper.log
```

---

### 3. Timeout Errors

**Problem**: `TimeoutException` or "Timeout waiting for page to load"

**Solution - Increase timeouts in config.py**:
```python
# Increase these values
IMPLICIT_WAIT = 15  # was 10 seconds
PAGE_LOAD_TIMEOUT = 45  # was 30 seconds
SCROLL_PAUSE = 3  # was 2 seconds
REQUEST_TIMEOUT = 20  # was 15 seconds
```

**Check your internet connection**:
```bash
# Test connectivity
ping google.com

# Test website accessibility
ping agnthos.se
```

---

### 4. "No module named 'undetected_chromedriver'"

**Problem**: `ModuleNotFoundError: No module named 'undetected_chromedriver'`

**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# If still failing, install individually
pip install undetected-chromedriver==3.5.4
pip install selenium==4.15.2
pip install beautifulsoup4==4.12.2
```

---

### 5. "failed to create temp directory"

**Problem**: Chrome driver temp directory error

**Solution**:
```python
# In config.py, add more Chrome options
CHROME_OPTIONS = {
    "disable-blink-features": "AutomationControlled",
    "disable-gpu": True,
    "no-sandbox": True,
    "disable-dev-shm-usage": True,  # Add this
}
```

Or clean Chrome cache:
```bash
# Windows
rmdir %APPDATA%\Local\Google\Chrome\User Data\Default\Cache /s /q
```

---

### 6. Resume Not Working

**Problem**: Using `--resume` but it starts over

**Checklist**:
1. ✅ `data/links_progress.json` exists?
2. ✅ Using correct flag: `python scraper.py --resume`
3. ✅ Check logs for error messages

**Debug**:
```bash
# Check progress file exists
dir data\links_progress.json

# Check its content
python -m json.tool data\links_progress.json
```

---

### 7. Images Not Downloading

**Problem**: `images/` directory is empty or images failed

**Check**:
```bash
# Verify images directory exists
dir images\

# Check for errors in log
findstr /I "image" logs\scraper.log
```

**Solutions**:
1. Check internet connection
2. Increase image timeout in config.py:
   ```python
   IMAGE_TIMEOUT = 15  # was 10
   ```
3. Check if image URLs are valid:
   ```bash
   # Try downloading one manually
   curl -o test.jpg https://agnthos.se/img/c/271-large_default.jpg
   ```

---

### 8. "connection reset by peer" or "connection aborted"

**Problem**: Network connection drops during scraping

**Solution 1 - Use Resume**:
```bash
python scraper.py --resume
```

**Solution 2 - Slow Down Scraping**:
```python
# In config.py, increase pause times
SCROLL_PAUSE = 5  # was 2 seconds
```

**Solution 3 - Check Network**:
```bash
# Test connection stability
ping -t agnthos.se  # Keep running, watch for timeouts
```

---

### 9. JSON Files are Empty

**Problem**: `products.json` or `links_progress.json` are empty

**Check**:
```bash
# View file size
dir data\products.json

# View content (first 100 lines)
type data\products.json | more
```

**Likely Causes**:
1. Scraper didn't run completely
2. Data not saved yet
3. Script interrupted

**Solution**:
```bash
# Run again
python scraper.py --resume
```

---

### 10. "Permission Denied" on Images Directory

**Problem**: Cannot write to images directory

**Solution - Windows**:
```bash
# Run terminal as Administrator
# Then try again
python scraper.py
```

**Solution - Linux/Mac**:
```bash
# Fix permissions
chmod -R 755 images/
chmod -R 755 data/
```

---

## Checking Logs

### View Real-Time Logs

**Windows PowerShell**:
```bash
Get-Content -Path "logs/scraper.log" -Wait
```

**Windows Command Prompt**:
```bash
type logs\scraper.log
```

**Linux/Mac**:
```bash
tail -f logs/scraper.log
```

### Parse Log for Errors

**Find all errors**:
```bash
# Windows
findstr /I "error" logs\scraper.log

# Linux/Mac
grep -i "error" logs/scraper.log
```

**Find specific information**:
```bash
# Find all scraped products
grep "Added product" logs\scraper.log | wc -l

# Find failed links
grep "Failed link" logs\scraper.log
```

---

## Debugging with Print Statements

### Add Debug Output

Edit `scraper.py` to add debugging:

```python
# In scrape_product method, add:
logger.debug(f"Product URL: {prod_url}")
logger.debug(f"Product Name: {prod_name}")
logger.debug(f"Image URL: {product.get('image_url')}")
```

Then run with verbose logging:

```python
# Edit config.py
LOG_LEVEL = "DEBUG"  # was "INFO"
```

---

## Performance Monitoring

### Check Memory Usage

```bash
# Watch memory during scraping
# Windows Task Manager: Ctrl+Shift+Esc
# Look for Chrome and Python processes
```

### Speed Up Scraping

In `config.py`:
```python
SCROLL_PAUSE = 1  # Reduce from 2 (careful!)
HEADLESS = True  # Run without GUI - faster
PAGE_LOAD_TIMEOUT = 20  # Reduce from 30
```

---

## File Integrity Checks

### Validate JSON Files

```bash
# Check if JSON is valid
python -c "import json; json.load(open('data/products.json'))"

# Check progress file
python -c "import json; json.load(open('data/links_progress.json'))"
```

### Count Products

```bash
python analyze_data.py --summary
```

---

## Reset and Start Over

### If Everything is Broken

```bash
# Backup current data
mkdir data_backup
copy data\* data_backup\

# Delete current data
del data\products.json
del data\links_progress.json

# Delete images (optional)
rmdir images /s /q

# Start fresh
python scraper.py
```

---

## Environment Information

### Print Debug Info

```bash
# Python version
python --version

# Check installed packages
pip list | grep -E "selenium|undetected|beautifulsoup"

# Check Chrome version
wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version

# Check Python location
where python
```

### Create Debug Report

```bash
# Collect all debug info
echo "=== Python Info ===" > debug_report.txt
python --version >> debug_report.txt
echo "=== Installed Packages ===" >> debug_report.txt
pip list >> debug_report.txt
echo "=== Data Files ===" >> debug_report.txt
dir data >> debug_report.txt
echo "=== Recent Errors ===" >> debug_report.txt
findstr /I "ERROR" logs\scraper.log >> debug_report.txt
```

---

## Getting Help

When reporting issues, include:

1. ✅ Error message from terminal
2. ✅ Last 20 lines of `logs/scraper.log`
3. ✅ Python version: `python --version`
4. ✅ Output of: `pip list`
5. ✅ Size of `data/products.json`
6. ✅ Your OS (Windows/Linux/Mac)

Example:

```bash
python --version > debug_info.txt
pip list >> debug_info.txt
echo === Last 20 lines of log === >> debug_info.txt
type logs\scraper.log | tail -n 20 >> debug_info.txt
dir data >> debug_info.txt
```

Then share `debug_info.txt` when asking for help.

---

## Advanced Debugging

### Monitor Selenium Actions

Edit `scraper.py` to add:

```python
from selenium.webdriver.chrome.service import Service
service = Service(log_path="chromedriver.log")
# Pass to Chrome initialization
```

### Check HTML Parsing

```python
# Test parser directly
from src.parser import CategoryParser
html = open('test_page.html').read()
categories = CategoryParser.extract_category_links_from_menu(html, "https://agnthos.se")
print(categories)
```

### Test Image Download

```python
from src.image_downloader import ImageDownloader
from pathlib import Path

downloader = ImageDownloader(Path("images"))
result = downloader.download_image("https://agnthos.se/img/c/271-large_default.jpg")
print(f"Downloaded: {result}")
```

---

Good luck! Check the logs first before troubleshooting. 95% of issues are in the logs! 📋
