const API = {
    status: '/api/status',
    connect: '/api/connect',
    disconnect: '/api/disconnect',
    brightness: '/api/brightness',
    text: '/api/text',
    anim: '/api/anim',
    diy: '/api/diy',
    logs: '/api/logs',
    preview: '/api/preview'
};

// State
let isConnected = false;
let currentAnim = 1;
let isEditingDIY = false;

// Editor Constants
const WIDTH = 42;
const HEIGHT = 56;
const PALETTE_COLORS = ['#000000', '#ffffff', '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#6366f1', '#a855f7', '#ec4899', '#333333', '#52525b', '#71717a', '#a1a1aa', '#d4d4d8'];
let editorState = { isDrawing: false, color: '#6366f1', tool: 'paint', brushSize: 1 };


// DIY Logic
const defaultDIY = ['👾', '💀', '🤡', '👻', '👽', '🎃', '🤖'];

// Init
document.addEventListener('DOMContentLoaded', () => {
    generateAnimGrid();
    generateDIYGrid();
    generateTextPresets();

    // Editor Init
    initGrid();
    initPalette();
    loadAutoSave();

    // Polling
    setInterval(updateStatus, 1000);
    setInterval(fetchLogs, 1000);

    // Restore Brightness
    const storedV = localStorage.getItem('mask_brightness');
    if (storedV) {
        const el = document.getElementById('brightness-slider');
        if (el) el.value = storedV;
    }
});

function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');

    // Show target view
    const target = document.getElementById(`view-${viewName}`);
    if (target) target.style.display = 'flex';
    // Actually our views contain top-bar and grid-layout.
    // grid-layout has flex:1.
    // So the view-section should probably be a flex column itself to match the previous .content > .top-bar structure.
    // We'll handle this in CSS or inline style.

    // Update Sidebar
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const nav = document.getElementById(`nav-${viewName}`);
    if (nav) nav.classList.add('active');
}

// --- DASHBOARD LOGIC ---

function toggleDIYEdit(e) {
    if (e) e.stopPropagation();
    isEditingDIY = !isEditingDIY;
    generateDIYGrid();
}

