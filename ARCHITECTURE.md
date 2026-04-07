# Scraper Flow Diagram & Architecture

## Main Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START SCRAPER                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         Setup Undetected Chrome Browser                      │
│   (Bypasses bot detection, maintains user-agent)             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│        Open https://agnthos.se/ in Browser                   │
│                                                               │
│    ⚠️  USER ACTION REQUIRED:                                 │
│    • Look at browser window                                  │
│    • Accept cookies (click button if visible)                │
│    • Press ENTER in terminal to continue                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │   PHASE 1: Extract Main Categories   │
        │                                      │
        │  Parse HTML mega menu               │
        │  Find all category links            │
        │  Store in links_progress.json       │
        └─────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │   PHASE 2: Scrape Each Category      │
        │                                      │
        │  For each category {                │
        │    Fetch category page              │
        │    Extract subcategories            │
        │    Download subcategory images      │
        │    For each subcategory {           │
        │      Fetch subcategory page         │
        │      Extract products               │
        │      For each product {             │
        │        Fetch product page           │
        │        Extract details              │
        │        Download product image       │
        │        Save all data                │
        │      }                              │
        │    }                                │
        │  }                                  │
        └─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│   Save Final Data to JSON Files                              │
│   • products.json (complete hierarchy)                       │
│   • links_progress.json (checkpoints)                        │
│   • images/ (all downloaded images)                          │
│   • logs/scraper.log (detailed log)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   SCRAPING COMPLETE ✓                        │
│                                                               │
│  Ready to use products.json with your website                │
└─────────────────────────────────────────────────────────────┘
```

## Data Structure Hierarchy

```
products.json
│
├── metadata
│   ├── website: "https://agnthos.se"
│   ├── total_categories: 20
│   ├── total_products: 2500
│   ├── last_updated: "2026-04-04T10:30:00"
│   └── scraping_status: "completed"
│
└── categories[] (main product categories)
    │
    ├── [0] Surgical instruments
    │   ├── id: "9"
    │   ├── name: "Surgical instruments"
    │   ├── url: "https://agnthos.se/9-surgical-instruments"
    │   ├── description: "..."
    │   │
    │   └── subcategories[] (sub-categories)
    │       │
    │       ├── [0] Stille Instruments
    │       │   ├── id: "145"
    │       │   ├── name: "Stille Instruments"
    │       │   ├── url: "https://agnthos.se/145-stille-instruments"
    │       │   ├── image_url: "https://..."
    │       │   │
    │       │   └── products[] (individual products)
    │       │       │
    │       │       ├── [0] Iris Scissors
    │       │       │   ├── id: "271"
    │       │       │   ├── name: "Iris Scissors"
    │       │       │   ├── url: "https://agnthos.se/271-iris-scissors"
    │       │       │   ├── subcategory: "Iris Scissors"
    │       │       │   ├── short_description: "..."
    │       │       │   ├── long_description: "..."
    │       │       │   ├── image_url: "https://..."
    │       │       │   ├── image_local_path: "images/abc123.jpg"
    │       │       │   │
    │       │       │   └── specifications[] (product variants)
    │       │       │       │
    │       │       │       ├── [0]
    │       │       │       │   ├── article_number: "101-8001"
    │       │       │       │   ├── description: "STILLE, Delicate Eye Scissors..."
    │       │       │       │   └── price: "Contact for price"
    │       │       │       │
    │       │       │       └── [1]
    │       │       │           ├── article_number: "101-8003"
    │       │       │           ├── description: "STILLE, Delicate Eye Scissors..."
    │       │       │           └── price: "Contact for price"
    │       │       │
    │       │       └── [1] Scissors
    │       │           ├── id: "272"
    │       │           ├── name: "Scissors"
    │       │           └── ... (similar structure)
    │       │
    │       └── [1] Scissors
    │           └── ... (similar structure)
    │
    ├── [1] Neuroscience
    │   └── ... (similar structure)
    │
    └── [2] Pumps and infusion
        └── ... (similar structure)
```

## Progress Tracking (Resume Feature)

```
links_progress.json
│
├── metadata
│   ├── created_at: "2026-04-04T10:00:00"
│   ├── last_scraped_at: "2026-04-04T11:30:00"
│   ├── total_links_found: 5200
│   ├── total_links_scraped: 2800
│   └── status: "in_progress"
│
├── categories[] (tracks which categories are done)
│   │
│   ├── [0]
│   │   ├── id: "9"
│   │   ├── name: "Surgical instruments"
│   │   ├── url: "https://agnthos.se/9-surgical-instruments"
│   │   ├── scraped: true  ✓ COMPLETE
│   │   │
│   │   └── subcategories[]
│   │       │
│   │       ├── [0]
│   │       │   ├── id: "145"
│   │       │   ├── name: "Stille Instruments"
│   │       │   ├── url: "https://agnthos.se/145-stille-instruments"
│   │       │   ├── scraped: true  ✓ COMPLETE
│   │       │   │
│   │       │   └── products[]
│   │       │       └── [0]
│   │       │           ├── id: "271"
│   │       │           ├── name: "Iris Scissors"
│   │       │           ├── url: "https://agnthos.se/271-iris-scissors"
│   │       │           └── scraped: true  ✓ COMPLETE
│   │       │
│   │       └── [1]
│   │           ├── id: "146"
│   │           ├── name: "Scissors"
│   │           ├── scraped: false  ✗ PENDING
│   │           └── ...
│   │
│   └── [1] PENDING...
│
└── failed_links[]
    └── [0]
        ├── url: "https://agnthos.se/broken-link"
        ├── reason: "Timeout"
        └── timestamp: "2026-04-04T10:45:00"
