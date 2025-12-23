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
let gridPixels = []; // Cache for DOM elements

let editorState = {
    isDrawing: false,
    color: '#6366f1',
    tool: 'paint',
    brushSize: 1,
    isFilled: true,
    isCentered: false,
    startX: 0,
    startY: 0,
    snapshot: [], // Stores grid colors before shape draw
    history: [],
    historyIndex: -1
};


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

    // Restore Editor Config
    loadEditorConfig();
});

function saveEditorConfig() {
    const config = {
        tool: editorState.tool,
        color: editorState.color,
        brushSize: editorState.brushSize,
        isFilled: editorState.isFilled,
        isCentered: editorState.isCentered
    };
    localStorage.setItem('mask_editor_config', JSON.stringify(config));
}

function loadEditorConfig() {
    try {
        const stored = JSON.parse(localStorage.getItem('mask_editor_config'));
        if (stored) {
            // Restore State
            editorState.tool = stored.tool || 'paint';
            editorState.color = stored.color || '#6366f1';
            editorState.brushSize = stored.brushSize || 1;
            editorState.isFilled = stored.isFilled !== undefined ? stored.isFilled : true;
            editorState.isCentered = stored.isCentered !== undefined ? stored.isCentered : false;

            // Update UI
            // 1. Tool
            setTool(editorState.tool);

            // 2. Color
            const colorInput = document.getElementById('customColor');
            if (colorInput) colorInput.value = editorState.color;
            // Update active swatch
            setTimeout(() => {
                document.querySelectorAll('.swatch').forEach(s => {
                    s.classList.toggle('active', s.style.backgroundColor === editorState.color || rgbToHex(s.style.backgroundColor) === editorState.color);
                });
            }, 100);

            // 3. Brush Size
            const brushInput = document.getElementById('brushInput');
            const brushVal = document.getElementById('brushVal');
            if (brushInput) brushInput.value = editorState.brushSize;
            if (brushVal) brushVal.innerText = editorState.brushSize + 'px';

            // 4. Toggles
            const fillCheck = document.getElementById('fillShapeCheck');
            if (fillCheck) fillCheck.checked = editorState.isFilled;

            const centerCheck = document.getElementById('centerModeCheck');
            if (centerCheck) centerCheck.checked = editorState.isCentered;
        }
    } catch (e) { console.warn("Error loading editor config", e); }
}

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

// --- EDITOR LOGIC ---
function initGrid() {
    const canvas = document.getElementById('canvas');
    if (!canvas) return;
    canvas.innerHTML = '';
    gridPixels = []; // Reset

    for (let i = 0; i < WIDTH * HEIGHT; i++) {
        const p = document.createElement('div');
        p.className = 'pixel';
        p.dataset.index = i;
        p.onmousedown = (e) => startDraw(e, p);
        p.onmouseenter = (e) => moveDraw(e, p);
        p.oncontextmenu = (e) => e.preventDefault();

        canvas.appendChild(p);
        gridPixels.push(p);
    }

    // Load Mask Layout
    try {
        fetch('/static/mask_layout.json')
            .then(res => res.json())
            .then(indices => {
                validMaskIndices = new Set(indices);
                gridPixels.forEach((p, i) => {
                    if (!validMaskIndices.has(i)) {
                        p.classList.add('hidden-pixel');
                    }
                });
            })
            .catch(e => console.warn("Could not load mask_layout.json", e));
    } catch (e) { }

    // Push initial history state
    // pushHistory(); // Restore if history functions exist

    document.body.onmouseup = () => {
        if (editorState.isDrawing) {
            editorState.isDrawing = false;
            saveAutoSave();
            // pushHistory(); 
        }
    };

    // Checkbox Listeners
    const fillCheck = document.getElementById('fillShapeCheck');
    if (fillCheck) fillCheck.onchange = (e) => editorState.isFilled = e.target.checked;

    const centerCheck = document.getElementById('centerModeCheck');
    if (centerCheck) centerCheck.onchange = (e) => editorState.isCentered = e.target.checked;
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
    // Only switch to paint if curr tool is erase
    if (editorState.tool === 'erase') {
        setTool('paint');
    }

    const input = document.getElementById('customColor');
    if (input) input.value = hex;

    document.querySelectorAll('.swatch').forEach(s => {
        const bg = s.style.backgroundColor; // rgb or hex
        // constant match
        const match = (bg === hex) || (rgbToHex(bg) === hex);
        s.classList.toggle('active', match);
    });
    saveEditorConfig();
}

