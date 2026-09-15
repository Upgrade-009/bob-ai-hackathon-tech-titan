from typing import Dict, Any
from ..database import fetch_one, fetch_all
from .congestion import calculate_congestion_risk

SYNTHETIC_ALTERNATE_PORTS = [
    {"name": "Port Alpha", "distance_nm": 45, "available_capacity_teu": 15000, "avg_wait_hrs": 1.2},
    {"name": "Port Beta", "distance_nm": 82, "available_capacity_teu": 22000, "avg_wait_hrs": 0.8},
    {"name": "Port Gamma", "distance_nm": 110, "available_capacity_teu": 18000, "avg_wait_hrs": 0.5}
]

def recommend_alternate_routing(vessel_id: str) -> Dict[str, Any]:
    """
    Generates alternate routing strategies for vessels experiencing HIGH or CRITICAL port congestion.
    Options include:
    1. Alternate Port Diversion (Port Alpha / Port Beta / Port Gamma - Clearly synthetic demo data)
    2. Alternate Berth Reassignment within current port
    3. Delayed Departure / Slow-Steaming schedule adjustment
    """
    vessel = fetch_one("SELECT * FROM vessels WHERE vessel_id = ?", (vessel_id,))
    if not vessel:
        return {"error": f"Vessel '{vessel_id}' not found."}

    congestion_data = calculate_congestion_risk()
    port_risk = congestion_data["overall_risk_level"]
    
    assigned_berth_id = vessel["assigned_berth"]
    berth_risk = "LOW"
    for b in congestion_data["berth_details"]:
        if b["berth_id"] == assigned_berth_id:
            berth_risk = b["risk_level"]
            break

    # Determine recommendation based on risk severity
    current_wait = float(vessel["estimated_waiting_time_hrs"])
    priority = vessel["priority"]

    if berth_risk in ("CRITICAL", "HIGH") or current_wait >= 8.0:
        if priority == "CRITICAL" or current_wait >= 12.0:
            # Option 1: Alternate Port Reroute
            alt_port = SYNTHETIC_ALTERNATE_PORTS[0]
            recommended_option = "Alternate Port Reroute"
            reason = (f"Berth {assigned_berth_id} is in {berth_risk} congestion with {current_wait}h queue. "
                      f"Rerouting vessel '{vessel['name']}' to synthetic {alt_port['name']} bypasses 10+ hours of terminal delay.")
            wait_reduction = max(round(current_wait - alt_port["avg_wait_hrs"], 1), 5.0)
            alt_berth_name = None
            alt_port_name = alt_port["name"]
            rec_priority = "HIGH"
        else:
            # Option 2: Alternate Berth Switch
            recommended_option = "Alternate Berth Reassignment"
            alt_port_name = None
            alt_berth_name = "B06 (South Quay 1)"
            reason = f"Reassigning from congested {assigned_berth_id} to low-occupancy berth B06 avoids 6.5 hours of waiting time."
            wait_reduction = round(current_wait * 0.7, 1)
            rec_priority = "MEDIUM"
    elif current_wait >= 3.0:
        # Option 3: Slow Steaming / Delayed Departure
        recommended_option = "Slow-Steaming / Speed Reduction"
        alt_port_name = None
        alt_berth_name = None
        reason = "Reducing cruising speed by 3 knots saves 12% fuel and synchronizes arrival with cleared berth window."
        wait_reduction = 3.0
        rec_priority = "LOW"
    else:
        recommended_option = "Proceed on Schedule"
        alt_port_name = None
        alt_berth_name = assigned_berth_id
        reason = f"Current berth {assigned_berth_id} operating smoothly with minimal waiting time ({current_wait}h)."
        wait_reduction = 0.0
        rec_priority = "LOW"

    return {
        "vessel_id": vessel_id,
        "vessel_name": vessel["name"],
        "current_status": vessel["status"],
        "congestion_level": berth_risk,
        "recommended_option": recommended_option,
        "alternate_port": alt_port_name,
        "alternate_berth": alt_berth_name,
        "reason": reason,
        "estimated_wait_reduction_hrs": wait_reduction,
        "priority": rec_priority,
        "is_synthetic_demo_data": True
    }
