# Container Congestion Predictor & Port Operations Optimiser
### IBM Bob AI Innovation Hackathon Round 1 Submission

**Team Name:** Tech Titans  
**Track:** AI  
**Problem Statement:** L1 — Container Congestion Predictor & Port Operations Optimiser  
**Repository:** [github.com/Upgrade-009/bob-ai-hackathon-tech-titans](https://github.com/Upgrade-009/bob-ai-hackathon-tech-titans)

---

## 🚢 Executive Summary

Port operators around the globe manually allocate berths, quay cranes, and yard space across hundreds of arriving container vessels. Congestion hotspots are detected reactively, leading to vessel queuing, demurrage costs, and delayed rerouting decisions.

**Team Tech Titans** presents an intelligent, real-time **Container Congestion Predictor & Port Operations Optimiser** integrated with **IBM Bob** via the Model Context Protocol (MCP).

Our system predicts berth congestion hotspots up to 72 hours in advance, automatically optimizes berth and quay crane assignments, calculates alternate routing strategies (including synthetic port diversions), and generates hour-by-hour operational plans for shift supervisors.

---

## ✨ Key Implemented Features

1. **Explainable Congestion Hotspot Predictor**:
   - Calculates a 0–100 congestion risk index (LOW, MEDIUM, HIGH, CRITICAL) using berth occupancy, queue density, vessel arrival clustering, active disruptions, and vessel priority.
   - Explains the exact root causes behind every congested berth.

2. **Constraint-Based Berth Optimiser**:
   - Dynamically matches vessel dimensions (length, draft) and arrival windows to berth capacity while preventing double-booking conflicts over time.

3. **Quay Crane Allocation Engine**:
   - Assigns available quay cranes (TEU/hr handling capacity) to vessels based on container volume and priority without dual-assigning cranes simultaneously.

4. **Alternate Routing Recommendation Engine**:
   - Automatically suggests alternate routing strategies (Port Alpha, Port Beta, Port Gamma synthetic diversions, berth switches, slow-steaming) during HIGH or CRITICAL congestion.

5. **Shift Supervisor 72-Hour Operations Plan**:
   - Generates a 6-hour time block operational plan for the next 72 hours with scheduled actions, assigned cranes, risk tags, and expected queue reduction impact.

6. **Bob Copilot AI Assistant & MCP Server**:
   - Context-aware chat copilot using local intelligence (with optional IBM watsonx.ai Granite support).
   - Dedicated Model Context Protocol server (`src/backend/mcp_server.py`) exposing real-time port telemetry tools directly to IBM Bob.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLite, Pydantic, pandas
- **Frontend**: Pure HTML5, CSS3 (Dark Theme Command Center), Vanilla JavaScript (No React/Node/npm dependency)
- **AI & Integrations**: Model Context Protocol (MCP), IBM Bob integration, optional IBM watsonx.ai REST interface
- **Database**: SQLite (`port_operations.db` auto-seeded on first run)

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.11 or higher installed on your system.

### 1. Install Dependencies
```bash
cd src/backend
pip install -r requirements.txt
```

### 2. Start the FastAPI Application Server
```bash
python -m uvicorn src.backend.main:app --reload --port 8000
```

### 3. Open the Dashboard in your Browser
Navigate to:
```
http://127.0.0.1:8000/
```

### 4. Run the IBM Bob MCP Server (CLI Verification)
```bash
python src/backend/mcp_server.py get_port_status
python src/backend/mcp_server.py get_congestion_hotspots
```

---

## 🎥 Demo & Artifact Links

- **Live Demo URL**: See `demo/live-demo-url.txt` (`NOT DEPLOYED` - Runs locally via Uvicorn)
- **Demo Video Link**: See `demo/demo-video-link.txt` (`NOT AVAILABLE YET`)
- **Required Screenshots Guide**: See `demo/screenshots/README.md`
- **Presentation Deck Outline**: See `presentation/README.md`

---

## 📄 Documentation Sitemap

- [docs/problem-statement.md](docs/problem-statement.md): Comprehensive problem context, affected stakeholders, and industry impact.
- [docs/solution-overview.md](docs/solution-overview.md): System architecture, data flow, algorithm mathematical formulas, and AI assistant design.
- [docs/architecture.md](docs/architecture.md): Mermaid architecture diagrams, component specifications, and security notes.
- [docs/setup-guide.md](docs/setup-guide.md): Executable step-by-step installation and troubleshooting guide.

---

## 💡 Known Limitations & Synthetic Data Disclosure

- **Synthetic/Demo Data**: Vessel schedules, berth capacities, crane assignments, and alternate ports (*Port Alpha, Port Beta, Port Gamma*) are synthetic data created specifically to demonstrate congestion algorithms and optimization scenarios.
- **Local AI Intelligence**: Default assistant responses run deterministically offline to guarantee zero external downtime. IBM watsonx.ai can be enabled by specifying environment variables (`WATSONX_API_KEY`, `WATSONX_PROJECT_ID`).

---

## 🏆 What We're Most Proud Of

- **Zero-Config Instant Start**: The SQLite database auto-seeds from CSV data on application launch without requiring manual SQL setup.
- **True MCP Server Integration**: Native Model Context Protocol implementation sharing exact service logic between web UI and IBM Bob agent tools.
- **Working Optimization & 72-Hour Planning**: Real constraint-based berth/crane matching and supervisor shift planning that measurably reduces simulated vessel queue wait times.