```

## File Organization

```
agnthos_scraper/
│
├── 📄 scraper.py              ← Main script - RUN THIS
│
├── 📄 config.py               ← Configuration settings
│
├── 📄 analyze_data.py         ← Data analysis tool
│
├── 📄 requirements.txt        ← Python dependencies
│
├── 📁 src/                    ← Source code modules
│   ├── __init__.py
│   ├── json_manager.py        ← Database operations
│   ├── parser.py              ← HTML parsing
│   └── image_downloader.py    ← Image handling
│
├── 📁 data/                   ← Output data
│   ├── products.json          ← Main product database (YOUR DATA!)
│   ├── links_progress.json    ← Checkpoint file
│   └── products_export.csv    ← (optional export)
│
├── 📁 images/                 ← Downloaded images
│   ├── abc123def456.jpg
│   ├── def789ghi012.png
│   └── ...
│
├── 📁 logs/                   ← Execution logs
│   └── scraper.log
│
├── 📄 README.md               ← Full documentation
├── 📄 QUICKSTART.md           ← Quick start guide
├── 📄 DEBUGGING.md            ← Troubleshooting
└── 📄 .gitignore              ← Git ignore rules
```

## Class Diagram

```
┌──────────────────────────────────┐
│      AgnthosScraper              │
├──────────────────────────────────┤
│ - driver: Selenium Driver        │
│ - wait: WebDriverWait            │
│ - products_manager               │
│ - progress_manager               │
│ - image_downloader               │
├──────────────────────────────────┤
│ + setup_browser()                │
│ + handle_cookies()               │
│ + get_page_html(url)             │
│ + scrape_main_categories()       │
│ + scrape_category(cat)           │
│ + scrape_subcategory(subcat)     │
│ + scrape_product(product)        │
│ + run()                          │
└──────────────────────────────────┘
         │     │     │
         │     │     └──────────────┐
         │     │                    ▼
         │     │         ┌──────────────────────┐
         │     │         │  ImageDownloader     │
         │     │         ├──────────────────────┤
         │     │         │ - images_dir         │
         │     │         ├──────────────────────┤
         │     │         │ + download_image()   │
         │     │         │ + download_batch()   │
         │     │         └──────────────────────┘
         │     │
         │     └──────────────────────────┐
         │                                ▼
         │                  ┌──────────────────────┐
         │                  │   ProductsManager    │
         │                  ├──────────────────────┤
         │                  │ - filepath           │
         │                  ├──────────────────────┤
         │                  │ + load()             │
         │                  │ + save()             │
         │                  │ + add_category()     │
         │                  │ + add_product()      │
         │                  └──────────────────────┘
         │
         └──────────────────────────────┐
                                        ▼
                          ┌──────────────────────┐
                          │  Parser Classes      │
                          ├──────────────────────┤
                          │CategoryParser        │
                          │SubcategoryParser     │
                          │ProductParser         │
                          │BreadcrumbParser      │
                          ├──────────────────────┤
                          │+ extract_*()         │
                          └──────────────────────┘
```

## Execution Timeline Example

```
Time    Action                              Status
────────────────────────────────────────────────────
00:00   Start scraper                       Starting...
00:05   Browser opens                       Browser ready
00:10   Wait for cookies (user presses)     Awaiting user input
00:15   User presses ENTER                  Cookies accepted ✓
00:20   Extract main categories (20)        Found 20 categories
00:30   Start category 1: Surgical          Processing...
00:40   Extract subcategories (8)           Found 8 subcategories
01:00   Process subcategory 1               Fetching...
01:15   Found 50 products                   Processing 50 products
02:00   Download 50 product details         Downloading...
02:30   Download 50 product images          Downloading...
03:00   Save to products.json               Category 1 complete ✓
03:05   Start category 2: Neuroscience      Processing...
...     (repeats for all categories)
40:00   All categories complete             ✓ Done!
40:10   Close browser                       Browser closed
40:15   Scraping complete                   FINISHED ✓
```

## Resume Flow (When Interrupted)

```
User presses Ctrl+C at 40:00
│
├─ Progress saved to links_progress.json
│  • 10 categories marked as complete
│  • 10 categories marked as pending
│
User runs: python scraper.py --resume
│
├─ Load links_progress.json
│
├─ Check pending categories (10 remaining)
│
├─ Skip already scraped items
│
├─ Resume from where it left off ✓
│
└─ Continue until complete
```

## Data Flow Diagram

```
agnthos.se Website
        │
        ▼
   Browser (Selenium)
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
    HTML Content    JavaScript Content
        │                 │
        └─────────────────┘
                │
                ▼
        BeautifulSoup Parser
                │
        ┌───────┼───────┐
        │       │       │
        ▼       ▼       ▼
   Categories Subcategories Products
        │       │       │
        ├───────┴───────┤
        │               │
        ▼               ▼
   Product Data    Image URLs
        │               │
        ├───────┬───────┤
        │       │       │
        ▼       ▼       ▼
    JSON     Images   Logs
   Storage   Storage  Files
        │       │       │
        └───────┴───────┘
                │
                ▼
          Your Website
             (Display)
```

This architecture ensures:
✓ Clean separation of concerns
✓ Easy to debug each component
✓ Checkpoint system for resuming
✓ Organized data output
