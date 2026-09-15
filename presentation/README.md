# Presentation Deck Outline - IBM Bob AI Hackathon Round 1

**Team Name:** Tech Titans  
**Problem Statement:** L1 — Container Congestion Predictor & Port Operations Optimiser  

---

## Slide Structure & Content

### Slide 1: Problem & Industry Challenge
- **Title**: Container Port Congestion & Operations Bottleneck
- **Key Points**:
  - Global ports suffer from reactive congestion management and manual berth/crane allocation.
  - Demurrage penalties, fuel waste, and vessel queuing costs maritime operators millions annually.
  - Current TOS systems lack real-time predictive intelligence and conflict-free optimization.

### Slide 2: Solution Architecture & Tech Stack
- **Title**: Intelligent Port Control Center
- **Key Points**:
  - Real-time 0–100 Congestion Index with root-cause explainability.
  - Constraint-based berth scheduler avoiding double-booking conflicts over time.
  - Quay crane allocation engine optimizing handling rates (TEU/hr).
  - Alternate routing engine generating synthetic port diversions (*Port Alpha, Port Beta, Port Gamma*).
  - Tech Stack: Python 3.11, FastAPI, SQLite, Vanilla HTML/CSS/JS.

### Slide 3: Demo & Core Workflow
- **Title**: Control Center Live Demo & 72-Hour Ops Plan
- **Key Points**:
  - Live command center UI displaying vessel queue, active disruptions, and berth occupancy gauges.
  - Shift supervisor 72-hour operational plan detailing 6-hour time block shift schedules.
  - 42.5% reduction in simulated vessel waiting time.

### Slide 4: IBM Bob & MCP Integration
- **Title**: Agentic Model Context Protocol (MCP) Integration
- **Key Points**:
  - Dedicated MCP Server (`src/backend/mcp_server.py`) exposing 7 tools to IBM Bob agents.
  - Context-aware Bob Copilot AI Assistant embedded in the dashboard UI.
  - Support for local deterministic execution + optional IBM watsonx.ai Granite LLM model integration.

### Slide 5: Business Impact & Scalability
- **Title**: Operational ROI & Future Roadmap
- **Key Points**:
  - Immediate ROI: Reduction in demurrage fees, vessel idle time, and shift planning labor overhead.
  - Scalability: Production-ready API architecture easily portable to enterprise PostgreSQL/Kubernetes infrastructure.
