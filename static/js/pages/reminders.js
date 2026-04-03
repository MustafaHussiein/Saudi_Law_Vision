// Reminders Page JavaScript
async function loadReminders() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/reminders', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const reminders = await response.json();
            displayReminders(reminders);
        }
    } catch (error) {
        console.error('Error loading reminders:', error);
    }
}

function displayReminders(reminders) {
    console.log('Reminders:', reminders);
    // Update UI with reminders
}

document.addEventListener('DOMContentLoaded', loadReminders);
