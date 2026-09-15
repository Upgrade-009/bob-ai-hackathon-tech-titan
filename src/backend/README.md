# Backend Services & MCP Integration (`src/backend/`)

The backend is built with Python 3.11+, FastAPI, and SQLite.

## Structure

```
src/backend/
├── main.py                 # FastAPI application & REST endpoint router
├── database.py             # SQLite connection & CSV auto-seeder
├── models.py               # Pydantic data schemas
├── mcp_server.py           # IBM Bob Model Context Protocol (MCP) tool server
├── requirements.txt        # Python dependency manifest
├── .env.example            # Environment configuration template
├── data/                   # Synthetic CSV datasets (vessels, berths, cranes, disruptions)
└── services/
    ├── congestion.py       # Congestion score algorithm & hotspot diagnostics
    ├── berth_optimizer.py  # Constraint-based berth scheduler
    ├── crane_optimizer.py  # Quay crane allocation engine
    ├── routing.py          # Alternate routing & synthetic port diversion engine
    ├── operations_plan.py  # 72-hour operational shift plan generator
    └── ai_assistant.py     # Bob Copilot query parser & tool wrapper
```

## Running the Backend Server
```bash
python -m uvicorn src.backend.main:app --reload --port 8000
```

## Running the MCP Tools CLI
```bash
python src/backend/mcp_server.py list
python src/backend/mcp_server.py get_port_status
```
