import os
import sys
import logging
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# ----------------------------
# Logging Configuration
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------
# Utility Functions
# ----------------------------

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is reachable and valid.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"URL check failed: {e}")
        return False

def sanitize_filename(url: str, default_name: str = "unnamed_file") -> str:
    """
    Extract a clean filename from a URL, falling back to default if needed.
    """
    path = urlparse(url).path
    filename = os.path.basename(path)

    if not filename or filename.endswith('/'):
        filename = default_name

    # Decode URL-encoded filenames
    filename = unquote(filename)

    # Strip any query strings
    filename = filename.split('?')[0]

    return filename

def download_file(url: str, folder_path: str, progress_bar=None) -> None:
    """
    Download an individual file and save it to the appropriate folder.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            filename = sanitize_filename(url)
            full_path = os.path.join(folder_path, filename)

            # Handle duplicate filenames
            base, ext = os.path.splitext(full_path)
            counter = 1
            while os.path.exists(full_path):
                full_path = f"{base}_{counter}{ext}"
                counter += 1

            with open(full_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            logger.info(f"Downloaded: {full_path}")
            if progress_bar:
                progress_bar.update(1)
        else:
            logger.warning(f"Failed to download: {url} - Status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Request error while downloading {url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")

# ----------------------------
# Core Download Logic
# ----------------------------

def download_resources(url: str, folder_path: str, max_workers: int = 4) -> None:
    """
    Download the HTML of the page and all linked images, scripts, and stylesheets.
    """
    if not is_valid_url(url):
        logger.error(f"Invalid or unreachable URL: {url}")
        return

    try:
        # Create subdirectories for content
        for subfolder in ['html', 'img', 'script', 'stylesheet']:
            os.makedirs(os.path.join(folder_path, subfolder), exist_ok=True)

        # Fetch HTML
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch HTML from {url} - Status code: {response.status_code}")
            return

        # Save HTML locally
        html_path = os.path.join(folder_path, 'html', 'index.html')
        with open(html_path, 'wb') as html_file:
            html_file.write(response.content)
        logger.info(f"HTML saved to: {html_path}")

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        resources = []

        # Extract resources from HTML tags
        for tag in soup.find_all(['img', 'script', 'link']):
            resource_url = None
            resource_type = ''

            if tag.name == 'img' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_type = 'img'
            elif tag.name == 'script' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_type = 'script'
            elif tag.name == 'link' and tag.get('rel') == ['stylesheet'] and tag.get('href'):
                resource_url = urljoin(url, tag['href'])
                resource_type = 'stylesheet'

            if resource_url:
                resources.append((resource_url, resource_type))

        # Download all resources concurrently
        with tqdm(total=len(resources), desc="Downloading resources", unit="file") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        download_file,
                        resource_url,
                        os.path.join(folder_path, resource_type),
                        pbar
                    )
                    for resource_url, resource_type in resources
                ]
                for future in futures:
                    future.result()  # Ensure errors get raised and logged

    except Exception as e:
        logger.error(f"Failed to process URL '{url}': {e}")

# ----------------------------
# CLI Entry Point
# ----------------------------

def main():
    """
    Entry point for command-line execution.
    """
    parser = argparse.ArgumentParser(description="Download HTML and resources from a webpage")
    parser.add_argument('url', help="Target webpage URL")
    parser.add_argument('-o', '--output', default='downloaded_files', help="Output directory")
    parser.add_argument('-w', '--workers', type=int, default=4, help="Number of concurrent downloads")

    args = parser.parse_args()
    download_resources(args.url, args.output, args.workers)

# Run if executed directly
if __name__ == "__main__":
    main()
