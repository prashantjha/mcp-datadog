from typing import Dict, Any
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from .apm import query_apm_errors, query_apm_latency, query_apm_spans

@mcp.tool()
def analyze_service_with_apm(
    service_name: str = Field(..., description="The name of the service to analyze"),
    from_time: int = Field(..., description="Start time in epoch seconds"),
    to_time: int = Field(..., description="End time in epoch seconds")
) -> Dict[str, Any]:
    """Perform root cause analysis for a service, including APM spans, errors, and latency."""
    try:
        # Step 1: Query APM latency
        latency_result = query_apm_latency(service_name, from_time, to_time)
        if latency_result["status"] != "success":
            return {"status": "error", "message": "Failed to retrieve APM latency", "details": latency_result}

        # Step 2: Query APM errors
        error_result = query_apm_errors(service_name, from_time, to_time)
        if error_result["status"] != "success":
            return {"status": "error", "message": "Failed to retrieve APM errors", "details": error_result}

        # Step 3: Query APM spans
        spans_result = query_apm_spans(service_name, from_time, to_time)
        if spans_result["status"] != "success":
            return {"status": "error", "message": "Failed to retrieve APM spans", "details": spans_result}

        # Aggregate results
        return {
            "status": "success",
            "message": "Root cause analysis with APM completed successfully",
            "content": {
                "latency": latency_result["content"],
                "errors": error_result["content"],
                "spans": spans_result["content"],
            },
        }
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error during root cause analysis with APM: {e}"}
