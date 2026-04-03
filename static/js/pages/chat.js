// Chat/Assistant Page JavaScript
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input?.value?.trim();
    
    if (!message) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/llm/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayMessage(data.response, 'assistant');
            if (input) input.value = '';
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

function displayMessage(text, role) {
    const messagesDiv = document.getElementById('messages');
    if (messagesDiv) {
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${role}`;
        messageEl.textContent = text;
        messagesDiv.appendChild(messageEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}
