# Quick Start Guide

## Step 1: Install Dependencies

```bash
cd agnthos_scraper
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Run the Scraper (First Time)

```bash
python scraper.py
```

This will:
1. Open a Chrome browser
2. Go to https://agnthos.se/
3. **IMPORTANT**: You will see a cookie acceptance prompt
   - Accept cookies in the browser
   - Then press ENTER in the terminal
4. Scraper will automatically fetch all data

⏱️ **Expected Duration**: 30-60 minutes depending on internet speed

## Step 3: Monitor Progress

Open another terminal and watch the logs:

```bash
# Windows PowerShell
Get-Content -Path "logs/scraper.log" -Wait
```

## Step 4: If Scraper Interrupts

Resume from checkpoint:

```bash
python scraper.py --resume
```

The scraper will skip already scraped items and continue!

## Step 5: View Your Data

### Option A: Analyze Statistics
```bash
python analyze_data.py --summary
python analyze_data.py --breakdown
python analyze_data.py --progress
```

### Option B: Export to CSV
```bash
python analyze_data.py --export-csv
```

## File Structure After Scraping

```
agnthos_scraper/
├── data/
│   ├── products.json          # Your complete product database
│   ├── links_progress.json    # Checkpoint for resuming
│   └── products_export.csv    # (if exported)
├── images/                    # All downloaded product images
│   ├── abc123def456.jpg
│   ├── def789ghi012.png
│   └── ...
└── logs/
    └── scraper.log            # Detailed execution log
```

## Integrating with Your Website

### Read products.json

```javascript
const fs = require('fs');

// Load products
const products = JSON.parse(fs.readFileSync('data/products.json', 'utf-8'));

// Access data
products.categories.forEach(category => {
  console.log(`Category: ${category.name}`);
  
  category.subcategories.forEach(subcat => {
    console.log(`  Subcategory: ${subcat.name}`);
    
    subcat.products.forEach(product => {
      console.log(`    Product: ${product.name}`);
      console.log(`    Image: ${product.image_local_path}`);
      console.log(`    Specs: ${product.specifications.length}`);
    });
  });
});
```

### Use Images

Images are stored locally in `images/` directory with paths like:
```
images/abc123def456.jpg
images/def789ghi012.png
```

Reference them in your website:
```html
<img src="images/abc123def456.jpg" alt="Product Name">
```

## Troubleshooting

### Browser doesn't open?
Edit `config.py` and change `HEADLESS = False`

### Timeout errors?
Increase in `config.py`:
```python
IMPLICIT_WAIT = 15  # was 10
PAGE_LOAD_TIMEOUT = 45  # was 30
```

### Cookies still not accepted?
- Check the browser window is visible
- Look for cookie banner and click "Accept"
- Then press ENTER in terminal

### Resume not working?
Make sure:
1. `data/links_progress.json` exists
2. You're using `--resume` flag
3. Check `logs/scraper.log` for errors

## Next Steps

1. ✅ Run scraper
2. ✅ Analyze data with `analyze_data.py`
3. ✅ Review `products.json` structure
4. ✅ Integrate with your website
5. ✅ Customize as needed

## File Descriptions

| File | Purpose |
|------|---------|
| `scraper.py` | Main scraper - run this |
| `config.py` | Configuration settings |
| `src/json_manager.py` | Database management |
| `src/parser.py` | HTML parsing |
| `src/image_downloader.py` | Image handling |
| `analyze_data.py` | Data analysis tool |

## Support

If you get stuck:
1. Check `logs/scraper.log` for detailed errors
2. Review README.md for detailed documentation
3. Check `data/links_progress.json` to see what was scraped

Good luck! 🎉
