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
        try:
            logger.info("Setting up undetected Chrome browser with stealth mode...")
            
            options = uc.ChromeOptions()
            
            # Critical stealth headers
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # User agent - realistic
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
            options.add_argument(f"user-agent={user_agent}")
            
            # Disable GPU and sandbox
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Window size
            options.add_argument("--window-size=1920,1080")
            
            # Additional stealth options
            options.add_argument("--disable-web-resources")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-default-apps")
            options.add_argument("--no-first-run")
            
            if HEADLESS:
                options.add_argument("--headless=new")
            
            # Use cached Chrome driver - avoid re-downloading
            # undetected-chromedriver caches in ~\appdata\roaming\undetected_chromedriver\
            logger.info("Setting up Chrome driver with caching (v146)...")
            try:
                # Try to use cached driver first
                self.driver = uc.Chrome(options=options, version_main=146, use_subprocess=False)
            except Exception as e:
                logger.warning(f"Error with cached driver, retrying: {e}")
                self.driver = uc.Chrome(options=options, version_main=146)
            
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
        
        logger.info(f"\nScraping category: {cat_name} ({cat_id})")
        logger.info(f"URL: {cat_url}")
        
        try:
            # IMMEDIATELY add category to products.json with empty structure
            self.products_manager.add_category_with_empty_structure(cat_id, cat_name, cat_url)
            
            # Fetch category page
            html = self.get_page_html(cat_url)
            if not html:
                return False
            
            # Extract description
            description = SubcategoryParser.extract_category_description(html)
            
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
                
                # Scrape subcategory and get its data
                subcat_data = self.scrape_subcategory(cat_id, cat_name, subcat)
                if subcat_data:
                    logger.info(f"  Subcategory data processed: {subcat['name']}")
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
    
    def scrape_subcategory(self, cat_id: str, cat_name: str, subcat: Dict[str, Any], parent_subcat_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
            
        Returns:
            Subcategory data dict with products, or None if failed
        """
        subcat_id = subcat['id']
        subcat_name = subcat['name']
        subcat_url = subcat['url']
        
        logger.info(f"  -> Subcategory: {subcat_name}")
        
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
                
                product_data = self.scrape_product(cat_id, parent_subcat_id or subcat_id, subcat_name, subcat)
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
                    
                    # IMMEDIATELY add to JSON with empty structure
                    if parent_subcat_id:
                        # This is a nested subcategory
                        self.products_manager.add_subcategory_to_subcategory(
                            cat_id, subcat_id, sub_subcat['id'], sub_subcat['name'], sub_subcat['url']
                        )
                    else:
                        # This is a second-level subcategory (direct child of category)
                        self.products_manager.add_subcategory_to_category(
                            cat_id, sub_subcat['id'], sub_subcat['name'], sub_subcat['url']
                        )
                    
                    # Recursively scrape this level
                    nested_data = self.scrape_subcategory(cat_id, cat_name, sub_subcat, parent_subcat_id=subcat_id)

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
                logger.info(f"      [{idx}/{len(products)}] Product: {product['name']}")
                
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
                product_data = self.scrape_product(cat_id, actual_parent_id, subcat_name, product)
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
    
    def scrape_product(self, cat_id: str, subcat_id: str, subcat_name: str, 
                      product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Scrape individual product details and return product data
        
        Args:
            cat_id: Category ID
            subcat_id: Subcategory ID
            subcat_name: Subcategory name
            product: Product dictionary
            
        Returns:
            Product data dict, or None if failed
        """
        prod_id = product['id']
        prod_name = product['name']
        prod_url = product['url']
        
        try:
            logger.info(f"        Opening product page...")
            
            # Fetch product page
            html = self.get_page_html(prod_url)
            if not html:
                logger.warning(f"        [FAIL] Failed to load HTML")
                return None
            
            # Extract product details with URL
            logger.info(f"        Parsing product data...")
            details = ProductParser.extract_product_details(html, prod_url)
            
            logger.info(f"        Title: {details.get('name', 'N/A')}")
            logger.info(f"        Article Numbers: {details.get('article_numbers', [])}")
            logger.info(f"        Variants: {len(details.get('variants', []))} found")
            logger.info(f"        Description: {details.get('short_description', 'N/A')[:100]}...")
            
            # Download product image
            local_image_path = None
            if product.get('image_url'):
                logger.info(f"        Downloading image...")
                local_image_path = self.image_downloader.download_image(product['image_url'])
                logger.info(f"        Image saved: {local_image_path}")
            
            # Create complete product data
            product_data = {
                'id': prod_id,
                'name': prod_name or details.get('name'),
                'title': details.get('title'),
                'url': prod_url,
                'subcategory': subcat_name,
                'short_description': details.get('short_description', ''),
                'long_description': details.get('long_description', ''),
                'article_numbers': details.get('article_numbers', []),
                'variants': details.get('variants', []),
                'specifications': details.get('specifications', []),
                'image_url': product.get('image_url', ''),
                'image_local_path': local_image_path
            }
            
            # IMMEDIATELY save to products.json in the proper hierarchy
            self.products_manager.add_product(cat_id, subcat_id, product_data)
            logger.info(f"        [SAVED] Product data saved to products.json")
            
            # Mark as scraped in progress tracker
            self.progress_manager.mark_product_scraped(cat_id, subcat_id, prod_id)
            
            logger.info(f"        [OK] Product completed: {prod_name}\n")
            return product_data
            
        except Exception as e:
            logger.error(f"✗ Error scraping product {prod_name}: {e}")
            self.progress_manager.add_failed_link(prod_url, str(e))
            return None
    
    def resume_scraping(self):
        """Resume scraping from where it left off"""
        logger.info("\n" + "=" * 80)
        logger.info("RESUME SCRAPING FROM CHECKPOINT")
        logger.info("=" * 80)
        
        try:
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
