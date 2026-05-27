/**
 * admin.js — Admin dashboard logic.
 *
 * Fetches reasoning logs, refund history, and customer data
 * from the backend API and renders them in the admin panels.
 */

(function () {
    const API_BASE = '/api';

    /**
     * Fetch and display all data for the admin dashboard.
     */
    async function refreshAdminData() {
        await Promise.all([
            loadLogs(),
            loadRefunds(),
            loadCustomers(),
        ]);
    }

    // Expose globally so app.js can call it on tab switch.
    window.refreshAdminData = refreshAdminData;

    // ── Reasoning Logs ───────────────────────────────────────────────

    async function loadLogs() {
        try {
            const res = await fetch(`${API_BASE}/admin/logs`);
            const data = await res.json();
            renderLogs(data);
        } catch {
            document.getElementById('logs-content').innerHTML =
                '<p style="color: var(--danger);">Failed to load logs.</p>';
        }
    }

    function renderLogs(sessions) {
        const container = document.getElementById('logs-content');
        const empty = document.getElementById('logs-empty');

        const sessionKeys = Object.keys(sessions);
        if (sessionKeys.length === 0) {
            empty.style.display = 'block';
            container.innerHTML = '';
            return;
        }
        empty.style.display = 'none';

        container.innerHTML = sessionKeys.map(sid => {
            const entries = sessions[sid];
            const shortId = sid.substring(0, 8);
            return `
                <div class="session-card">
                    <div class="session-header" onclick="this.nextElementSibling.classList.toggle('open')">
                        <span class="session-id">Session: ${shortId}…</span>
                        <span class="session-count">${entries.length} steps</span>
                    </div>
                    <div class="session-body">
                        ${entries.map(e => renderLogEntry(e)).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }

    function renderLogEntry(entry) {
        const time = new Date(entry.timestamp).toLocaleTimeString();
        const detail = typeof entry.detail === 'object'
            ? JSON.stringify(entry.detail, null, 2)
            : entry.detail;

        return `
            <div class="log-entry ${entry.step_type}">
                <span class="log-time">${time}</span>
                <div class="log-type">${entry.step_type.replace(/_/g, ' ')}</div>
                <div class="log-detail">${escapeHtml(detail)}</div>
            </div>
        `;
    }

    // ── Refund History ───────────────────────────────────────────────

    async function loadRefunds() {
        try {
            const res = await fetch(`${API_BASE}/admin/refunds`);
            const data = await res.json();
            renderRefunds(data);
        } catch {
            /* silent */
        }
    }

    function renderRefunds(refunds) {
        const table = document.getElementById('refunds-table');
        const tbody = document.getElementById('refunds-tbody');
        const empty = document.getElementById('refunds-empty');

        if (refunds.length === 0) {
            table.style.display = 'none';
            empty.style.display = 'block';
            return;
        }
        empty.style.display = 'none';
        table.style.display = 'table';

        tbody.innerHTML = refunds.map(r => `
            <tr>
                <td style="font-family:monospace; color:var(--accent-light);">${r.refund_id}</td>
                <td>${r.order_id}</td>
                <td>${r.customer_id}</td>
                <td>${r.item_name}</td>
                <td>$${Number(r.amount).toFixed(2)}</td>
                <td><span class="badge badge-${r.status}">${r.status}</span></td>
                <td style="font-size:0.78rem; color:var(--text-muted);">
                    ${r.timestamp ? new Date(r.timestamp).toLocaleString() : '—'}
                </td>
            </tr>
        `).join('');
    }

    // ── Customers ────────────────────────────────────────────────────

    async function loadCustomers() {
        try {
            const res = await fetch(`${API_BASE}/customers`);
            const data = await res.json();
            renderCustomers(data);
        } catch {
            /* silent */
        }
    }

    function renderCustomers(customers) {
        const tbody = document.getElementById('customers-tbody');
        tbody.innerHTML = customers.map(c => `
            <tr>
                <td style="font-family:monospace; color:var(--accent-light);">${c.id}</td>
                <td>${c.name}</td>
                <td>${c.email}</td>
                <td><span class="badge badge-${c.membership_tier}">${c.membership_tier}</span></td>
                <td>${c.total_orders}</td>
                <td>$${Number(c.total_spent).toFixed(2)}</td>
            </tr>
        `).join('');
    }

    // ── Helpers ──────────────────────────────────────────────────────

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ── Refresh button ──────────────────────────────────────────────
    document.getElementById('refresh-btn').addEventListener('click', refreshAdminData);

    // Initial load of customers (available immediately)
    loadCustomers();
})();
