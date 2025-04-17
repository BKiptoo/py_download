import os
import sys
import logging
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Validate if the provided URL is well-formed."""
    try:
        result = requests.head(url, allow_redirects=True, timeout=5)
        return result.status_code == 200
    except requests.RequestException:
        return False

def download_file(url, folder_path, progress_bar=None):
    """Download a single file from the given URL."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))
            # Ensure filename is valid
            if not filename or filename.endswith('/'):
                filename = os.path.join(folder_path, 'unnamed_file')
            # Handle duplicate filenames
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filename):
                filename = f"{base}_{counter}{ext}"
                counter += 1
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.info(f"Downloaded: {filename}")
            if progress_bar:
                progress_bar.update(1)
        else:
            logger.warning(f"Failed to download: {url} - Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")

def download_resources(url, folder_path, max_workers=4):
    """Download HTML and associated resources from the given URL."""
    try:
        # Validate URL
        if not is_valid_url(url):
            logger.error(f"Invalid or unreachable URL: {url}")
            return

        # Create necessary directories
        for subfolder in ['html', 'img', 'script', 'stylesheet']:
            os.makedirs(os.path.join(folder_path, subfolder), exist_ok=True)

        # Fetch and save HTML
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch HTML from {url} - Status code: {response.status_code}")
            return

        html_filename = os.path.join(folder_path, 'html', 'index.html')
        with open(html_filename, 'wb') as html_file:
            html_file.write(response.content)
        logger.info(f"Downloaded HTML: {html_filename}")

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        resources = []

        # Collect resources
        for tag in soup.find_all(['img', 'script', 'link']):
            resource_url = None
            resource_type = tag.name

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

        # Download resources concurrently with progress bar
        with tqdm(total=len(resources), desc="Downloading resources") as pbar:
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
                    future.result()

    except Exception as e:
        logger.error(f"Error processing {url}: {e}")

def main():
    """Main function to handle command-line arguments and initiate scraping."""
    parser = argparse.ArgumentParser(description="Web resource downloader")
    parser.add_argument('url', help="URL of the webpage to download")
    parser.add_argument(
        '-o', '--output',
        default='downloaded_files',
        help="Output folder path (default: downloaded_files)"
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help="Number of concurrent download workers (default: 4)"
    )
    args = parser.parse_args()

    download_resources(args.url, args.output, args.workers)

if __name__ == "__main__":
    main()
