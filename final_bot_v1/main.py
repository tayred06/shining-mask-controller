#!/usr/bin/env python3
"""
FINAL TWITCH MASK BOT
---------------------
Combines:
- Animation control (!anim, !randanim)
- Text display (!say)
- Voice Activity Detection (VAD) for lip-sync
- Event handling (Follows, Subs) with "Merci" overlay
"""

import os
import sys
import asyncio
import signal
import time
import argparse
import random
import json
from typing import Optional, Dict, Any

# Third-party imports
from twitchio.ext import commands
from dotenv import load_dotenv

# Local imports
from mask_controller import MaskTextDisplay

# Load environment variables
load_dotenv()

# ==========================================
# VAD / MICROPHONE CLASS
# ==========================================
class MicrophoneVAD:
    """Simple VAD based on RMS with hysteresis."""
    def __init__(self, samplerate=16000, blocksize=1024, threshold_on=0.020, threshold_off=0.012, device=None):
        import numpy as np
        self.np = np
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.threshold_on = threshold_on
        self.threshold_off = threshold_off
        self.device = device
        self.queue: asyncio.Queue[float] = asyncio.Queue(maxsize=10)
        self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"[VAD] status={status}")
        try:
            rms = float(self.np.sqrt(self.np.mean(indata.astype(self.np.float32) ** 2)))
            if not self.queue.full():
                self.queue.put_nowait(rms)
        except Exception:
            pass

    async def start(self):
        try:
            import sounddevice as sd
        except ImportError:
            print("❌ sounddevice not found. Mic disabled.")
            raise
        
        self._stream = sd.InputStream(
            channels=1,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype='float32',
            device=self.device,
            callback=self._audio_callback,
        )
        self._stream.start()
        print(f"[VAD] Micro started (device={self.device})")

    async def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    async def speaking_states(self):
        speaking = False
        avg = 0.0
        alpha = 0.2
        while True:
            rms = await self.queue.get()
            avg = alpha * rms + (1 - alpha) * avg
            if speaking:
                if avg < self.threshold_off:
                    speaking = False
                    yield False
            else:
                if avg > self.threshold_on:
                    speaking = True
                    yield True

# ==========================================
# MASK COORDINATOR
# ==========================================
class MaskCoordinator:
    """Manages the mask state, prioritizing events over animations/VAD."""
    
    def __init__(self):
        self.mask = MaskTextDisplay()
        self.lock = asyncio.Lock()
        
        # State
        self.mode = "ANIMATION" # or "SPEECH"
        self.current_anim_id = 18
        self.vad_enabled = False
        
        # Faces for speech mode
        self.face_open = ":O"
        self.face_closed = ":)"
        self.last_face_open_state = None
        
        # Overlay management
        self.overlay_active = False
        self.overlay_until = 0.0

    async def connect(self):
        return await self.mask.connect()

    async def disconnect(self):
        await self.mask.disconnect()

    async def set_mode_speech(self):
        async with self.lock:
            self.mode = "SPEECH"
            # self.vad_enabled = True # VAD disabled by user request
            print("🎭 Mode changed to SPEECH (VAD Disabled)")
            await self._refresh_state()

    async def set_mode_animation(self, anim_id):
        async with self.lock:
            self.mode = "ANIMATION"
            self.vad_enabled = False
            self.current_anim_id = int(anim_id)
            print(f"🎭 Mode changed to ANIMATION {anim_id}")
            await self._refresh_state()

    async def update_vad_face(self, is_open):
        """Called by VAD loop when speech state changes"""
        if not self.vad_enabled or self.overlay_active:
            return

        # Filtering updates to avoid excessive BLE traffic
        if self.last_face_open_state == is_open:
            return
            
        async with self.lock:
            if not self.vad_enabled or self.overlay_active:
                return
            
            self.last_face_open_state = is_open
            text = self.face_open if is_open else self.face_closed
            
            try:
                self.mask.set_text_color_by_rgb((255, 255, 255))
                await self.mask.set_scrolling_text(text, scroll_mode='steady', speed=50)
            except Exception as e:
                print(f"❌ VAD Face Error: {e}")

    async def show_overlay_message(self, text, duration=5.0, color=(0, 255, 0)):
        """High priority message (Alerts, Follows, Say)"""
        async with self.lock:
            self.overlay_active = True
            
            # Adjust duration based on text length if generic
            if len(text) > 5 and duration == 5.0:
                duration = 2.0 + (len(text) * 0.5)
            
            self.overlay_until = time.time() + duration
            
            print(f"🚨 Overlay: {text}")
            
            try:
                self.mask.set_text_color_by_rgb(color)
                # Auto-scroll if long
                mode = 'scroll_left' if len(text) > 4 else 'steady'
                await self.mask.set_scrolling_text(text, scroll_mode=mode, speed=50)
            except Exception as e:
                print(f"❌ Overlay Error: {e}")
            
        await asyncio.sleep(duration)
        
        async with self.lock:
            self.overlay_active = False
            self.overlay_until = 0.0
            await self._refresh_state()

    async def _refresh_state(self):
        """Restores the current mode's default look."""
        try:
            if self.mode == "ANIMATION":
                await self.mask.set_animation(self.current_anim_id)
            elif self.mode == "SPEECH":
                self.mask.set_text_color_by_rgb((255, 255, 255))
                await self.mask.set_scrolling_text(self.face_closed, scroll_mode='steady', speed=50)
        except Exception as e:
            print(f"❌ Refresh State Error: {e}")

