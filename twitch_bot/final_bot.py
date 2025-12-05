#!/usr/bin/env python3
"""
Final Twitch Bot for Shining Mask
---------------------------------
Integrates:
- Twitch Chat & Helix (Follows/Subs)
- Ultimate Mask Controller (Bold, Colors, Decorations)
- Auto-revert to Image 1
- Configurable settings via chat
"""

import os
import sys
import asyncio
import time
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from twitchio.ext import commands

# Charger les variables d'environnement
load_dotenv()

# Ajouter le dossier src au path pour importer les modules existants
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
SRC_DIR = ROOT_DIR / 'src'
sys.path.append(str(SRC_DIR))

try:
    from working.ultimate_text_display_with_bold import CompleteMaskController
except ImportError as e:
    print(f"❌ Erreur: Impossible d'importer CompleteMaskController: {e}")
    print(f"Vérifiez que {SRC_DIR}/working/ultimate_text_display_with_bold.py existe.")
    sys.exit(1)

# --- Extension du contrôleur pour ajouter show_image ---
class FinalMaskController(CompleteMaskController):
    async def show_image(self, image_num, bank=1):
        """Affiche une image prédéfinie du masque (ex: 1)"""
        try:
            # Construction de la commande "PLAY"
            # Format: [Length] [Command String] [Bank] [ImageID]
            cmd_str = "PLAY"
            args = bytes([bank, image_num])
            
            payload = bytearray()
            payload.append(len(cmd_str) + len(args))
            payload.extend(cmd_str.encode('ascii'))
            payload.extend(args)
            
            await self.send_command(payload)
            return True
        except Exception as e:
            print(f"❌ Erreur show_image: {e}")
            return False

# Fichier de configuration
CONFIG_FILE = Path(__file__).resolve().parent / 'config.json'