function startDraw(e, target) {
    if (e.button !== 0 && e.button !== 2) return;
    editorState.isDrawing = true;

    if (['rect', 'circle', 'line'].includes(editorState.tool)) {
        const pos = getPos(target);
        editorState.startX = pos.x;
        editorState.startY = pos.y;

        // Snapshot
        editorState.snapshot = gridPixels.map(p => p.style.backgroundColor); // Simple map

        // Draw initial point (shift doesn't matter yet really)
        drawShape(pos.x, pos.y, e.shiftKey);
    } else {
        paint(target, (e.button === 2) || (editorState.tool === 'erase'));
    }
}

function moveDraw(e, target) {
    if (!editorState.isDrawing) return;

    if (['rect', 'circle', 'line'].includes(editorState.tool)) {
        const pos = getPos(target);
        drawShape(pos.x, pos.y, e.shiftKey);
    } else {
        paint(target, (e.buttons === 2) || (editorState.tool === 'erase'));
    }
}

function getPos(target) {
    const idx = parseInt(target.dataset.index);
    return { x: idx % WIDTH, y: Math.floor(idx / WIDTH) };
}

function drawShape(currentX, currentY, isConstrained) {
    if (!gridPixels.length) return;

    // 1. Restore Snapshot
    for (let i = 0; i < gridPixels.length; i++) {
        if (editorState.snapshot[i] !== undefined) {
            gridPixels[i].style.backgroundColor = editorState.snapshot[i];
        }
    }

    // 2. Calculate Bounds with Constraint
    let x0, x1, y0, y1;

    // START CONSTRAINT LOGIC
    let targetX = currentX;
    let targetY = currentY;

    if (isConstrained) {
        // "Perfect Shape" Logic
        const dx = Math.abs(targetX - editorState.startX);
        const dy = Math.abs(targetY - editorState.startY);
        const maxDelta = Math.max(dx, dy);

        // Adjust target to be exactly maxDelta away from start
        // Keep direction
        targetX = editorState.startX + (targetX >= editorState.startX ? maxDelta : -maxDelta);
        targetY = editorState.startY + (targetY >= editorState.startY ? maxDelta : -maxDelta);
    }
    // END CONSTRAINT LOGIC

    // Bounds Calculation
    if (editorState.isCentered) {
        // Center Mode
        // With constraint, we already adjusted targetX/Y relative to start, so radius is effectively determined.
        // Actually for center mode, if constrained, radiusX should equal radiusY.

        const dx = Math.abs(targetX - editorState.startX);
        const dy = Math.abs(targetY - editorState.startY);

        // If constrained, we already made dx == dy above?
        // Let's re-verify:
        // Center mode implies startX,Y is center.
        // x0 = startX - dx, x1 = startX + dx

        x0 = editorState.startX - dx;
        x1 = editorState.startX + dx;
        y0 = editorState.startY - dy;
        y1 = editorState.startY + dy;
    } else {
        // Corner Mode
        // targetX/Y are the other corner.
        // We need min/max to iterate.
        // We still need to clamp to Grid?
        // Note: targetX might be out of bounds due to constraint. We clamp Loop bounds, not logic bounds necessarily.

        x0 = Math.min(editorState.startX, targetX);
        x1 = Math.max(editorState.startX, targetX);
        y0 = Math.min(editorState.startY, targetY);
        y1 = Math.max(editorState.startY, targetY);
    }

    // Clamp loop bounds
    const loopX0 = Math.max(0, Math.min(WIDTH - 1, x0));
    const loopX1 = Math.max(0, Math.min(WIDTH - 1, x1));
    const loopY0 = Math.max(0, Math.min(HEIGHT - 1, y0));
    const loopY1 = Math.max(0, Math.min(HEIGHT - 1, y1));

    const color = editorState.color;
    const sizeInput = document.getElementById('brushInput');
    const size = sizeInput ? parseInt(sizeInput.value) : 1;

    if (editorState.tool === 'line') {
        // Line Logic
        // For lines, snapshot restore is handled.
        // Constraint logic handled above (diagonal/straight).
        // Wait, line constraint is usually snap to angle (0, 45, 90).
        // My generic constraint logic forces square diagonal (45 deg).
        // If user wants straight lines?
        // "Perfect Shapes" usually implies Square/Circle.
        // For Line, Shift usually means snap to closest 45deg increment.
        // Let's implement special line constraint logic.

        let lx1 = currentX; // Use raw input for angle calc
        let ly1 = currentY;

        if (isConstrained) {
            const dx = Math.abs(lx1 - editorState.startX);
            const dy = Math.abs(ly1 - editorState.startY);
            if (dy < dx / 2) ly1 = editorState.startY; // Horizontal
            else if (dx < dy / 2) lx1 = editorState.startX; // Vertical
            else {
                const d = Math.max(dx, dy);
                lx1 = editorState.startX + (lx1 > editorState.startX ? d : -d);
                ly1 = editorState.startY + (ly1 > editorState.startY ? d : -d);
            }
        }
        drawLine(editorState.startX, editorState.startY, lx1, ly1, color);
        return;
    }

    // Rect / Circle
    for (let y = loopY0; y <= loopY1; y++) {
        for (let x = loopX0; x <= loopX1; x++) {
            let shouldPaint = false;

            if (editorState.tool === 'rect') {
                if (editorState.isFilled) {
                    shouldPaint = true; // Inside bounds
                } else {
                    // Border 
                    // Need to check if logic bounds match.
                    // Strictly: if x is x0 OR x is x1 ...
                    // Since x0, x1 might be floats or outside, we check "nearness"?
                    // Actually x0, x1 are integers here.
                    if (x === x0 || x === x1 || y === y0 || y === y1) shouldPaint = true;
                }
            } else if (editorState.tool === 'circle') {
                // Ellipse equation: ((x-cx)^2 / rx^2) + ... <= 1
                const cx = (x0 + x1) / 2;
                const cy = (y0 + y1) / 2;
                const rx = Math.abs(x1 - x0) / 2;
                const ry = Math.abs(y1 - y0) / 2;

                if (rx < 0.5 || ry < 0.5) shouldPaint = true;
                else {
                    const val = Math.pow(x - cx, 2) / Math.pow(rx, 2) + Math.pow(y - cy, 2) / Math.pow(ry, 2);
                    if (editorState.isFilled) {
                        if (val <= 1.05) shouldPaint = true;
                    } else {
                        // Border: 0.8 <= val <= 1.2 approx?
                        // Adaptive thickness?
                        // Lets try logic:
                        if (val >= 0.85 && val <= 1.15) shouldPaint = true;
                    }
                }
            }

            if (shouldPaint) {
                // If filled, we just paint the single pixel (unless we want super-thick filled shapes?)
                // Usually filled shapes don't respect brush size for the interior, just the edge.
                // But simplified: drawDot for border, just set pixel for interior.

                if (editorState.isFilled) {
                    // Fill logic: just single pixel at x,y
                    const idx = y * WIDTH + x;
                    const p = gridPixels[idx];
                    if (p && !p.classList.contains('hidden-pixel')) {
                        p.style.backgroundColor = color;
                    }
                } else {
                    // Border logic: use brush size
                    drawDot(x, y, color, size);
                }
            }
        }
    }
}

