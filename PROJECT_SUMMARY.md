# Project Summary - Agnthos Website Scraper

## What You Have

A complete, production-ready web scraping solution for agnthos.se that:

✅ **Extracts Product Data** - Full hierarchical structure with all details
✅ **Handles Cookies** - Manual cookie acceptance with user prompt
✅ **Downloads Images** - Stores all product images locally
✅ **Checkpoint System** - Resume from interruptions
✅ **Clean JSON Output** - Organized, nested hierarchy ready for websites
✅ **Detailed Logging** - Track what's happening at every step
✅ **Error Handling** - Graceful failure with recovery options

---

## Quick Start (3 Steps)

### Step 1: Install
```bash
cd agnthos_scraper
pip install -r requirements.txt
```

### Step 2: Run
```bash
python scraper.py
# When browser opens:
# 1. Accept cookies on the webpage
# 2. Press ENTER in terminal
```

### Step 3: Use Your Data
```bash
# View products
python analyze_data.py --summary

# Export to CSV
python analyze_data.py --export-csv

# Use products.json in your website
```

---

## File Locations & What They Mean

| File | Size | Purpose |
|------|------|---------|
| `data/products.json` | 5-10 MB | **YOUR MAIN DATABASE** - All product data |
| `data/links_progress.json` | 1-2 MB | Checkpoint file - for resuming |
| `images/` folder | 500MB-2GB | All downloaded product images |
| `logs/scraper.log` | 10-50 MB | Detailed execution log |

---

## Data Structure You Get

```json
{
  "categories": [
    {
      "name": "Surgical instruments",
      "subcategories": [
        {
          "name": "Stille Instruments",
          "products": [
            {
              "name": "Iris Scissors",
              "description": "...",
              "image_local_path": "images/abc123.jpg",
              "specifications": [
                {
                  "article_number": "101-8001",
                  "description": "STILLE, Delicate Eye Scissors...",
                  "price": "Contact for price"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Perfect for displaying on your website!

---

## How Checkpoint/Resume Works

**Scenario**: You start scraping at 5:00 PM, but internet cuts off at 6:30 PM after 60% completion.

```
Normal run:  5:00 PM ──→ 6:30 PM (STOPS) ✗
Resume run:  6:30 PM ──→ 7:00 PM (COMPLETES) ✓
```

**How it works**:
1. Script saves progress to `links_progress.json` continuously
2. If interrupted, simply run: `python scraper.py --resume`
3. Automatically skips already-scraped items
4. Continues from where it left off

**No data loss!** ✓

---

## Project Structure Explained

```
agnthos_scraper/
│
├── scraper.py          ← THIS IS YOUR MAIN SCRIPT
│                         Run: python scraper.py
│
├── config.py           ← CUSTOMIZE HERE
│                         Change timeouts, headless mode, etc.
│
├── src/
│   ├── json_manager.py   ← Saves/loads your data
│   ├── parser.py         ← Extracts data from HTML
│   └── image_downloader.py ← Downloads images
│
├── data/               ← YOUR OUTPUT GOES HERE
│   ├── products.json    ← Use this in your website!
│   └── links_progress.json ← Checkpoint file
│
└── images/             ← Downloaded product images
```

---

## Key Features Explained

### 1. Undetected Chrome Driver
```python
# Why? Website might block bots
# Solution: Uses undetected Chrome that looks like real browser
```

### 2. Cookie Handling
```
1. Browser opens website
2. You see cookie banner
3. You click "Accept"
4. You press ENTER in terminal
5. Scraping starts
```

### 3. Hierarchical Data
```
Surgical instruments
  ├─ Stille Instruments
  │   ├─ Iris Scissors
  │   │   ├─ Product 1 (article 101-8001)
  │   │   ├─ Product 2 (article 101-8003)
  │   │   └─ ...
  │   ├─ Scissors
  │   └─ ...
  └─ ...
Neuroscience
  └─ ...
```

### 4. Image Management
```
Original URL:  https://agnthos.se/img/c/271-large_default.jpg?cb=...
Stored as:     images/abc123def456.jpg
Referenced in: "image_local_path": "images/abc123def456.jpg"
```

---

## Integration Examples

### Use in HTML/JavaScript

```html
<!-- Load products -->
<script>
  fetch('data/products.json')
    .then(r => r.json())
    .then(data => {
      // Build product listings
      data.categories.forEach(cat => {
        console.log(cat.name);
        cat.subcategories.forEach(sub => {
          sub.products.forEach(prod => {
            // Display product
            console.log(prod.name, prod.image_local_path);
          });
        });
      });
    });