function generateDIYGrid() {
    const grid = document.getElementById('diy-grid-container') || document.querySelector('.diy-grid');
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

    while (icons.length < 7) icons.push('❓');

    icons.forEach((icon, index) => {
        if (index >= 7) return;
        const id = index + 1;
        const btn = document.createElement('button');
        btn.className = 'anim-item';
        btn.style.fontSize = "24px";
        btn.innerText = icon;

        if (isEditingDIY) {
            btn.title = `Click to change Preset ${id}`;
            btn.style.cursor = "text";
            btn.style.borderColor = "var(--accent)";
            btn.onclick = (e) => {
                e.stopPropagation();
                const newIcon = prompt(`Enter new emoji for Preset ${id}:`, icon);
                if (newIcon) {
                    icons[index] = newIcon;
                    localStorage.setItem('mask_diy_icons', JSON.stringify(icons));
                    generateDIYGrid();
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
        mode = data.mode;

        updateConnectionUI();
        updateActiveAnim();

        const modeText = document.getElementById('mode-text');
        if (modeText) modeText.innerText = mode || "--";

    } catch (e) { }
}

function updateConnectionUI() {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-text');
    const btn = document.getElementById('connect-btn');

    if (isConnected) {
        if (dot) dot.className = 'status-dot connected';
        if (text) {
            text.innerText = 'CONNECTED';
            text.style.color = "var(--accent)";
        }
        if (btn) {
            btn.innerText = 'DISCONNECT MASK';
            btn.onclick = disconnectMask;
            btn.classList.add('btn-danger');
            btn.classList.remove('btn-primary');
        }
    } else {
        if (dot) dot.className = 'status-dot disconnected';
        if (text) {
            text.innerText = 'DISCONNECTED';
            text.style.color = "var(--text-muted)";
        }
        if (btn) {
            btn.innerText = 'CONNECT MASK';
            btn.onclick = connectMask;
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-primary');
        }
    }
}

async function connectMask() { await fetch(API.connect, { method: 'POST' }); }
async function disconnectMask() { await fetch(API.disconnect, { method: 'POST' }); }

// Text Presets
let isEditingTextPresets = false;
function toggleTextPresetEdit(e) {
    if (e) e.stopPropagation();
    isEditingTextPresets = !isEditingTextPresets;
    generateTextPresets();
}

function generateTextPresets() {
    const container = document.getElementById('text-presets-container');
    if (!container) return;
    container.innerHTML = '';

    let presets = ["Welcome! 👋", "Hype! 🔥", "GG! 🎮"];
    try {
        const stored = JSON.parse(localStorage.getItem('mask_text_presets'));
        if (stored && Array.isArray(stored)) presets = stored;
    } catch (e) { }

    presets.forEach((text, index) => {
        const btn = document.createElement('button');
        btn.className = 'btn sm';
        btn.style.border = "1px solid var(--border)";
        btn.innerText = text;

        if (isEditingTextPresets) {
            btn.title = "Click to Edit or Delete";
            btn.classList.add('btn-danger');
            btn.onclick = (e) => {
                e.stopPropagation();
                const action = prompt(`Edit text (clear to delete):`, text);
                if (action === null) return;
                if (action.trim() === "") {
                    if (confirm("Delete this preset?")) {
                        presets.splice(index, 1);
                        localStorage.setItem('mask_text_presets', JSON.stringify(presets));
                        generateTextPresets();
                    }
                } else {
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
        }
        container.appendChild(btn);
    });

    if (!isEditingTextPresets) {
        const addBtn = document.createElement('button');
        addBtn.className = 'btn sm';
        addBtn.innerText = '+';
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
    await fetch(API.diy, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
}
async function setAnim(id) {
    await fetch(API.anim, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
}

// Logs
let lastLogLength = 0;
async function fetchLogs() {
    try {
        const res = await fetch(API.logs);
        const data = await res.json();
        const logs = data.logs || [];

        // Updates ALL terminal windows (both Dashboard and Editor)
        document.querySelectorAll('.terminal-window').forEach(container => {
            // Avoid full re-render if nothing changed (basic check on length and active)
            // But since we have multiple, simple check is safer.
            // We can optimize if needed.

            const html = logs.map(l => {
                let type = 'info';
                if (l.includes('Error') || l.includes('Failed')) type = 'error';
                else if (l.includes('Sent') || l.includes('Success') || l.includes('Upload')) type = 'success';
                return `<div class="log-line ${type}"><span class="log-ts">></span>${escapeHtml(l)}</div>`;
            }).join('');

            // Only update if different
            if (container.innerHTML !== html) {
                const isAtBottom = (container.scrollHeight - container.scrollTop - container.clientHeight) < 50;
                container.innerHTML = html;
                if (isAtBottom) container.scrollTop = container.scrollHeight;
            }
        });

    } catch (e) { }
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function generateAnimGrid() {
    const grid = document.getElementById('anim-grid');
    if (!grid) return;
    grid.innerHTML = '';
    for (let i = 1; i <= 40; i++) {
        const btn = document.createElement('button');
        btn.className = 'anim-item';
        btn.innerText = i;
        btn.onclick = () => setAnim(i);
        btn.id = `anim-btn-${i}`;
        grid.appendChild(btn);
    }
}

function updateActiveAnim() {
    document.querySelectorAll('.anim-item').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`anim-btn-${currentAnim}`);
    if (btn) btn.classList.add('active');
}

function toggleConnect() {
    if (isConnected) disconnectMask();
    else connectMask();
}

// --- EDITOR LOGIC ---

function initGrid() {
    const canvas = document.getElementById('canvas');
    if (!canvas) return;
    canvas.innerHTML = '';
    for (let i = 0; i < WIDTH * HEIGHT; i++) {
        const p = document.createElement('div');
        p.className = 'pixel';
        p.onmousedown = (e) => startDraw(e, p);
        p.onmouseenter = (e) => moveDraw(e, p);
        p.oncontextmenu = (e) => e.preventDefault();
        canvas.appendChild(p);
    }
    document.body.onmouseup = () => {
        if (editorState.isDrawing) { editorState.isDrawing = false; saveAutoSave(); }
    };
}

function initPalette() {
    const pal = document.getElementById('palette');
    if (!pal) return;
    PALETTE_COLORS.forEach(c => {
        const s = document.createElement('div');
        s.className = 'swatch';
        s.style.backgroundColor = c;
        s.onclick = () => setColor(c);
        pal.appendChild(s);
    });
}

function setColor(hex) {
    editorState.color = hex;
    editorState.tool = 'paint';
    const input = document.getElementById('customColor');
    if (input) input.value = hex;

    document.querySelectorAll('.swatch').forEach(s => {
        s.classList.toggle('active', s.style.backgroundColor === hex || rgbToHex(s.style.backgroundColor) === hex);
    });
}

function startDraw(e, target) {
    e.preventDefault();
    editorState.isDrawing = true;
    paint(target, (e.button === 2) || (editorState.tool === 'erase'));
}

function moveDraw(e, target) {
    if (!editorState.isDrawing) return;
    paint(target, (e.buttons === 2) || (editorState.tool === 'erase'));
}

function paint(target, erase) {
    const canvas = document.getElementById('canvas');
    const idx = Array.from(canvas.children).indexOf(target);
    if (idx === -1) return;
    const cx = idx % WIDTH;
    const cy = Math.floor(idx / WIDTH);

    const sizeInput = document.getElementById('brushInput');
    const size = sizeInput ? parseInt(sizeInput.value) : 1;
    const color = erase ? '#000000' : editorState.color;

    let start = 0, end = 0;
    if (size === 2) end = 1;
    else if (size === 3) { start = -1; end = 1; }
    else if (size === 4) { start = -1; end = 2; }

    for (let dy = start; dy <= end; dy++) {
        for (let dx = start; dx <= end; dx++) {
            const nx = cx + dx;
            const ny = cy + dy;
            if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) {
                canvas.children[ny * WIDTH + nx].style.backgroundColor = color;
            }
        }
    }
}

function setTool(t) {
    editorState.tool = t;
    const btnPaint = document.getElementById('btnPaint');
    const btnErase = document.getElementById('btnErase');
    if (btnPaint) btnPaint.className = t === 'paint' ? 'btn btn-primary' : 'btn';
    if (btnErase) btnErase.className = t === 'erase' ? 'btn btn-primary' : 'btn';
}

function fillGrid() {
    const canvas = document.getElementById('canvas');
    if (!canvas) return;
    Array.from(canvas.children).forEach(p => p.style.backgroundColor = editorState.color);
    saveAutoSave();
}

function clearGrid() {
    const canvas = document.getElementById('canvas');
    if (!canvas) return;
    Array.from(canvas.children).forEach(p => p.style.backgroundColor = '#000000');
    saveAutoSave();
}

function rgbToHex(rgb) {
    if (!rgb) return '#000000';
    if (rgb.startsWith('#')) return rgb;
    const a = rgb.match(/\d+/g);
    if (!a) return '#000000';
    return "#" + ((1 << 24) + (+a[0] << 16) + (+a[1] << 8) + +a[2]).toString(16).slice(1);
}

function saveAutoSave() {
    const canvas = document.getElementById('canvas');
    if (!canvas) return;
    const pixels = Array.from(canvas.children).map(p => rgbToHex(p.style.backgroundColor));
    localStorage.setItem('mask_editor_save', JSON.stringify(pixels));
}

function loadAutoSave() {
    try {
        const d = JSON.parse(localStorage.getItem('mask_editor_save'));
        const canvas = document.getElementById('canvas');
        if (d && Array.isArray(d) && canvas) {
            d.forEach((hex, i) => { if (canvas.children[i]) canvas.children[i].style.backgroundColor = hex; });
        }
    } catch (e) { }
}

async function sendToMask() {
    const btn = document.getElementById('uploadBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ SENDING...";
    }
    const canvas = document.getElementById('canvas');
    if (!canvas) return;

    const pixels = Array.from(canvas.children).map(p => rgbToHex(p.style.backgroundColor));

    try {
        const res = await fetch(API.preview, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pixels })
        });
        const d = await res.json();
        if (btn) {
            if (d.status === 'ok') btn.innerText = "✅ SENT!";
            else btn.innerText = "❌ ERROR";
        }
    } catch (e) {
        if (btn) btn.innerText = "❌ FAIL";
    }
    setTimeout(() => { if (btn) { btn.disabled = false; btn.innerText = "⚡ SEND TO MASK"; } }, 2000);
}

function handleImport(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const tmp = document.createElement('canvas');
                tmp.width = WIDTH; tmp.height = HEIGHT;
                const ctx = tmp.getContext('2d');
                ctx.fillStyle = "#000";
                ctx.fillRect(0, 0, WIDTH, HEIGHT);
                ctx.drawImage(img, 0, 0, WIDTH, HEIGHT);
                const d = ctx.getImageData(0, 0, WIDTH, HEIGHT).data;
                const canvas = document.getElementById('canvas');
                if (!canvas) return;

                for (let i = 0; i < canvas.children.length; i++) {
                    const r = d[i * 4], g = d[i * 4 + 1], b = d[i * 4 + 2];
                    const hex = "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
                    canvas.children[i].style.backgroundColor = hex;
                }
                saveAutoSave();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Event Listeners for Editor
document.addEventListener('DOMContentLoaded', () => {
    const brushInput = document.getElementById('brushInput');
    if (brushInput) brushInput.oninput = (e) => document.getElementById('brushVal').innerText = e.target.value;

    const customColor = document.getElementById('customColor');
    if (customColor) customColor.oninput = (e) => setColor(e.target.value);
});
