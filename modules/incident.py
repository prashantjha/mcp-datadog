from pydantic import BaseModel, Field
import json
import logging
import sys
from datadog_api_client import ApiClient
from datadog_api_client.v2.api.incidents_api import IncidentsApi
from config import configuration
from mcp.server.fastmcp import FastMCP
from typing import Optional

mcp = FastMCP("Datadog Incident Service")

class ListIncidentsParams(BaseModel):
    page_size: int = Field(10, ge=1, le=100)
    page_offset: int = Field(0, ge=0)

class GetIncidentParams(BaseModel):
    incident_id: str

@mcp.tool()
def list_incidents(params: ListIncidentsParams = ListIncidentsParams()) -> dict:
    """Retrieves a list of incidents from Datadog."""
    try:
        with ApiClient(configuration) as api_client:
            incidents_api = IncidentsApi(api_client)
            response = incidents_api.list_incidents(
                page_size=params.page_size, page_offset=params.page_offset
            )

            if not response.data:
                return {"status": "error", "message": "No incidents data returned", "content": []}

            incidents_data = [json.dumps(d, indent=2) for d in response.data]
            return {
                "status": "success",
                "message": "Incidents retrieved successfully",
                "content": incidents_data
            }
    except Exception as e:
        return {"status": "error", "message": f"Error fetching incidents: {e}", "content": []}
    finally:
        pass

@mcp.tool()
def get_incident(params: GetIncidentParams) -> dict:
    """Retrieves a specific incident from Datadog."""
    try:
        with ApiClient(configuration) as api_client:
            incidents_api = IncidentsApi(api_client)
            response = incidents_api.get_incident(params.incident_id)

            if not response.data:
                return {"status": "error", "message": "No incident data returned", "content": []}

            return {
                "status": "success",
                "message": "Incident retrieved successfully",
                "content": [{"type": "text", "text": json.dumps(response.data, indent=2)}]
            }
    except Exception as e:
        return {"status": "error", "message": f"Error fetching incident: {e}", "content": []}
    finally:
        pass

@mcp.tool()
def update_incident(incident_id: str, title: Optional[str] = None, status: Optional[str] = None) -> dict:
    """Update an existing incident."""
    try:
        with ApiClient(configuration) as api_client:
            incidents_api = IncidentsApi(api_client)
            body = {"data": {"attributes": {}}}
            if title:
                body["data"]["attributes"]["title"] = title
            if status:
                body["data"]["attributes"]["status"] = status

            response = incidents_api.update_incident(incident_id, body=body)
            return {"status": "success", "message": "Incident updated successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error updating incident: {e}", "content": []}

@mcp.tool()
def delete_incident(incident_id: str) -> dict:
    """Delete an incident."""
    try:
        with ApiClient(configuration) as api_client:
            incidents_api = IncidentsApi(api_client)
            incidents_api.delete_incident(incident_id)
            return {"status": "success", "message": "Incident deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting incident: {e}"}
