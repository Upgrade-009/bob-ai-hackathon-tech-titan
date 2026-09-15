# Solution Overview: Port Operations Optimiser

## 1. System Mechanism & Workflow

The **Container Congestion Predictor & Port Operations Optimiser** operates through an end-to-end data pipeline:

1. **Telemetry & Data Ingestion**: SQLite database ingests vessel ETAs, container volumes, berth capacities, crane handling rates (TEU/hr), and active weather/equipment disruptions.
2. **Predictive Congestion Engine**: Evaluates berth occupancy, queue density, arrival concentration, disruption severity, and vessel priority to generate a 0–100 risk score (LOW, MEDIUM, HIGH, CRITICAL).
3. **Constraint-Based Optimization Engines**:
   - **Berth Optimiser**: Matches vessel length and draft constraints to berths, selecting optimal service windows while preventing double-booking.
   - **Quay Crane Optimiser**: Allocates available cranes based on container volumes without dual-assigning cranes concurrently.
4. **Alternate Routing Generator**: Recommends synthetic port diversions (*Port Alpha, Port Beta, Port Gamma*), berth switches, or slow-steaming when congestion exceeds threshold limits.
5. **72-Hour Operational Plan**: Synthesizes shift schedules into 6-hour time blocks for supervisors.
6. **IBM Bob Copilot & MCP Tools**: Exposes real-time tool endpoints (`src/backend/mcp_server.py`) for natural language chat and direct agent execution.

## 2. Mathematical Congestion Formula

The congestion score $S_{\text{berth}}$ for berth $b$ is computed as:

$$S_{\text{berth}} = \min\left(100, \, 0.35 \times \text{Occupancy}_{\%} + 0.25 \times \min(100, \, Q \times 15) + 0.10 \times (V_{\text{priority}} \times 5) + D_{\text{impact}}\right)$$

Where:
- $\text{Occupancy}_{\%}$: Current berth capacity utilization percentage.
- $Q$: Number of queued vessels assigned to the berth.
- $V_{\text{priority}}$: Count of HIGH/CRITICAL priority vessels pending.
- $D_{\text{impact}}$: Active disruption penalty points (15 for CRITICAL, 10 for HIGH, 5 for MEDIUM).

Risk levels map directly to:
- **0–29**: LOW
- **30–49**: MEDIUM
- **50–74**: HIGH
- **75–100**: CRITICAL

## 3. IBM Bob & MCP Integration Role
The backend implements a dedicated MCP tool server (`src/backend/mcp_server.py`) providing tools (`get_port_status`, `get_vessel_risk`, `get_congestion_hotspots`, `optimise_berths`, `optimise_cranes`, `recommend_alternate_route`, `generate_72_hour_plan`). IBM Bob agents can execute these tools directly to inspect port telematics and perform schedule optimization.
