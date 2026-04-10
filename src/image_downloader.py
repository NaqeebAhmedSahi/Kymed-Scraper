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
    
    def download_image(self, image_url: str, sub_path: str = "", filename: str = "", timeout: int = 10) -> Optional[str]:
        """
        Download image from URL and save locally
        
        Args:
            image_url: URL of the image
            sub_path: Sub-directory path (e.g., "Category/Subcategory")
            filename: Preferred filename (e.g., product title)
            timeout: Request timeout in seconds
            
        Returns:
            Local file path relative to images_dir, or None if failed
        """
        if not image_url or not isinstance(image_url, str):
            logger.warning(f"Invalid image URL: {image_url}")
            return None
        
        try:
            # Prepare directory
            target_dir = self.images_dir
            if sub_path:
                target_dir = self.images_dir / self._sanitize_path(sub_path)
                target_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare filename
            if not filename:
                filename = self._generate_unique_filename(image_url)
            else:
                filename = self._sanitize_filename(filename, image_url)
            
            filepath = target_dir / filename
            rel_path = f"images/{self._sanitize_path(sub_path)}/{filename}".replace("//", "/")
            
            # Skip if already downloaded
            if filepath.exists():
                logger.debug(f"Image already exists: {rel_path}")
                return rel_path
            
            # Download image with headers to avoid 403 Forbidden
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://agnthos.se/'
            }
            response = requests.get(image_url, headers=headers, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Post-download validation: if too small, it's likely a captcha stub
            if filepath.stat().st_size < 1024:
                logger.warning(f"        [WARN] Direct download returned suspiciously small file ({filepath.stat().st_size} bytes). Deleting.")
                filepath.unlink()
                return None

            logger.info(f"Downloaded image: {rel_path} ({filepath.stat().st_size} bytes)")
            return rel_path
            
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

    def download_via_canvas(self, driver, image_url: str, sub_path: str = "", filename: str = "") -> Optional[str]:
        """
        Download image by loading it into an <img> tag and drawing to a <canvas>.
        This is a highly resilient method as it mimics actual browser rendering.
        """
        if not image_url:
            return None

        try:
            # Prepare directory and filename
            target_dir = self.images_dir
            if sub_path:
                target_dir = self.images_dir / self._sanitize_path(sub_path)
                target_dir.mkdir(parents=True, exist_ok=True)
            
            if not filename:
                filename = self._generate_unique_filename(image_url)
            else:
                filename = self._sanitize_filename(filename, image_url)
            
            filepath = target_dir / filename
            rel_path = f"images/{self._sanitize_path(sub_path)}/{filename}".replace("//", "/")

            # JavaScript to load image and extract via canvas
            # We use an async script to handle the image load
            js_script = """
            var url = arguments[0];
            var callback = arguments[arguments.length - 1];
            
            var img = new Image();
            img.crossOrigin = "anonymous"; 
            img.onload = function() {
                var canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                try {
                    var dataURL = canvas.toDataURL('image/jpeg', 0.95);
                    callback(dataURL.split(',')[1]);
                } catch (err) {
                    callback("ERROR: Canvas failed: " + err.message);
                }
            };
            img.onerror = function() {
                callback("ERROR: Image failed to load at " + url);
            };
            img.src = url;
            """
            
            logger.info(f"        [CANVAS] Downloading via Canvas: {image_url}")
            driver.set_script_timeout(30)
            base64_data = driver.execute_async_script(js_script, image_url)
            
            # If CORS failed, try without crossOrigin
            if isinstance(base64_data, str) and "Canvas failed" in base64_data:
                logger.warning("        [WARN] Canvas tainted, trying without crossOrigin...")
                js_script_no_cors = js_script.replace('img.crossOrigin = "anonymous";', '')
                base64_data = driver.execute_async_script(js_script_no_cors, image_url)

            if isinstance(base64_data, str) and base64_data.startswith("ERROR"):
                logger.error(f"        [FAIL] Canvas download failed: {base64_data}")
                return None
            
            import base64
            img_data = base64.b64decode(base64_data)
            
            if len(img_data) < 1024:
                logger.warning(f"        [WARN] Canvas returned small file ({len(img_data)} bytes).")
                return None

            # Save the file
            with open(filepath, 'wb') as f:
                f.write(img_data)
            
            logger.info(f"        [OK] Saved via Canvas: {rel_path} ({len(img_data)} bytes)")
            return rel_path

        except Exception as e:
            logger.error(f"        [ERROR] Canvas download failed: {e}")
            return None

    def download_via_browser(self, driver, image_url: str, sub_path: str = "", filename: str = "", retries: int = 2) -> Optional[str]:
        """
        Download image using the browser's fetch API and save locally.
        This bypasses most bot protections since it uses the browser's active session.
        """
        if not image_url:
            return None

        try:
            # Prepare directory and filename
            target_dir = self.images_dir
            if sub_path:
                target_dir = self.images_dir / self._sanitize_path(sub_path)
                target_dir.mkdir(parents=True, exist_ok=True)
            
            if not filename:
                filename = self._generate_unique_filename(image_url)
            else:
                filename = self._sanitize_filename(filename, image_url)
            
            filepath = target_dir / filename
            rel_path = f"images/{self._sanitize_path(sub_path)}/{filename}".replace("//", "/")

            # Use javascript to fetch image data as base64
            # We use credentials: 'include' to ensure session cookies are sent
            js_script = """
            var url = arguments[0];
            var callback = arguments[arguments.length - 1];
            
            async function attemptFetch(retriesLeft) {
                try {
                    const response = await fetch(url, { credentials: 'include' });
                    if (!response.ok) {
                        if (response.status === 403 && retriesLeft > 0) {
                            // Wait a bit and retry on 403
                            await new Promise(r => setTimeout(r, 1000));
                            return attemptFetch(retriesLeft - 1);
                        }
                        throw new Error('HTTP error, status = ' + response.status);
                    }
                    const blob = await response.blob();
                    const reader = new FileReader();
                    reader.onloadend = () => callback(reader.result.split(',')[1]);
                    reader.onerror = () => callback("ERROR: FileReader failed");
                    reader.readAsDataURL(blob);
                } catch (err) {
                    if (retriesLeft > 0) {
                        await new Promise(r => setTimeout(r, 1000));
                        return attemptFetch(retriesLeft - 1);
                    }
                    callback("ERROR: " + err.message);
                }
            }
            
            attemptFetch(arguments[1]);
            """
            
            logger.info(f"        [BROWSER] Downloading via JS: {image_url}")
            # Set a long timeout for the script to ensure image loads
            driver.set_script_timeout(45)
            base64_data = driver.execute_async_script(js_script, image_url, retries)
            
            if isinstance(base64_data, str) and base64_data.startswith("ERROR"):
                logger.error(f"        [FAIL] JS Image download failed: {base64_data}")
                return None
            
            import base64
            img_data = base64.b64decode(base64_data)
            
            # Post-download validation: if too small, it's likely a captcha stub
            if len(img_data) < 1024:
                logger.warning(f"        [WARN] Browser download returned suspiciously small file ({len(img_data)} bytes).")
                return None

            # Save the file
            with open(filepath, 'wb') as f:
                f.write(img_data)
            
            logger.info(f"        [OK] Saved via browser: {rel_path} ({len(img_data)} bytes)")
            return rel_path

        except Exception as e:
            logger.error(f"        [ERROR] Browser download failed: {e}")
            return None
    
    def _sanitize_path(self, path_str: str) -> str:
        """Sanitize directory names"""
        import re
        # Remove invalid chars for directory names
        return "/".join([re.sub(r'[<>:"/\\|?*]', '', p.replace(' ', '_')).strip('_') for p in path_str.split('/')])

    def _sanitize_filename(self, filename: str, url: str) -> str:
        """Sanitize filename and keep extension"""
        import re
        import os
        ext = self._get_extension(url)
        # Remove invalid chars
        clean_name = re.sub(r'[<>:"/\\|?*]', '', filename.replace(' ', '_')).strip('_')
        if not clean_name:
            return self._generate_unique_filename(url)
        return f"{clean_name}.{ext}"

    def _get_extension(self, url: str) -> str:
        """Extract extension from URL"""
        try:
            path = urlparse(url).path
            if '.' in path:
                ext = path.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    return ext
            return 'jpg'
        except:
            return 'jpg'

    def _generate_unique_filename(self, url: str) -> str:
        """Generate a unique filename from URL"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            return f"{url_hash}.{self._get_extension(url)}"
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
