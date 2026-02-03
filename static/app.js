const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const historyList = document.getElementById('history-list');

let ws;

function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        statusText.textContent = 'Connected - Idle';
    };

    ws.onmessage = (event) => {
        const state = JSON.parse(event.data);
        updateUI(state);
    };

    ws.onclose = () => {
        statusText.textContent = 'Disconnected';
        statusIndicator.className = 'status-indicator';
        setTimeout(connect, 2000);
    };
}

function updateUI(state) {
    statusIndicator.className = `status-indicator ${state.status}`;
    statusText.textContent = state.status.charAt(0).toUpperCase() + state.status.slice(1);

    if (state.history && state.history.length > 0) {
        historyList.innerHTML = state.history.map(item => `
            <li>
                <div class="text">${escapeHtml(item.text)}</div>
                <div class="timestamp">${formatTime(item.timestamp)}</div>
            </li>
        `).join('');
    } else {
        historyList.innerHTML = '<li class="empty">No transcriptions yet</li>';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

connect();