# ==========================================
# TWITCH BOT
# ==========================================
class FinalTwitchBot(commands.Bot):
    def __init__(self, token, channel, nick, coordinator: MaskCoordinator):
        super().__init__(token=token, prefix='!', initial_channels=[channel], nick=nick)
        self.coordinator = coordinator
        self.channel_name = channel

    async def event_ready(self):
        print(f"✅ Twitch Bot Ready: {self.nick} connected to {self.channel_name}")
        print("💡 Commands: !anim <id>, !randanim, !say <text>, !face")

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name='anim')
    async def cmd_anim(self, ctx, anim_id: str):
        """!anim <id> : Switch to specific animation."""
        try:
            val = int(anim_id)
            await self.coordinator.set_mode_animation(val)
            await ctx.send(f"🎭 Animation set to {val}")
        except ValueError:
            await ctx.send("❌ ID must be a number")

    @commands.command(name='randanim')
    async def cmd_randanim(self, ctx):
        """!randanim : Switch to a random animation for 10s."""
        # Exclude 18 (default) from random choice
        choices = [i for i in range(1, 41) if i != 18]
        val = random.choice(choices)
        
        await self.coordinator.set_mode_animation(val)
        await ctx.send(f"🎲 Random animation: {val} (10s)")
        
        # Wait 10s then revert to default (18)
        await asyncio.sleep(10)
        # Check if we are still on that random animation (simple check)
        # ideally we'd lock or check state, but simple revert is fine
        if self.coordinator.current_anim_id == val:
            await self.coordinator.set_mode_animation(18)
            print("🔙 Reverting to default animation (18)")

    @commands.command(name='face')
    async def cmd_face(self, ctx):
        """!face : Switch to Speech/Face mode."""
        await self.coordinator.set_mode_speech()
        await ctx.send("🗣️ Switched to Face/Speech mode")

    @commands.command(name='say')
    async def cmd_say(self, ctx, *, text: str):
        """!say <text> : Scroll text on mask."""
        await self.coordinator.show_overlay_message(text, duration=5+(len(text)*0.2), color=(255, 0, 255))

    @commands.command(name='testfollow')
    async def cmd_testfollow(self, ctx):
        """Simulate a follow."""
        await self.coordinator.show_overlay_message(f"Merci {ctx.author.name}", color=(0, 255, 255))

    async def event_raw_usernotice(self, channel, tags):
        """Handle Subs/Gifts"""
        msg_id = tags.get('msg-id')
        display_name = tags.get('display-name') or 'User'
        if msg_id in {'sub', 'resub', 'subgift', 'anonsubgift'}:
            print(f"🎁 Sub Event: {display_name}")
            asyncio.create_task(self.coordinator.show_overlay_message(f"Merci {display_name} <3", duration=8.0, color=(255, 215, 0)))

