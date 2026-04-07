# Agnthos Website Scraper

A comprehensive web scraping solution for agnthos.se using Selenium with undetected Chrome driver and BeautifulSoup for HTML parsing.

## Project Structure

```
agnthos_scraper/
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── scraper.py               # Main scraper script
├── src/
│   ├── __init__.py
│   ├── json_manager.py      # JSON file management with checkpoints
│   ├── parser.py            # BeautifulSoup HTML parsers
│   └── image_downloader.py  # Image download and storage
├── data/
│   ├── products.json        # Complete product data hierarchy
│   └── links_progress.json  # Scraping progress and checkpoints
├── images/                  # Downloaded product images
└── logs/
    └── scraper.log          # Detailed scraping logs
```

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to customize:

- **HEADLESS**: Set to `True` to run browser without GUI (default: `False`)
- **IMPLICIT_WAIT**: Time to wait for page elements (default: 10 seconds)
- **PAGE_LOAD_TIMEOUT**: Maximum page load time (default: 30 seconds)
- **SCROLL_PAUSE**: Pause between page actions (default: 2 seconds)
- **IMAGE_TIMEOUT**: Image download timeout (default: 10 seconds)

## Usage

### First Run (Fresh Scraping)

```bash
python scraper.py
```

The scraper will:
1. Launch browser window
2. Open https://agnthos.se/
3. **Wait for your manual action**: Accept cookies on the browser, then press ENTER in terminal
4. Automatically scrape all categories, subcategories, and products
5. Download all product images locally
6. Save progress to JSON files

### Resume Scraping

If the scraper is interrupted (network issue, computer shutdown, etc.), resume with:

```bash
python scraper.py --resume
```

This will:
- Read the checkpoint from `links_progress.json`
- Skip already scraped items
- Continue from where it left off

### Headless Mode

To run without browser GUI:

```bash
python scraper.py --headless
```

## Data Structure

### products.json

Complete hierarchical product data:

```json
{
  "metadata": {
    "website": "https://agnthos.se",
    "total_categories": 20,
    "total_products": 2500,
    "last_updated": "2026-04-04T10:30:00",
    "scraping_status": "in_progress"
  },
  "categories": [
    {
      "id": "9",
      "name": "Surgical instruments",
      "url": "https://agnthos.se/9-surgical-instruments",
      "description": "...",
      "subcategories": [
        {
          "id": "145",
          "name": "Stille Instruments",
          "url": "https://agnthos.se/145-stille-instruments",
          "image_url": "https://...",
          "image_alt": "Stille Instruments",
          "products": [
            {
              "id": "271",
              "name": "Iris Scissors",
              "url": "https://agnthos.se/271-iris-scissors",
              "subcategory": "Iris Scissors",
              "short_description": "Delicate eye scissors with sharp or blunt tips...",
              "long_description": "Complete detailed description...",
              "image_url": "https://...",
              "image_local_path": "images/abc123def456.jpg",
              "specifications": [
                {
                  "article_number": "101-8001",
                  "description": "STILLE, Delicate Eye Scissors Straight/Sharp, 9,5cm",
                  "price": "Contact for price"
                },
                {
                  "article_number": "101-8003",
                  "description": "STILLE, Delicate Eye Scissors Curved/Sharp, 9,5cm",
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

### links_progress.json

Progress tracking for checkpointing:

```json
{
  "metadata": {
    "created_at": "2026-04-04T10:00:00",
    "last_scraped_at": "2026-04-04T11:30:00",
    "total_links_found": 5200,
    "total_links_scraped": 2800,
    "status": "in_progress"
  },
  "categories": [
    {
      "id": "9",
      "name": "Surgical instruments",
      "url": "https://agnthos.se/9-surgical-instruments",
      "scraped": true,
      "subcategories": [
        {
          "id": "145",
          "name": "Stille Instruments",
          "url": "https://agnthos.se/145-stille-instruments",
          "scraped": true,
          "products": [
            {
              "id": "271",
              "name": "Iris Scissors",
              "url": "https://agnthos.se/271-iris-scissors",
              "scraped": true
            }
          ]
        }
      ]
    }
  ],
  "failed_links": [
    {
      "url": "https://agnthos.se/some-broken-link",
      "reason": "Timeout",
      "timestamp": "2026-04-04T10:45:00"
    }
  ],
  "pending_links": []
}
```

## Scraping Flow

```
1. Initialize browser with Selenium & undetected Chrome
   ↓
