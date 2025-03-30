from pydantic import BaseModel, Field
import json
from datadog_api_client import ApiClient
from datadog_api_client.v2.api.incidents_api import IncidentsApi
from config import configuration, logger
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog Incident Service")

class ListIncidentsParams(BaseModel):
    page_size: int = Field(10, ge=1, le=100)
    page_offset: int = Field(0, ge=0)

class GetIncidentParams(BaseModel):
    incident_id: str

import logging
logger = logging.getLogger(__name__)

@mcp.tool()
def list_incidents(params: ListIncidentsParams = ListIncidentsParams()) -> dict:
    """Retrieves a list of incidents from Datadog."""
    logger.info("Starting list_incidents")
    try:
        with ApiClient(configuration) as api_client:
            incidents_api = IncidentsApi(api_client)
            response = incidents_api.list_incidents(
                page_size=params.page_size, page_offset=params.page_offset
            )

            if not response.data:
                raise ValueError("No incidents data returned")

            incidents_data = [json.dumps(d, indent=2) for d in response.data]
            result = {"content": [{"type": "text", "text": "\n".join(incidents_data)}]}
            logger.info("Successfully retrieved incidents.")
            return result
    except Exception as e:
        logger.error(f"Failed to retrieve incidents: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error fetching incidents: {e}"}]}
    finally:
        logger.info("Exiting list_incidents")

@mcp.tool()
def get_incident(params: GetIncidentParams) -> dict:
    """Retrieves a specific incident from Datadog."""
    logger.info("Starting get_incident")
    try:
        with ApiClient(configuration) as api_client:
            incidents_api = IncidentsApi(api_client)
            response = incidents_api.get_incident(params.incident_id)

            if not response.data:
                raise ValueError("No incident data returned")

            result = {"content": [{"type": "text", "text": json.dumps(response.data, indent=2)}]}
            logger.info("Successfully retrieved incident.")
            return result
    except Exception as e:
        logger.error(f"Failed to retrieve incident: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error fetching incident: {e}"}]}
    finally:
        logger.info("Exiting get_incident")
