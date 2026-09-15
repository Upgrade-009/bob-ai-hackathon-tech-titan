from pydantic import BaseModel, Field
from typing import List, Optional

# Vessel Models
class Vessel(BaseModel):
    vessel_id: str
    name: str
    eta: str
    current_port: str
    destination: str
    cargo_type: str
    container_count: int
    priority: str
    assigned_berth: Optional[str] = None
    estimated_waiting_time_hrs: float
    length_m: float
    draft_m: float
    status: str

# Berth Models
class Berth(BaseModel):
    berth_id: str
    name: str
    max_ship_length: float
    max_draft: float
    capacity_teu: int
    current_occupancy: float
    status: str
    zone: str

# Crane Models
class Crane(BaseModel):
    crane_id: str
    name: str
    berth_id: str
    handling_rate_teu_hr: int
    status: str
    assigned_vessel_id: Optional[str] = None

# Disruption Models
class Disruption(BaseModel):
    disruption_id: str
    type: str
    affected_target: str
    severity: str
    description: str
    start_time: str
    expected_duration_hrs: int
    is_active: int

# Dashboard Models
class DashboardSummary(BaseModel):
    total_vessels: int
    vessels_at_risk: int
    congested_berths_count: int
    average_waiting_time_hrs: float
    critical_hotspots: List[str]
    active_disruptions_count: int
    fleet_crane_utilization_pct: float

# Congestion Model
class CongestionFactor(BaseModel):
    factor: str
    impact_score: float
    description: str

class BerthCongestionDetail(BaseModel):
    berth_id: str
    berth_name: str
    occupancy_pct: float
    queue_count: int
    congestion_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    primary_causes: List[str]

class CongestionPrediction(BaseModel):
    overall_port_congestion_score: float
    overall_risk_level: str
    berth_details: List[BerthCongestionDetail]
    recommendation_summary: str

# Optimization Requests & Responses
class BerthOptimizeRequest(BaseModel):
    vessel_id: str
    preferred_berth_id: Optional[str] = None

class BerthOptimizeResponse(BaseModel):
    vessel_id: str
    recommended_berth: str
    berth_name: Optional[str] = None
    expected_start_time: str
    expected_completion_time: str
    estimated_service_hrs: float
    reason: str
    double_booking_prevented: bool = True

class CraneOptimizeRequest(BaseModel):
    vessel_id: str
    berth_id: str

class CraneOptimizeResponse(BaseModel):
    vessel_id: str
    berth_id: str
    assigned_cranes: List[str]
    total_handling_capacity_teu_hr: int
    estimated_handling_duration_hrs: float
    crane_utilization_pct: float
    reason: str

# Alternate Routing Models
class AlternateRouteRequest(BaseModel):
    vessel_id: str

class AlternateRouteRecommendation(BaseModel):
    vessel_id: str
    vessel_name: Optional[str] = None
    current_status: str
    congestion_level: str
    recommended_option: str  # Alternate Port, Alternate Berth, Delayed Departure, Rerouting
    alternate_port: Optional[str] = None
    alternate_berth: Optional[str] = None
    reason: str
    estimated_wait_reduction_hrs: float
    priority: str
    is_synthetic_demo_data: bool = True

# 72-Hour Operations Plan Models
class PlanItem(BaseModel):
    time_block: str
    vessel_id: str
    vessel_name: str
    berth_id: str
    cranes: List[str]
    action: str
    priority: str
    congestion_risk: str
    expected_impact: str

class OperationsPlanResponse(BaseModel):
    plan_horizon: str = "72 Hours"
    total_scheduled_operations: int
    current_plan: List[PlanItem]
    recommended_changes: List[str]
    expected_impact_summary: str

# AI Assistant Models
class AssistantRequest(BaseModel):
    question: str

class AssistantResponse(BaseModel):
    question: str
    answer: str
    used_tool: str
    tool_output: dict
