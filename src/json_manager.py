"""
JSON Manager - Handles all JSON file operations for data persistence
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONManager:
    """Manages JSON file operations with proper error handling"""
    
    def __init__(self, filepath: Path):
        """Initialize JSON manager"""
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
    def load(self) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        try:
            if self.filepath.exists():
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded data from {self.filepath}")
                return data
            logger.warning(f"File not found: {self.filepath}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {self.filepath}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {self.filepath}: {e}")
            return {}
    
    def save(self, data: Dict[str, Any]):
        """Save JSON file with proper formatting"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {self.filepath}")
        except Exception as e:
            logger.error(f"Error saving to {self.filepath}: {e}")
    
    def append_to_list(self, key: str, value: Any):
        """Append value to a list in JSON"""
        try:
            data = self.load()
            if key not in data:
                data[key] = []
            data[key].append(value)
            self.save(data)
        except Exception as e:
            logger.error(f"Error appending to {key}: {e}")
    
    def update_nested(self, keys: List[str], value: Any):
        """Update nested dictionary value"""
        try:
            data = self.load()
            current = data
            
            # Navigate to the nested location
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the value
            current[keys[-1]] = value
            self.save(data)
        except Exception as e:
            logger.error(f"Error updating nested value: {e}")


class ProductsManager(JSONManager):
    """Manages products data structure"""
    
    def initialize_structure(self):
        """Initialize the products structure"""
        structure = {
            "metadata": {
                "website": "https://agnthos.se",
                "total_categories": 0,
                "total_products": 0,
                "last_updated": datetime.now().isoformat(),
                "scraping_status": "in_progress"
            },
            "categories": []
        }
        self.save(structure)
        logger.info("Initialized products structure")
    
    def add_category(self, category_data: Dict[str, Any]):
        """Add a new category"""
        data = self.load()
        data["categories"].append(category_data)
        data["metadata"]["total_categories"] = len(data["categories"])
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.save(data)
        logger.info(f"Added category: {category_data.get('name')}")
    
    def get_category(self, category_id: str) -> Dict[str, Any]:
        """Get category by ID"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                return cat
        return {}
    
    def update_category(self, category_id: str, updates: Dict[str, Any]):
        """Update category data"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                cat.update(updates)
                self.save(data)
                logger.info(f"Updated category: {category_id}")
                return
        logger.warning(f"Category not found: {category_id}")
    
    def add_category_with_empty_structure(self, cat_id: str, cat_name: str, cat_url: str):
        """Add category with empty subcategories and products arrays"""
        data = self.load()
        category = {
            "id": cat_id,
            "name": cat_name,
            "url": cat_url,
            "description": "",
            "image_url": "",
            "image_local_path": "",
            "subcategories": [],
            "products": []
        }
        data["categories"].append(category)
        data["metadata"]["total_categories"] = len(data["categories"])
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.save(data)
        logger.info(f"Added category with empty structure: {cat_name}")
    
    def _find_subcategory_recursive(self, items: List[Dict[str, Any]], subcat_id: str) -> Optional[Dict[str, Any]]:
        """Find subcategory by ID recursively in any list of subcategories"""
        for item in items:
            if item.get("id") == subcat_id:
                return item
            
            # Search in nested subcategories
            if "subcategories" in item and item["subcategories"]:
                found = self._find_subcategory_recursive(item["subcategories"], subcat_id)
                if found:
                    return found
        return None

    def add_subcategory_to_category(self, category_id: str, subcat_id: str, subcat_name: str, subcat_url: str):
        """Add subcategory to a specific category"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                # Check if it already exists
                if self._find_subcategory_recursive(cat.get("subcategories", []), subcat_id):
                    return True
                
                subcategory = {
                    "id": subcat_id,
                    "name": subcat_name,
                    "url": subcat_url,
                    "description": "",
                    "image_url": "",
                    "image_local_path": "",
                    "subcategories": [],
                    "products": []
                }
                cat["subcategories"].append(subcategory)
                data["metadata"]["last_updated"] = datetime.now().isoformat()
                self.save(data)
                logger.info(f"Added subcategory to {category_id}: {subcat_name}")
                return True
        logger.warning(f"Category not found: {category_id}")
        return False
    
    def add_subcategory_to_subcategory(self, category_id: str, parent_subcat_id: str, subcat_id: str, subcat_name: str, subcat_url: str):
        """Add nested subcategory to any level subcategory"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                # Find the parent subcategory anywhere in the hierarchy
                parent = self._find_subcategory_recursive(cat.get("subcategories", []), parent_subcat_id)
                
                if parent:
                    # Check if subcategory already exists
                    if self._find_subcategory_recursive(parent.get("subcategories", []), subcat_id):
                        return True
                    
                    nested_subcat = {
                        "id": subcat_id,
                        "name": subcat_name,
                        "url": subcat_url,
                        "description": "",
                        "image_url": "",
                        "image_local_path": "",
                        "subcategories": [],
                        "products": []
                    }
                    if "subcategories" not in parent:
                        parent["subcategories"] = []
                    parent["subcategories"].append(nested_subcat)
                    data["metadata"]["last_updated"] = datetime.now().isoformat()
                    self.save(data)
                    logger.info(f"Added nested subcategory to {parent_subcat_id}: {subcat_name}")
                    return True
        logger.warning(f"Parent subcategory not found: {parent_subcat_id}")
        return False
    
    def update_subcategory_image(self, category_id: str, subcat_id: str, image_url: str, local_path: str):
        """Update subcategory image data anywhere in the hierarchy"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                subcat = self._find_subcategory_recursive(cat.get("subcategories", []), subcat_id)
                if subcat:
                    subcat["image_url"] = image_url
                    subcat["image_local_path"] = local_path
                    self.save(data)
                    return True
        return False

    def update_subcategory_description(self, category_id: str, subcat_id: str, description: str):
        """Update subcategory description anywhere in the hierarchy"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                subcat = self._find_subcategory_recursive(cat.get("subcategories", []), subcat_id)
                if subcat:
                    subcat["description"] = description
                    self.save(data)
                    return True
        return False

    def update_category_image(self, category_id: str, image_url: str, local_path: str):
        """Update category image data"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                cat["image_url"] = image_url
                cat["image_local_path"] = local_path
                self.save(data)
                return True
        return False

    def update_category_description(self, category_id: str, description: str):
        """Update category description data"""
        data = self.load()
        for cat in data.get("categories", []):
             if cat.get("id") == category_id:
                 cat["description"] = description
                 self.save(data)
                 return True
        return False

    def add_product_to_subcategory(self, category_id: str, parent_subcat_id: str, product_id: str, product_name: str, product_url: str):
        """Add product to any level subcategory"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                # Find the parent subcategory anywhere in the hierarchy
                subcat = self._find_subcategory_recursive(cat.get("subcategories", []), parent_subcat_id)
                
                if subcat:
                    if "products" not in subcat:
                        subcat["products"] = []
                    
                    # Check if product already exists
                    for existing_prod in subcat["products"]:
                        if existing_prod.get("id") == product_id:
                            return True
                    
                    product = {
                        "id": product_id,
                        "name": product_name,
                        "url": product_url,
                        "title": None,
                        "description": None,
                        "short_description": None,
                        "buy_info": {},
                        "full_details": None
                    }
                    subcat["products"].append(product)
                    data["metadata"]["total_products"] += 1
                    data["metadata"]["last_updated"] = datetime.now().isoformat()
                    self.save(data)
                    logger.info(f"Added product to {parent_subcat_id}: {product_name}")
                    return True
        logger.warning(f"Subcategory not found: {parent_subcat_id}")
        return False
    
    def update_product_details(self, category_id: str, parent_subcat_id: str, product_id: str, details: Dict[str, Any]):
        """Update product details anywhere in the hierarchy"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                subcat = self._find_subcategory_recursive(cat.get("subcategories", []), parent_subcat_id)
                if subcat:
                    for product in subcat.get("products", []):
                        if product.get("id") == product_id:
                            product.update(details)
                            data["metadata"]["last_updated"] = datetime.now().isoformat()
                            self.save(data)
                            logger.info(f"Updated product details: {product_id}")
                            return True
        logger.warning(f"Product or subcategory not found: {product_id}")
        return False
    
    def add_product(self, category_id: str, subcategory_id: str, product_data: Dict[str, Any]):
        """Add product to specific category and subcategory anywhere in the hierarchy"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                # Find the subcategory anywhere in the hierarchy
                subcat = self._find_subcategory_recursive(cat.get("subcategories", []), subcategory_id)
                
                if subcat:
                    if "products" not in subcat:
                        subcat["products"] = []
                    subcat["products"].append(product_data)
                    data["metadata"]["total_products"] += 1
                    data["metadata"]["last_updated"] = datetime.now().isoformat()
                    self.save(data)
                    logger.info(f"Added product: {product_data.get('name')}")
                    return
        logger.warning(f"Category or subcategory not found: {subcategory_id}")


