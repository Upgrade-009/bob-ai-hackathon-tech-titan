// Port Operations Control Center - Pure Vanilla JavaScript Frontend

document.addEventListener("DOMContentLoaded", () => {
    // State
    let state = {
        dashboard: null,
        vessels: [],
        berths: [],
        cranes: [],
        disruptions: [],
        congestion: null,
        operationsPlan: null
    };

    // Initialize UI
    initClock();
    initTabNavigation();
    initEventListeners();
    fetchTelemetryData();

    // 1. Live Clock
    function initClock() {
        const clockEl = document.getElementById("live-clock");
        function updateClock() {
            const now = new Date();
            clockEl.textContent = now.toTimeString().split(" ")[0] + " UTC";
        }
        updateClock();
        setInterval(updateClock, 1000);
    }

    // 2. Tab Navigation
    function initTabNavigation() {
        const navButtons = document.querySelectorAll(".nav-item");
        const tabContents = document.querySelectorAll(".tab-content");
        const pageTitle = document.getElementById("page-title");

        const tabTitles = {
            "dashboard": "Port Operations Overview",
            "vessel-analysis": "Vessel Fleet Analysis & Telematics",
            "congestion-routing": "Congestion Diagnostics & Alternate Routing",
            "optimization-studio": "Berth & Quay Crane Optimization Studio",
            "operations-plan": "Shift Supervisor 72-Hour Operational Plan"
        };

        navButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-tab");
                navButtons.forEach(b => b.classList.remove("active"));
                tabContents.forEach(c => c.classList.remove("active"));

                btn.classList.add("active");
                document.getElementById(`tab-${targetTab}`).classList.add("active");
                pageTitle.textContent = tabTitles[targetTab] || "Port Operations";
            });
        });
    }

    // 3. Global Event Listeners
    function initEventListeners() {
        // Refresh Button
        document.getElementById("btn-refresh").addEventListener("click", () => {
            fetchTelemetryData();
        });

        // Toggle Assistant Drawer
        const drawer = document.getElementById("assistant-drawer");
        document.getElementById("btn-toggle-assistant").addEventListener("click", () => {
            drawer.classList.toggle("hidden");
        });
        document.getElementById("btn-close-assistant").addEventListener("click", () => {
            drawer.classList.add("hidden");
        });

        // Chat Quick Prompts
        document.querySelectorAll(".chip-btn").forEach(chip => {
            chip.addEventListener("click", () => {
                const prompt = chip.getAttribute("data-prompt");
                document.getElementById("chat-input").value = prompt;
                sendChatMessage(prompt);
            });
        });

        // Chat Form Submit
        document.getElementById("chat-form").addEventListener("submit", (e) => {
            e.preventDefault();
            const input = document.getElementById("chat-input");
            const msg = input.value.trim();
            if (msg) {
                sendChatMessage(msg);
                input.value = "";
            }
        });

        // Routing Form Submit
        document.getElementById("routing-form").addEventListener("submit", (e) => {
            e.preventDefault();
            const vId = document.getElementById("route-vessel-select").value;
            submitRoutingOptimization(vId);
        });

        // Berth Optimizer Form Submit
        document.getElementById("berth-opt-form").addEventListener("submit", (e) => {
            e.preventDefault();
            const vId = document.getElementById("berth-vessel-select").value;
            submitBerthOptimization(vId);
        });

        // Crane Optimizer Form Submit
        document.getElementById("crane-opt-form").addEventListener("submit", (e) => {
            e.preventDefault();
            const vId = document.getElementById("crane-vessel-select").value;
            const bId = document.getElementById("crane-berth-select").value;
            submitCraneOptimization(vId, bId);
        });

        // Vessel Table Search Filter
        document.getElementById("vessel-search").addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase();
            filterVesselsTable(query);
        });
    }

    // 4. API Fetching
    async function fetchTelemetryData() {
        showLoading(true);
        try {
            const [dashRes, vesselsRes, berthsRes, cranesRes, disruptionsRes, congestionRes, planRes] = await Promise.all([
                fetch("/api/dashboard"),
                fetch("/api/vessels"),
                fetch("/api/berths"),
                fetch("/api/cranes"),
                fetch("/api/disruptions"),
                fetch("/api/congestion"),
                fetch("/api/operations-plan")
            ]);

            state.dashboard = await dashRes.json();
            state.vessels = await vesselsRes.json();
            state.berths = await berthsRes.json();
            state.cranes = await cranesRes.json();
            state.disruptions = await disruptionsRes.json();
            state.congestion = await congestionRes.json();
            state.operationsPlan = await planRes.json();

            renderDashboard();
            renderVesselsTable();
            renderCongestionDiagnostics();
            renderOptimizationSelects();
            renderOperationsPlan();

        } catch (err) {
            console.error("Telemetry fetch error:", err);
            alert("Failed to connect to backend API server at /api/*");
        } finally {
            showLoading(false);
        }
    }

    function showLoading(visible) {
        const overlay = document.getElementById("loading-overlay");
        if (visible) overlay.classList.remove("hidden");
        else overlay.classList.add("hidden");
    }

    // 5. Render Dashboard Tab
    function renderDashboard() {
        const d = state.dashboard;
        if (!d) return;

        document.getElementById("kpi-total-vessels").textContent = d.total_vessels;
        document.getElementById("kpi-vessels-at-risk").textContent = d.vessels_at_risk;
        document.getElementById("kpi-congested-berths").textContent = d.congested_berths_count;
        document.getElementById("kpi-avg-wait").textContent = `${d.average_waiting_time_hrs} hrs`;
        document.getElementById("kpi-crane-util").textContent = `${d.fleet_crane_utilization_pct}%`;

        // Overall Risk Badge
        const c = state.congestion;
        const riskBadge = document.getElementById("overall-risk-badge");
        if (c) {
            riskBadge.textContent = `${c.overall_risk_level} RISK (${c.overall_port_congestion_score}/100)`;
            riskBadge.className = `badge badge-${c.overall_risk_level}`;
        }

        // Render Berth Occupancy List
        const berthContainer = document.getElementById("berth-occupancy-list");
        berthContainer.innerHTML = "";
        state.berths.forEach(b => {
            const occ = Math.round(b.current_occupancy);
            let barColor = "var(--status-green)";
            if (occ >= 80) barColor = "var(--status-red)";
            else if (occ >= 60) barColor = "var(--status-orange)";
            else if (occ >= 40) barColor = "var(--status-yellow)";

            const item = document.createElement("div");
            item.className = "berth-item";
            item.innerHTML = `
                <div class="berth-info">
                    <strong>${b.berth_id} - ${b.name}</strong>
                    <span>${occ}% Occupied (${b.status})</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${occ}%; background-color: ${barColor}"></div>
                </div>
            `;
            berthContainer.appendChild(item);
        });

        // Render Active Disruptions
        const disruptionsContainer = document.getElementById("disruptions-list");
        document.getElementById("disruptions-count").textContent = state.disruptions.length;
        disruptionsContainer.innerHTML = "";
        
        state.disruptions.slice(0, 4).forEach(dis => {
            const dCard = document.createElement("div");
            dCard.className = "disruption-card";
            dCard.innerHTML = `
                <h4><i class="fa-solid fa-triangle-exclamation"></i> ${dis.type} (${dis.severity})</h4>
                <p><strong>Target:</strong> ${dis.affected_target} | <strong>Duration:</strong> ~${dis.expected_duration_hrs}h</p>
                <p>${dis.description}</p>
            `;
            disruptionsContainer.appendChild(dCard);
        });

        // Render High Priority Queue Table
        const queueBody = document.getElementById("queue-table-body");
        queueBody.innerHTML = "";
        const highPriorityVessels = state.vessels.filter(v => v.priority === "HIGH" || v.priority === "CRITICAL").slice(0, 5);
        
        highPriorityVessels.forEach(v => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${v.vessel_id}</strong></td>
                <td>${v.name}</td>
                <td>${formatDate(v.eta)}</td>
                <td><span class="badge badge-${v.priority}">${v.priority}</span></td>
                <td>${v.container_count.toLocaleString()} TEUs</td>
                <td>${v.assigned_berth || 'Unassigned'}</td>
                <td>${v.estimated_waiting_time_hrs}h</td>
                <td><span class="badge">${v.status}</span></td>
            `;
            queueBody.appendChild(tr);
        });
    }

    // 6. Render Vessel Directory Table
    function renderVesselsTable() {
        const body = document.getElementById("vessels-full-table-body");
        body.innerHTML = "";
        state.vessels.forEach(v => {
            const tr = document.createElement("tr");
            tr.setAttribute("data-search", `${v.vessel_id} ${v.name}`.toLowerCase());
            
            let risk = "LOW";
            if (v.priority === "CRITICAL" || v.estimated_waiting_time_hrs >= 10) risk = "CRITICAL";
            else if (v.priority === "HIGH" || v.estimated_waiting_time_hrs >= 6) risk = "HIGH";
            else if (v.estimated_waiting_time_hrs >= 3) risk = "MEDIUM";

            tr.innerHTML = `
                <td><strong>${v.vessel_id}</strong></td>
                <td>${v.name}</td>
                <td>${formatDate(v.eta)}</td>
                <td>${v.current_port} → ${v.destination}</td>
                <td>${v.cargo_type}</td>
                <td>${v.container_count.toLocaleString()} TEU</td>
                <td><span class="badge badge-${v.priority}">${v.priority}</span></td>
                <td>${v.assigned_berth || 'Pending'}</td>
                <td>${v.estimated_waiting_time_hrs}h</td>
                <td><span class="badge badge-${risk}">${risk}</span></td>
                <td>
                    <button class="btn-secondary btn-sm-optimize" data-vid="${v.vessel_id}">
                        Optimise
                    </button>
                </td>
            `;
            body.appendChild(tr);
        });

        // Add Quick Optimize button handlers
        document.querySelectorAll(".btn-sm-optimize").forEach(btn => {
            btn.addEventListener("click", () => {
                const vid = btn.getAttribute("data-vid");
                document.querySelector("[data-tab='optimization-studio']").click();
                document.getElementById("berth-vessel-select").value = vid;
            });
        });
    }

    function filterVesselsTable(query) {
        const rows = document.querySelectorAll("#vessels-full-table-body tr");
        rows.forEach(r => {
            const text = r.getAttribute("data-search");
            if (text.includes(query)) r.style.display = "";
            else r.style.display = "none";
        });
    }

    // 7. Render Congestion Diagnostics
    function renderCongestionDiagnostics() {
        const c = state.congestion;
        if (!c) return;

        const container = document.getElementById("congestion-explainability-container");
        container.innerHTML = "";

        c.berth_details.forEach(b => {
            const card = document.createElement("div");
            card.className = "disruption-card";
            card.style.borderLeftColor = b.risk_level === "CRITICAL" ? "var(--status-red)" : (b.risk_level === "HIGH" ? "var(--status-orange)" : "var(--status-green)");
            
            const causesList = b.primary_causes.map(cause => `<li>${cause}</li>`).join("");
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4>${b.berth_id} - ${b.berth_name}</h4>
                    <span class="badge badge-${b.risk_level}">${b.risk_level} (${b.congestion_score}/100)</span>
                </div>
                <p><strong>Occupancy:</strong> ${b.occupancy_pct}% | <strong>Queue Count:</strong> ${b.queue_count} vessel(s)</p>
                <ul style="padding-left:1.2rem; margin-top:0.4rem; font-size:0.85rem; color:var(--text-secondary);">
                    ${causesList}
                </ul>
            `;
            container.appendChild(card);
        });
    }

    // 8. Render Select Options for Optimizers
    function renderOptimizationSelects() {
        const rSelect = document.getElementById("route-vessel-select");
        const bSelect = document.getElementById("berth-vessel-select");
        const cVesselSelect = document.getElementById("crane-vessel-select");
        const cBerthSelect = document.getElementById("crane-berth-select");

        rSelect.innerHTML = "";
        bSelect.innerHTML = "";
        cVesselSelect.innerHTML = "";
        cBerthSelect.innerHTML = "";

        state.vessels.forEach(v => {
            const opt = `<option value="${v.vessel_id}">${v.vessel_id} - ${v.name} (${v.priority})</option>`;
            rSelect.insertAdjacentHTML("beforeend", opt);
            bSelect.insertAdjacentHTML("beforeend", opt);
            cVesselSelect.insertAdjacentHTML("beforeend", opt);
        });

        state.berths.forEach(b => {
            const opt = `<option value="${b.berth_id}">${b.berth_id} - ${b.name}</option>`;
            cBerthSelect.insertAdjacentHTML("beforeend", opt);
        });
    }

    // 9. Submit Alternate Routing Optimization
    async function submitRoutingOptimization(vesselId) {
        try {
            const res = await fetch("/api/route/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ vessel_id: vesselId })
            });
            const data = await res.json();
            
            const card = document.getElementById("routing-result-card");
            card.classList.remove("hidden");
            card.innerHTML = `
                <h4><i class="fa-solid fa-compass"></i> Routing Recommendation for ${data.vessel_name} (${data.vessel_id})</h4>
                <p><strong>Recommended Strategy:</strong> <span class="badge badge-${data.priority}">${data.recommended_option}</span></p>
                <p><strong>Alternate Target:</strong> ${data.alternate_port || data.alternate_berth || 'Current Schedule'}</p>
                <p><strong>Estimated Wait Reduction:</strong> ~${data.estimated_wait_reduction_hrs} hours</p>
                <p><strong>Reasoning:</strong> ${data.reason}</p>
                <small style="color:var(--text-secondary); display:block; margin-top:0.4rem;">* Alternate ports (Port Alpha / Port Beta / Port Gamma) are synthetic demo alternatives.</small>
            `;
        } catch (err) {
            alert("Error running alternate routing calculation.");
        }
    }

    // 10. Submit Berth Optimization
    async function submitBerthOptimization(vesselId) {
        try {
            const res = await fetch("/api/berth/optimise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ vessel_id: vesselId })
            });
            const data = await res.json();
            
            const card = document.getElementById("berth-opt-result");
            card.classList.remove("hidden");
            card.innerHTML = `
                <h4><i class="fa-solid fa-circle-check"></i> Optimal Berth Assigned: ${data.recommended_berth} (${data.berth_name})</h4>
                <p><strong>Service Window:</strong> ${formatDate(data.expected_start_time)} → ${formatDate(data.expected_completion_time)} (~${data.estimated_service_hrs}h)</p>
                <p><strong>Conflict Prevention:</strong> Double-booking prevented across timeline.</p>
                <p><strong>Rationale:</strong> ${data.reason}</p>
            `;
            fetchTelemetryData(); // Refresh UI
        } catch (err) {
            alert("Error running berth optimization.");
        }
    }

    // 11. Submit Crane Optimization
    async function submitCraneOptimization(vesselId, berthId) {
        try {
            const res = await fetch("/api/crane/optimise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ vessel_id: vesselId, berth_id: berthId })
            });
            const data = await res.json();
            
            const card = document.getElementById("crane-opt-result");
            card.classList.remove("hidden");
            card.innerHTML = `
                <h4><i class="fa-solid fa-tower-observation"></i> Quay Cranes Allocated: ${data.assigned_cranes.join(", ")}</h4>
                <p><strong>Total Capacity:</strong> ${data.total_handling_capacity_teu_hr} TEU/hr</p>
                <p><strong>Est. Handling Duration:</strong> ${data.estimated_handling_duration_hrs} hours</p>
                <p><strong>Fleet Utilization:</strong> ${data.crane_utilization_pct}%</p>
                <p><strong>Rationale:</strong> ${data.reason}</p>
            `;
            fetchTelemetryData(); // Refresh UI
        } catch (err) {
            alert("Error running crane optimization.");
        }
    }

    // 12. Render 72-Hour Operations Plan
    function renderOperationsPlan() {
        const plan = state.operationsPlan;
        if (!plan) return;

        document.getElementById("plan-impact-summary").innerHTML = `
            <strong><i class="fa-solid fa-chart-line"></i> Operational Impact:</strong> ${plan.expected_impact_summary}
        `;

        const body = document.getElementById("plan-table-body");
        body.innerHTML = "";

        plan.current_plan.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${item.time_block}</strong></td>
                <td>${item.vessel_id} (${item.vessel_name})</td>
                <td>${item.berth_id}</td>
                <td>${item.cranes.join(", ")}</td>
                <td>${item.action}</td>
                <td><span class="badge badge-${item.priority}">${item.priority}</span></td>
                <td><span class="badge badge-${item.congestion_risk}">${item.congestion_risk}</span></td>
                <td style="font-size:0.85rem;">${item.expected_impact}</td>
            `;
            body.appendChild(tr);
        });
    }

    // 13. Bob Copilot AI Chat Messages
    async function sendChatMessage(message) {
        const chatContainer = document.getElementById("chat-messages");

        // Append User Message
        const uMsg = document.createElement("div");
        uMsg.className = "chat-bubble user";
        uMsg.textContent = message;
        chatContainer.appendChild(uMsg);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Append Thinking Indicator
        const tMsg = document.createElement("div");
        tMsg.className = "chat-bubble assistant";
        tMsg.innerHTML = `<em>Bob Copilot is analyzing port telematics...</em>`;
        chatContainer.appendChild(tMsg);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const res = await fetch("/api/assistant", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: message })
            });
            const data = await res.json();

            // Replace thinking indicator with response
            tMsg.innerHTML = formatMarkdownResponse(data.answer);
            chatContainer.scrollTop = chatContainer.scrollHeight;

        } catch (err) {
            tMsg.innerHTML = `<span style="color:var(--status-red)">Error communicating with Bob Copilot AI backend.</span>`;
        }
    }

    function formatMarkdownResponse(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    function formatDate(isoStr) {
        if (!isoStr) return "--";
        try {
            const d = new Date(isoStr);
            return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return isoStr;
        }
    }
});
