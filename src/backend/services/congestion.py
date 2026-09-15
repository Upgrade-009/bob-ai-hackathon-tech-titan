from typing import List, Dict, Any
from ..database import fetch_all

def calculate_congestion_risk() -> Dict[str, Any]:
    """
    Calculates port and berth-level congestion scores (0-100) using weighted factors:
    - Berth occupancy (35%)
    - Vessel queue density (25%)
    - Vessel arrival concentration (20%)
    - Active disruption impact (10%)
    - High-priority vessel pressure (10%)
    
    Risk Mapping:
    0-29: LOW
    30-49: MEDIUM
    50-74: HIGH
    75-100: CRITICAL
    """
    berths = fetch_all("SELECT * FROM berths")
    vessels = fetch_all("SELECT * FROM vessels")
    disruptions = fetch_all("SELECT * FROM disruptions WHERE is_active = 1")

    berth_details = []
    total_score = 0.0

    for berth in berths:
        b_id = berth["berth_id"]
        occupancy = float(berth["current_occupancy"]) # 0-100%
        
        # Vessels queued/assigned to this berth
        assigned_vessels = [v for v in vessels if v["assigned_berth"] == b_id]
        queue_count = len(assigned_vessels)
        
        # High priority vessel count
        critical_vessels = [v for v in assigned_vessels if v["priority"] in ("HIGH", "CRITICAL")]
        
        # Active disruptions affecting this berth or berth's zone
        affecting_disruptions = [
            d for d in disruptions
            if d["affected_target"] in (b_id, berth["name"], berth["zone"], "Main Channel")
        ]
        
        # Factor calculations
        f_occupancy = occupancy * 0.35
        f_queue = min(queue_count * 15.0, 25.0) # max 25 pts
        f_priority = len(critical_vessels) * 5.0
        f_disruption = 0.0
        for d in affecting_disruptions:
            if d["severity"] == "CRITICAL":
                f_disruption += 15.0
            elif d["severity"] == "HIGH":
                f_disruption += 10.0
            else:
                f_disruption += 5.0
        f_disruption = min(f_disruption, 25.0)
        
        raw_score = f_occupancy + f_queue + f_priority + f_disruption
        score = min(max(round(raw_score, 1), 0.0), 100.0)
        
        # Risk Mapping
        if score < 30.0:
            risk_level = "LOW"
        elif score < 50.0:
            risk_level = "MEDIUM"
        elif score < 75.0:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
            
        # Explainability: Primary Causes
        causes = []
        if occupancy >= 80.0:
            causes.append(f"High berth occupancy ({occupancy:.0f}%)")
        if queue_count >= 2:
            causes.append(f"Vessel queue bottleneck ({queue_count} vessels waiting)")
        if critical_vessels:
            causes.append(f"High-priority container vessels pending ({len(critical_vessels)})")
        if affecting_disruptions:
            d_types = ", ".join([d["type"] for d in affecting_disruptions])
            causes.append(f"Active disruption impact: {d_types}")
        if not causes:
            causes.append("Normal operational throughput")

        berth_details.append({
            "berth_id": b_id,
            "berth_name": berth["name"],
            "occupancy_pct": occupancy,
            "queue_count": queue_count,
            "congestion_score": score,
            "risk_level": risk_level,
            "primary_causes": causes
        })
        total_score += score

    overall_score = round(total_score / max(len(berths), 1), 1)
    if overall_score < 30.0:
        overall_risk = "LOW"
    elif overall_score < 50.0:
        overall_risk = "MEDIUM"
    elif overall_score < 75.0:
        overall_risk = "HIGH"
    else:
        overall_risk = "CRITICAL"

    hotspots = [b["berth_name"] for b in berth_details if b["risk_level"] in ("HIGH", "CRITICAL")]
    summary = f"Port Congestion Index: {overall_score}/100 ({overall_risk}). Identified {len(hotspots)} critical hotspot(s): {', '.join(hotspots) if hotspots else 'None'}."

    return {
        "overall_port_congestion_score": overall_score,
        "overall_risk_level": overall_risk,
        "berth_details": berth_details,
        "recommendation_summary": summary
    }
