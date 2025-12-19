const API = {
    status: '/api/status',
    connect: '/api/connect',
    disconnect: '/api/disconnect',
    brightness: '/api/brightness',
    text: '/api/text',
    anim: '/api/anim',
    diy: '/api/diy',
    logs: '/api/logs'
};

// State
let isConnected = false;
let currentAnim = 1;
let isEditingDIY = false;

// DIY Logic
const defaultDIY = ['👾', '💀', '🤡', '👻', '👽', '🎃', '🤖'];

// Init
document.addEventListener('DOMContentLoaded', () => {
    generateAnimGrid();
    generateDIYGrid();
    generateTextPresets();
    setInterval(updateStatus, 1000);
    setInterval(fetchLogs, 2000);

    // Restore Brightness
    const storedV = localStorage.getItem('mask_brightness');
    if (storedV) {
        document.getElementById('brightness-slider').value = storedV;
    }

    // Accordion Logic & Restore State
    // Accordion Logic DISABLED (Always Open)
    /*
    const cards = [
        'control-card', 'diy-card', 'logs-card',
        'text-card', 'anim-card'
    ];

    cards.forEach(className => {
        const card = document.querySelector(`.${className}`);
        if (!card) return;

        // Restore state
        const isCollapsed = localStorage.getItem(`mask_collapsed_${className}`) === 'true';
        if (isCollapsed) {
            card.classList.add('collapsed');
        }

        // Attach listener (except if clicked on button)
        const header = card.querySelector('.card-header');
        if (header) {
            header.addEventListener('click', (e) => {
                // Ignore if clicked on a button inside header
                if (e.target.tagName === 'BUTTON') return;

                const nowCollapsed = card.classList.toggle('collapsed');
                localStorage.setItem(`mask_collapsed_${className}`, nowCollapsed);
            });
        }
    });
    */
});

function toggleDIYEdit(e) {
    if (e) e.stopPropagation();
    isEditingDIY = !isEditingDIY;

    // UI Feedback
    const btn = document.getElementById('diy-edit-btn');
    const grid = document.querySelector('.diy-grid');

    if (isEditingDIY) {
        btn.classList.add('active');
        btn.innerText = '💾'; // Save icon
        grid.classList.add('editing');
    } else {
        btn.classList.remove('active');
        btn.innerText = '✏️';
        grid.classList.remove('editing');
    }

    generateDIYGrid();
}

function generateDIYGrid() {
    const grid = document.querySelector('.diy-grid');
    if (!grid) return;
    grid.innerHTML = '';

    // Load custom
    let icons = defaultDIY;
    try {
        const stored = JSON.parse(localStorage.getItem('mask_diy_icons'));
        if (stored && Array.isArray(stored) && stored.length > 0) {
            icons = stored;
        }
    } catch (e) { }

    // Ensure we have 7 items
    while (icons.length < 7) icons.push('❓');

    icons.forEach((icon, index) => {
        if (index >= 7) return;
        const id = index + 1;
        const btn = document.createElement('button');
        btn.innerText = icon;

        if (isEditingDIY) {
            btn.title = `Click to change Preset ${id}`;
            btn.style.cursor = "text";
            btn.onclick = (e) => {
                e.stopPropagation();
                const newIcon = prompt(`Enter new emoji for Preset ${id}:`, icon);
                if (newIcon) {
                    icons[index] = newIcon;
                    localStorage.setItem('mask_diy_icons', JSON.stringify(icons));
                    generateDIYGrid(); // Refresh
                }
            };
        } else {
            btn.title = `Display Preset ${id}`;
            btn.onclick = () => setDIY(id);
        }

        grid.appendChild(btn);
    });
}

async function updateStatus() {
    try {
        const res = await fetch(API.status);
        const data = await res.json();

        isConnected = data.connected;
        currentAnim = data.current_anim;

        updateConnectionUI();
        updateActiveAnim();
    } catch (e) {
        console.error("Status error", e);
    }
}

function updateConnectionUI() {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-text');
    const btn = document.getElementById('connect-btn');

    if (isConnected) {
        dot.className = 'dot connected';
        text.innerText = 'Connected';
        btn.innerText = 'Disconnect';
        btn.onclick = disconnectMask;
        btn.classList.add('btn-danger');
    } else {
        dot.className = 'dot disconnected';
        text.innerText = 'Disconnected';
        btn.innerText = 'Connect Mask';
        btn.onclick = connectMask;
        btn.classList.remove('btn-danger');
    }
}

async function connectMask() {
    await fetch(API.connect, { method: 'POST' });
}

async function disconnectMask() {
    await fetch(API.disconnect, { method: 'POST' });
}

// Text Presets Logic
let isEditingTextPresets = false;