// Helper to draw a "brush stroke" at a point
function drawDot(cx, cy, color, size) {
    let start = 0, end = 0;
    // Map size 1..4 to offsets
    if (size === 2) end = 1;
    else if (size === 3) { start = -1; end = 1; }
    else if (size === 4) { start = -1; end = 2; }

    // For size 1: start=0, end=0 -> loops 0..0 -> just (0,0) offset

    for (let dy = start; dy <= end; dy++) {
        for (let dx = start; dx <= end; dx++) {
            const nx = cx + dx;
            const ny = cy + dy;
            if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) {
                const idx = ny * WIDTH + nx;
                const p = gridPixels[idx];
                if (p && !p.classList.contains('hidden-pixel')) {
                    p.style.backgroundColor = color;
                }
            }
        }
    }
}

function drawLine(x0, y0, x1, y1, color) {
    const sizeInput = document.getElementById('brushInput');
    const size = sizeInput ? parseInt(sizeInput.value) : 1;

    // Bresenham
    let dx = Math.abs(x1 - x0);
    let dy = Math.abs(y1 - y0);
    let sx = (x0 < x1) ? 1 : -1;
    let sy = (y0 < y1) ? 1 : -1;
    let err = dx - dy;

    while (true) {
        // Draw brush at current point
        drawDot(x0, y0, color, size);

        if (x0 === x1 && y0 === y1) break;
        let e2 = 2 * err;
        if (e2 > -dy) { err -= dy; x0 += sx; }
        if (e2 < dx) { err += dx; y0 += sy; }
    }
}

