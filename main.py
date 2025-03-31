import logging
import sys
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', stream=sys.stderr) # Redirect logs to stderr

from mcp.server.fastmcp import FastMCP
from modules import mcp_tools  # Import tool functions

from config import DATADOG_API_KEY, DATADOG_APP_KEY, DATADOG_SITE  # Import API keys

# Initialize MCP server
mcp = FastMCP("Datadog Integration Service")

for tool in mcp_tools:
    mcp.tool()(tool)



@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

if __name__ == "__main__":
    mcp.run()
