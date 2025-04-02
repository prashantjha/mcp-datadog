from .monitor import create_monitor, delete_monitor, get_monitor, update_monitor
from .apm import query_apm_errors, query_apm_latency, query_apm_spans
from .root_cause import analyze_service_with_apm

# List of tools for registration
mcp_tools = [
    get_monitor_status,
    create_monitor_config_policy,
    update_monitor_config_policy,
    delete_monitor_config_policy,
    list_monitor_config_policies,
    search_monitors,
    list_dashboards,
    list_prompts,
    list_downtimes,
    create_downtime,
    update_downtime,
    cancel_downtime,
    list_hosts,
    mute_host,
    unmute_host,
    get_host_totals,
    list_incidents,
    get_incident,
    list_traces,
    query_metrics,
    list_metrics,
    query_logs,
    create_event,
]

mcp_tools.extend([
    create_monitor,
    delete_monitor,
    get_monitor,
    update_monitor,
    query_apm_errors,
    query_apm_latency,
    query_apm_spans,
    analyze_service_with_apm,
])
