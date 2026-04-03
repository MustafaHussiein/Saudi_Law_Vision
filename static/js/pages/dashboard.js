// Dashboard Page JavaScript
async function loadDashboardStats() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/analytics/dashboard', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            updateDashboard(stats);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateDashboard(stats) {
    // Update dashboard cards with stats
    console.log('Dashboard stats:', stats);
}

document.addEventListener('DOMContentLoaded', loadDashboardStats);
