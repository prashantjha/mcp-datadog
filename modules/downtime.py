from pydantic import BaseModel, Field
import json
import time
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.downtimes_api import DowntimesApi
from config import configuration, logger
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Dashboards and Downtime Service")



class DowntimeResponse(BaseModel):
    id: int
    scope: str
    message: str
    start: int
    end: int


import logging
logger = logging.getLogger(__name__)

@mcp.tool()
def list_downtimes(
    current_only: bool = Field(default=False, description="List only currently active downtimes")
) -> dict:
    """Retrieves a list of Datadog scheduled downtimes."""
    logger.info("Starting list_downtimes")
    try:
        with ApiClient(configuration) as api_client:
            downtimes_api = DowntimesApi(api_client)
            response = downtimes_api.list_downtimes(current_only=current_only)

            if not response:
                result = {
                    "content": {
                        "downtimes": [],
                        "total": 0,
                        "message": "No downtimes found."
                    }
                }
                logger.info("No downtimes found.")
                return result

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
            logger.info("Successfully retrieved downtimes.")
            return result
    except Exception as e:
        logger.error(f"Failed to retrieve downtimes: {e}", exc_info=True)
        return {
            "content": {
                "downtimes": [],
                "total": 0,
                "message": f"Error fetching downtimes: {e}"
            }
        }
    finally:
        logger.info("Exiting list_downtimes")
