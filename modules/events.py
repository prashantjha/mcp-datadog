from typing import Optional, Dict, Any
from pydantic import Field
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.events_api import EventsApi
from config import configuration
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Events Service")

@mcp.tool()
def delete_event(
    event_id: int = Field(..., description="The ID of the event to delete")
) -> Dict[str, Any]:
    """Delete a specific event."""
    try:
        with ApiClient(configuration) as api_client:
            events_api = EventsApi(api_client)
            events_api.delete_event(event_id)
            return {"status": "success", "message": "Event deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting event: {e}"}
