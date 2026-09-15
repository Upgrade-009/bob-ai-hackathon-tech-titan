from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Dict, Any

from .database import init_db, fetch_all, fetch_one
from .models import (
    DashboardSummary, Vessel, Berth, Crane, Disruption,
    BerthOptimizeRequest, BerthOptimizeResponse,
    CraneOptimizeRequest, CraneOptimizeResponse,
    AlternateRouteRequest, AlternateRouteRecommendation,
    OperationsPlanResponse, AssistantRequest, AssistantResponse
)
from .services.congestion import calculate_congestion_risk
from .services.berth_optimizer import optimize_berth_assignment
from .services.crane_optimizer import optimize_crane_assignment
from .services.routing import recommend_alternate_routing
from .services.operations_plan import generate_72_hour_operations_plan
from .services.ai_assistant import query_ai_assistant

app = FastAPI(
    title="Container Congestion Predictor & Port Operations Optimiser API",
    description="IBM Bob AI Hackathon Round 1 - Team Tech Titans Backend API",
    version="1.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables & seed synthetic dataset on startup
@app.on_event("startup")
def startup_event():
    init_db()

# 1. Health Check
@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "Port Operations Optimiser API",
        "version": "1.0.0",
        "database": "SQLite Connected"
    }

# 2. Dashboard Summary KPIs
@app.get("/api/dashboard", response_model=DashboardSummary)
def get_dashboard_summary():
    vessels = fetch_all("SELECT * FROM vessels")
    berths = fetch_all("SELECT * FROM berths")
    cranes = fetch_all("SELECT * FROM cranes")
    disruptions = fetch_all("SELECT * FROM disruptions WHERE is_active = 1")

    total_vessels = len(vessels)
    vessels_at_risk = len([v for v in vessels if v["priority"] in ("HIGH", "CRITICAL") or v["estimated_waiting_time_hrs"] > 6.0])
    congested_berths = [b for b in berths if b["status"] == "CONGESTED" or b["current_occupancy"] >= 80.0]
    
    total_wait = sum([float(v["estimated_waiting_time_hrs"]) for v in vessels])
    avg_wait = round(total_wait / max(total_vessels, 1), 1)

    critical_hotspots = [b["name"] for b in congested_berths]
    if not critical_hotspots and disruptions:
        critical_hotspots = [d["affected_target"] for d in disruptions[:2]]

    active_cranes = len([c for c in cranes if c["status"] == "IN_USE"])
    crane_utilization = round((active_cranes / max(len(cranes), 1)) * 100, 1)

    return DashboardSummary(
        total_vessels=total_vessels,
        vessels_at_risk=vessels_at_risk,
        congested_berths_count=len(congested_berths),
        average_waiting_time_hrs=avg_wait,
        critical_hotspots=critical_hotspots,
        active_disruptions_count=len(disruptions),
        fleet_crane_utilization_pct=crane_utilization
    )

# 3. Vessels Endpoints
@app.get("/api/vessels", response_model=List[Vessel])
def get_vessels():
    return fetch_all("SELECT * FROM vessels ORDER BY eta ASC")

@app.get("/api/vessels/{vessel_id}", response_model=Vessel)
def get_vessel_by_id(vessel_id: str):
    vessel = fetch_one("SELECT * FROM vessels WHERE vessel_id = ?", (vessel_id,))
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel with ID '{vessel_id}' not found.")
    return vessel

# 4. Congestion Endpoints
@app.get("/api/congestion")
def get_congestion():
    return calculate_congestion_risk()

# 5. Berths Endpoints
@app.get("/api/berths", response_model=List[Berth])
def get_berths():
    return fetch_all("SELECT * FROM berths ORDER BY berth_id ASC")

# 6. Cranes Endpoints
@app.get("/api/cranes", response_model=List[Crane])
def get_cranes():
    return fetch_all("SELECT * FROM cranes ORDER BY crane_id ASC")

# 7. Disruptions Endpoints
@app.get("/api/disruptions", response_model=List[Disruption])
def get_disruptions():
    return fetch_all("SELECT * FROM disruptions ORDER BY is_active DESC, severity DESC")

# 8. Assignments Endpoint
@app.get("/api/assignments")
def get_assignments():
    return fetch_all("SELECT * FROM assignments ORDER BY assignment_id DESC")

# 9. 72-Hour Operations Plan Endpoint
@app.get("/api/operations-plan", response_model=OperationsPlanResponse)
def get_operations_plan():
    return generate_72_hour_operations_plan()

# 10. Alternate Routing Optimization POST Endpoint
@app.post("/api/route/recommend", response_model=AlternateRouteRecommendation)
def post_route_recommend(req: AlternateRouteRequest):
    res = recommend_alternate_routing(req.vessel_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

# 11. Berth Optimization POST Endpoint
@app.post("/api/berth/optimise", response_model=BerthOptimizeResponse)
def post_berth_optimise(req: BerthOptimizeRequest):
    res = optimize_berth_assignment(req.vessel_id, req.preferred_berth_id)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# 12. Crane Optimization POST Endpoint
@app.post("/api/crane/optimise", response_model=CraneOptimizeResponse)
def post_crane_optimise(req: CraneOptimizeRequest):
    res = optimize_crane_assignment(req.vessel_id, req.berth_id)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# 13. AI Assistant / Bob Copilot Endpoint
@app.post("/api/assistant", response_model=AssistantResponse)
def post_ai_assistant(req: AssistantRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return query_ai_assistant(req.question.strip())

# Serve Frontend Static Files
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def read_root():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html not found, but API is running."}
