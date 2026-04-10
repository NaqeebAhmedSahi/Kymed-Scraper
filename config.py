"""
Configuration file for Agnthos Web Scraper
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys

# Base paths
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (PyInstaller)
    # The executable folder where data/images/logs should live
    BASE_DIR = Path(os.path.dirname(sys.executable))
    # The temporary folder where the bundled source code is extracted
    BUNDLE_DIR = Path(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
else:
    # Standard development environment
    BASE_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = BASE_DIR

DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"
LOGS_DIR = BASE_DIR / "logs"
SRC_DIR = BUNDLE_DIR / "src"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
SRC_DIR.mkdir(exist_ok=True)

# File paths
PRODUCTS_JSON = DATA_DIR / "products.json"
LINKS_PROGRESS_JSON = DATA_DIR / "links_progress.json"
LOG_FILE = LOGS_DIR / "scraper.log"

# Debug mode - set to True to pause after each page load
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Website settings
BASE_URL = os.getenv("BASE_URL", "https://agnthos.se/")
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))  # seconds
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))  # seconds

# Scraping settings
SCROLL_PAUSE = int(os.getenv("SCROLL_PAUSE", "2"))  # seconds between actions
IMAGE_TIMEOUT = int(os.getenv("IMAGE_TIMEOUT", "10"))  # seconds for downloading images
REQUEST_TIMEOUT = 15  # seconds

# Chrome driver settings
CHROME_OPTIONS = {
    "disable-blink-features": "AutomationControlled",
    "disable-gpu": True,
    "no-sandbox": True,
}

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
