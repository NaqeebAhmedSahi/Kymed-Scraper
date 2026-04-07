"""
Data Analysis Utility - Analyze scraped data and generate statistics
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PRODUCTS_JSON, LINKS_PROGRESS_JSON

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Analyzes scraped data and provides statistics"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.products_data = self._load_json(PRODUCTS_JSON)
        self.progress_data = self._load_json(LINKS_PROGRESS_JSON)
    
    @staticmethod
    def _load_json(filepath: Path) -> Dict[str, Any]:
        """Load JSON file"""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return {}
    
    def print_summary(self):
        """Print scraping summary statistics"""
        if not self.products_data:
            logger.warning("No product data found")
            return
        
        metadata = self.products_data.get('metadata', {})
        categories = self.products_data.get('categories', [])
        
        print("\n" + "=" * 80)
        print("SCRAPING SUMMARY")
        print("=" * 80)
        print(f"Website: {metadata.get('website')}")
        print(f"Last Updated: {metadata.get('last_updated')}")
        print(f"Scraping Status: {metadata.get('scraping_status')}")
        print(f"\nTotal Categories: {len(categories)}")
        print(f"Total Products: {metadata.get('total_products', 0)}")
        print()
        
        total_subcats = 0
        total_specs = 0
        
        for cat in categories:
            subcats = cat.get('subcategories', [])
            total_subcats += len(subcats)
            
            for subcat in subcats:
                products = subcat.get('products', [])
                for prod in products:
                    specs = prod.get('specifications', [])
                    total_specs += len(specs)
        
        print(f"Total Subcategories: {total_subcats}")
        print(f"Total Specifications: {total_specs}")
    
    def print_category_breakdown(self):
        """Print detailed breakdown by category"""
        categories = self.products_data.get('categories', [])
        
        if not categories:
            logger.warning("No categories found")
            return
        
        print("\n" + "=" * 80)
        print("CATEGORY BREAKDOWN")
        print("=" * 80)
        
        for cat in categories:
            cat_name = cat.get('name')
            subcats = cat.get('subcategories', [])
            total_products = sum(len(s.get('products', [])) for s in subcats)
            
            print(f"\n📁 {cat_name}")
            print(f"   Subcategories: {len(subcats)}")
            print(f"   Total Products: {total_products}")
            
            for subcat in subcats:
                subcat_name = subcat.get('name')
                products = subcat.get('products', [])
                print(f"   ├─ {subcat_name}: {len(products)} products")
    
    def print_scraping_progress(self):
        """Print scraping progress statistics"""
        if not self.progress_data:
            logger.warning("No progress data found")
            return
        
        metadata = self.progress_data.get('metadata', {})
        failed = self.progress_data.get('failed_links', [])
        
        print("\n" + "=" * 80)
        print("SCRAPING PROGRESS")
        print("=" * 80)
        print(f"Created At: {metadata.get('created_at')}")
        print(f"Last Scraped: {metadata.get('last_scraped_at')}")
        print(f"Total Links Found: {metadata.get('total_links_found')}")
        print(f"Total Links Scraped: {metadata.get('total_links_scraped')}")
        print(f"Status: {metadata.get('status')}")
        print(f"Failed Links: {len(failed)}")
        
        if failed:
            print(f"\n⚠ Failed Links ({len(failed)}):")
            for item in failed[:10]:  # Show first 10
                print(f"  - {item.get('url')}: {item.get('reason')}")
            if len(failed) > 10:
                print(f"  ... and {len(failed) - 10} more")
    
    def export_csv_summary(self, output_path: Path = None):
        """Export categories and products as CSV"""
        if output_path is None:
            output_path = Path("data/products_export.csv")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # CSV header
                f.write("Category,Subcategory,Product,URL,Image,Specifications Count\n")
                
                categories = self.products_data.get('categories', [])
                for cat in categories:
                    cat_name = cat.get('name')
                    for subcat in cat.get('subcategories', []):
                        subcat_name = subcat.get('name')
                        for prod in subcat.get('products', []):
                            prod_name = prod.get('name')
                            prod_url = prod.get('url')
                            prod_image = prod.get('image_local_path', '')
                            spec_count = len(prod.get('specifications', []))
                            
                            # Escape quotes
                            cat_name_esc = cat_name.replace('"', '""')
                            subcat_name_esc = subcat_name.replace('"', '""')
                            prod_name_esc = prod_name.replace('"', '""')
                            
                            f.write(f'"{cat_name_esc}","{subcat_name_esc}","{prod_name_esc}","{prod_url}","{prod_image}",{spec_count}\n')
            
            logger.info(f"CSV export saved to {output_path}")
            print(f"\n✓ CSV export saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
    
    def list_categories(self):
        """List all categories"""
        categories = self.products_data.get('categories', [])
        
        print("\n" + "=" * 80)
        print("CATEGORIES LIST")
        print("=" * 80)
        
        for idx, cat in enumerate(categories, 1):
            print(f"{idx}. {cat.get('name')} (ID: {cat.get('id')})")
            print(f"   URL: {cat.get('url')}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze scraped data')
    parser.add_argument('--summary', action='store_true', help='Print summary statistics')
    parser.add_argument('--breakdown', action='store_true', help='Print category breakdown')
    parser.add_argument('--progress', action='store_true', help='Print scraping progress')
    parser.add_argument('--export-csv', action='store_true', help='Export to CSV')
    parser.add_argument('--list-categories', action='store_true', help='List all categories')
    parser.add_argument('--all', action='store_true', help='Print everything')
    
    args = parser.parse_args()
    
    analyzer = DataAnalyzer()
    
    if args.all or not any([args.summary, args.breakdown, args.progress, args.export_csv, args.list_categories]):
        # Default: print everything
        analyzer.print_summary()
        analyzer.print_category_breakdown()
        analyzer.print_scraping_progress()
    else:
        if args.summary:
            analyzer.print_summary()
        if args.breakdown:
            analyzer.print_category_breakdown()
        if args.progress:
            analyzer.print_scraping_progress()
        if args.export_csv:
            analyzer.export_csv_summary()
        if args.list_categories:
            analyzer.list_categories()


if __name__ == '__main__':
    main()
