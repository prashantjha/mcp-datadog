import json
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.hosts_api import HostsApi
from config import configuration, logger
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Host Service")

import logging
logger = logging.getLogger(__name__)

@mcp.tool()
def get_host_list() -> dict:
    """Retrieves a list of hosts from Datadog."""
    logger.info("Starting get_host_list")
    try:
        with ApiClient(configuration) as api_client:
            hosts_api = HostsApi(api_client)
            response = hosts_api.list_hosts()

            hosts_data = [
                {"id": host.id, "name": host.name, "status": host.up}
                for host in response.host_list
            ]

            result = {"content": [{"type": "text", "text": json.dumps(hosts_data, indent=2)}]}
            logger.info("Successfully retrieved hosts.")
            return result

    except Exception as e:
        logger.error(f"Failed to retrieve hosts: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error fetching hosts: {e}"}]}
    finally:
        logger.info("Exiting get_host_list")
