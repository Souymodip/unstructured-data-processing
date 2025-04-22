from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import web_tools
import test_tools
from python_code_executor import execute_python_code
from starlette.applications import Starlette
from starlette.routing import Mount

# Create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def add_note(message: str) -> str:
    """
    Append a new note to the sticky note file.

    Args:
        message (str): The note content to be added.

    Returns:
        str: Confirmation message indicating the note was saved.
    """
    return test_tools.add_note(message)


@mcp.tool()
def read_notes() -> str:
    """
    Read and return all notes from the sticky note file.

    Returns:
        str: All notes as a single string separated by line breaks.
             If no notes exist, a default message is returned.
    """
    return test_tools.read_notes()


@mcp.resource("notes://latest")
def get_latest_note() -> str:
    """
    Get the most recently added note from the sticky note file.

    Returns:
        str: The last note entry. If no notes exist, a default message is returned.
    """
    return test_tools.get_latest_note()


@mcp.prompt()
def note_summary_prompt() -> str:
    """
    Generate a prompt asking the AI to summarize all current notes.

    Returns:
        str: A prompt string that includes all notes and asks for a summary.
             If no notes exist, a message will be shown indicating that.
    """
    return test_tools.note_summary_prompt()


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
    return web_tools.web_search(query, max_results)


@mcp.tool()
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
    return web_tools.download_from_index_page(url, extensions, download_folder, base_url)


@mcp.tool()
def run_python(code: str, timeout: int = 30) -> str:
    """
    Execute Python code provided as a string and return the results.

    Args:
        code (str): The Python code to execute.
        timeout (int, optional): Maximum execution time in seconds. Defaults to 30.

    Returns:
        str: A formatted string with execution results including stdout,
             stderr if applicable, and any error messages.
    """
    # Execute the code
    result = execute_python_code(code, timeout)

    # Format the output
    output_parts = []

    if result['success']:
        output_parts.append("✅ Code executed successfully")
    else:
        output_parts.append("❌ Execution failed")

    if result['stdout']:
        output_parts.append("\n📤 Standard Output:\n" + result['stdout'])
    else:
        output_parts.append("\n📤 Standard Output: <no output>")

    if not result['success']:
        error_msg = result['exception']['type'] + ": " + result['exception']['message']
        output_parts.append("\n⚠️ Error:\n" + error_msg)

        if result['exception']['traceback']:
            output_parts.append("\n🔍 Traceback:\n" + result['exception']['traceback'])

    # For debugging purposes, you might want to include globals
    # output_parts.append("\nGlobals:\n" + str(result['globals']))

    return "\n".join(output_parts)

# … your mcp = FastMCP("Demo") and all @mcp.tool()/@mcp.resource()/@mcp.prompt() …

# Create an ASGI app that serves MCP over SSE & HTTP
app = Starlette(
    routes=[
        # Mount all the MCP endpoints (SSE and /messages) at the root
        Mount("/", app=mcp.sse_app()),
    ]
)

# Optional: if you still want to run via mcp.run() when invoked directly
if __name__ == "__main__":
    mcp.run()

