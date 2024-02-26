import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_file(url, folder_path):
    try:
        # Send a GET request to download the file
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract filename from URL
            filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))
            # Save the file to the specified folder
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url} - Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def download_resources(url, folder_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            # Save the HTML file
            html_filename = os.path.join(folder_path, 'html', 'index.html')
            with open(html_filename, 'wb') as html_file:
                html_file.write(response.content)
            print(f"Downloaded HTML: {html_filename}")
            # Find all tags with src or href attributes
            tags = soup.find_all(['img', 'script', 'link'])
            for tag in tags:
                # Extract the URL from the src or href attribute
                if tag.get('src'):
                    resource_url = urljoin(url, tag['src'])
                elif tag.get('href'):
                    resource_url = urljoin(url, tag['href'])
                else:
                    continue
                # Determine resource type and folder
                resource_type = tag.name
                if resource_type == 'link':
                    resource_type = tag.get('type', 'stylesheet')
                resource_folder = os.path.join(folder_path, resource_type)
                # Create folder if it doesn't exist
                if not os.path.exists(resource_folder):
                    os.makedirs(resource_folder)
                # Download the resource
                download_file(resource_url, resource_folder)
        else:
            print(f"Failed to fetch HTML content from {url} - Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching HTML content from {url}: {e}")

def main():
    url = 'https://example.com/example/template/index.html'
    folder_path = 'downloaded_files'
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if not os.path.exists(os.path.join(folder_path, 'html')):
        os.makedirs(os.path.join(folder_path, 'html'))
    
    # Download resources
    download_resources(url, folder_path)

if __name__ == "__main__":
    main()
