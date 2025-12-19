import os
import asyncio
import json
from aiohttp import web
from typing import List

class WebServer:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.log_buffer: List[str] = []
        self.max_logs = 100
        
        # Setup Routes
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/api/status', self.handle_status)
        self.app.router.add_post('/api/connect', self.handle_connect)
        self.app.router.add_post('/api/disconnect', self.handle_disconnect)
        self.app.router.add_post('/api/brightness', self.handle_brightness)
        self.app.router.add_post('/api/text', self.handle_text)
        self.app.router.add_post('/api/anim', self.handle_anim)
        self.app.router.add_post('/api/diy', self.handle_diy)
        self.app.router.add_get('/api/logs', self.handle_logs)
        
        # Static files
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.app.router.add_static('/static/', static_path)
        
    async def start(self, port=8080):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', port)
        await self.site.start()
        self.log(f"🌍 Dashboard hosted at http://localhost:{port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()

    def log(self, message):
        """Append log to buffer"""
        # print(message) # REMOVED to avoid recursion with main.py's WebLogger
        self.log_buffer.append(message)
        if len(self.log_buffer) > self.max_logs:
            self.log_buffer.pop(0)

    # --- Handlers ---

    async def handle_index(self, request):
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return web.Response(text=f.read(), content_type='text/html')
        except FileNotFoundError:
            return web.Response(text="Template not found", status=404)

    async def handle_status(self, request):
        return web.json_response({
            "connected": self.coordinator.mask.client.is_connected if (self.coordinator.mask and self.coordinator.mask.client) else False,
            "mode": self.coordinator.mode,
            "current_anim": self.coordinator.current_anim_id
        })

    async def handle_connect(self, request):
        # Trigger connection in background to avoid blocking
        asyncio.create_task(self.coordinator.connect())
        return web.json_response({"status": "connecting"})

    async def handle_disconnect(self, request):
        await self.coordinator.disconnect()
        return web.json_response({"status": "disconnected"})

    async def handle_brightness(self, request):
        data = await request.json()
        value = int(data.get('value', 100))
        # Mask expects brightness related command?
        # Check if MaskTextDisplay has set_brightness
        # If not, implement or ignore. scrolling_text_controller usually has it.
        # Assuming set_brightness(0-255? or 0-20?)
        # Let's assume scrolling_text_controller has set_brightness(value)
        # We'll map 0-100 to what it needs.
        # Actually scrolling_text_controller.set_brightness usually takes simplified values.
        # Let's try sending it.
        try:
            # Map 0-100 to mask range (often 1-20 or 255)
            # Default to direct pass if unknown, safeguard:
            # final_bot_v1 mask might not expose it directly in MaskTextDisplay, let's check.
            # We'll try calling it if it exists.
             if hasattr(self.coordinator.mask, 'set_brightness'):
                 await self.coordinator.mask.set_brightness(value)
                 self.log(f"💡 Brightness set to {value}")
                 return web.json_response({"status": "ok"})
             else:
                 return web.json_response({"status": "error", "message": "Not supported"}, status=400)
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_text(self, request):
        data = await request.json()
        text = data.get('text', '')
        color_hex = data.get('color', '#FFFFFF')
        scroll = data.get('scroll', False)
        speed = data.get('speed') # Optional
        
        # Convert hex to rgb
        h = color_hex.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Use coordinator to show message (prioritize)
        await self.coordinator.show_overlay_message(text, duration=None, color=rgb, speed=speed)
        self.log(f"💬 Sent text: {text}")
        return web.json_response({"status": "ok"})

    async def handle_anim(self, request):
        data = await request.json()
        anim_id = int(data.get('id', 1))
        await self.coordinator.set_mode_animation(anim_id)
        self.log(f"🎭 Animation set to {anim_id}")
        return web.json_response({"status": "ok"})

    async def handle_diy(self, request):
        data = await request.json()
        img_id = int(data.get('id', 1))
        # Using set_diy_image we added
        async with self.coordinator.lock:
             self.coordinator.mode = "DIY"
             await self.coordinator.mask.set_diy_image(img_id)
        self.log(f"🖼️ DIY Image {img_id}")
        return web.json_response({"status": "ok"})

    async def handle_logs(self, request):
        return web.json_response({"logs": self.log_buffer})
