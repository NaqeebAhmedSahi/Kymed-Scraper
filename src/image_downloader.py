"""
Image Downloader - Handles downloading and saving product images
"""
import logging
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)


class ImageDownloader:
    """Downloads and saves images locally"""
    
    def __init__(self, images_dir: Path):
        """
        Initialize image downloader
        
        Args:
            images_dir: Directory to save images
        """
        self.images_dir = images_dir
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def download_image(self, image_url: str, timeout: int = 10) -> Optional[str]:
        """
        Download image from URL and save locally
        
        Args:
            image_url: URL of the image
            timeout: Request timeout in seconds
            
        Returns:
            Local file path relative to images_dir, or None if failed
        """
        if not image_url or not isinstance(image_url, str):
            logger.warning(f"Invalid image URL: {image_url}")
            return None
        
        try:
            # Generate filename from URL
            filename = self._generate_filename(image_url)
            filepath = self.images_dir / filename
            
            # Skip if already downloaded
            if filepath.exists():
                logger.debug(f"Image already exists: {filename}")
                return f"images/{filename}"
            
            # Download image
            response = requests.get(image_url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filename}")
            return f"images/{filename}"
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout downloading image: {image_url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error downloading image: {image_url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error downloading image: {image_url} - {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading image: {image_url} - {e}")
            return None
    
    @staticmethod
    def _generate_filename(url: str) -> str:
        """
        Generate a unique filename from URL
        
        Args:
            url: Image URL
            
        Returns:
            Filename with extension
        """
        try:
            # Parse URL to get path
            parsed = urlparse(url)
            path = parsed.path
            
            # Extract extension
            if '.' in path:
                extension = path.split('.')[-1].lower()
                # Validate extension
                if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    pass
                else:
                    extension = 'jpg'
            else:
                extension = 'jpg'
            
            # Create hash from URL for unique filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            
            return f"{url_hash}.{extension}"
            
        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            return f"image_{hashlib.md5(url.encode()).hexdigest()[:8]}.jpg"
    
    def download_batch(self, image_urls: list) -> dict:
        """
        Download multiple images
        
        Args:
            image_urls: List of image URLs
            
        Returns:
            Dictionary mapping original URL to local path
        """
        results = {}
        
        for url in image_urls:
            local_path = self.download_image(url)
            if local_path:
                results[url] = local_path
        
        logger.info(f"Downloaded {len(results)}/{len(image_urls)} images")
        return results