</script>
```

### Use in Python

```python
import json

with open('data/products.json') as f:
    data = json.load(f)

for category in data['categories']:
    print(f"Category: {category['name']}")
    for subcat in category['subcategories']:
        print(f"  Subcategory: {subcat['name']}")
        for product in subcat['products']:
            print(f"    Product: {product['name']}")
```

### Display Images

```html
<!-- Use local image paths from JSON -->
<img src="images/abc123def456.jpg" alt="Product Name">

<!-- Works because images are stored in images/ directory -->
```

---

## Common Commands

```bash
# First time run
python scraper.py

# Resume after interruption
python scraper.py --resume

# Run in headless mode (no browser window)
python scraper.py --headless

# View scraping summary
python analyze_data.py --summary

# View detailed breakdown
python analyze_data.py --breakdown

# Export to CSV
python analyze_data.py --export-csv

# View real-time logs (Windows PowerShell)
Get-Content -Path "logs/scraper.log" -Wait

# View real-time logs (Linux/Mac)
tail -f logs/scraper.log
```

---

## Troubleshooting

### Most Common Issues

1. **"Browser doesn't open"**
   - Set `HEADLESS = False` in config.py
   - Or run: `python scraper.py`

2. **"Stuck on cookie acceptance"**
   - Look at browser window
   - Click cookie acceptance button
   - Press ENTER in terminal

3. **"Timeout errors"**
   - Increase timeouts in config.py:
   ```python
   IMPLICIT_WAIT = 15  # was 10
   PAGE_LOAD_TIMEOUT = 45  # was 30
   ```

4. **"Resume not working"**
   - Check `data/links_progress.json` exists
   - Use flag: `python scraper.py --resume`
   - Check `logs/scraper.log` for errors

---

## Performance

**Expected Times**:
- First run (full scrape): 30-60 minutes
- Resume: 5-20 minutes (varies by what's left)
- Analysis: 1-5 seconds

**Data Size**:
- products.json: 5-10 MB
- Images folder: 500 MB - 2 GB
- Total: ~2-3 GB for complete website

---

## What Gets Scraped

✓ **Categories** - All main product categories
✓ **Subcategories** - Sub-divisions within categories
✓ **Products** - Individual product listings
✓ **Descriptions** - Short and long descriptions
✓ **Images** - Product images (stored locally)
✓ **Specifications** - Article numbers, pricing info
✓ **Links** - Direct URLs to each item
✓ **Metadata** - Last updated timestamp, status

✗ **What we DON'T scrape**:
- Customer reviews (if any)
- Real-time pricing (some sites hide it)
- User-specific data
- Dynamic content requiring login

---

## Next Steps After Scraping

1. ✅ Run scraper
   ```bash
   python scraper.py
   ```

2. ✅ Verify data
   ```bash
   python analyze_data.py --summary
   ```

3. ✅ Review products.json structure
   ```bash
   python -m json.tool data/products.json | head -100
   ```

4. ✅ Integrate with your website
   - Copy `data/products.json` to your web project
   - Copy `images/` folder to your web project
   - Load and display using JavaScript/Python

5. ✅ Customize display
   - Add filters by category
   - Add search functionality
   - Style products as needed

---

## Tips & Tricks

### Speed Up Scraping
```python
# In config.py:
HEADLESS = True  # Don't show browser window
SCROLL_PAUSE = 1  # Reduce pause between actions (careful!)
```

### Skip Images (if not needed)
```python
# In scraper.py, comment out:
# local_image_path = self.image_downloader.download_image(...)
```

### Analyze Partially Scraped Data
```bash
# Even if scraping is interrupted, analyze what you have:
python analyze_data.py --summary
```

### Export as CSV for Excel
```bash
python analyze_data.py --export-csv
# Creates: data/products_export.csv
# Open in Excel to view
```

---

## Support Resources

- **Quick Start**: Read `QUICKSTART.md`
- **Full Docs**: Read `README.md`
- **Debugging**: Read `DEBUGGING.md`
- **Architecture**: Read `ARCHITECTURE.md`
- **Logs**: Check `logs/scraper.log` for detailed info

---

## System Requirements

- **Python**: 3.8 or higher
- **Chrome**: Latest version installed
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 3-5GB free space (for images)
- **Internet**: Stable connection required

---

## You're All Set! 🎉

Everything is ready to go. Just run:

```bash
python scraper.py
```

And follow the on-screen instructions. Good luck!

For questions or issues, check the documentation files included in the project.
