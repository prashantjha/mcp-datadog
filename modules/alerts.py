from typing import Optional, Dict, Any
from pydantic import Field
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from config import configuration
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Alerts Service")

@mcp.tool()
def mute_alert(
    monitor_id: int = Field(..., description="The ID of the monitor to mute"),
    scope: Optional[str] = Field(default=None, description="The scope to mute"),
    end: Optional[int] = Field(default=None, description="The end time for the mute in epoch seconds")
) -> Dict[str, Any]:
    """Mute an alert for a specific monitor."""
    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            body = {"scope": scope, "end": end}
            response = monitors_api.mute_monitor(monitor_id, body=body)
            return {"status": "success", "message": "Alert muted successfully", "content": response.to_dict()}
    except ApiException as e:
        return {"status": "error", "message": f"API error while muting alert: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error while muting alert: {e}"}

@mcp.tool()
def unmute_alert(
    monitor_id: int = Field(..., description="The ID of the monitor to unmute")
) -> Dict[str, Any]:
    """Unmute an alert for a specific monitor."""
    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            response = monitors_api.unmute_monitor(monitor_id)
            return {"status": "success", "message": "Alert unmuted successfully", "content": response.to_dict()}
    except ApiException as e:
        return {"status": "error", "message": f"API error while unmuting alert: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error while unmuting alert: {e}"}
