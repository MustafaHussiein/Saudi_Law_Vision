// Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Legal Tech Platform loaded');
    
    // Check authentication
    const token = localStorage.getItem('access_token');
    if (!token && !window.location.pathname.includes('/login')) {
        // window.location.href = '/login';
    }
});

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}