2. Open https://agnthos.se/ and wait for cookie acceptance
   ↓
3. Extract main categories from mega menu (Phase 1)
   ↓
4. For each category (Phase 2):
   a. Fetch category page
   b. Extract subcategories with images
   c. For each subcategory:
      i. Fetch subcategory page
      ii. Extract product listings
      iii. For each product:
           - Fetch product detail page
           - Extract specifications, descriptions, prices
           - Download product image
           - Save to products.json
   d. Mark as scraped in progress.json
   ↓
5. Save complete data to JSON files
6. Exit browser
```

## Key Features

✅ **Checkpoint System**: Resume from where you left off
✅ **Undetected Chrome**: Bypasses anti-bot detection
✅ **Cookie Handling**: Manual cookie acceptance with user prompt
✅ **Image Storage**: Automatic image download and local caching
✅ **Hierarchical Data**: Maintains complete category → subcategory → product structure
✅ **Error Tracking**: Logs failed links for debugging
✅ **Detailed Logging**: Both console and file-based logging
✅ **Timeout Handling**: Graceful handling of timeouts and connection errors

## Logging

Logs are saved to `logs/scraper.log` with detailed information:

- ✓ Successfully scraped items
- ✗ Errors and failures
- → Processing status
- ⚠ Warnings

Monitor logs during scraping:

```bash
# On Windows (PowerShell)
Get-Content -Path "logs/scraper.log" -Wait

# On Linux/Mac
tail -f logs/scraper.log
```

## Troubleshooting

### Issue: "Browser window doesn't open"
**Solution**: Set `HEADLESS = False` in config.py to see the browser. Headless mode hides the window.

### Issue: "Timeout waiting for elements"
**Solution**: Increase `IMPLICIT_WAIT` and `PAGE_LOAD_TIMEOUT` in config.py

### Issue: "Cookie dialog not disappearing"
**Solution**: The scraper waits for you to manually accept cookies. Check the browser window and click the cookie acceptance button, then press ENTER in terminal.

### Issue: "Images not downloading"
**Solution**: Check internet connection and verify `IMAGES_DIR` is writable

### Issue: "Resume not working"
**Solution**: Ensure `links_progress.json` exists in `data/` directory. Check logs for errors.

## Performance Tips

1. **Increase speed**: Reduce `SCROLL_PAUSE` and `IMAGE_TIMEOUT` (be careful with timeouts)
2. **Headless mode**: Enable `HEADLESS = True` for faster execution
3. **Skip images**: Comment out image download in `scraper.py` if not needed
4. **Parallel processing**: Currently sequential - can be optimized for parallel category scraping

## Output Files

- **products.json**: ~5-10 MB (depending on product count)
- **links_progress.json**: ~1-2 MB
- **Images directory**: ~500 MB - 2 GB (depending on image count and quality)
- **Logs**: ~10-50 MB per complete run

## Integration with Your Website

Use the generated `products.json` directly in your website:

```javascript
// Load products from JSON
fetch('data/products.json')
  .then(response => response.json())
  .then(data => {
    console.log(data.categories); // Array of categories
    // Build UI from this structure
  });
```

## Support & Debugging

For issues:
1. Check `logs/scraper.log` for detailed error messages
2. Check `data/links_progress.json` for scraping status
3. Verify all dependencies installed: `pip install -r requirements.txt`
4. Ensure Chrome browser is updated to latest version

## License

This project is for educational and authorized scraping purposes only. Ensure you have permission to scrape the target website.
