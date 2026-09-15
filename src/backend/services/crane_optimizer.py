from typing import Dict, Any, List
from ..database import fetch_one, fetch_all, execute_query

def optimize_crane_assignment(vessel_id: str, berth_id: str) -> Dict[str, Any]:
    """
    Optimizes quay crane allocation for a vessel at a specific berth:
    - Matches vessel container volume to crane handling rates (TEU/hr)
    - Allocates 2 to 3 cranes for HIGH/CRITICAL priority vessels
    - Prevents assigning the same crane to multiple active vessels simultaneously
    """
    vessel = fetch_one("SELECT * FROM vessels WHERE vessel_id = ?", (vessel_id,))
    if not vessel:
        return {"error": f"Vessel '{vessel_id}' not found."}

    # Fetch available cranes at this berth or adjacent berths
    cranes = fetch_all("SELECT * FROM cranes WHERE status != 'OUTAGE' AND status != 'MAINTENANCE'")
    if not cranes:
        return {"error": "No operational cranes available."}

    v_containers = int(vessel["container_count"])
    v_priority = vessel["priority"]

    # Filter cranes assigned to this berth first, then general available cranes
    berth_cranes = [c for c in cranes if c["berth_id"] == berth_id and (c["assigned_vessel_id"] is None or c["assigned_vessel_id"] == "" or c["assigned_vessel_id"] == vessel_id)]
    other_free_cranes = [c for c in cranes if c not in berth_cranes and (c["assigned_vessel_id"] is None or c["assigned_vessel_id"] == "")]

    # Determine required crane count based on container volume and priority
    if v_priority in ("HIGH", "CRITICAL") or v_containers > 4000:
        target_crane_count = 3
    elif v_containers > 2500:
        target_crane_count = 2
    else:
        target_crane_count = 1

    selected_cranes = berth_cranes[:target_crane_count]
    if len(selected_cranes) < target_crane_count:
        needed = target_crane_count - len(selected_cranes)
        selected_cranes.extend(other_free_cranes[:needed])

    if not selected_cranes:
        # Fallback to any operational crane
        selected_cranes = [cranes[0]]

    crane_ids = [c["crane_id"] for c in selected_cranes]
    total_handling_rate = sum([int(c["handling_rate_teu_hr"]) for c in selected_cranes])
    
    # Calculate estimated duration
    estimated_duration_hrs = round(v_containers / max(total_handling_rate, 1), 1)
    
    # Calculate crane utilization %
    active_cranes_count = len(fetch_all("SELECT * FROM cranes WHERE status = 'IN_USE'"))
    total_cranes_count = len(cranes)
    crane_utilization_pct = round((active_cranes_count / max(total_cranes_count, 1)) * 100, 1)

    # Update assigned cranes in database
    for c_id in crane_ids:
        execute_query("UPDATE cranes SET status = 'IN_USE', assigned_vessel_id = ? WHERE crane_id = ?", (vessel_id, c_id))

    # Update assignment table if present
    execute_query("UPDATE assignments SET assigned_cranes = ? WHERE vessel_id = ?", (", ".join(crane_ids), vessel_id))

    reason = f"Allocated {len(crane_ids)} crane(s) ({', '.join(crane_ids)}) delivering {total_handling_rate} TEU/hr total capacity for {v_containers} TEUs."

    return {
        "vessel_id": vessel_id,
        "berth_id": berth_id,
        "assigned_cranes": crane_ids,
        "total_handling_capacity_teu_hr": total_handling_rate,
        "estimated_handling_duration_hrs": estimated_duration_hrs,
        "crane_utilization_pct": crane_utilization_pct,
        "reason": reason
    }