function toggleTextPresetEdit(e) {
    if (e) e.stopPropagation();
    isEditingTextPresets = !isEditingTextPresets;

    // UI Feedback
    const btn = document.getElementById('text-edit-btn');
    const grid = document.querySelector('.text-presets-grid');

    if (isEditingTextPresets) {
        btn.classList.add('active');
        btn.innerText = '💾';
        grid.classList.add('editing');
    } else {
        btn.classList.remove('active');
        btn.innerText = '✏️';
        grid.classList.remove('editing');
    }
    generateTextPresets();
}

function generateTextPresets() {
    const container = document.querySelector('.text-presets-grid');
    if (!container) return;
    container.innerHTML = '';

    let presets = ["Welcome! 👋", "Hype! 🔥", "GG! 🎮"];
    try {
        const stored = JSON.parse(localStorage.getItem('mask_text_presets'));
        if (stored && Array.isArray(stored)) presets = stored;
    } catch (e) { }

    presets.forEach((text, index) => {
        const btn = document.createElement('button');
        btn.className = 'preset-btn';
        btn.innerText = text;

        if (isEditingTextPresets) {
            btn.title = "Click to Edit or Delete";
            btn.style.cursor = "alias";
            btn.onclick = (e) => {
                e.stopPropagation();
                // Prompt user
                const action = prompt(`Edit text (clear to delete):`, text);
                if (action === null) return; // Cancelled

                if (action.trim() === "") {
                    // Delete
                    if (confirm("Delete this preset?")) {
                        presets.splice(index, 1);
                        localStorage.setItem('mask_text_presets', JSON.stringify(presets));
                        generateTextPresets();
                    }
                } else {
                    // Update
                    presets[index] = action;
                    localStorage.setItem('mask_text_presets', JSON.stringify(presets));
                    generateTextPresets();
                }
            };
        } else {
            btn.title = "Click to send";
            btn.onclick = () => {
                document.getElementById('text-input').value = text;
                sendText();
            };
            // Keep right click delete just in case? Or remove to clean up?
            // User asked for Edit Mode, let's keep context menu as power user feature or disable to avoid confusion.
            // Let's keep it disabled in normal mode to rely on Edit Mode.
        }
        container.appendChild(btn);
    });

    // Add Button (only show if not editing? or keep)
    if (!isEditingTextPresets) {
        const addBtn = document.createElement('button');
        addBtn.className = 'preset-btn add-new';
        addBtn.innerText = '+';
        addBtn.title = "Save current text as preset";
        addBtn.onclick = () => {
            const val = document.getElementById('text-input').value;
            if (val) {
                presets.push(val);
                localStorage.setItem('mask_text_presets', JSON.stringify(presets));
                generateTextPresets();
            } else {
                alert("Type text above to save it as a preset!");
            }
        };
        container.appendChild(addBtn);
    }
}

async function setBrightness(val) {
    // ...
    localStorage.setItem('mask_brightness', val);
    await fetch(API.brightness, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: parseInt(val) })
    });
}

async function sendText() {
    const text = document.getElementById('text-input').value;
    const color = document.getElementById('text-color').value;
    const speedVal = document.getElementById('text-speed').value;

    // standard Speed Slider: Right = Faster (Lower Delay)
    // 1 (Left) -> 100ms (Slowest)
    // 5 (Mid) -> 60ms
    // 10 (Right) -> 10ms (Fastest)
    const speedValInt = parseInt(speedVal);
    const speedMs = 110 - (speedValInt * 10);

    if (!text) return;

    await fetch(API.text, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, color, speed: speedMs })
    });
}

async function setDIY(id) {
    await fetch(API.diy, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });
}

async function setAnim(id) {
    await fetch(API.anim, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });
}

// Logs
let lastLogContent = "";
let isUserScrollingLogs = false;

async function fetchLogs() {
    try {
        const res = await fetch(API.logs);
        const data = await res.json();
        const newContent = data.logs.join('\n');

        if (newContent !== lastLogContent) {
            const container = document.getElementById('log-console');

            // Check if user is near bottom before updating
            const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;

            container.textContent = newContent;
            lastLogContent = newContent;

            if (isAtBottom) {
                container.scrollTop = container.scrollHeight;
            }
        }
    } catch (e) {
        // ignore
    }
}

// Helpers
function generateAnimGrid() {
    const grid = document.querySelector('.anim-grid');
    grid.innerHTML = '';

    // 1-40 Anims
    for (let i = 1; i <= 40; i++) {
        const btn = document.createElement('button');
        btn.className = 'anim-btn';
        btn.innerText = i;
        btn.onclick = () => setAnim(i);
        btn.id = `anim-btn-${i}`;
        grid.appendChild(btn);
    }
}

function updateActiveAnim() {
    document.querySelectorAll('.anim-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`anim-btn-${currentAnim}`);
    if (btn) btn.classList.add('active');
}

function toggleConnect() {
    if (isConnected) disconnectMask();
    else connectMask();
}
