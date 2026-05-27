/**
 * app.js — Main application router.
 *
 * Handles tab-based navigation between Chat and Admin views.
 */

document.addEventListener('DOMContentLoaded', () => {
    const navTabs = document.querySelectorAll('.nav-tab');
    const views = document.querySelectorAll('.view');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.view;

            // Update active tab
            navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update active view
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(`view-${target}`).classList.add('active');

            // If switching to admin, refresh data
            if (target === 'admin' && typeof window.refreshAdminData === 'function') {
                window.refreshAdminData();
            }
        });
    });

    // Admin sub-tabs
    const adminTabs = document.querySelectorAll('.admin-tab');
    const adminPanels = document.querySelectorAll('.admin-panel');

    adminTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.panel;

            adminTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            adminPanels.forEach(p => p.classList.remove('active'));
            document.getElementById(`panel-${target}`).classList.add('active');
        });
    });
});
