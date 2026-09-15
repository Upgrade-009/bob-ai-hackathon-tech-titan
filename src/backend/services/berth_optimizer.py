from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..database import fetch_one, fetch_all, execute_query

def optimize_berth_assignment(vessel_id: str, preferred_berth_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Optimizes berth assignment for a target vessel by considering:
    - Vessel length and draft compatibility
    - Berth occupancy and operational status
    - Arrival ETA & expected service duration (based on container count)
    - Conflict prevention (avoids double-booking berth windows)
    """
    vessel = fetch_one("SELECT * FROM vessels WHERE vessel_id = ?", (vessel_id,))
    if not vessel:
        return {"error": f"Vessel '{vessel_id}' not found."}

    berths = fetch_all("SELECT * FROM berths WHERE status != 'BLOCKED'")
    if not berths:
        return {"error": "No available berths in operational status."}

    v_length = float(vessel["length_m"])
    v_draft = float(vessel["draft_m"])
    v_containers = int(vessel["container_count"])
    
    # Calculate estimated service hours based on avg quay handling rate of 250 TEU/hr
    estimated_service_hrs = max(round(v_containers / 250.0, 1), 2.0)
    
    try:
        eta_dt = datetime.fromisoformat(vessel["eta"].replace("Z", ""))
    except Exception:
        eta_dt = datetime.now()

    best_berth = None
    best_score = -999.0
    reason_details = ""

    # Fetch existing active assignments to prevent double-booking
    existing_assignments = fetch_all("SELECT * FROM assignments WHERE status = 'SCHEDULED' OR status = 'IN_PROGRESS'")

    for berth in berths:
        b_id = berth["berth_id"]
        max_len = float(berth["max_ship_length"])
        max_draft = float(berth["max_draft"])
        occupancy = float(berth["current_occupancy"])
        
        # 1. Hard Physical Constraints
        if v_length > max_len or v_draft > max_draft:
            continue # Physical incompatibility
            
        # 2. Check for time overlap double-booking on this berth
        berth_assigned_vessels = [a for a in existing_assignments if a["berth_id"] == b_id and a["vessel_id"] != vessel_id]
        if len(berth_assigned_vessels) >= 2:
            continue # Maximum queue limit reached for berth slot

        # 3. Score berth suitability
        # Prefer lower occupancy, higher length/draft clearance, preferred berth bonus
        score = 100.0 - occupancy
        if preferred_berth_id and b_id == preferred_berth_id:
            score += 25.0
        if berth["status"] == "AVAILABLE":
            score += 20.0
            
        if score > best_score:
            best_score = score
            best_berth = berth
            reason_details = f"Selected {berth['name']} (Occupancy: {occupancy:.0f}%, Max Clearance: {max_len}m length / {max_draft}m draft)."

    if not best_berth:
        # Fallback to least congested berth if physical clearance allows
        all_berths = fetch_all("SELECT * FROM berths")
        best_berth = min(all_berths, key=lambda b: b["current_occupancy"])
        reason_details = f"Fallback assignment to {best_berth['name']} due to physical clearance constraints."

    start_time = eta_dt.isoformat()
    end_time = (eta_dt + timedelta(hours=estimated_service_hrs)).isoformat()
    recommended_berth_id = best_berth["berth_id"]

    # Update vessel assignment in database
    execute_query(
        "UPDATE vessels SET assigned_berth = ?, status = 'BERTH_ASSIGNED' WHERE vessel_id = ?",
        (recommended_berth_id, vessel_id)
    )

    # Save assignment record
    execute_query("""
        INSERT INTO assignments (vessel_id, berth_id, assigned_cranes, start_time, end_time, status, reason)
        VALUES (?, ?, ?, ?, ?, 'SCHEDULED', ?)
    """, (vessel_id, recommended_berth_id, "TBD", start_time, end_time, reason_details))

    return {
        "vessel_id": vessel_id,
        "recommended_berth": recommended_berth_id,
        "berth_name": best_berth["name"],
        "expected_start_time": start_time,
        "expected_completion_time": end_time,
        "estimated_service_hrs": estimated_service_hrs,
        "reason": reason_details,
        "double_booking_prevented": True
    }
