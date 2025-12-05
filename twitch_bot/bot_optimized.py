#!/usr/bin/env python3
"""
Final Twitch Bot for Shining Mask
---------------------------------
Integrates:
- Twitch Chat & Helix (Follows/Subs)
- Optimized Mask Controller (Text Scrolling)
- Async Queue for messages
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from twitchio.ext import commands
# Add parent directory to path to allow imports from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller_optimized import OptimizedMaskController, PatternConfig

# Charger les variables d'environnement
load_dotenv()

# Configuration
TWITCH_TOKEN = os.environ.get('TWITCH_TOKEN')
CHANNEL_NAME = os.environ.get('TWITCH_CHANNEL')
CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
APP_TOKEN = os.environ.get('TWITCH_APP_TOKEN')

class ExtendedMaskController(OptimizedMaskController):
    async def show_animation(self, anim_id):
        """Affiche une animation intégrée (ANIM)"""
        try:
            async with self.ble_lock:
                # Commande: [Len] ANIM [ID]
                # Len = 4(ANIM) + 1(ID) = 5
                cmd = bytearray([5]) + b'ANIM' + bytes([anim_id])
                await self.ble_manager.send_command(cmd)
                return True
        except Exception as e:
            print(f"❌ Erreur show_animation: {e}")
            return False

    async def show_image(self, img_id):
        """Affiche une image intégrée (IMAG)"""
        try:
            async with self.ble_lock:
                cmd = bytearray([5]) + b'IMAG' + bytes([img_id])
                await self.ble_manager.send_command(cmd)
                return True
        except Exception as e:
            print(f"❌ Erreur show_image: {e}")
            return False

class FinalTwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[CHANNEL_NAME])
        self.mask_controller = ExtendedMaskController()
        # Désactiver le clignotement automatique qui cause des uploads intempestifs
        self.mask_controller.config.animation_settings['auto_blink_enabled'] = False
        
        self.mask_queue = asyncio.Queue()
        self.mask_task = None
        self.helix_user_id = None
        
        # Animation Loop
        self.animation_running = False
        self.animation_task = None
        
        # Configuration
        self.config_file = Path(__file__).resolve().parent / 'config.json'
        self.load_config()

    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration chargée depuis {self.config_file}")
            except Exception as e:
                print(f"⚠️ Erreur chargement config: {e}")
                self.config = self.get_default_config()
        else:
            print("⚠️ Fichier config introuvable, utilisation défaut")
            self.config = self.get_default_config()
            self.save_config()

    def get_default_config(self):
        base_cfg = {
            "scroll_speed": 50,
            "scroll_mode": "scroll_left",
            "text_color": "magenta",
            "decoration": "lines",
            "bold": False,
            "repeat": 1
        }
        return {
            "default_image": 1,
            "say": base_cfg.copy(),
            "follow": {**base_cfg, "text_color": "green", "bold": True, "repeat": 2},
            "sub": {**base_cfg, "text_color": "yellow", "decoration": "waves", "bold": True, "repeat": 2}
        }

    def save_config(self):
        """Sauvegarde la configuration actuelle"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("💾 Configuration sauvegardée")
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")

    async def event_ready(self):
        print(f'✅ Logged in as | {self.nick}')
        print(f'📺 Channel | {CHANNEL_NAME}')
        
        # Démarrage du contrôleur masque
        if await self.mask_controller.initialize():
            print("✅ Masque connecté et prêt !")
            self.mask_task = asyncio.create_task(self.process_mask_queue())
            
            # Démarrage de l'animation par défaut
            await self.start_animation_loop()
        else:
            print("⚠️ Impossible de connecter le masque")

        # Setup Helix pour les follows
        if CLIENT_ID and APP_TOKEN:
            self.loop.create_task(self.setup_helix())

    async def setup_helix(self):
        """Récupère l'ID du broadcaster pour Helix"""
        import requests
        try:
            def _req():
                return requests.get(
                    'https://api.twitch.tv/helix/users',
                    params={'login': CHANNEL_NAME},
                    headers={'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {APP_TOKEN}'},
                    timeout=10,
                )
            resp = await asyncio.to_thread(_req)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data'):
                    self.helix_user_id = data['data'][0]['id']
                    print(f"✅ Helix configuré pour user_id={self.helix_user_id}")
                    self.loop.create_task(self.follow_watcher())
        except Exception as e:
            print(f"❌ Helix setup error: {e}")

    async def follow_watcher(self):
        """Surveille les nouveaux followers"""
        print("👀 Surveillance des follows active...")
        last_follow_id = None
        import requests
        
        while True:
            try:
                def _req():
                    return requests.get(
                        'https://api.twitch.tv/helix/channels/followers',
                        params={'broadcaster_id': self.helix_user_id, 'first': 1},
                        headers={'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {APP_TOKEN}'},
                        timeout=10,
                    )
                resp = await asyncio.to_thread(_req)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('data', [])
                    if items:
                        top = items[0]
                        fid = top.get('user_id')
                        fname = top.get('user_name')
                        
                        if last_follow_id is None:
                            last_follow_id = fid
                        elif fid != last_follow_id:
                            last_follow_id = fid
                            print(f"🔔 NOUVEAU FOLLOW: {fname}")
                            await self.handle_follow(fname)
                
                await asyncio.sleep(10)
            except Exception as e:
                print(f"❌ Erreur watcher: {e}")
                await asyncio.sleep(30)

    async def start_animation_loop(self):
        """Met l'animation par défaut"""
        print("🎬 Mise en place de l'animation par défaut (3)")
        await self.mask_controller.show_animation(3)

    async def stop_animation_loop(self):
        """Pas besoin d'arrêter une boucle, juste un log"""
        pass

    async def _animation_loop(self):
        """Obsolète"""
        pass

    async def process_mask_queue(self):
        """Traite la file d'attente des messages pour le masque"""
        while True:
            try:
                item = await self.mask_queue.get()
                text = item['text']
                cfg = item.get('config', {})
                
                print(f"🎭 Envoi au masque: {text}")
                
                # 1. Pause Animation
                await self.stop_animation_loop()
                await asyncio.sleep(1.0) # Pause pour laisser le BLE respirer
                
                # 2. Affichage Texte avec Config
                # TODO: PatternConfig ne supporte pas encore 'decoration' ou 'bold' nativement
                # On passe 'color' et 'category'
                pattern = PatternConfig(
                    name="temp", 
                    text=text, 
                    color=cfg.get('text_color', 'white'), 
                    category="text"
                )
                await self.mask_controller._send_text_pattern(pattern)
                
                # 3. Attente Lecture
                repeat = cfg.get('repeat', 1)
                duration = (5.0 + (len(text) * 0.3)) * repeat + 2.0 # +2s de marge
                await asyncio.sleep(duration)
                
                # 4. Reprise Animation
                await self.start_animation_loop()
                
                self.mask_queue.task_done()
            except Exception as e:
                print(f"❌ Erreur queue masque: {e}")
                await asyncio.sleep(1)

    async def queue_mask_message(self, text, config=None):
        """Ajoute un message à la file d'attente"""
        await self.mask_queue.put({'text': text, 'config': config or {}})

    async def handle_follow(self, pseudo, is_sub=False):
        """Gère l'affichage d'un follow/sub"""
        message = f"Merci {pseudo}"
        cfg_key = 'follow'
        
        if is_sub:
            message = f"MERCI SUB {pseudo} <3"
            cfg_key = 'sub'
            
        cfg = self.config.get(cfg_key, self.config.get('say'))
        await self.queue_mask_message(message, cfg)

    @commands.command(name='say')
    async def cmd_say(self, ctx, *, text: str):
        """!say [message] - Affiche un message personnalisé"""
        print(f"💬 Commande !say: {text}")
        cfg = self.config.get('say', {})
        await self.queue_mask_message(text, cfg)

    @commands.command(name='config')
    async def cmd_config(self, ctx, section: str = None, setting: str = None, value: str = None):
        """!config [section] [setting] [value]"""
        if not section:
            await ctx.send("❓ Usage: !config [say|follow|sub] [speed|color|repeat] [valeur]")
            return

        section = section.lower()
        if section not in ['say', 'follow', 'sub']:
            await ctx.send("❌ Section inconnue")
            return
            
        if not setting:
            cfg = self.config.get(section, {})
            cfg_str = ", ".join(f"{k}={v}" for k, v in cfg.items())
            await ctx.send(f"⚙️ Config [{section}]: {cfg_str}")
            return

        setting = setting.lower()
        changed = False
        cfg = self.config[section]
        
        if setting == 'color':
            cfg['text_color'] = value
            await ctx.send(f"✅ Couleur réglée à {value}")
            changed = True
        elif setting == 'repeat':
            try:
                cfg['repeat'] = int(value)
                await ctx.send(f"✅ Répétitions: {value}")
                changed = True
            except:
                await ctx.send("❌ Nombre invalide")
        
        if changed:
            self.save_config()

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    async def event_raw_usernotice(self, channel, tags):
        """Gère les subs et resubs"""
        msg_id = tags.get('msg-id')
        if msg_id in {'sub', 'resub', 'subgift', 'anonsubgift', 'giftpaidupgrade'}:
            display_name = tags.get('display-name') or tags.get('login') or 'Ami'
            print(f"💎 SUB EVENT: {display_name}")
            await self.handle_follow(display_name, is_sub=True)

def main():
    bot = FinalTwitchBot()
    print("🚀 Démarrage du Bot Final Shining Mask...")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Arrêt demandé...")

if __name__ == "__main__":
    main()
