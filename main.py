from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import web_tools
import test_tools
from python_code_executor import execute_python_code
from starlette.applications import Starlette
from starlette.routing import Mount

# Create an MCP server
mcp = FastMCP("Demo")


@mcp.resource("notes://latest")
def get_csv() -> str:
    csv_path = "/Users/souymodip/GIT/example_csv/chart-3-100.csv"
    ret = ""
    with open(csv_path, 'r') as f:
        ret = f.read()
    return ret



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

# Create an ASGI app that serves MCP over SSE & HTTP
# app = Starlette(
#     routes=[
#         # Mount all the MCP endpoints (SSE and /messages) at the root
#         Mount("/", app=mcp.sse_app()),
#     ]
# )

# Optional: if you still want to run via mcp.run() when invoked directly
if __name__ == "__main__":
    mcp.run()

