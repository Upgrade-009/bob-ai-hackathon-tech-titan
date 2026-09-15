"""
IBM Bob / Model Context Protocol (MCP) Server for Port Operations Optimiser.
Exposes real-time port telemetry, congestion prediction, berth/crane optimization,
alternate routing, and 72-hour operational planning tools to IBM Bob.
"""
import sys
import json
from pathlib import Path

# Add backend directory and root directory to sys.path if executed standalone
root_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from src.backend.database import fetch_all, fetch_one, init_db
    from src.backend.services.congestion import calculate_congestion_risk
    from src.backend.services.berth_optimizer import optimize_berth_assignment
    from src.backend.services.crane_optimizer import optimize_crane_assignment
    from src.backend.services.routing import recommend_alternate_routing
    from src.backend.services.operations_plan import generate_72_hour_operations_plan
except ModuleNotFoundError:
    from database import fetch_all, fetch_one, init_db
    from services.congestion import calculate_congestion_risk
    from services.berth_optimizer import optimize_berth_assignment
    from services.crane_optimizer import optimize_crane_assignment
    from services.routing import recommend_alternate_routing
    from services.operations_plan import generate_72_hour_operations_plan

# MCP Tool Implementations (Shared Business Logic)
def get_port_status():
    """Returns high-level port telemetry including total vessels, berths, cranes, and active disruptions."""
    init_db()
    vessels = fetch_all("SELECT * FROM vessels")
    berths = fetch_all("SELECT * FROM berths")
    cranes = fetch_all("SELECT * FROM cranes")
    disruptions = fetch_all("SELECT * FROM disruptions WHERE is_active = 1")
    return {
        "status": "OPERATIONAL",
        "total_vessels": len(vessels),
        "total_berths": len(berths),
        "total_cranes": len(cranes),
        "active_disruptions": len(disruptions),
        "congested_berths": [b["name"] for b in berths if b["status"] == "CONGESTED"]
    }

def get_vessel_risk(vessel_id: str = None):
    """Returns risk assessment and priority metrics for all vessels or a specific target vessel."""
    init_db()
    if vessel_id:
        vessel = fetch_one("SELECT * FROM vessels WHERE vessel_id = ?", (vessel_id,))
        if not vessel:
            return {"error": f"Vessel '{vessel_id}' not found."}
        return vessel
    return fetch_all("SELECT vessel_id, name, priority, assigned_berth, estimated_waiting_time_hrs, status FROM vessels ORDER BY priority DESC")

def get_congestion_hotspots():
    """Returns calculated congestion risk scores and explainable hotspot causes across berths."""
    init_db()
    return calculate_congestion_risk()

def optimise_berths(vessel_id: str, preferred_berth_id: str = None):
    """Calculates conflict-free berth assignment for a vessel considering length, draft, ETA, and capacity."""
    init_db()
    return optimize_berth_assignment(vessel_id, preferred_berth_id)

def optimise_cranes(vessel_id: str, berth_id: str):
    """Allocates available quay cranes to a vessel based on container volume and priority."""
    init_db()
    return optimize_crane_assignment(vessel_id, berth_id)

def recommend_alternate_route(vessel_id: str):
    """Recommends alternate routing or synthetic port diversion (Port Alpha/Beta/Gamma) during high congestion."""
    init_db()
    return recommend_alternate_routing(vessel_id)

def generate_72_hour_plan():
    """Generates the hour-by-hour operational shift plan for the next 72 hours."""
    init_db()
    return generate_72_hour_operations_plan()

# Standard JSON-RPC / MCP CLI Invocation Interface
MCP_TOOLS = {
    "get_port_status": get_port_status,
    "get_vessel_risk": get_vessel_risk,
    "get_congestion_hotspots": get_congestion_hotspots,
    "optimise_berths": optimise_berths,
    "optimise_cranes": optimise_cranes,
    "recommend_alternate_route": recommend_alternate_route,
    "generate_72_hour_plan": generate_72_hour_plan
}

def main():
    """Command-line runner for IBM Bob / MCP integration testing."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd in MCP_TOOLS:
            args = sys.argv[2:]
            res = MCP_TOOLS[cmd](*args) if args else MCP_TOOLS[cmd]()
            print(json.dumps(res, indent=2))
            return
        elif cmd in ("--help", "-h", "list"):
            print("Available IBM Bob MCP Tools:")
            for tool_name in MCP_TOOLS:
                print(f"  - {tool_name}")
            return
            
    # Default output
    print(json.dumps({
        "mcp_server": "IBM Bob Port Operations Optimiser MCP Server",
        "protocol_version": "1.0.0",
        "available_tools": list(MCP_TOOLS.keys())
    }, indent=2))

if __name__ == "__main__":
    main()