# --- Bot Twitch ---
class FinalTwitchBot(commands.Bot):
    def __init__(self, mask_controller):
        self.mask = mask_controller
        
        # Charger la configuration
        self.load_config()
        
        # Variables Twitch
        token = os.environ.get('TWITCH_TOKEN')
        self.channel_name = os.environ.get('TWITCH_CHANNEL')
        nick = os.environ.get('TWITCH_NICK')
        
        if not token or not self.channel_name or not nick:
            print("❌ Erreur: Variables d'environnement manquantes (.env)")
            sys.exit(1)
            
        super().__init__(token=token, prefix='!', initial_channels=[self.channel_name], nick=nick)
        
        # Helix (pour les follows)
        self.client_id = os.environ.get('TWITCH_CLIENT_ID')
        self.app_token = os.environ.get('TWITCH_APP_TOKEN')
        self.helix_user_id = None
        
        # État
        self.display_lock = asyncio.Lock()
        self.default_image = self.config.get('default_image', 1)
        
        # Animation loop
        self.animation_running = False
        self.animation_task = None
        self.num_animation_frames = 7  # Nombre d'images dans l'animation
        self.animation_delay = 0.05  # Délai entre chaque frame



    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration chargée depuis {CONFIG_FILE}")
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
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("💾 Configuration sauvegardée")
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")

    async def event_ready(self):
        print(f"✅ Bot connecté à Twitch en tant que {self.nick}")
        print(f"📺 Chaîne: {self.channel_name}")
        
        # Connexion au masque
        print("🔄 Connexion au masque...")
        try:
            await self.mask.connect()
            # Config initiale
            await self.mask.set_brightness(1)  # 25% de luminosité (64/255 ≈ 25%)
            # Démarrer l'animation loop
            await self.start_animation_loop()
            print("✅ Masque prêt et animation démarrée")
        except Exception as e:
            print(f"❌ Erreur connexion masque: {e}")

        # Démarrer le watcher de follows
        if self.client_id and self.app_token:
            self.loop.create_task(self.setup_helix())
        else:
            print("⚠️ Pas de Client-ID/App-Token, les follows ne seront pas détectés.")

    async def setup_helix(self):
        """Récupère l'ID du broadcaster pour Helix"""
        import requests
        try:
            def _req():
                return requests.get(
                    'https://api.twitch.tv/helix/users',
                    params={'login': self.channel_name},
                    headers={'Client-ID': self.client_id, 'Authorization': f'Bearer {self.app_token}'},
                    timeout=10,
                )
            resp = await asyncio.to_thread(_req)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data'):
                    self.helix_user_id = data['data'][0]['id']
                    print(f"✅ Helix configuré pour user_id={self.helix_user_id}")
                    self.loop.create_task(self.follow_watcher())
                else:
                    print("❌ Helix: Utilisateur introuvable")
            else:
                print(f"❌ Helix: Erreur API {resp.status_code}")
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
                        headers={'Client-ID': self.client_id, 'Authorization': f'Bearer {self.app_token}'},
                        timeout=10,
                    )
                resp = await asyncio.to_thread(_req)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('data', [])
                    if items:
                        top = items[0]
                        fid = top.get('user_id')
                        fname = top.get('user_name') or 'Ami'
                        
                        if last_follow_id is None:
                            last_follow_id = fid # Premier passage, on ignore
                        elif fid != last_follow_id:
                            last_follow_id = fid
                            print(f"🔔 NOUVEAU FOLLOW: {fname}")
                            await self.handle_follow(fname)
                
                await asyncio.sleep(10) # Vérifier toutes les 10s
            except Exception as e:
                print(f"❌ Erreur watcher: {e}")
                await asyncio.sleep(30)

    async def event_raw_usernotice(self, channel, tags):
        """Gère les subs et resubs"""
        msg_id = tags.get('msg-id')
        if msg_id in {'sub', 'resub', 'subgift', 'anonsubgift', 'giftpaidupgrade'}:
            display_name = tags.get('display-name') or tags.get('login') or 'Ami'
            print(f"💎 SUB EVENT: {display_name}")
            await self.handle_follow(display_name, is_sub=True)

    async def handle_follow(self, pseudo, is_sub=False):
        """Affiche le message de remerciement"""
        message = f"Merci {pseudo}"
        cfg_key = 'follow'
        
        if is_sub:
            message = f"MERCI SUB {pseudo} <3"
            cfg_key = 'sub'
            
        # Récupérer la config spécifique
        cfg = self.config.get(cfg_key, self.config.get('say')) # Fallback sur say si manquant
        await self.display_sequence(message, cfg)

    @commands.command(name='say')
    async def cmd_say(self, ctx, *, text: str):
        """!say [message] - Affiche un message personnalisé"""
        print(f"💬 Commande !say: {text}")
        cfg = self.config.get('say', {})
        await self.display_sequence(text, cfg)

    @commands.command(name='config')
    async def cmd_config(self, ctx, section: str = None, setting: str = None, value: str = None):
        """!config [section] [setting] [value] (ex: !config say color red)"""
        if not section:
            await ctx.send("❓ Usage: !config [say|follow|sub] [speed|color|deco|bold|repeat] [valeur]")
            return

        section = section.lower()
        if section not in ['say', 'follow', 'sub']:
            await ctx.send("❌ Section inconnue. Utilisez: say, follow, sub")
            return
            
        if not setting:
            # Afficher la config de la section
            cfg = self.config.get(section, {})
            cfg_str = ", ".join(f"{k}={v}" for k, v in cfg.items())
            await ctx.send(f"⚙️ Config [{section}]: {cfg_str}")
            return

        setting = setting.lower()
        changed = False
        cfg = self.config[section]
        
        if setting == 'speed':
            try:
                val = int(value)
                cfg['scroll_speed'] = max(0, min(255, val))
                await ctx.send(f"✅ [{section}] Vitesse réglée à {cfg['scroll_speed']}")
                changed = True
            except:
                await ctx.send("❌ Vitesse invalide (0-255)")
                
        elif setting == 'color':
            # On teste la couleur sur le masque pour valider, mais on ne l'applique pas tout de suite
            if self.mask.set_text_color(value):
                cfg['text_color'] = value
                await ctx.send(f"✅ [{section}] Couleur réglée à {value}")
                changed = True
            else:
                await ctx.send("❌ Couleur inconnue")
                
        elif setting == 'deco':
            cfg['decoration'] = value
            await ctx.send(f"✅ [{section}] Décoration réglée à {value}")
            changed = True
            
        elif setting == 'bold':
            is_bold = value.lower() in ['on', 'true', '1', 'yes']
            cfg['bold'] = is_bold
            await ctx.send(f"✅ [{section}] Gras: {'Activé' if is_bold else 'Désactivé'}")
            changed = True
            
        elif setting == 'repeat':
            try:
                val = int(value)
                cfg['repeat'] = max(1, val)
                await ctx.send(f"✅ [{section}] Répétitions: {cfg['repeat']}")
                changed = True
            except:
                await ctx.send("❌ Nombre invalide")
            
        else:
            await ctx.send("❌ Paramètre inconnu")

        if changed:
            self.save_config()
    
    async def start_animation_loop(self):
        """Démarre la boucle d'animation"""
        # Arrêter l'animation existante si elle tourne
        await self.stop_animation_loop()
        
        self.animation_running = True
        self.animation_task = self.loop.create_task(self._animation_loop())
        print("🎬 Animation loop démarrée")
    
    async def stop_animation_loop(self):
        """Arrête la boucle d'animation"""
        self.animation_running = False
        if self.animation_task and not self.animation_task.done():
            self.animation_task.cancel()
            try:
                await self.animation_task
            except asyncio.CancelledError:
                pass
        print("⏹️ Animation loop arrêtée")
    
    async def _animation_loop(self):
        """Boucle d'animation en arrière-plan"""
        try:
            while self.animation_running:
                for image_id in range(1, self.num_animation_frames + 1):
                    if not self.animation_running:
                        break
                    await self.mask.show_image(image_id, bank=1)
                    await asyncio.sleep(self.animation_delay)
        except asyncio.CancelledError:
            print("🎬 Animation loop cancelled")
        except Exception as e:
            print(f"❌ Erreur dans animation loop: {e}")

    async def display_sequence(self, text, cfg):
        """Gère l'affichage temporaire puis retour à l'animation"""
        async with self.display_lock:
            # Arrêter l'animation pendant l'affichage du texte
            await self.stop_animation_loop()
            
            try:
                # 1. Appliquer les configurations de l'événement
                self.mask.set_text_color(cfg.get('text_color', 'magenta'))
                self.mask.set_decoration_style(cfg.get('decoration', 'lines'))
                self.mask.set_bold(cfg.get('bold', False))
                
                # 2. Afficher le texte
                speed = cfg.get('scroll_speed', 50)
                mode = cfg.get('scroll_mode', 'scroll_left')
                repeat = cfg.get('repeat', 1)
                
                await self.mask.set_scrolling_text(text, scroll_mode=mode, speed=speed)
                
                # 3. Calculer la durée d'attente
                char_count = len(text)
                base_time = 6.0 
                char_time = 0.8 
                
                speed_factor = 50.0 / max(1, speed)
                loop_duration = (base_time + (char_count * char_time)) * speed_factor
                total_wait = loop_duration * repeat
                
                print(f"⏱️ Attente de {total_wait:.1f}s pour {repeat} passages (Config: {cfg.get('text_color')})...")
                await asyncio.sleep(total_wait)
                
            except Exception as e:
                print(f"❌ Erreur display_sequence: {e}")
            finally:
                # 4. Redémarrer l'animation
                print("🔙 Redémarrage de l'animation")
                await self.start_animation_loop()

def main():
    # Initialisation du contrôleur
    mask = FinalMaskController()
    
    # Création du bot
    bot = FinalTwitchBot(mask)
    
    print("🚀 Démarrage du Bot Final Shining Mask...")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Arrêt demandé...")
    finally:
        # Nettoyage si besoin (asyncio loop closed by bot.run usually)
        pass

if __name__ == "__main__":
    main()
