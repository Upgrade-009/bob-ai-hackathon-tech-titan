# Architecture & Component Design

## 1. System Architecture Diagram

```mermaid
graph TD
    Client UI[Vanilla HTML/CSS/JS Frontend Dashboard] -->|REST API /api/*| FastAPI[FastAPI Web Server main.py]
    IBMBob[IBM Bob Agent] -->|MCP Protocol / JSON-RPC| MCPServer[MCP Server mcp_server.py]
    
    FastAPI --> Services[Business Logic Services Layer]
    MCPServer --> Services
    
    subgraph Services Layer
        Congestion[Congestion Service]
        BerthOpt[Berth Optimizer Service]
        CraneOpt[Crane Optimizer Service]
        Routing[Routing Recommendation Service]
        OpsPlan[72-Hour Ops Plan Service]
        AIAssistant[Bob Copilot AI Assistant]
    end
    
    Services --> DB[SQLite Database port_operations.db]
    DB --> CSVs[Data CSV Ingester vessels, berths, cranes, disruptions]
```

## 2. Component Specification

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5, CSS3, JS | Single Page Dashboard with sidebar navigation, KPI cards, tables, and AI Copilot chat drawer. |
| **REST API Server** | FastAPI, Uvicorn | Exposes 13 validated Pydantic endpoints for dashboard KPIs, vessels, congestion, optimizers, and chat assistant. |
| **MCP Server** | Python MCP SDK | Exposes 7 tools to IBM Bob for agentic tool use. Shares exact business logic with web API. |
| **Database Layer** | SQLite (`port_operations.db`) | Relational persistence with automated CSV seed data loader. |
| **AI Assistant** | Local Intelligence / watsonx.ai | Deterministic natural language query parser with optional IBM watsonx Granite LLM fallback. |

## 3. Security & Scalability Notes
- **Zero Credentials Leaked**: No real API keys or tokens are stored in source files. Environment template provided in `.env.example`.
- **Validation**: All POST payloads validated using Pydantic schemas returning clean HTTP 400/404 error codes.
- **Scalability**: SQLite handles up to 100,000 requests/day cleanly. Easy upgrade path to PostgreSQL via standard SQL abstraction.
