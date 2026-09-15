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
                const targetEl = document.getElementById(`tab-${targetTab}`);
                if (targetEl) targetEl.classList.add("active");
                if (pageTitle) pageTitle.textContent = tabTitles[targetTab] || "Port Operations";

                // Requirement 2: Scroll reset to top on navigation
                const mainContent = document.querySelector(".main-content");
                if (mainContent) mainContent.scrollTop = 0;
                window.scrollTo(0, 0);

                // Requirement 3: Auto-close Bob Copilot drawer on navigation
                const drawer = document.getElementById("assistant-drawer");
                if (drawer) drawer.classList.add("hidden");
            });
        });
    }

    // 3. Global Event Listeners
    function initEventListeners() {
        // Refresh Telemetry Button with Loading Feedback (Requirement 5)
        const refreshBtn = document.getElementById("btn-refresh");
        if (refreshBtn) {
            refreshBtn.addEventListener("click", async () => {
                const origHTML = refreshBtn.innerHTML;
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Refreshing...`;
                
                await fetchTelemetryData();
                
                refreshBtn.innerHTML = `<i class="fa-solid fa-check"></i> Refreshed`;
                setTimeout(() => {
                    refreshBtn.innerHTML = origHTML;
                    refreshBtn.disabled = false;
                }, 1200);
            });
        }

        // Toggle Assistant Drawer
        const drawer = document.getElementById("assistant-drawer");
        const toggleBtn = document.getElementById("btn-toggle-assistant");
        const closeBtn = document.getElementById("btn-close-assistant");

        if (toggleBtn && drawer) {
            toggleBtn.addEventListener("click", () => {
                drawer.classList.toggle("hidden");
            });
        }
        if (closeBtn && drawer) {
            closeBtn.addEventListener("click", () => {
                drawer.classList.add("hidden");
            });
        }

        // Chat Quick Prompts
        document.querySelectorAll(".chip-btn").forEach(chip => {
            chip.addEventListener("click", () => {
                const prompt = chip.getAttribute("data-prompt");
                const input = document.getElementById("chat-input");
                if (input) input.value = prompt;
                sendChatMessage(prompt);
            });
        });

        // Chat Form Submit
        const chatForm = document.getElementById("chat-form");
        if (chatForm) {
            chatForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const input = document.getElementById("chat-input");
                const msg = input ? input.value.trim() : "";
                if (msg) {
                    sendChatMessage(msg);
                    if (input) input.value = "";
                }
            });
        }

        // Routing Form Submit
        const routingForm = document.getElementById("routing-form");
        if (routingForm) {
            routingForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const select = document.getElementById("route-vessel-select");
                const vId = select ? select.value : "";
                if (vId) submitRoutingOptimization(vId);
            });
        }

        // Berth Optimizer Form Submit
        const berthForm = document.getElementById("berth-opt-form");
        if (berthForm) {
            berthForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const select = document.getElementById("berth-vessel-select");
                const vId = select ? select.value : "";
                if (vId) submitBerthOptimization(vId);
            });
        }

        // Crane Optimizer Form Submit
        const craneForm = document.getElementById("crane-opt-form");
        if (craneForm) {
            craneForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const vSelect = document.getElementById("crane-vessel-select");
                const bSelect = document.getElementById("crane-berth-select");
                const vId = vSelect ? vSelect.value : "";
                const bId = bSelect ? bSelect.value : "";
                if (vId && bId) submitCraneOptimization(vId, bId);
            });
        }

        // Vessel Table Search Filter
        const searchInput = document.getElementById("vessel-search");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                const query = e.target.value.toLowerCase();
                filterVesselsTable(query);
            });
        }
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

            // Ensure status indicator reads connected
            const statusIndicator = document.querySelector(".status-indicator");
            if (statusIndicator) {
                statusIndicator.innerHTML = `<span class="dot online"></span> API Connected`;
            }

        } catch (err) {
            console.error("Telemetry fetch error:", err);
            const statusIndicator = document.querySelector(".status-indicator");
            if (statusIndicator) {
                statusIndicator.innerHTML = `<span class="dot offline" style="background:#ef4444"></span> Connection Offline`;
            }
        } finally {
            showLoading(false);
        }
    }

    function showLoading(visible) {
        const overlay = document.getElementById("loading-overlay");
        if (overlay) {
            if (visible) overlay.classList.remove("hidden");
            else overlay.classList.add("hidden");
        }
    }

    // 5. Render Dashboard Tab
    function renderDashboard() {
        const d = state.dashboard;
        if (!d) return;

        const elTotal = document.getElementById("kpi-total-vessels");
        const elRisk = document.getElementById("kpi-vessels-at-risk");
        const elBerths = document.getElementById("kpi-congested-berths");
        const elWait = document.getElementById("kpi-avg-wait");
        const elUtil = document.getElementById("kpi-crane-util");

        if (elTotal) elTotal.textContent = d.total_vessels ?? 0;
        if (elRisk) elRisk.textContent = d.vessels_at_risk ?? 0;
        if (elBerths) elBerths.textContent = d.congested_berths_count ?? 0;
        if (elWait) elWait.textContent = `${d.average_waiting_time_hrs ?? 0} hrs`;
        if (elUtil) elUtil.textContent = `${d.fleet_crane_utilization_pct ?? 0}%`;

        // Overall Risk Badge
        const c = state.congestion;
        const riskBadge = document.getElementById("overall-risk-badge");
        if (c && riskBadge) {
            const rLevel = c.overall_risk_level || "LOW";
            const rScore = c.overall_port_congestion_score ?? 0;
            riskBadge.textContent = `${rLevel} RISK (${rScore}/100)`;
            riskBadge.className = `badge badge-${rLevel}`;
        }

        // Render Berth Occupancy List
        const berthContainer = document.getElementById("berth-occupancy-list");
        if (berthContainer && state.berths) {
            berthContainer.innerHTML = "";
            state.berths.forEach(b => {
                const occ = Math.round(b.current_occupancy || 0);
                let barColor = "var(--status-green)";
                if (occ >= 80) barColor = "var(--status-red)";
                else if (occ >= 60) barColor = "var(--status-orange)";
                else if (occ >= 40) barColor = "var(--status-yellow)";

                const item = document.createElement("div");
                item.className = "berth-item";
                item.innerHTML = `
                    <div class="berth-info">
                        <strong>${b.berth_id || 'Berth'} - ${b.name || 'Main Quay'}</strong>
                        <span>${occ}% Occupied (${b.status || 'AVAILABLE'})</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: ${occ}%; background-color: ${barColor}"></div>
                    </div>
                `;
                berthContainer.appendChild(item);
            });
        }

        // Render Active Disruptions
        const disruptionsContainer = document.getElementById("disruptions-list");
        const countBadge = document.getElementById("disruptions-count");
        if (countBadge && state.disruptions) {
            countBadge.textContent = state.disruptions.length;
        }
        if (disruptionsContainer && state.disruptions) {
            disruptionsContainer.innerHTML = "";
            state.disruptions.slice(0, 4).forEach(dis => {
                const dCard = document.createElement("div");
                dCard.className = "disruption-card";
                dCard.innerHTML = `
                    <h4><i class="fa-solid fa-triangle-exclamation"></i> ${dis.type || 'Disruption'} (${dis.severity || 'LOW'})</h4>
                    <p><strong>Target:</strong> ${dis.affected_target || 'Port'} | <strong>Duration:</strong> ~${dis.expected_duration_hrs || 0}h</p>
                    <p>${dis.description || 'Active operational advisory.'}</p>
                `;
                disruptionsContainer.appendChild(dCard);
            });
        }

        // Render High Priority Queue Table
        const queueBody = document.getElementById("queue-table-body");
        if (queueBody && state.vessels) {
            queueBody.innerHTML = "";
            const highPriorityVessels = state.vessels.filter(v => v.priority === "HIGH" || v.priority === "CRITICAL").slice(0, 5);
            
            highPriorityVessels.forEach(v => {
                const tr = document.createElement("tr");
                const vName = v.name || v.vessel_id || "Vessel";
                const vBerth = v.assigned_berth || "Unassigned";
                const vWait = v.estimated_waiting_time_hrs ?? 0;
                tr.innerHTML = `
                    <td><strong>${v.vessel_id}</strong></td>
                    <td>${vName}</td>
                    <td>${formatDate(v.eta)}</td>
                    <td><span class="badge badge-${v.priority || 'LOW'}">${v.priority || 'LOW'}</span></td>
                    <td>${(v.container_count || 0).toLocaleString()} TEUs</td>
                    <td>${vBerth}</td>
                    <td>${vWait}h</td>
                    <td><span class="badge">${v.status || 'SCHEDULED'}</span></td>
                `;
                queueBody.appendChild(tr);
            });
        }
    }

    // 6. Render Vessel Directory Table
    function renderVesselsTable() {
        const body = document.getElementById("vessels-full-table-body");
        if (!body || !state.vessels) return;

        body.innerHTML = "";
        state.vessels.forEach(v => {
            const tr = document.createElement("tr");
            const vName = v.name || v.vessel_id || "Vessel";
            tr.setAttribute("data-search", `${v.vessel_id} ${vName}`.toLowerCase());
            
            let risk = "LOW";
            const waitTime = v.estimated_waiting_time_hrs ?? 0;
            if (v.priority === "CRITICAL" || waitTime >= 10) risk = "CRITICAL";
            else if (v.priority === "HIGH" || waitTime >= 6) risk = "HIGH";
            else if (waitTime >= 3) risk = "MEDIUM";

            tr.innerHTML = `
                <td><strong>${v.vessel_id}</strong></td>
                <td>${vName}</td>
                <td>${formatDate(v.eta)}</td>
                <td>${v.current_port || 'Origin'} → ${v.destination || 'Port'}</td>
                <td>${v.cargo_type || 'Containers'}</td>
                <td>${(v.container_count || 0).toLocaleString()} TEU</td>
                <td><span class="badge badge-${v.priority || 'LOW'}">${v.priority || 'LOW'}</span></td>
                <td>${v.assigned_berth || 'Pending'}</td>
                <td>${waitTime}h</td>
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
                const optTabBtn = document.querySelector("[data-tab='optimization-studio']");
                if (optTabBtn) optTabBtn.click();
                const berthSelect = document.getElementById("berth-vessel-select");
                if (berthSelect && vid) berthSelect.value = vid;
            });
        });
    }

    function filterVesselsTable(query) {
        const rows = document.querySelectorAll("#vessels-full-table-body tr");
        rows.forEach(r => {
            const text = r.getAttribute("data-search") || "";
            if (text.includes(query)) r.style.display = "";
            else r.style.display = "none";
        });
    }

    // 7. Render Congestion Diagnostics
    function renderCongestionDiagnostics() {
        const c = state.congestion;
        const container = document.getElementById("congestion-explainability-container");
        if (!c || !container) return;

        container.innerHTML = "";
        c.berth_details.forEach(b => {
            const card = document.createElement("div");
            card.className = "disruption-card";
            card.style.borderLeftColor = b.risk_level === "CRITICAL" ? "var(--status-red)" : (b.risk_level === "HIGH" ? "var(--status-orange)" : "var(--status-green)");
            
            const causesList = (b.primary_causes || []).map(cause => `<li>${cause}</li>`).join("");
            const bId = b.berth_id || "Berth";
            const bName = b.berth_name || "Quay";

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4>${bId} - ${bName}</h4>
                    <span class="badge badge-${b.risk_level || 'LOW'}">${b.risk_level || 'LOW'} (${b.congestion_score ?? 0}/100)</span>
                </div>
                <p><strong>Occupancy:</strong> ${b.occupancy_pct ?? 0}% | <strong>Queue Count:</strong> ${b.queue_count ?? 0} vessel(s)</p>
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

        if (rSelect) rSelect.innerHTML = "";
        if (bSelect) bSelect.innerHTML = "";
        if (cVesselSelect) cVesselSelect.innerHTML = "";
        if (cBerthSelect) cBerthSelect.innerHTML = "";

        if (state.vessels) {
            state.vessels.forEach(v => {
                const vName = v.name || v.vessel_id || "Vessel";
                const opt = `<option value="${v.vessel_id}">${v.vessel_id} - ${vName} (${v.priority || 'LOW'})</option>`;
                if (rSelect) rSelect.insertAdjacentHTML("beforeend", opt);
                if (bSelect) bSelect.insertAdjacentHTML("beforeend", opt);
                if (cVesselSelect) cVesselSelect.insertAdjacentHTML("beforeend", opt);
            });
        }

        if (state.berths) {
            state.berths.forEach(b => {
                const bName = b.name || b.berth_id || "Quay";
                const opt = `<option value="${b.berth_id}">${b.berth_id} - ${bName}</option>`;
                if (cBerthSelect) cBerthSelect.insertAdjacentHTML("beforeend", opt);
            });
        }
    }

    // 9. Submit Alternate Routing Optimization (Fix requirement 1B: No undefined vessel name)
    async function submitRoutingOptimization(vesselId) {
        try {
            const res = await fetch("/api/route/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ vessel_id: vesselId })
            });
            const data = await res.json();
            
            // Match vessel name from state if backend omits it
            const matchedVessel = state.vessels.find(v => v.vessel_id === vesselId);
            const displayVesselName = data.vessel_name || (matchedVessel ? matchedVessel.name : vesselId);

            const card = document.getElementById("routing-result-card");
            if (card) {
                card.classList.remove("hidden");
                card.innerHTML = `
                    <h4><i class="fa-solid fa-compass"></i> Routing Recommendation for ${displayVesselName} (${data.vessel_id})</h4>
                    <p><strong>Recommended Strategy:</strong> <span class="badge badge-${data.priority || 'MEDIUM'}">${data.recommended_option || 'Proceed'}</span></p>
                    <p><strong>Alternate Target:</strong> ${data.alternate_port || data.alternate_berth || 'Current Schedule'}</p>
                    <p><strong>Estimated Wait Reduction:</strong> ~${data.estimated_wait_reduction_hrs ?? 0} hours</p>
                    <p><strong>Reasoning:</strong> ${data.reason || 'Operational assessment complete.'}</p>
                    <small style="color:var(--text-secondary); display:block; margin-top:0.4rem;">* Alternate ports (Port Alpha / Port Beta / Port Gamma) are synthetic demo alternatives.</small>
                `;
            }
        } catch (err) {
            console.error("Routing error:", err);
            alert("Error running alternate routing calculation.");
        }
    }

    // 10. Submit Berth Optimization (Fix requirement 1A: No undefined berth name)
    async function submitBerthOptimization(vesselId) {
        try {
            const res = await fetch("/api/berth/optimise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ vessel_id: vesselId })
            });
            const data = await res.json();
            
            // Match berth name from state if backend omits it
            const matchedBerth = state.berths.find(b => b.berth_id === data.recommended_berth);
            const displayBerthName = data.berth_name || (matchedBerth ? matchedBerth.name : data.recommended_berth);

            const card = document.getElementById("berth-opt-result");
            if (card) {
                card.classList.remove("hidden");
                card.innerHTML = `
                    <h4><i class="fa-solid fa-circle-check"></i> Optimal Berth Assigned: ${data.recommended_berth} - ${displayBerthName}</h4>
                    <p><strong>Service Window:</strong> ${formatDate(data.expected_start_time)} → ${formatDate(data.expected_completion_time)} (~${data.estimated_service_hrs ?? 0}h)</p>
                    <p><strong>Conflict Prevention:</strong> Double-booking prevented across timeline.</p>
                    <p><strong>Rationale:</strong> ${data.reason || 'Optimal clearance and window matched.'}</p>
                `;
            }
            fetchTelemetryData(); // Refresh UI state
        } catch (err) {
            console.error("Berth optimization error:", err);
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
            if (card) {
                card.classList.remove("hidden");
                const cranesList = (data.assigned_cranes || []).join(", ") || "C01";
                card.innerHTML = `
                    <h4><i class="fa-solid fa-tower-observation"></i> Quay Cranes Allocated: ${cranesList}</h4>
                    <p><strong>Total Capacity:</strong> ${data.total_handling_capacity_teu_hr ?? 0} TEU/hr</p>
                    <p><strong>Est. Handling Duration:</strong> ${data.estimated_handling_duration_hrs ?? 0} hours</p>
                    <p><strong>Fleet Utilization:</strong> ${data.crane_utilization_pct ?? 0}%</p>
                    <p><strong>Rationale:</strong> ${data.reason || 'Crane handling allocated.'}</p>
                `;
            }
            fetchTelemetryData(); // Refresh UI state
        } catch (err) {
            console.error("Crane optimization error:", err);
            alert("Error running crane optimization.");
        }
    }

    // 12. Render 72-Hour Operations Plan (Requirement 7: Complete 72-hour horizon)
    function renderOperationsPlan() {
        const plan = state.operationsPlan;
        if (!plan) return;

        const summaryEl = document.getElementById("plan-impact-summary");
        if (summaryEl) {
            summaryEl.innerHTML = `
                <strong><i class="fa-solid fa-chart-line"></i> Operational Impact:</strong> ${plan.expected_impact_summary || 'Schedule optimized for 72-hour horizon.'}
            `;
        }

        const body = document.getElementById("plan-table-body");
        if (!body || !plan.current_plan) return;

        body.innerHTML = "";
        plan.current_plan.forEach(item => {
            const tr = document.createElement("tr");
            const vName = item.vessel_name || item.vessel_id || "Vessel";
            const cranesStr = (item.cranes && item.cranes.length) ? item.cranes.join(", ") : "C01";

            tr.innerHTML = `
                <td><strong>${item.time_block || 'Hour 00-06'}</strong></td>
                <td>${item.vessel_id} (${vName})</td>
                <td>${item.berth_id || 'B01'}</td>
                <td>${cranesStr}</td>
                <td>${item.action || 'Scheduled Operation'}</td>
                <td><span class="badge badge-${item.priority || 'LOW'}">${item.priority || 'LOW'}</span></td>
                <td><span class="badge badge-${item.congestion_risk || 'LOW'}">${item.congestion_risk || 'LOW'}</span></td>
                <td style="font-size:0.85rem;">${item.expected_impact || 'On schedule'}</td>
            `;
            body.appendChild(tr);
        });
    }

    // 13. Bob Copilot AI Chat Messages (Requirement 4 & 8: Input box UI & data integrity)
    async function sendChatMessage(message) {
        const chatContainer = document.getElementById("chat-messages");
        if (!chatContainer || !message) return;

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

            // Replace thinking indicator with formatted response
            tMsg.innerHTML = formatMarkdownResponse(data.answer || "Operational data analysis complete.");
            chatContainer.scrollTop = chatContainer.scrollHeight;

        } catch (err) {
            console.error("Chat error:", err);
            tMsg.innerHTML = `<span style="color:var(--status-red)">Error communicating with Bob Copilot AI backend.</span>`;
        }
    }

    function formatMarkdownResponse(text) {
        if (!text) return "";
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
