from pydantic import BaseModel, Field
import json
import time
import logging
import sys
from datadog_api_client import ApiClient
from datadog_api_client.v2.api.incidents_api import IncidentsApi
from datadog_api_client.v2.api.spans_api import SpansApi
from config import configuration
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Datadog Traces Service")

@mcp.tool()
def list_traces(
    query: str,
    from_time: int = Field(default_factory=lambda: int(time.time()) - 900, description="Start time in epoch seconds (default: last 15 minutes)"),
    to_time: int = Field(default_factory=lambda: int(time.time()), description="End time in epoch seconds (default: now)"),
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of traces to return (default: 100)"),
    sort: str = Field(default="-timestamp", description="Sort order for traces, default is descending timestamp"),
    service: str = Field(default=None, description="Filter by service name"),
    operation: str = Field(default=None, description="Filter by operation name")
) -> dict:
    """Retrieves APM traces from Datadog."""
    # logger.info("Starting list_traces")
    try:
        with ApiClient(configuration) as api_client:
            spans_api = SpansApi(api_client)
            filter_query = [query]
            if service:
                filter_query.append(f"service:{service}")
            if operation:
                filter_query.append(f"operation:{operation}")

            response = spans_api.list_spans(
                body={
                    "data": {
                        "attributes": {
                            "filter": {
                                "query": " ".join(filter_query),
                                "from": from_time,
                                "to": to_time,
                            },
                            "sort": sort,
                            "page": {"limit": limit},
                        },
                        "type": "search_request",
                    }
                }
            )

            if not response.data:
                raise ValueError("No traces data returned")

            try:
                result = {"content": [{"type": "text", "text": json.dumps(response.data, indent=2)}]}
                # logger.info("Successfully retrieved traces.")
                return result
            except TypeError as e:
                # logger.error(f"Failed to serialize traces to JSON: {e}. Data: {response.data}", exc_info=True)
                return {"content": [{"type": "text", "text": f"Error serializing traces: {e}"}]}
    except Exception as e:
        # logger.error(f"Failed to retrieve traces: {e}", exc_info=True)
        return {"content": [{"type": "text", "text": f"Error fetching traces: {e}"}]}
    finally:
        # logger.info("Exiting list_traces")
        pass
