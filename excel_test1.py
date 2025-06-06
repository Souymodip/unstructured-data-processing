import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from urllib.parse import urlparse, urljoin
from typing import List, Optional, Union
import logging


def download_from_index_page(
        url: str,
        extensions: Optional[List[str]] = None,
        download_folder: str = "downloaded_data",
        base_url: Optional[str] = None
) -> List[str]:
    """
    MCP server tool to download files with specified extensions from a web page.

    This tool scrapes a given index/start page for links to files with the specified
    extensions, creates a local folder, and downloads all the matching files.

    Args:
        url (str): The URL of the index/start page to scrape for file links.
        extensions (List[str], optional): List of file extensions to download.
            Defaults to [".pdf", ".xlsx", ".csv", ".xls"].
        download_folder (str, optional): Name of the folder to store downloaded files.
            Defaults to "downloaded_data".
        base_url (str, optional): Base URL to prepend to relative links.
            If not provided, it will be extracted from the input URL.

    Returns:
        List[str]: List of paths to the successfully downloaded files.

    Example:
        >>> download_from_index_page(
        ...     "https://www.mlit.go.jp/kankocho/tokei_hakusyo/shukuhakutokei.html",
        ...     extensions=[".pdf", ".xlsx"],
        ...     download_folder="mlit_data"
        ... )
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Set default extensions if none provided
    if extensions is None:
        extensions = [".pdf", ".xlsx", ".csv", ".xls"]

    # Ensure extensions have leading dots
    extensions = [ext if ext.startswith('.') else '.' + ext for ext in extensions]

    # Determine base URL if not provided
    if base_url is None:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    logging.info(f"Scraping index page: {url}")
    logging.info(f"Looking for files with extensions: {extensions}")

    # Create download directory
    os.makedirs(download_folder, exist_ok=True)
    logging.info(f"Download folder created: {download_folder}")

    # Fetch and parse the index page
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch index page: {e}")
        return []

    # Find all links
    links = soup.find_all("a")
    logging.info(f"Found {len(links)} links on the page")

    # Filter links with desired extensions
    data_links = []
    for link in links:
        if not link.has_attr('href'):
            continue

        href = link["href"]

        # Check if the link ends with any of the specified extensions
        if any(href.lower().endswith(ext.lower()) for ext in extensions):
            data_links.append(link)

    logging.info(f"Found {len(data_links)} links with specified extensions")

    # Process and download each file
    downloaded_files = []
    for i, link in enumerate(data_links, 1):
        href = link["href"]

        # Handle relative vs absolute URLs
        if href.startswith(('http://', 'https://')):
            full_url = href
        elif href.startswith('/'):
            full_url = urljoin(base_url, href)
        else:
            # Handle relative paths that don't start with '/'
            full_url = urljoin(url, href)

        # Get filename from URL
        filename = os.path.basename(urlparse(full_url).path)

        # Handle special characters or empty filenames
        if not filename or len(filename) <= 1:
            filename = f"file_{i}{os.path.splitext(href)[1]}"

        file_path = os.path.join(download_folder, filename)

        # Download the file
        try:
            logging.info(f"[{i}/{len(data_links)}] Downloading: {full_url} -> {file_path}")
            file_response = requests.get(full_url, stream=True, timeout=60)
            file_response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            downloaded_files.append(file_path)
            logging.info(f"✓ Successfully downloaded: {filename}")

        except Exception as e:
            logging.error(f"✗ Failed to download {full_url}: {e}")

    logging.info(f"Download completed. {len(downloaded_files)}/{len(data_links)} files downloaded to {download_folder}")
    return downloaded_files


if __name__ == "__main__":
    download_from_index_page(url="https://www.mlit.go.jp/kankocho/tokei_hakusyo/shukuhakutokei.html")