function paint(target, erase) {
    const idx = parseInt(target.dataset.index);
    if (isNaN(idx)) return;

    const cx = idx % WIDTH;
    const cy = Math.floor(idx / WIDTH);

    const sizeInput = document.getElementById('brushInput');
    const size = sizeInput ? parseInt(sizeInput.value) : 1;
    const color = erase ? '#000000' : editorState.color;

    drawDot(cx, cy, color, size);
}

function setTool(t) {
    editorState.tool = t;
    const ids = { 'paint': 'btnPaint', 'erase': 'btnErase', 'rect': 'btnRect', 'circle': 'btnCircle', 'line': 'btnLine' };

    Object.keys(ids).forEach(k => {
        const el = document.getElementById(ids[k]);
        if (el) {
            el.className = 'tool-btn';
            if (k === t) el.classList.add('active');
        }
    });

    const canvas = document.getElementById('canvas');
    if (canvas) {
        if (['paint', 'rect', 'circle', 'line'].includes(t)) canvas.style.cursor = 'crosshair';
        else if (t === 'erase') canvas.style.cursor = 'cell';
    }
    saveEditorConfig();
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
// Event Listeners for Editor
document.addEventListener('DOMContentLoaded', () => {
    // Brush Input Listener
    const brushInput = document.getElementById('brushInput');
    if (brushInput) {
        brushInput.oninput = (e) => {
            const val = parseInt(e.target.value);
            const label = document.getElementById('brushVal');
            if (label) label.innerText = val + 'px';
            editorState.brushSize = val;
            saveEditorConfig();
        };
    }

    const customColor = document.getElementById('customColor');
    if (customColor) customColor.oninput = (e) => setColor(e.target.value);

    // Toggles
    const fillCheck = document.getElementById('fillShapeCheck');
    if (fillCheck) {
        fillCheck.onchange = (e) => {
            editorState.isFilled = e.target.checked;
            saveEditorConfig();
        };
    }

    const centerCheck = document.getElementById('centerModeCheck');
    if (centerCheck) {
        centerCheck.onchange = (e) => {
            editorState.isCentered = e.target.checked;
            saveEditorConfig();
        };
    }
});
