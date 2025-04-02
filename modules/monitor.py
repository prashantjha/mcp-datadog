from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
import os
from pydantic import Field

mcp = FastMCP("Datadog Monitor Service")

configuration = Configuration()
configuration.api_key["apiKeyAuth"] = os.getenv("DATADOG_API_KEY")
configuration.api_key["appKeyAuth"] = os.getenv("DATADOG_APP_KEY")
configuration.server_variables["site"] = os.getenv("DATADOG_SITE", "datadoghq.com")

@mcp.tool()
def create_monitor(
    name: str = Field(..., description="The name of the monitor"),
    type: str = Field(..., description="The type of the monitor (e.g., 'metric alert')"),
    query: str = Field(..., description="The query to evaluate for the monitor"),
    message: Optional[str] = Field(default=None, description="The message to include with notifications"),
    tags: Optional[List[str]] = Field(default=None, description="A list of tags to associate with the monitor")
) -> Dict[str, Any]:
    """Create a new monitor."""
    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            body = {
                "name": name,
                "type": type,
                "query": query,
                "message": message,
                "tags": tags or []
            }
            response = monitors_api.create_monitor(body=body)
            return {"status": "success", "message": "Monitor created successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error creating monitor: {e}"}

@mcp.tool()
def delete_monitor(
    monitor_id: int = Field(..., description="The ID of the monitor to delete")
) -> Dict[str, Any]:
    """Delete a specific monitor."""
    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            monitors_api.delete_monitor(monitor_id)
            return {"status": "success", "message": "Monitor deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting monitor: {e}"}

@mcp.tool()
def get_monitor(
    monitor_id: int = Field(..., description="The ID of the monitor to retrieve")
) -> Dict[str, Any]:
    """Retrieve details of a specific monitor."""
    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            response = monitors_api.get_monitor(monitor_id)
            return {"status": "success", "message": "Monitor retrieved successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error retrieving monitor: {e}"}

@mcp.tool()
def update_monitor(
    monitor_id: int = Field(..., description="The ID of the monitor to update"),
    name: Optional[str] = Field(default=None, description="The new name of the monitor"),
    query: Optional[str] = Field(default=None, description="The new query for the monitor"),
    message: Optional[str] = Field(default=None, description="The new message for the monitor"),
    tags: Optional[List[str]] = Field(default=None, description="The new tags for the monitor")
) -> Dict[str, Any]:
    """Update an existing monitor."""
    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            body = {}
            if name:
                body["name"] = name
            if query:
                body["query"] = query
            if message:
                body["message"] = message
            if tags:
                body["tags"] = tags
            response = monitors_api.update_monitor(monitor_id, body=body)
            return {"status": "success", "message": "Monitor updated successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error updating monitor: {e}"}