# ==========================================
# FOLLOW WATCHER (Helix API)
# ==========================================
async def follow_watcher(coordinator, channel_name):
    client_id = os.environ.get('TWITCH_CLIENT_ID')
    app_token = os.environ.get('TWITCH_APP_TOKEN') 
    
    if not client_id or not app_token:
        print("⚠️ Missing TWITCH_CLIENT_ID or TWITCH_APP_TOKEN for Follows.")
        return

    import requests

    def get_user_id(login):
        r = requests.get('https://api.twitch.tv/helix/users', 
                         params={'login': login},
                         headers={'Client-ID': client_id, 'Authorization': f'Bearer {app_token}'})
        if r.status_code == 200 and r.json()['data']:
            return r.json()['data'][0]['id']
        return None

    def get_last_follow(user_id):
        r = requests.get('https://api.twitch.tv/helix/users/follows',
                         params={'to_id': user_id, 'first': 1},
                         headers={'Client-ID': client_id, 'Authorization': f'Bearer {app_token}'})
        if r.status_code == 200:
            data = r.json()
            if data['data']:
                return data['data'][0]
        return None

    print("🔍 Resolving Channel ID for Follows...")
    user_id = await asyncio.to_thread(get_user_id, channel_name)
    if not user_id:
        print("❌ Could not resolve Channel ID. Follow watcher disabled.")
        return

    print(f"👀 Watching follows for ID {user_id}")
    last_follow_id = None
    
    # Init last follow
    init_follow = await asyncio.to_thread(get_last_follow, user_id)
    if init_follow:
        last_follow_id = init_follow['from_id']

    while True:
        try:
            follow = await asyncio.to_thread(get_last_follow, user_id)
            if follow:
                fid = follow['from_id']
                fname = follow['from_name']
                if last_follow_id and fid != last_follow_id:
                    print(f"🔔 NEW FOLLOW: {fname}")
                    last_follow_id = fid
                    asyncio.create_task(coordinator.show_overlay_message(f"Merci {fname}", color=(0, 255, 255)))
                elif last_follow_id is None:
                    last_follow_id = fid
        except Exception as e:
            print(f"⚠️ Follow Watcher Error: {e}")
        
        await asyncio.sleep(30) # Check every 30s

# ==========================================
# MAIN LOOP
# ==========================================
async def main():
    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-mic', action='store_true')
    args = parser.parse_args()

    # Env vars
    token = os.environ.get('TWITCH_TOKEN')
    channel = os.environ.get('TWITCH_CHANNEL')
    nick = os.environ.get('TWITCH_NICK')
    
    if not token or not channel:
        print("❌ Missing TWITCH_TOKEN or TWITCH_CHANNEL in .env")
        return

    # Init
    coordinator = MaskCoordinator()
    bot = FinalTwitchBot(token, channel, nick, coordinator)
    
    # VAD Disabled
    vad = None
    # if not args.no_mic: ...

    # Connect to Mask
    print("🔄 Connecting to Mask...")
        
    async def mask_connect_loop():
        backoff = 2.0
        while True:
            try:
                if await coordinator.connect():
                    print("✅ Mask Connected.")
                    # Default start state
                    await coordinator.set_mode_animation(18)
                    return
            except Exception as e:
                print(f"❌ Mask connection failed ({e}). Retrying in {backoff}s...")
            
            await asyncio.sleep(backoff)
            backoff = min(60.0, backoff * 1.5)
    
    # Start connection in background
    asyncio.create_task(mask_connect_loop())
    
    
    # Tasks
    tasks = [
        asyncio.create_task(bot.start()),
        asyncio.create_task(follow_watcher(coordinator, channel)),
    ]
    
    # VAD Loop removed by user request
    # if vad: ...

    # Wait
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        pass
    finally:
        print("🛑 Shutting down...")
        await coordinator.disconnect()
        if vad: await vad.stop()

if __name__ == "__main__":
    asyncio.run(main())
