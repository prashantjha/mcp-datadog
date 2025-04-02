from typing import Optional, Dict, Any, List
from pydantic import Field
from datadog_api_client import ApiClient
from datadog_api_client.v1.api.service_level_objectives_api import ServiceLevelObjectivesApi
from config import configuration
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Datadog SLO Service")

@mcp.tool()
def list_slos(
    query: Optional[str] = Field(default=None, description="Query to filter SLOs"),
    limit: int = Field(default=10, description="Maximum number of SLOs to return"),
    offset: int = Field(default=0, description="Offset for pagination")
) -> Dict[str, Any]:
    """List Service Level Objectives (SLOs)."""
    try:
        with ApiClient(configuration) as api_client:
            slo_api = ServiceLevelObjectivesApi(api_client)
            response = slo_api.list_slos(query=query, limit=limit, offset=offset)
            return {"status": "success", "message": "SLOs listed successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error listing SLOs: {e}"}

@mcp.tool()
def get_slo(
    slo_id: str = Field(..., description="The ID of the SLO to retrieve")
) -> Dict[str, Any]:
    """Get details of a specific SLO."""
    try:
        with ApiClient(configuration) as api_client:
            slo_api = ServiceLevelObjectivesApi(api_client)
            response = slo_api.get_slo(slo_id)
            return {"status": "success", "message": "SLO retrieved successfully", "content": response.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"Error retrieving SLO: {e}"}

@mcp.tool()
def delete_slo(
    slo_id: str = Field(..., description="The ID of the SLO to delete")
) -> Dict[str, Any]:
    """Delete a specific SLO."""
    try:
        with ApiClient(configuration) as api_client:
            slo_api = ServiceLevelObjectivesApi(api_client)
            slo_api.delete_slo(slo_id)
            return {"status": "success", "message": "SLO deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting SLO: {e}"}
