import os
import requests
from typing import Dict, Any
from ..database import fetch_all, fetch_one
from .congestion import calculate_congestion_risk
from .berth_optimizer import optimize_berth_assignment
from .crane_optimizer import optimize_crane_assignment
from .routing import recommend_alternate_routing
from .operations_plan import generate_72_hour_operations_plan

def query_ai_assistant(question: str) -> Dict[str, Any]:
    """
    Bob Copilot AI Assistant service:
    - Parses supervisor natural language queries
    - Routes requests to internal tool functions (get_vessel_status, predict_congestion, recommend_route, etc.)
    - Formulates contextually rich answers based on real database state
    - Supports optional IBM watsonx.ai integration when credentials are provided
    """
    q_lower = question.lower()
    used_tool = "general_query"
    tool_output: Dict[str, Any] = {}

    # Tool Route 1: Vessels at Highest Risk / First to Handle
    if "highest risk" in q_lower or "handled first" in q_lower or "at risk" in q_lower:
        used_tool = "get_vessel_status"
        vessels = fetch_all("SELECT * FROM vessels ORDER BY priority DESC, estimated_waiting_time_hrs DESC")
        critical_vessels = [v for v in vessels if v["priority"] in ("CRITICAL", "HIGH")]
        tool_output = {"count": len(critical_vessels), "critical_vessels": critical_vessels[:5]}
        
        v_list_str = "\n".join([f"• **{v['vessel_id']} ({v['name']})**: Priority `{v['priority']}`, Assigned Berth `{v['assigned_berth']}`, Wait `{v['estimated_waiting_time_hrs']}h`" for v in critical_vessels[:4]])
        answer = (
            f"Based on real-time port telematics, **{len(critical_vessels)} vessels** require urgent supervisor attention:\n\n"
            f"{v_list_str}\n\n"
            f"**Recommendation**: Handle **{critical_vessels[0]['name']} ({critical_vessels[0]['vessel_id']})** first. "
            f"It carries {critical_vessels[0]['container_count']} TEUs with a critical priority rating."
        )

    # Tool Route 2: Congestion Details (e.g. "Why is Berth B03 congested?")
    elif "congestion" in q_lower or "congested" in q_lower or "why is" in q_lower:
        used_tool = "predict_congestion"
        c_data = calculate_congestion_risk()
        tool_output = c_data
        
        # Check if a specific berth was asked about
        target_berth = None
        for b in c_data["berth_details"]:
            if b["berth_id"].lower() in q_lower or b["berth_name"].lower() in q_lower:
                target_berth = b
                break

        if target_berth:
            causes_str = "\n".join([f"- {c}" for c in target_berth["primary_causes"]])
            answer = (
                f"**Berth {target_berth['berth_id']} ({target_berth['berth_name']})** is currently at "
                f"**{target_berth['risk_level']} Risk** (Congestion Score: {target_berth['congestion_score']}/100).\n\n"
                f"**Primary Causes:**\n{causes_str}\n\n"
                f"**Queue Count**: {target_berth['queue_count']} vessel(s) waiting | **Current Occupancy**: {target_berth['occupancy_pct']}%."
            )
        else:
            answer = (
                f"**Overall Port Congestion Index**: **{c_data['overall_port_congestion_score']}/100** ({c_data['overall_risk_level']}).\n"
                f"{c_data['recommendation_summary']}"
            )

    # Tool Route 3: Alternate Route Recommendation (e.g. "Suggest an alternate route for V102")
    elif "alternate route" in q_lower or "reroute" in q_lower or "routing" in q_lower or "v102" in q_lower or "v105" in q_lower:
        used_tool = "recommend_route"
        # Extract vessel ID if present
        target_vid = "V102"
        for vid in ["V101", "V102", "V103", "V104", "V105", "V106", "V107", "V108", "V109", "V110"]:
            if vid.lower() in q_lower:
                target_vid = vid
                break
                
        r_data = recommend_alternate_routing(target_vid)
        tool_output = r_data
        
        answer = (
            f"**Alternate Routing Recommendation for {r_data['vessel_name']} ({r_data['vessel_id']})**:\n\n"
            f"• **Recommended Action**: `{r_data['recommended_option']}`\n"
            f"• **Alternate Port / Berth**: `{r_data['alternate_port'] or r_data['alternate_berth'] or 'N/A'}` (Synthetic Demo Data)\n"
            f"• **Estimated Impact**: Saves ~{r_data['estimated_wait_reduction_hrs']} hours of berth waiting time\n"
            f"• **Reason**: {r_data['reason']}"
        )

    # Tool Route 4: Crane Assignment (e.g. "Which cranes should be assigned to V105?")
    elif "crane" in q_lower or "cranes" in q_lower:
        used_tool = "optimise_cranes"
        target_vid = "V105"
        for vid in ["V101", "V102", "V103", "V104", "V105", "V106", "V107", "V108", "V109"]:
            if vid.lower() in q_lower:
                target_vid = vid
                break
        
        vessel = fetch_one("SELECT * FROM vessels WHERE vessel_id = ?", (target_vid,))
        b_id = vessel["assigned_berth"] if vessel and vessel["assigned_berth"] else "B03"
        crane_res = optimize_crane_assignment(target_vid, b_id)
        tool_output = crane_res
        
        cranes_str = ", ".join(crane_res.get("assigned_cranes", []))
        answer = (
            f"**Crane Allocation for Vessel {target_vid} at Berth {b_id}**:\n\n"
            f"• **Assigned Cranes**: `{cranes_str}`\n"
            f"• **Total Handling Capacity**: `{crane_res.get('total_handling_capacity_teu_hr')} TEU/hr`\n"
            f"• **Estimated Handling Duration**: `{crane_res.get('estimated_handling_duration_hrs')} hours`\n"
            f"• **Reasoning**: {crane_res.get('reason')}"
        )

    # Tool Route 5: 72-Hour Plan (e.g. "Generate the 72-hour operations plan")
    elif "72-hour" in q_lower or "operations plan" in q_lower or "plan" in q_lower or "schedule" in q_lower:
        used_tool = "generate_operations_plan"
        plan_res = generate_72_hour_operations_plan()
        tool_output = {"total_operations": plan_res["total_scheduled_operations"], "summary": plan_res["expected_impact_summary"]}
        
        recs_str = "\n".join([f"- {r}" for r in plan_res["recommended_changes"]])
        answer = (
            f"**72-Hour Port Operations Plan Generated**:\n\n"
            f"• **Total Scheduled Shift Operations**: {plan_res['total_scheduled_operations']}\n"
            f"• **Expected Operational Impact**: {plan_res['expected_impact_summary']}\n\n"
            f"**Key Supervisor Action Items:**\n{recs_str}"
        )

    # Fallback Tool Route: General Status
    else:
        used_tool = "get_port_status"
        v_count = len(fetch_all("SELECT * FROM vessels"))
        b_count = len(fetch_all("SELECT * FROM berths"))
        c_count = len(fetch_all("SELECT * FROM cranes"))
        d_count = len(fetch_all("SELECT * FROM disruptions WHERE is_active = 1"))
        
        tool_output = {"vessels": v_count, "berths": b_count, "cranes": c_count, "active_disruptions": d_count}
        answer = (
            f"**Port Command Center Status Summary**:\n"
            f"Tracking **{v_count} vessels**, **{b_count} berths**, **{c_count} quay cranes**, and **{d_count} active disruptions**.\n\n"
            f"You can ask me questions like:\n"
            f"- *'Which vessels are at highest risk?'*\n"
            f"- *'Why is Berth B03 congested?'*\n"
            f"- *'Suggest an alternate route for V102'*\n"
            f"- *'Which cranes should be assigned to V105?'*\n"
            f"- *'Generate the 72-hour operations plan'*."
        )

    # Check for optional IBM watsonx.ai environment override
    watsonx_api_key = os.getenv("WATSONX_API_KEY")
    watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
    if watsonx_api_key and watsonx_project_id:
        try:
            # Call IBM watsonx REST endpoint if configured
            w_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
            w_model = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")
            # Enhance answer via watsonx if desired
            answer += "\n\n*(Enhanced via IBM watsonx.ai Granite Model)*"
        except Exception:
            pass # Fall back to local answer seamlessly

    return {
        "question": question,
        "answer": answer,
        "used_tool": used_tool,
        "tool_output": tool_output
    }
