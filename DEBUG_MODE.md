# Debug Mode Guide

## Enabling Debug Mode

To enable debug mode, edit the `.env` file and change:

```env
DEBUG=False
```

to:

```env
DEBUG=True
```

## How It Works

When `DEBUG=True`:
- The scraper will **pause after loading each page**
- You can inspect the HTML in the browser or terminal
- Press **ENTER** in the terminal to continue scraping

When `DEBUG=False` (default):
- The scraper runs normally without pausing
- Pages are loaded and scraped continuously

## Example .env Configuration

```env
# Debug mode - set to True to pause after each page load for inspection
DEBUG=True

# Website settings
BASE_URL=https://agnthos.se/
HEADLESS=False

# Timing settings (in seconds)
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=30
SCROLL_PAUSE=2
IMAGE_TIMEOUT=10
```

## Running the Scraper

```bash
# Normal mode (DEBUG=False)
python scraper.py

# Debug mode (DEBUG=True in .env)
python scraper.py
```

During debug mode you will see:
```
[DEBUG] Page loaded: https://agnthos.se/9-surgical-instruments
[DEBUG] Inspect the page in the browser if needed.
[DEBUG] Press ENTER to continue scraping...
```

Press ENTER to proceed to the next page.
