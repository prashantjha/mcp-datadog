from .monitor import get_monitor_status
from .dashboard import list_dashboards,list_prompts
from .downtime import list_downtimes
from .host import get_host_list
from .incident import list_incidents,get_incident
from .trace import list_traces

# List of tools for registration
mcp_tools = [ 
				get_monitor_status,
				list_dashboards,
				list_downtimes,
				get_host_list,
				list_incidents,
				get_incident,
				list_traces,
				list_prompts
			]
