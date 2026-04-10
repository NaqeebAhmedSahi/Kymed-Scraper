"""
Parser - BeautifulSoup parsers for extracting data from HTML
"""
import logging
import requests
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import uuid

logger = logging.getLogger(__name__)


class CategoryParser:
    """Parser for extracting category data"""
    
    @staticmethod
    def extract_category_links_from_menu(html: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract main categories from the mega menu HTML
        
        Args:
            html: HTML content of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of category dictionaries with name and URL
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            categories = []
            
            # Find all category links in the menu
            # Looking for: <a href="..." class="cbp-column-title nav-link cbp-category-title">
            category_links = soup.find_all('a', class_='cbp-column-title nav-link cbp-category-title')
            
            for link in category_links:
                url = link.get('href', '').strip()
                name = link.get_text(strip=True)
                
                if url and name:
                    # Extract category ID from URL (e.g., /9-surgical-instruments -> 9)
                    cat_id = re.search(r'/(\d+)-', url)
                    cat_id = cat_id.group(1) if cat_id else str(uuid.uuid4())[:8]
                    
                    categories.append({
                        'id': cat_id,
                        'name': name,
                        'url': urljoin(base_url, url),
                        'type': 'main_category'
                    })
            
            logger.info(f"Extracted {len(categories)} main categories")
            return categories
            
        except Exception as e:
            logger.error(f"Error extracting category links: {e}")
            return []


class SubcategoryParser:
    """Parser for extracting subcategory data from category pages"""
    
    @staticmethod
    def is_product_page(url: str) -> bool:
        """
        Detect if a URL is a product page (ends with .html)
        vs a category/subcategory page (just ID-name format)
        
        Args:
            url: Page URL
            
        Returns:
            True if it's a product page, False otherwise
        """
        return url.strip().endswith('.html')
    
    @staticmethod
    def extract_subcategories_from_page(html: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract all subcategories from any category/subcategory page
        Works for multiple nesting levels (subcategories → sub-subcategories → products)
        
        Args:
            html: HTML content of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of subcategory dictionaries with URLs and names
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            subcategories = []
            
            # Find the product list subcategory section
            subcat_container = soup.find('div', class_='product-list-subcategories')
            
            if not subcat_container:
                logger.warning("Subcategory container not found")
                return subcategories
            
            # Find all subcategory items using the correct selector
            subcat_items = subcat_container.find_all('div', class_='product-list-subcategory')
            
            logger.info(f"Found {len(subcat_items)} items in this section")
            
            for idx, item in enumerate(subcat_items, 1):
                try:
                    # Extract link - using subcategory-name class
                    link_elem = item.find('a', class_='subcategory-name')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '').strip()
                    name = link_elem.get_text(strip=True)
                    
                    if not url or not name:
                        continue
                    
                    # Extract ID from URL
                    # Handle both formats:
                    # - /271-iris-scissors -> 271
                    # - /delicate-iris-scissors/1472-stille-... -> 1472
                    match = re.search(r'/(\d+)(?:-|\.)', url)
                    item_id = match.group(1) if match else str(uuid.uuid4())[:8]
                    
                    full_url = urljoin(base_url, url)
                    
                    # Extract image and convert to high quality
                    img_elem = item.find('img')
                    image_url = img_elem.get('src', '').strip() if img_elem else ''
                    if image_url:
                        # For category images (/img/c/), large_default is usually the best
                        # For product images (/img/p/), thickbox_default is better
                        if '/img/p/' in image_url:
                            image_url = image_url.replace('large_default', 'thickbox_default')
                        # For category images, we keep large_default or search for category_default
                        # but based on 404 error, thickbox_default definitely doesn't work for /img/c/
                    
                    subcat_dict = {
                        'id': item_id,
                        'name': name,
                        'url': full_url,
                        'image_url': urljoin(base_url, image_url),
                        'type': 'subcategory'
                    }
                    
                    subcategories.append(subcat_dict)
                    
                    # PRINT IMMEDIATELY - show user what we're finding
                    logger.info(f"  [{idx}] {name}")
                    logger.info(f"      ID: {item_id} | URL: {full_url}")
                    
                except Exception as e:
                    logger.warning(f"Error parsing subcategory item {idx}: {e}")
                    continue
            
            logger.info(f"\n[OK] Extracted {len(subcategories)} subcategory items total\n")
            return subcategories
            
        except Exception as e:
            logger.error(f"Error extracting subcategories: {e}")
            return []
    
    @staticmethod
    def extract_category_description(html: str) -> str:
        """
        Extract category description from the top of the page
        
        Args:
            html: HTML content of the page
            
        Returns:
            Description text or empty string
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Use the specific selector provided by the user
            desc_div = soup.find('div', class_='category-description')
            if not desc_div:
                desc_div = soup.find('div', class_='category-description-top')
            
            if desc_div:
                # Extract all text, maintaining some spacing between paragraphs
                paragraphs = desc_div.find_all(['p', 'span'])
                if paragraphs:
                    return "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                return desc_div.get_text(strip=True)
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            return ""


class ProductParser:
    """Parser for extracting product data from product pages"""
    
    @staticmethod
    def extract_products_from_page(html: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract product listings from subcategory page
        
        Args:
            html: HTML content of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of product dictionaries with basic info
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            products = []
            
            # Find the product list subcategories section
            subcat_container = soup.find('div', class_='product-list-subcategories')
            
            if not subcat_container:
                logger.warning("Product list container not found")
                return products
            
            # Find all product items
            product_items = subcat_container.find_all('div', class_='product-list-subcategory')
            
            for item in product_items:
                try:
                    # Extract link and name
                    link_elem = item.find('a', class_='subcategory-name')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '').strip()
                    name = link_elem.get_text(strip=True)
                    
                    # Extract image and convert to high quality
                    img_elem = item.find('img')
                    image_url = img_elem.get('src', '').strip() if img_elem else ''
                    if image_url:
                        # Only upgrade to thickbox_default if it's a product image
                        if '/img/p/' in image_url:
                            image_url = image_url.replace('large_default', 'thickbox_default')
                    
                    if url and name:
                        # Extract product ID from URL
                        prod_id = re.search(r'/(\d+)-|/(\d+)\.html', url)
                        if prod_id:
                            prod_id = prod_id.group(1) or prod_id.group(2)
                        else:
                            prod_id = str(uuid.uuid4())[:8]
                        
                        products.append({
                            'id': prod_id,
                            'name': name,
                            'url': urljoin(base_url, url),
                            'image_url': urljoin(base_url, image_url),
                            'type': 'product_preview'
                        })
                except Exception as e:
                    logger.warning(f"Error parsing individual product: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} product previews")
            return products
            
        except Exception as e:
            logger.error(f"Error extracting products: {e}")
            return []
    
    @staticmethod
    def get_perfect_hd_url(base_url: str, img_id: str) -> str:
        """
        Construct the 'Perfect HD' URL (un-padded original image) from a PrestaShop image ID.
        Pattern: base_url/img/p/[digit1]/[digit2]/.../ID.jpg
        """
        if not img_id or not img_id.isdigit():
            return ""
        
        # Standard PrestaShop image path: each digit represents a subfolder
        path_parts = list(img_id)
        path = "/".join(path_parts)
        
        return f"https://agnthos.se/img/p/{path}/{img_id}.jpg"

    @staticmethod
    def extract_product_details(html: str, url: str = "") -> Dict[str, Any]:
        """
        Extract detailed product information from product detail page
        
        Args:
            html: HTML content of the product page
            url: Product page URL
            
        Returns:
            Dictionary with detailed product information
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract product name from h1.page-title
            title_elem = soup.find('h1', class_='page-title')
            if not title_elem:
                title_elem = soup.find('h1', class_='h1 page-title')
            name = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract product description (short)
            desc_elem = soup.find('div', id=lambda x: x and 'product-description-short' in x)
            short_description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract full description (long) from all rte-content divs
            rte_divs = soup.find_all('div', class_='rte-content')
            long_description = ""
            for div in rte_divs:
                text = div.get_text(strip=True)
                if text and text != short_description:  # Avoid duplicates
                    if long_description:
                        long_description += " " + text
                    else:
                        long_description = text
            
            # Extract product specifications/variants from buy table
            specifications = ProductParser._extract_specifications(html)
            
            # Extract article numbers from specifications
            article_numbers = []
            for spec in specifications:
                if spec.get('article_number'):
                    article_numbers.append(spec['article_number'])
            
            # Extract multiple images
            all_images = []
            
            # 1. Look for all images with data-image-large-src (this is the HD version)
            # We return BOTH the Perfect HD URL and the original URL for fallback
            import re
            hd_img_elements = soup.find_all('img', attrs={"data-image-large-src": True})
            for img in hd_img_elements:
                hd_url = img.get('data-image-large-src')
                if hd_url:
                    full_original_url = urljoin(url, hd_url)
                    # Always add the original URL first
                    if full_original_url not in all_images:
                        all_images.append(full_original_url)
                    # Also add the Perfect HD URL
                    match = re.search(r'/(\d+)-', hd_url)
                    if match:
                        img_id = match.group(1)
                        perfect_url = ProductParser.get_perfect_hd_url("https://agnthos.se", img_id)
                        if perfect_url and perfect_url not in all_images:
                            all_images.append(perfect_url)
            
            # 2. Fallback to main image swiper if not found by attribute
            if not all_images:
                image_container = soup.find('div', id='product-images-large')
                if image_container:
                    img_elems = image_container.find_all('img')
                    for img in img_elems:
                        hd_url = img.get('content') or img.get('src')
                        if hd_url:
                            full_original_url = urljoin(url, hd_url)
                            if full_original_url not in all_images:
                                all_images.append(full_original_url)
                            # Also add Perfect HD version
                            match = re.search(r'/(\d+)-', hd_url)
                            if match:
                                img_id = match.group(1)
                                perfect_url = ProductParser.get_perfect_hd_url("https://agnthos.se", img_id)
                                if perfect_url and perfect_url not in all_images:
                                    all_images.append(perfect_url)
            
            # 3. Final fallback to any product-like image
            if not all_images:
                cover_img = soup.find('img', class_='img-fluid')
                if cover_img:
                    hd_url = cover_img.get('src')
                    if hd_url:
                        full_original_url = urljoin(url, hd_url)
                        if full_original_url not in all_images:
                            all_images.append(full_original_url)
                        match = re.search(r'/(\d+)-', hd_url)
                        if match:
                            img_id = match.group(1)
                            perfect_url = ProductParser.get_perfect_hd_url("https://agnthos.se", img_id)
                            if perfect_url and perfect_url not in all_images:
                                all_images.append(perfect_url)

            return {
                'name': name,
                'title': name,
                'short_description': short_description,
                'description': short_description,
                'full_details': long_description,
                'long_description': long_description,
                'specifications': specifications,
                'buy_info': specifications,
                'variants': specifications,
                'article_numbers': article_numbers,
                'url': url,
                'image_urls': all_images
            }
        except Exception as e:
            logger.error(f"Error extracting product details: {e}")
            return {
                'name': "",
                'title': "",
                'short_description': "",
                'description': "",
                'long_description': "",
                'full_details': "",
                'specifications': [],
                'buy_info': [],
                'variants': [],
                'article_numbers': [],
                'url': url,
                'image_urls': []
            }
    
    @staticmethod
    def _extract_specifications(html: str) -> List[Dict[str, Any]]:
        """
        Extract product specifications from HTML table
        
        Args:
            html: HTML content of the product page
            
        Returns:
            List of specification dictionaries (Article number, Description, Price)
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            specifications = []
            
            # Find the buy table
            buy_table = soup.find('table', class_='table buy-table')
            if not buy_table:
                logger.warning("Buy table not found")
                return specifications
            
            # Find all rows in tbody
            rows = buy_table.find_all('tr')
            
            for row in rows:
                # Skip header row
                if row.find('th', scope='col'):
                    continue
                
                try:
                    # Extract article number
                    art_no_elem = row.find('strong')
                    art_no = art_no_elem.get_text(strip=True) if art_no_elem else ""
                    
                    # Extract description (all td elements)
                    tds = row.find_all('td')
                    description = ""
                    price = "Contact for price"
                    
                    if len(tds) >= 2:
                        description = tds[0].get_text(strip=True)
                        if len(tds) > 1:
                            price_elem = tds[1].find('a')
                            price = price_elem.get_text(strip=True) if price_elem else price
                    
                    if art_no or description:
                        specifications.append({
                            'article_number': art_no,
                            'description': description,
                            'price': price
                        })
                except Exception as e:
                    logger.warning(f"Error parsing specification row: {e}")
                    continue
            
            logger.info(f"Extracted {len(specifications)} specifications")
            return specifications
            
        except Exception as e:
            logger.error(f"Error extracting specifications: {e}")
            return []


class BreadcrumbParser:
    """Parser for extracting breadcrumb navigation"""
    
    @staticmethod
    def extract_breadcrumb(html: str) -> List[str]:
        """Extract breadcrumb navigation from page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            breadcrumb = []
            
            # Find breadcrumb elements (might vary by page structure)
            # Usually: <a> elements in nav or specific breadcrumb container
            breadcrumb_items = soup.find_all('a', class_='nav-link')
            
            for item in breadcrumb_items[:5]:  # Limit to prevent too many items
                text = item.get_text(strip=True)
                if text:
                    breadcrumb.append(text)
            
            return breadcrumb
            
        except Exception as e:
            logger.error(f"Error extracting breadcrumb: {e}")
            return []
