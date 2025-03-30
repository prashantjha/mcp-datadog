from pydantic import BaseModel, Field
import json
import time
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from config import configuration, logger
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Dashboards Service")

class DashboardResponse(BaseModel):
    id: str
    title: str
    url: str

dashboard_list_schema = {
    "type": "object",
    "properties": {
        "dashboards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"}
                }
            }
        },
        "total": {"type": "integer"},
        "message": {"type": "string"}
    }
}

import logging
logger = logging.getLogger(__name__)

@mcp.tool()
def list_dashboards(
    name: str = Field(default=None, description="Filter dashboards by name"),
    tags: list[str] = Field(default=None, description="Filter dashboards by tags")
) -> dict:
    """Retrieves a list of Datadog dashboards with optional filtering by name and tags."""
    logger.info("Starting list_dashboards")
    try:
        with ApiClient(configuration) as api_client:
            dashboards_api = DashboardsApi(api_client)
            response = dashboards_api.list_dashboards(filter_shared=False)

            if not response.dashboards:
                result = {
                    "content": {
                        "dashboards": [],
                        "total": 0,
                        "message": "No dashboards found."
                    }
                }
                logger.info("No dashboards found.")
                return result

            # Apply filters if provided
            filtered_dashboards = response.dashboards
            if name:
                search_term = name.lower()
                filtered_dashboards = [
                    d for d in filtered_dashboards if d.title and search_term in d.title.lower()
                ]
            if tags:
                filtered_dashboards = [
                    d for d in filtered_dashboards if set(tags).issubset(set(d.tags or []))
                ]

            dashboards_data = [
                DashboardResponse(
                    id=d.id,
                    title=d.title,
                    url=f"https://app.datadoghq.com/dashboard/{d.id}"
                ).dict()
                for d in filtered_dashboards
            ]

            result = {
                "content": {
                    "dashboards": dashboards_data,
                    "total": len(dashboards_data),
                    "message": "Successfully retrieved dashboards."
                }
            }
            logger.info("Successfully retrieved dashboards.")
            return result
    except Exception as e:
        logger.error(f"Failed to retrieve dashboards: {e}", exc_info=True)
        return {
            "content": {
                "dashboards": [],
                "total": 0,
                "message": f"Error fetching dashboards: {e}"
            }
        }
    finally:
        logger.info("Exiting list_dashboards")

@mcp.tool()
def list_prompts() -> dict:
    """Placeholder function for prompts/list to avoid method not found errors."""
    logger.info("Starting list_prompts")
    try:
        result = {
            "content": {
                "prompts": [],
                "total": 0,
                "message": "No prompts available."
            }
        }
        logger.info("No prompts available.")
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve prompts: {e}", exc_info=True)
        return {
            "content": {
                "prompts": [],
                "total": 0,
                "message": f"Error fetching prompts: {e}"
            }
        }
    finally:
        logger.info("Exiting list_prompts")
