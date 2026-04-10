"""
Main Scraper - Orchestrates the entire scraping process
Uses Selenium with undetected Chrome driver for cookie handling and navigation
"""
import logging
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *
from src.json_manager import ProductsManager, LinksProgressManager
from src.parser import CategoryParser, SubcategoryParser, ProductParser, BreadcrumbParser
from src.image_downloader import ImageDownloader


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgnthosScraper:
    """Main scraper class that orchestrates the entire scraping process"""
    
    def __init__(self):
        """Initialize scraper with managers and browser"""
        self.base_url = BASE_URL
        self.products_manager = ProductsManager(PRODUCTS_JSON)
        self.progress_manager = LinksProgressManager(LINKS_PROGRESS_JSON)
        self.image_downloader = ImageDownloader(IMAGES_DIR)
        self.driver = None
        self.wait = None
        
        logger.info("=" * 80)
        logger.info("AGNTHOS SCRAPER INITIALIZED")
        logger.info("=" * 80)
    
    def setup_browser(self):
        """Setup Chrome browser with undetected driver and advanced stealth options"""
        def get_options():
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # User agent - realistic
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            options.add_argument(f"user-agent={user_agent}")
            
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-web-resources")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-default-apps")
            options.add_argument("--no-first-run")
            
            if HEADLESS:
                options.add_argument("--headless=new")
            return options

        try:
            logger.info("Setting up undetected Chrome browser with stealth mode...")
            
            # Versions to try in order (None means auto-detect)
            # Starting with auto-detect, then falling back to explicit recent versions
            # Updated version order: try 143 first as requested, then future-proof downward
            versions_to_try = [
                None, 143, 150, 149, 148, 147, 146, 145, 144, 142, 141, 140, 
                139, 138, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 
                126, 125, 124, 123, 122, 121, 120
            ]
            
            self.driver = None
            for version in versions_to_try:
                try:
                    vn_str = str(version) if version else "Auto-detect"
                    logger.info(f"🚀 Initializing Chrome... (Version: {vn_str})")
                    
                    if version:
                        self.driver = uc.Chrome(options=get_options(), version_main=version, use_subprocess=True)
                    else:
                        self.driver = uc.Chrome(options=get_options(), use_subprocess=True)
                    
                    if self.driver:
                        logger.info(f"✅ Successfully initialized Chrome with version: {vn_str}")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize Chrome version {version}: {e}")
                    if self.driver:
                        try: self.driver.quit()
                        except: pass
                    continue
            
            if not self.driver:
                # Last resort: try without use_subprocess
                logger.info("🔄 Last resort: Attempting initialization without subprocess...")
                self.driver = uc.Chrome(options=get_options(), use_subprocess=False)
            
            # Execute stealth scripts
            logger.info("Injecting stealth JavaScript...")
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US'],
                    });
                """
            })
            
            self.wait = WebDriverWait(self.driver, IMPLICIT_WAIT)
            
            logger.info("Browser setup complete with stealth mode activated")
            
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            raise
    
    def close_browser(self):
    
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
    
    def handle_cookies(self):
        """
        Handle cookie acceptance dialog
        This will pause and wait for user to press ENTER to accept cookies
        """
        logger.info("=" * 80)
        logger.info("COOKIE ACCEPTANCE REQUIRED")
        logger.info("=" * 80)
        logger.info("Opening website: " + self.base_url)
        
        try:
            # Add realistic delays before request
            time.sleep(2)
            
            logger.info("Sending request to website...")
            self.driver.get(self.base_url)
            
            # Wait for page to load with multiple delays
            logger.info("Waiting for page to load...")
            time.sleep(5)
            
            # Take screenshot to show user
            logger.info("Page loaded. Waiting for user to accept cookies...")
            logger.info("Press ENTER in the terminal after accepting cookies on the browser")
            
            # Wait for user input
            input("\n>>> Press ENTER after accepting cookies: ")
            
            logger.info("Proceeding with scraping...")
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Error during cookie handling: {e}")
            raise
    
    def get_page_html(self, url: str) -> Optional[str]:
        """
        Get page HTML using Selenium
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.debug(f"Fetching: {url}")
            self.driver.get(url)
            time.sleep(SCROLL_PAUSE)
            
            # DEBUG MODE: If enabled, pause and wait for user input
            if DEBUG:
                # Flush all handlers to ensure message appears
                for handler in logger.handlers:
                    handler.flush()
                import sys
                sys.stdout.flush()
                sys.stderr.flush()
                
                logger.info(f"\n[DEBUG] Page loaded: {url}")
                logger.info("[DEBUG] Inspect the page in the browser if needed.")
                logger.info("[DEBUG] Press ENTER to continue scraping...")
                
                # Flush again before waiting for input
                for handler in logger.handlers:
                    handler.flush()
                sys.stdout.flush()
                
                # Wait for user input
                input()
            
            # Get page source
            html = self.driver.page_source
            return html
            
        except TimeoutException:
            logger.error(f"Timeout fetching {url}")
            self.progress_manager.add_failed_link(url, "Timeout")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            self.progress_manager.add_failed_link(url, str(e))
            return None
    
    def scrape_main_categories(self):
        """
        Scrape main categories from homepage
        This extracts the main category structure
        """
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: SCRAPING MAIN CATEGORIES")
        logger.info("=" * 80)
        
        try:
            # Get homepage HTML
            html = self.get_page_html(self.base_url)
            if not html:
                logger.error("Failed to get homepage HTML")
                return False
            
            # Extract main categories from menu
            categories = CategoryParser.extract_category_links_from_menu(html, self.base_url)
            
            if not categories:
                logger.error("No categories found on homepage")
                return False
            
            logger.info(f"Found {len(categories)} main categories")
            
            # Initialize data structures
            self.products_manager.initialize_structure()
            self.progress_manager.initialize_progress()
            
            # Add categories to progress tracker
            for category in categories:
                self.progress_manager.add_category_link(
                    category['id'],
                    category['name'],
                    category['url']
                )
            
            logger.info(f"Added {len(categories)} categories to progress tracker")
            return True
            
        except Exception as e:
            logger.error(f"Error in main category scraping: {e}")
            return False
    
    def scrape_category(self, category: Dict[str, Any]) -> bool:
        """
        Scrape a single category and its subcategories
        
        Args:
            category: Category dictionary with id, name, url
            
        Returns:
            True if successful
        """
        cat_id = category['id']
        cat_name = category['name']
        cat_url = category['url']
        
        logger.info(f"\n📂 CATEGORY: {cat_name} ({cat_id})")
        logger.info(f"🔗 URL: {cat_url}")
        
        try:
            # IMMEDIATELY add category to products.json with empty structure
            self.products_manager.add_category_with_empty_structure(cat_id, cat_name, cat_url)
            
            # Fetch category page
            html = self.get_page_html(cat_url)
            if not html:
                return False
            
            # Extract description
            cat_description = SubcategoryParser.extract_category_description(html)
            if cat_description:
                logger.info(f"📝 Category Description: {cat_description[:100]}...")
                self.products_manager.update_category_description(cat_id, cat_description)
            
            # Extract subcategories
            subcategories = SubcategoryParser.extract_subcategories_from_page(html, self.base_url)
            
            if not subcategories:
                logger.warning(f"No subcategories found for {cat_name}")
                return False
            
            logger.info(f"Found {len(subcategories)} subcategories")
            
            # Process each subcategory and add them IMMEDIATELY to products.json
            for subcat in subcategories:
                self.progress_manager.add_subcategory_link(
                    cat_id,
                    subcat['id'],
                    subcat['name'],
                    subcat['url']
                )
                
                # IMMEDIATELY add empty subcategory structure to products.json
                self.products_manager.add_subcategory_to_category(
                    cat_id,
                    subcat['id'],
                    subcat['name'],
                    subcat['url']
                )

                # Hierarchical path for subcategory images
                path_prefix = cat_name
                # Use Canvas-based download to bypass bot protection
                local_path = self.image_downloader.download_via_canvas(
                    self.driver,
                    subcat['image_url'], 
                    sub_path=path_prefix, 
                    filename=subcat['name']
                )
                # Fallback if canvas fails
                if not local_path:
                    local_path = self.image_downloader.download_image(
                        subcat['image_url'], 
                        sub_path=path_prefix, 
                        filename=subcat['name']
                    )
                self.products_manager.update_subcategory_image(cat_id, subcat['id'], subcat['image_url'], local_path)
                
                # Scrape subcategory and get its data
                subcat_data = self.scrape_subcategory(cat_id, cat_name, subcat, path_prefix=f"{path_prefix}/{subcat['name']}")
                if subcat_data:
                    logger.info(f"  ✅ Subcategory completed: {subcat['name']}")
                else:
                    logger.warning(f"Failed to scrape subcategory: {subcat['name']}")
            
            # Mark category as scraped
            self.progress_manager.mark_category_scraped(cat_id)
            logger.info(f"[OK] Category completed: {cat_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error scraping category {cat_name}: {e}")
            self.progress_manager.add_failed_link(cat_url, str(e))
            return False
    
    def scrape_subcategory(self, cat_id: str, cat_name: str, subcat: Dict[str, Any], 
                          parent_subcat_id: Optional[str] = None, path_prefix: str = "") -> Optional[Dict[str, Any]]:
        """
        Scrape a subcategory - which may contain either:
        1. More subcategories (sub-subcategories) → recurse deeper
        2. Actual products → scrape each product
        3. A single product page (URL ends with .html) → scrape product details
        
        Args:
            cat_id: Parent category ID
            cat_name: Parent category name
            subcat: Subcategory dictionary
            parent_subcat_id: If this is a nested subcategory, the parent's ID
            path_prefix: Hierarchical path for image storage
            
        Returns:
            Subcategory data dict with products, or None if failed
        """
        subcat_id = subcat['id']
        subcat_name = subcat['name']
        subcat_url = subcat['url']
        
        # SKIP if already scraped (only if not at level 1 or forced)
        if self.progress_manager.is_subcategory_scraped(cat_id, subcat_id):
            logger.info(f"  [SKIP] Subcategory already scraped: {subcat_name}")
            return None
            
        logger.info(f"  📁 Subcategory: {subcat_name}")
        
        try:
            # Check if this URL is actually a product detail page (ends with .html)
            if SubcategoryParser.is_product_page(subcat_url):
                logger.info(f"    [PRODUCT PAGE DETECTED] {subcat_name}")
                # This is actually a product, not a subcategory
                # Add it to the JSON immediately
                if parent_subcat_id:
                    self.products_manager.add_product_to_subcategory(
                        cat_id, parent_subcat_id, subcat_id, subcat_name, subcat_url
                    )
                
                product_data = self.scrape_product(cat_id, cat_name, parent_subcat_id or subcat_id, subcat_name, subcat, path_prefix=path_prefix)
                if product_data:
                    # Update the product details in JSON
                    self.products_manager.update_product_details(
                        cat_id, parent_subcat_id or subcat_id, subcat_id, product_data
                    )
                    return {
                        'id': subcat_id,
                        'name': subcat_name,
                        'url': subcat_url,
                        'is_product': True,
                        'products': [product_data]
                    }
                return None
            
            # Fetch subcategory page
            html = self.get_page_html(subcat_url)
            if not html:
                return None
            
            # Extract description for this subcategory
            subcat_description = SubcategoryParser.extract_category_description(html)
            if subcat_description:
                logger.info(f"    📝 Description: {subcat_description[:100]}...")
                self.products_manager.update_subcategory_description(cat_id, subcat_id, subcat_description)
            
            # First, try to extract sub-subcategories (another level of nesting)
            sub_subcategories = SubcategoryParser.extract_subcategories_from_page(html, self.base_url)
            
            if sub_subcategories:
                # This level contains MORE subcategories, recurse deeper
                logger.info(f"    Found {len(sub_subcategories)} sub-subcategories - going deeper...")
                
                # Build the subcategory data with nested products
                subcat_data = {
                    'id': subcat_id,
                    'name': subcat_name,
                    'url': subcat_url,
                    'products': []
                }
                
                for sub_subcat in sub_subcategories:
                    # IMMEDIATELY save to progress
                    self.progress_manager.add_subcategory_link(
                        cat_id,
                        sub_subcat['id'],
                        sub_subcat['name'],
                        sub_subcat['url']
                    )
                    
                    # IMMEDIATELY add to JSON with proper nesting
                    if parent_subcat_id:
                        # This is a level 3+ subcategory (Category -> Sub -> Sub-Sub -> ...)
                        # For now, JSON manager supports level 3. We'll ensure it adds to the correct parent.
                        self.products_manager.add_subcategory_to_subcategory(
                            cat_id, subcat_id, sub_subcat['id'], sub_subcat['name'], sub_subcat['url']
                        )
                    else:
                        # This is a level 2 subcategory (Category -> Sub -> Sub-Sub)
                        self.products_manager.add_subcategory_to_subcategory(
                            cat_id, subcat_id, sub_subcat['id'], sub_subcat['name'], sub_subcat['url']
                        )
                    
                    # Download nested subcategory image if available
                    if sub_subcat.get('image_url'):
                        logger.info(f"    🖼️ Downloading image for nested subcategory: {sub_subcat['name']}")
                        # Use Canvas-based download to bypass bot protection
                        local_path = self.image_downloader.download_via_canvas(
                            self.driver,
                            sub_subcat['image_url'], 
                            sub_path=path_prefix, 
                            filename=sub_subcat['name']
                        )
                        # Fallback if canvas fails
                        if not local_path:
                            local_path = self.image_downloader.download_image(
                                sub_subcat['image_url'], 
                                sub_path=path_prefix, 
                                filename=sub_subcat['name']
                            )
                        self.products_manager.update_subcategory_image(cat_id, sub_subcat['id'], sub_subcat['image_url'], local_path)
                    
                    # Recursively scrape this level, appending current subcategory to prefix
                    new_prefix = f"{path_prefix}/{sub_subcat['name']}"
                    nested_data = self.scrape_subcategory(cat_id, cat_name, sub_subcat, 
                                                         parent_subcat_id=subcat_id, path_prefix=new_prefix)

                    if nested_data:
                        # Add nested subcategory to this level's products (for now, treat as product for hierarchy)
                        subcat_data['products'].append(nested_data)
                    else:
                        logger.warning(f"    Failed to scrape sub-subcategory: {sub_subcat['name']}")
                
                # Mark subcategory as scraped
                self.progress_manager.mark_subcategory_scraped(cat_id, subcat_id)
                logger.info(f"    [OK] Subcategory completed: {subcat_name}")
                return subcat_data
            
            # If no sub-subcategories, extract products from this level
            products = ProductParser.extract_products_from_page(html, self.base_url)
            
            if not products:
                logger.warning(f"    No products found in {subcat_name}")
                self.progress_manager.mark_subcategory_scraped(cat_id, subcat_id)
                return {
                    'id': subcat_id,
                    'name': subcat_name,
                    'url': subcat_url,
                    'products': []
                }
            
            logger.info(f"    Found {len(products)} products")
            
            # Process each product and save IMMEDIATELY to JSON
            for idx, product in enumerate(products, 1):
                # SKIP if already scraped
                if self.progress_manager.is_product_scraped(cat_id, subcat['id'], product['id']):
                    logger.info(f"      [SKIP] Product already scraped: {product['name']}")
                    continue
                    
                logger.info(f"      📦 [{idx}/{len(products)}] Product: {product['name']}")
                
                # IMMEDIATELY add product structure to JSON before scraping details
                actual_parent_id = parent_subcat_id or subcat_id
                self.products_manager.add_product_to_subcategory(
                    cat_id, actual_parent_id, product['id'], product['name'], product['url']
                )
                
                # IMMEDIATELY save to progress before scraping
                self.progress_manager.add_product_link(
                    cat_id,
                    actual_parent_id,
                    product['id'],
                    product['name'],
                    product['url']
                )
                
                # Scrape product details
                product_data = self.scrape_product(cat_id, cat_name, actual_parent_id, subcat_name, product, path_prefix=path_prefix)
                if product_data:
                    # Update product details in JSON immediately
                    self.products_manager.update_product_details(
                        cat_id, actual_parent_id, product['id'], product_data
                    )
                else:
                    logger.warning(f"        [FAIL] Failed to scrape product: {product['name']}")
            
            # Mark subcategory as scraped
            self.progress_manager.mark_subcategory_scraped(cat_id, subcat_id)
            logger.info(f"    [OK] Subcategory completed: {subcat_name}")
            
            return {
                'id': subcat_id,
                'name': subcat_name,
                'url': subcat_url,
                'products': products
            }
            
        except Exception as e:
            logger.error(f"Error scraping subcategory {subcat_name}: {e}")
            self.progress_manager.add_failed_link(subcat_url, str(e))
            return False
    
    def scrape_product(self, cat_id: str, cat_name: str, subcat_id: str, subcat_name: str, 
                      product: Dict[str, Any], path_prefix: str = "") -> Optional[Dict[str, Any]]:
        """
        Scrape individual product details and return product data
        """
        prod_id = product['id']
        prod_name = product['name']
        prod_url = product['url']
        
        try:
            logger.info(f"        [DEBUG] Scramping product: {prod_name}")
            logger.info(f"        [DEBUG] Context: Category={cat_name} ({cat_id}), Subcategory={subcat_name} ({subcat_id})")
            
            # Fetch product page
            html = self.get_page_html(prod_url)
            if not html:
                logger.warning(f"        [FAIL] Failed to load HTML for {prod_url}")
                return None
            
            # Extract product details with URL
            logger.info(f"        Parsing product data from {prod_url}...")
            details = ProductParser.extract_product_details(html, prod_url)
            
            if not details or not details.get('name'):
                logger.warning(f"        [WARN] Parser returned empty details for {prod_name}")
            
            logger.info(f"        📝 Name: {details.get('name', 'N/A')}")
            logger.info(f"        🔢 Article Numbers: {details.get('article_numbers', [])}")
            logger.info(f"        🛠️  Variants: {len(details.get('variants', []))} found")
            logger.info(f"        📜 Description: {details.get('short_description', 'N/A')[:60]}...")
            
            # Multi-image downloading logic
            # Get gallery images from the detail page
            gallery_urls = details.get('image_urls', [])
            
            # Combine with preview image from the category list
            all_url_candidates = []
            if product.get('image_url'):
                all_url_candidates.append(product['image_url'])
            all_url_candidates.extend(gallery_urls)
            
            # De-duplicate while keeping BOTH Perfect HD and original URLs
            # We store: { img_id: { 'perfect_hd': url, 'original': url } }
            unique_images = {}
            for url in all_url_candidates:
                # Extract image ID (e.g., '4903' from '4903-thickbox_default/...')
                match = re.search(r'/(\d+)-', url)
                if not match:
                    # Try another pattern if the first one fails
                    match = re.search(r'/(\d+)\.jpg', url)
                
                img_id = match.group(1) if match else url
                
                if img_id not in unique_images:
                    unique_images[img_id] = {'perfect_hd': None, 'original': None}
                
                # Check if this URL is a Perfect HD digit-split URL
                if '/img/p/' in url and re.match(r'.*/img/p/[\d/]+/\d+\.jpg$', url):
                    unique_images[img_id]['perfect_hd'] = url
                else:
                    # This is an original URL (thickbox_default, large_default, etc.)
                    # Always keep the best original we find
                    if not unique_images[img_id]['original']:
                        unique_images[img_id]['original'] = url
                    # Prefer thickbox_default over other formats
                    elif 'thickbox_default' in url:
                        unique_images[img_id]['original'] = url
                
                # If we have a digit ID, generate Perfect HD URL
                if img_id.isdigit() and not unique_images[img_id]['perfect_hd']:
                    unique_images[img_id]['perfect_hd'] = ProductParser.get_perfect_hd_url("https://agnthos.se", img_id)
                
                # If we don't have an original yet, construct one from thickbox_default
                if img_id.isdigit() and not unique_images[img_id]['original']:
                    unique_images[img_id]['original'] = f"https://agnthos.se/{img_id}-thickbox_default/.jpg"
            
            local_image_paths = []
            if unique_images:
                logger.info(f"        Downloading {len(unique_images)} unique HD images via Canvas...")
                for idx, (img_id, urls) in enumerate(unique_images.items(), 1):
                    # For multiple images, always add a suffix to be safe and consistent
                    filename = f"{prod_name}_{idx}"
                    
                    # Try Perfect HD first, then fall back to original
                    perfect_hd_url = urls.get('perfect_hd')
                    original_url = urls.get('original')
                    
                    logger.info(f"        [{idx}/{len(unique_images)}] HD image ID={img_id}")
                    
                    # Detect and purge existing corrupted images (usually < 1KB if they are captcha stubs)
                    target_dir = self.image_downloader.images_dir
                    if path_prefix:
                        target_dir = target_dir / self.image_downloader._sanitize_path(path_prefix)
                    
                    filename_with_ext = self.image_downloader._sanitize_filename(filename, (perfect_hd_url or original_url))
                    existing_file = target_dir / filename_with_ext
                    if existing_file.exists() and existing_file.stat().st_size < 1024:
                        logger.warning(f"        [PURGE] Deleting corrupted image file (size: {existing_file.stat().st_size} bytes)")
                        existing_file.unlink()

                    local_path = None
                    
                    # Strategy 1: Try Perfect HD URL via Canvas
                    if perfect_hd_url:
                        logger.info(f"        Trying Perfect HD: {perfect_hd_url}")
                        local_path = self.image_downloader.download_via_canvas(
                            self.driver, perfect_hd_url, 
                            sub_path=path_prefix, filename=filename
                        )
                    
                    # Strategy 2: If Perfect HD failed, try Original URL via Canvas
                    if not local_path and original_url:
                        logger.info(f"        [FALLBACK] Trying original URL via Canvas: {original_url}")
                        local_path = self.image_downloader.download_via_canvas(
                            self.driver, original_url,
                            sub_path=path_prefix, filename=filename
                        )
                    
                    # Strategy 3: Try Original URL via browser fetch
                    if not local_path and original_url:
                        logger.info(f"        [FALLBACK] Trying original URL via browser fetch...")
                        local_path = self.image_downloader.download_via_browser(
                            self.driver, original_url,
                            sub_path=path_prefix, filename=filename
                        )
                    
                    # Strategy 4: Last resort - direct requests with any available URL
                    if not local_path:
                        fallback_url = original_url or perfect_hd_url
                        if fallback_url:
                            logger.info(f"        [FALLBACK] Last resort direct download: {fallback_url}")
                            local_path = self.image_downloader.download_image(
                                fallback_url,
                                sub_path=path_prefix, filename=filename
                            )
                        
                    if local_path:
                        local_image_paths.append(local_path)
                        logger.info(f"        [OK] Image {idx} saved: {local_path}")
                    else:
                        logger.error(f"        [FAIL] Could not download image ID={img_id} with any method")
            
            # Create complete product data
            product_data = {
                'id': prod_id,
                'name': prod_name or details.get('name'),
                'title': details.get('title') or details.get('name'),
                'url': prod_url,
                'subcategory': subcat_name,
                'short_description': details.get('short_description', ''),
                'long_description': details.get('full_details', '') or details.get('long_description', ''),
                'article_numbers': details.get('article_numbers', []),
                'variants': details.get('variants', []),
                'specifications': details.get('specifications', []),
                'buy_info': details.get('buy_info', []),
                'full_details': details.get('full_details', ''),
                'image_url': all_url_candidates[0] if all_url_candidates else '', # Primary image URL
                'image_urls': all_url_candidates, # All image URLs
                'image_local_path': local_image_paths[0] if local_image_paths else '', # Primary local path
                'image_local_paths': local_image_paths # All local paths
            }
            
            # IMMEDIATELY save to products.json in the proper hierarchy
            logger.info(f"        [SAVE] Updating products.json for {prod_id}...")
            self.products_manager.update_product_details(cat_id, subcat_id, prod_id, product_data)
            
            # Mark as scraped in progress tracker
            self.progress_manager.mark_product_scraped(cat_id, subcat_id, prod_id)
            
            logger.info(f"        [OK] Product completed: {prod_name}\n")
            return product_data
            
        except Exception as e:
            logger.error(f"✗ Error scraping product {prod_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.progress_manager.add_failed_link(prod_url, str(e))
            return None
    
    def resume_scraping(self):
        """Resume scraping from where it left off"""
        logger.info("\n" + "=" * 80)
        logger.info("RESUME SCRAPING FROM CHECKPOINT")
        logger.info("=" * 80)
        
        try:
            # Check if progress file exists
            if not LINKS_PROGRESS_JSON.exists():
                logger.error(f"Cannot resume: Progress file NOT found at {LINKS_PROGRESS_JSON}")
                logger.info("Please run the scraper WITHOUT the --resume flag to start a fresh scan.")
                return False

            # Get pending categories
            pending_categories = self.progress_manager.get_pending_categories()
            
            if not pending_categories:
                logger.info("No pending categories to scrape")
                return True
            
            logger.info(f"Found {len(pending_categories)} pending categories to scrape")
            
            for category in pending_categories:
                cat_id = category['id']
                cat_name = category['name']
                
                # Check if category was already partially scraped
                pending_subcats = self.progress_manager.get_pending_subcategories(cat_id)
                
                if pending_subcats:
                    logger.info(f"\nResuming category: {cat_name}")
                    logger.info(f"  {len(pending_subcats)} pending subcategories")
                    
                    # Continue scraping this category
                    self.scrape_category(category)
                else:
                    logger.info(f"Category fully scraped: {cat_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in resume scraping: {e}")
            return False
    
    def run(self, resume: bool = False):
        """
        Main execution method
        
        Args:
            resume: If True, resume from last checkpoint; if False, start fresh
        """
        try:
            self.setup_browser()
            
            # Handle cookies
            self.handle_cookies()
            
            if resume:
                # Resume from checkpoint
                success = self.resume_scraping()
            else:
                # Start fresh scraping
                # Phase 1: Scrape main categories
                if not self.scrape_main_categories():
                    logger.error("Failed to scrape main categories")
                    return False
                
                # Phase 2: Scrape each category
                logger.info("\n" + "=" * 80)
                logger.info("PHASE 2: SCRAPING ALL CATEGORIES AND PRODUCTS")
                logger.info("=" * 80)
                
                pending_categories = self.progress_manager.get_pending_categories()
                logger.info(f"Starting to scrape {len(pending_categories)} categories")
                
                for idx, category in enumerate(pending_categories, 1):
                    logger.info(f"\n[{idx}/{len(pending_categories)}] Processing category...")
                    self.scrape_category(category)
                    
                    # Small pause between categories
                    time.sleep(1)
            
            logger.info("\n" + "=" * 80)
            logger.info("SCRAPING COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            logger.info(f"Products JSON: {PRODUCTS_JSON}")
            logger.info(f"Progress JSON: {LINKS_PROGRESS_JSON}")
            logger.info(f"Images Directory: {IMAGES_DIR}")
            
            return True
            
        except KeyboardInterrupt:
            logger.warning("\n\nScraping interrupted by user")
            logger.info("Progress saved. Use --resume flag to continue from checkpoint")
            return False
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            return False
        finally:
            self.close_browser()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agnthos Website Scraper')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    scraper = AgnthosScraper()
    success = scraper.run(resume=args.resume)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
