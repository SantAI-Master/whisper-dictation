const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const historyList = document.getElementById('history-list');
const modeSingleBtn = document.getElementById('mode-single');
const modeDocumentBtn = document.getElementById('mode-document');
const modeHint = document.getElementById('mode-hint');

let ws;
let currentMode = 'single-line';

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

    // Update mode toggle
    if (state.format_mode) {
        currentMode = state.format_mode;
        updateModeUI(currentMode);
    }

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

function updateModeUI(mode) {
    if (mode === 'single-line') {
        modeSingleBtn.classList.add('active');
        modeDocumentBtn.classList.remove('active');
        modeHint.textContent = 'Safe for chat apps - no Enter key';
    } else {
        modeSingleBtn.classList.remove('active');
        modeDocumentBtn.classList.add('active');
        modeHint.textContent = 'Allows paragraphs - for emails & docs';
    }
}

async function setMode(mode) {
    // Update UI immediately for responsiveness
    currentMode = mode;
    updateModeUI(mode);

    try {
        await fetch(`/api/mode?mode=${mode}`, { method: 'POST' });
    } catch (err) {
        console.error('Failed to set mode:', err);
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

// Mode toggle click handlers
modeSingleBtn.addEventListener('click', () => setMode('single-line'));
modeDocumentBtn.addEventListener('click', () => setMode('document'));

// Set initial mode UI state
updateModeUI(currentMode);

connect();
