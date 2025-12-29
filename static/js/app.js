let socket = null;
let currentUser = null;
let currentToken = null;
let selectedUserId = null;

// Auth Functions
function showSignup() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('auth-error').textContent = '';
    document.getElementById('signup-error').textContent = '';
}

function showLogin() {
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('auth-error').textContent = '';
    document.getElementById('signup-error').textContent = '';
}

async function handleSignup() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const errorDiv = document.getElementById('signup-error');
    
    if (!name || !email || !password) {
        errorDiv.textContent = 'Please fill all fields';
        return;
    }
    
    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            currentToken = data.token;
            initializeChat();
        } else {
            errorDiv.textContent = data.error || 'Signup failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error. Please try again.';
    }
}

async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('auth-error');
    
    if (!email || !password) {
        errorDiv.textContent = 'Please fill all fields';
        return;
    }
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            currentToken = data.token;
            initializeChat();
        } else {
            errorDiv.textContent = data.error || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error. Please try again.';
    }
}

function handleLogout() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    currentUser = null;
    currentToken = null;
    selectedUserId = null;
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('chat-section').style.display = 'none';
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
}

// Chat Functions
async function initializeChat() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('chat-section').style.display = 'flex';
    document.getElementById('current-user-name').textContent = currentUser.name;
    
    await loadUsers();
    connectWebSocket();
}

async function loadUsers() {
    try {
        const response = await fetch('/api/users', {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayUsers(data.users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function displayUsers(users) {
    const userList = document.getElementById('user-list');
    userList.innerHTML = '';
    
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        userItem.innerHTML = `
            <div class="user-status" id="status-${user.id}"></div>
            <span>${user.name}</span>
        `;
        userItem.onclick = () => selectUser(user, userItem);
        userList.appendChild(userItem);
    });
}

async function selectUser(user, userElement) {
    selectedUserId = user.id;
    
    // Update UI
    document.querySelectorAll('.user-item').forEach(item => {
        item.classList.remove('active');
    });
    userElement.classList.add('active');
    
    document.getElementById('chat-with-name').textContent = `Chatting with ${user.name}`;
    document.getElementById('message-input').disabled = false;
    document.getElementById('send-btn').disabled = false;
    
    // Load chat history
    await loadChatHistory(user.id);
}

async function loadChatHistory(userId) {
    try {
        const response = await fetch(`/api/messages?user_id=${userId}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayMessages(data.messages);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function displayMessages(messages) {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    
    messages.forEach(msg => {
        const isSent = msg.sender_id === currentUser.id;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
        
        const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-header">${isSent ? 'You' : msg.sender_name}</div>
            <div class="message-text">${escapeHtml(msg.message)}</div>
            <div class="message-time">${time}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
    });
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// WebSocket Functions
function connectWebSocket() {
    socket = io({
        auth: { token: currentToken }
    });
    
    socket.on('connect', () => {
        console.log('WebSocket connected');
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
    });
    
    socket.on('new_message', (data) => {
        if (data.sender_id === selectedUserId || data.receiver_id === selectedUserId) {
            addMessageToChat(data);
        }
    });
    
    socket.on('user_online', (data) => {
        const statusEl = document.getElementById(`status-${data.user_id}`);
        if (statusEl) {
            statusEl.classList.add('online');
        }
    });
    
    socket.on('user_offline', (data) => {
        const statusEl = document.getElementById(`status-${data.user_id}`);
        if (statusEl) {
            statusEl.classList.remove('online');
        }
    });
    
    socket.on('error', (data) => {
        console.error('WebSocket error:', data.message);
    });
    
    socket.on('message_sent', (data) => {
        if (data.receiver_id === selectedUserId || data.sender_id === currentUser.id) {
            addMessageToChat(data);
        }
    });
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message || !selectedUserId || !socket) return;
    
    socket.emit('send_message', {
        token: currentToken,
        receiver_id: selectedUserId,
        message: message
    });
    
    input.value = '';
}

function addMessageToChat(msg) {
    const chatMessages = document.getElementById('chat-messages');
    const isSent = msg.sender_id === currentUser.id;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
    
    const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-header">${isSent ? 'You' : msg.sender_name}</div>
        <div class="message-text">${escapeHtml(msg.message)}</div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

