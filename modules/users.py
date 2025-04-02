from typing import Optional, Dict, Any
from pydantic import Field
from datadog_api_client import ApiClient
from datadog_api_client.v2.api.users_api import UsersApi
from config import configuration
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Users Service")

@mcp.tool()
def list_users() -> Dict[str, Any]:
    """List all users."""
    try:
        with ApiClient(configuration) as api_client:
            users_api = UsersApi(api_client)
            response = users_api.list_users()
            return {"status": "success", "message": "Users listed successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error listing users: {e}"}

@mcp.tool()
def get_user(
    user_id: str = Field(..., description="The ID of the user to retrieve")
) -> Dict[str, Any]:
    """Get details of a specific user."""
    try:
        with ApiClient(configuration) as api_client:
            users_api = UsersApi(api_client)
            response = users_api.get_user(user_id)
            return {"status": "success", "message": "User retrieved successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error retrieving user: {e}"}
