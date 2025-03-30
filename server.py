import os
import json
import logging
from dotenv import load_dotenv
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.downtimes_api import DowntimesApi
from datadog_api_client.v1.api.hosts_api import HostsApi
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Datadog API Credentials
DATADOG_API_KEY = os.getenv("DATADOG_API_KEY")
DATADOG_APP_KEY = os.getenv("DATADOG_APP_KEY")
DATADOG_SITE = os.getenv("DATADOG_SITE", "datadoghq.com")  # Default to datadoghq.com

# Initialize Datadog API Configuration
configuration = Configuration()
configuration.api_key["apiKeyAuth"] = DATADOG_API_KEY
configuration.api_key["appKeyAuth"] = DATADOG_APP_KEY
configuration.server_variables["site"] = DATADOG_SITE
configuration.verify_ssl = True  # Enable SSL verification for production

# Initialize the MCP server
mcp = FastMCP("Datadog Integration Service")

@mcp.tool()
def get_monitor_status(name: str = None, group_states: list[str] = None, tags: list[str] = None) -> dict:
    """
    Retrieves the current status of Datadog monitors based on specified criteria.

    Args:
        name (str, optional): Filter monitors by name. Defaults to None.
        group_states (list[str], optional): Filter monitors by group states (e.g., ['Alert', 'OK']). Defaults to None.
        tags (list[str], optional): Filter monitors by tags. Defaults to None.

    Returns:
        dict: A dictionary containing a summary and detailed information about the retrieved monitors.
              The 'content' key holds a list of text-based reports.
    """
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

            summary = {
                "alert": 0,
                "warn": 0,
                "no_data": 0,
                "ok": 0,
                "ignored": 0,
                "skipped": 0,
                "unknown": 0,
            }
            for monitor in response:
                status = str(monitor.overall_state).lower() if monitor.overall_state else "unknown"
                summary[status] = summary.get(status, 0) + 1

            return {
                "content": [
                    {"type": "text", "text": "Datadog Monitors:\n" + json.dumps(monitors_data, indent=2)},
                    {"type": "text", "text": "Monitor Status Summary:\n" + json.dumps(summary, indent=2)},
                ]
            }

    except Exception as e:
        logger.error(f"Failed to retrieve monitor status: {e}")
        return {"content": [{"type": "text", "text": f"Error fetching monitor status: {e}"}]}

@mcp.tool()
def get_dashboard_list() -> dict:
    """
    Retrieves a list of all Datadog dashboards.

    Returns:
        dict: A dictionary containing a list of dashboards with their ID, title, URL, and description.
              The 'content' key holds a text-based report.
    """
    try:
        with ApiClient(configuration) as api_client:
            dashboards_api = DashboardsApi(api_client)
            response = dashboards_api.list_dashboards()

            if not response.dashboards:
                raise ValueError("No dashboard data returned from Datadog API.")

            dashboards_data = [
                {
                    "id": dashboard.id,
                    "title": dashboard.title,
                    "url": f"https://app.{DATADOG_SITE}/dashboard/{dashboard.id}",
                    "description": dashboard.description or "",
                }
                for dashboard in response.dashboards
            ]

            return {
                "content": [
                    {"type": "text", "text": "Datadog Dashboards:\n" + json.dumps(dashboards_data, indent=2)}
                ]
            }

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard list: {e}")
        return {"content": [{"type": "text", "text": f"Error fetching dashboards: {e}"}]}

@mcp.tool()
def get_downtime_list() -> dict:
    """
    Retrieves a list of currently scheduled downtimes in Datadog.

    Returns:
        dict: A dictionary containing a list of downtime schedules.
              The 'content' key holds a text-based report.
    """
    try:
        with ApiClient(configuration) as api_client:
            downtimes_api = DowntimesApi(api_client)
            response = downtimes_api.list_downtimes()

            downtimes_data = [
                {
                    "id": downtime.id,
                    "scope": downtime.scope,
                    "start": downtime.start,
                    "end": downtime.end,
                    "message": downtime.message,
                    "monitor_tags": downtime.monitor_tags,
                    "timezone": downtime.timezone,
                }
                for downtime in response
            ]

            return {
                "content": [
                    {"type": "text", "text": "Scheduled Downtimes:\n" + json.dumps(downtimes_data, indent=2)}
                ]
            }

    except Exception as e:
        logger.error(f"Failed to retrieve downtime list: {e}")
        return {"content": [{"type": "text", "text": f"Error fetching downtimes: {e}"}]}

@mcp.tool()
def get_host_list() -> dict:
    """
    Retrieves a list of hosts reporting to Datadog and their current up/down status.

    Returns:
        dict: A dictionary containing a list of hosts with their ID, name, and status.
              The 'content' key holds a text-based report.
    """
    try:
        with ApiClient(configuration) as api_client:
            hosts_api = HostsApi(api_client)
            response = hosts_api.list_hosts()

            hosts_data = [
                {
                    "id": host.id,
                    "name": host.name,
                    "status": host.up,
                }
                for host in response.host_list
            ]

            return {
                "content": [
                    {"type": "text", "text": "Datadog Hosts:\n" + json.dumps(hosts_data, indent=2)}
                ]
            }

    except Exception as e:
        logger.error(f"Failed to retrieve host list: {e}")
        return {"content": [{"type": "text", "text": f"Error fetching hosts: {e}"}]}

# Run the MCP server if the script is executed directly
if __name__ == "__main__":
    mcp.run()