from mcp.server.fastmcp import FastMCP
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
import os
import logging

# Initialize a separate MCP instance for monitors
mcp = FastMCP("Datadog Monitor Service")

# Configure Datadog API
configuration = Configuration()
configuration.api_key["apiKeyAuth"] = os.getenv("DATADOG_API_KEY")
configuration.api_key["appKeyAuth"] = os.getenv("DATADOG_APP_KEY")
configuration.server_variables["site"] = os.getenv("DATADOG_SITE", "datadoghq.com")

# Configure logging
logging.basicConfig(level=logging.INFO)
import json

logger = logging.getLogger(__name__)

@mcp.tool()
def get_monitor_status(name: str = None, group_states: list[str] = None, tags: list[str] = None) -> dict:
    """Fetch Datadog monitor status."""
    logger.info("Starting get_monitor_status")
    group_states = group_states or []
    tags = tags or []

    try:
        with ApiClient(configuration) as api_client:
            monitors_api = MonitorsApi(api_client)
            response = monitors_api.list_monitors(
                group_states=','.join(group_states) if group_states else None,
                name=name,
                tags=','.join(tags) if tags else None
            )

            if not response:
                raise ValueError("No monitor data returned from Datadog API.")

            monitors_data = [
                {
                    "name": monitor.name or "",
                    "id": monitor.id or 0,
                    "status": str(monitor.overall_state).lower() if monitor.overall_state else "unknown",
                    "message": monitor.message,
                    "tags": monitor.tags or [],
                    "query": monitor.query or "",
                    "last_updated_ts": int(monitor.modified.timestamp()) if monitor.modified else None,
                }
                for monitor in response
            ]

            summary = {status: 0 for status in ["alert", "warn", "no_data", "ok", "ignored", "skipped", "unknown"]}
            for monitor in response:
                status = str(monitor.overall_state).lower() if monitor.overall_state else "unknown"
                summary[status] = summary.get(status, 0) + 1

            result = {
                "content": [
                    {"type": "text", "text": "Datadog Monitors:\n" + json.dumps(monitors_data, indent=2)},
                    {"type": "text", "text": "Monitor Status Summary:\n" + json.dumps(summary, indent=2)},
                ]
            }
            logger.info("Completed get_monitor_status successfully")
            return result

    except Exception as e:
        logger.error(f"Failed to retrieve monitor status: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error fetching monitor status: {e}"}]}
    finally:
        logger.info("Exiting get_monitor_status")
