from pydantic import BaseModel, Field
import json
import time
import logging
import sys
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.downtimes_api import DowntimesApi
from config import configuration
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Datadog Dashboards and Downtime Service")

class DowntimeResponse(BaseModel):
    id: int
    scope: str
    message: str
    start: int
    end: int

@mcp.tool()
def list_downtimes(
    current_only: bool = Field(default=False, description="List only currently active downtimes")
) -> dict:
    """Retrieves a list of Datadog scheduled downtimes."""
    # logger.info("Starting list_downtimes")
    try:
        with ApiClient(configuration) as api_client:
            downtimes_api = DowntimesApi(api_client)
            response = downtimes_api.list_downtimes(current_only=current_only)

            if response is not None:
                downtimes_data = [
                    DowntimeResponse(
                        id=d.id,
                        scope=d.scope,
                        message=d.message or "No message provided",
                        start=d.start,
                        end=d.end or 0
                    ).dict()
                    for d in response
                ]

                result = {
                    "content": {
                        "downtimes": downtimes_data,
                        "total": len(downtimes_data),
                        "message": "Successfully retrieved downtimes."
                    }
                }
                # logger.info("Successfully retrieved downtimes.")
                return result
            else:
                result = {
                    "content": {
                        "downtimes": [],
                        "total": 0,
                        "message": "Error: Invalid response from Datadog API."
                    }
                }
                # logger.error("Invalid response from Datadog API.")
                return result
    except Exception as e:
        # logger.error(f"Failed to retrieve downtimes: {e}", exc_info=True)
        return {
            "content": {
                "downtimes": [],
                "total": 0,
                "message": f"Error fetching downtimes: {e}"
            }
        }
    finally:
        # logger.info("Exiting list_downtimes")
        pass
