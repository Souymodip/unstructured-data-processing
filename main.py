from mcp.server.fastmcp import FastMCP
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
from urllib.parse import urlparse, urljoin
from typing import List, Optional, Union
import logging

# Create an MCP server
mcp = FastMCP("Demo")

NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.txt")


def ensure_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")


@mcp.tool()
def add_note(message: str) -> str:
    """
    Append a new note to the sticky note file.

    Args:
        message (str): The note content to be added.

    Returns:
        str: Confirmation message indicating the note was saved.
    """
    ensure_file()
    with open(NOTES_FILE, "a") as f:
        f.write(message + "\n")
    return "Note saved!"


@mcp.tool()
def read_notes() -> str:
    """
    Read and return all notes from the sticky note file.

    Returns:
        str: All notes as a single string separated by line breaks.
             If no notes exist, a default message is returned.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    return content or "No notes yet."


@mcp.resource("notes://latest")
def get_latest_note() -> str:
    """
    Get the most recently added note from the sticky note file.

    Returns:
        str: The last note entry. If no notes exist, a default message is returned.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        lines = f.readlines()
    return lines[-1].strip() if lines else "No notes yet."


@mcp.prompt()
def note_summary_prompt() -> str:
    """
    Generate a prompt asking the AI to summarize all current notes.

    Returns:
        str: A prompt string that includes all notes and asks for a summary.
             If no notes exist, a message will be shown indicating that.
    """
    ensure_file()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    if not content:
        return "There are no notes yet."

    return f"Summarize the current notes: {content}"


@mcp.tool()
def web_search(query: str, max_results: int = 3) -> str:
    """
    Search the internet for information related to the given query and return relevant results.

    This tool performs a web search, fetches the top results, extracts content from those pages,
    and returns a summary of the most relevant information found.

    Args:
        query (str): The search query to look up on the internet.
        max_results (int, optional): Maximum number of web pages to analyze. Defaults to 3.

    Returns:
        str: A compilation of relevant information found from the search results,
             including source URLs and snippets of content.
    """
    # Encode the query for URL
    encoded_query = quote_plus(query)

    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Perform the search using a search engine
    search_url = f"https://www.google.com/search?q={encoded_query}"
    try:
        search_response = requests.get(search_url, headers=headers, timeout=10)
        search_response.raise_for_status()
    except Exception as e:
        return f"Error performing search: {str(e)}"

    # Parse the search results to extract links
    soup = BeautifulSoup(search_response.text, 'html.parser')
    result_links = []

    # Extract links from Google search results
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/url?q='):
            # Extract actual URL from Google's redirect URL
            url = href.split('/url?q=')[1].split('&')[0]
            if not any(domain in url for domain in ['google.', 'youtube.']):
                result_links.append(url)

    # Limit to the specified number of results
    result_links = result_links[:max_results]

    if not result_links:
        return "No relevant results found for the query."

    # Process each link to extract relevant content
    results = []
    for i, url in enumerate(result_links):
        try:
            # Fetch the webpage
            page_response = requests.get(url, headers=headers, timeout=10)
            page_response.raise_for_status()

            # Parse the content
            page_soup = BeautifulSoup(page_response.text, 'html.parser')

            # Extract the title
            title = page_soup.title.string if page_soup.title else "No title found"

            # Extract main content (this is a simplified approach)
            # Remove script and style elements
            for script in page_soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = page_soup.get_text(separator=' ', strip=True)

            # Clean up text (remove extra whitespace)
            text = re.sub(r'\s+', ' ', text).strip()

            # Limit the content length
            max_content_length = 500
            content = text[:max_content_length] + "..." if len(text) > max_content_length else text

            # Add to results
            results.append(f"Source {i + 1}: {url}\nTitle: {title}\nContent snippet: {content}\n")

        except Exception as e:
            results.append(f"Source {i + 1}: {url}\nError extracting content: {str(e)}\n")

    # Combine all results
    combined_results = f"Search results for: '{query}'\n\n" + "\n".join(results)

    return combined_results


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