class LinksProgressManager(JSONManager):
    """Manages scraping progress and links tracking"""
    
    def initialize_progress(self):
        """Initialize progress structure"""
        structure = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_scraped_at": None,
                "total_links_found": 0,
                "total_links_scraped": 0,
                "status": "initialized"
            },
            "categories": [],
            "failed_links": [],
            "pending_links": []
        }
        self.save(structure)
        logger.info("Initialized progress structure")
    
    def add_category_link(self, category_id: str, category_name: str, category_url: str):
        """Add category link to tracking"""
        data = self.load()
        cat_entry = {
            "id": category_id,
            "name": category_name,
            "url": category_url,
            "scraped": False,
            "subcategories": []
        }
        data["categories"].append(cat_entry)
        data["metadata"]["total_links_found"] += 1
        self.save(data)
        logger.info(f"Added category link: {category_name}")
    
    def add_subcategory_link(self, category_id: str, subcat_id: str, subcat_name: str, subcat_url: str):
        """Add subcategory link"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                subcat_entry = {
                    "id": subcat_id,
                    "name": subcat_name,
                    "url": subcat_url,
                    "scraped": False,
                    "products": []
                }
                cat["subcategories"].append(subcat_entry)
                data["metadata"]["total_links_found"] += 1
                self.save(data)
                logger.info(f"Added subcategory link: {subcat_name}")
                return
    
    def add_product_link(self, category_id: str, subcat_id: str, product_id: str, 
                        product_name: str, product_url: str):
        """Add product link"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                for subcat in cat.get("subcategories", []):
                    if subcat.get("id") == subcat_id:
                        product_entry = {
                            "id": product_id,
                            "name": product_name,
                            "url": product_url,
                            "scraped": False
                        }
                        subcat["products"].append(product_entry)
                        data["metadata"]["total_links_found"] += 1
                        self.save(data)
                        return
    
    def mark_category_scraped(self, category_id: str):
        """Mark category as scraped"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                cat["scraped"] = True
                data["metadata"]["total_links_scraped"] += 1
                data["metadata"]["last_scraped_at"] = datetime.now().isoformat()
                self.save(data)
                logger.info(f"Marked category as scraped: {category_id}")
                return
    
    def mark_subcategory_scraped(self, category_id: str, subcat_id: str):
        """Mark subcategory as scraped"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                for subcat in cat.get("subcategories", []):
                    if subcat.get("id") == subcat_id:
                        subcat["scraped"] = True
                        data["metadata"]["total_links_scraped"] += 1
                        data["metadata"]["last_scraped_at"] = datetime.now().isoformat()
                        self.save(data)
                        logger.info(f"Marked subcategory as scraped: {subcat_id}")
                        return
    
    def mark_product_scraped(self, category_id: str, subcat_id: str, product_id: str):
        """Mark product as scraped"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                for subcat in cat.get("subcategories", []):
                    if subcat.get("id") == subcat_id:
                        for product in subcat.get("products", []):
                            if product.get("id") == product_id:
                                product["scraped"] = True
                                data["metadata"]["last_scraped_at"] = datetime.now().isoformat()
                                self.save(data)
                                logger.info(f"Marked product as scraped: {product_id}")
                                return
    
    def get_pending_categories(self) -> List[Dict[str, Any]]:
        """Get all unscraped categories"""
        data = self.load()
        return [cat for cat in data.get("categories", []) if not cat.get("scraped", False)]
    
    def get_pending_subcategories(self, category_id: str) -> List[Dict[str, Any]]:
        """Get unscraped subcategories for a category"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                return [subcat for subcat in cat.get("subcategories", []) 
                       if not subcat.get("scraped", False)]
        return []
    
    def is_subcategory_scraped(self, category_id: str, subcat_id: str) -> bool:
        """Check if a subcategory is already marked as scraped"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                for subcat in cat.get("subcategories", []):
                    if subcat.get("id") == subcat_id:
                        return subcat.get("scraped", False)
        return False

    def is_product_scraped(self, category_id: str, subcat_id: str, product_id: str) -> bool:
        """Check if a product is already marked as scraped"""
        data = self.load()
        for cat in data.get("categories", []):
            if cat.get("id") == category_id:
                for subcat in cat.get("subcategories", []):
                    if subcat.get("id") == subcat_id:
                        for product in subcat.get("products", []):
                            if product.get("id") == product_id:
                                return product.get("scraped", False)
        return False

    def add_failed_link(self, url: str, reason: str):
        """Track failed links"""
        data = self.load()
        data["failed_links"].append({
            "url": url,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        self.save(data)
        logger.warning(f"Added failed link: {url} - {reason}")
