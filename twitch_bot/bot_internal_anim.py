#!/usr/bin/env python3
"""
Bot Twitch Mask Controller - Version Animation Interne
Ce bot utilise les animations pré-enregistrées dans le masque (ID 1 à N)
au lieu de stream des images depuis le PC.
"""

# ==========================================
# CONFIGURATION FACILE
# ==========================================
DEFAULT_ANIMATION_ID = 18  # ID de l'animation par défaut (1-20+ selon le masque)

# CONFIGURATION GENERALE
SCROLL_SPEED = 50       # Vitesse de défilement du texte (0-255)
SCROLL_MODE = 3         # 3 = Scroll Left (Standard)
TEXT_COLOR = (255, 0, 255) # Couleur par défaut (R, G, B)
# ==========================================

import os
import sys
import asyncio
import json
import random
from pathlib import Path
from dotenv import load_dotenv
from twitchio.ext import commands

# Charger les variables d'environnement
load_dotenv()

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
SRC_DIR = ROOT_DIR / 'src'
sys.path.append(str(SRC_DIR))

try:
    from working.ultimate_text_display_with_bold import CompleteMaskController
except ImportError as e:
    print(f"❌ Erreur Import: {e}")
    sys.exit(1)

CFG_FILE = CURRENT_DIR / 'config.json'

class InternalAnimMaskController(CompleteMaskController):
    async def set_animation(self, anim_id):
        """
        Lance une animation interne du masque via la commande ANIM.
        Protocol: 05 41 4E 49 4D <ID>
        """
        try:
            cmd_str = "ANIM"
            args = bytes([int(anim_id)])
            
            payload = bytearray()
            payload.append(len(cmd_str) + len(args))
            payload.extend(cmd_str.encode('ascii'))
            payload.extend(args)
            
            await self.send_command(payload)
            print(f"🎭 Animation {anim_id} activée")
            return True
        except Exception as e:
            print(f"❌ Erreur set_animation: {e}")
            return False

class InternalAnimBot(commands.Bot):
    def __init__(self):
        self.mask = InternalAnimMaskController()
        self.display_lock = asyncio.Lock()
        
        # Load env vars
        token = os.environ.get('TWITCH_TOKEN')
        channel = os.environ.get('TWITCH_CHANNEL')
        nick = os.environ.get('TWITCH_NICK')
        
        if not token:
            print("❌ .env manquant ou incomplet")
            sys.exit(1)
            
        super().__init__(token=token, prefix='!', initial_channels=[channel], nick=nick)
        self.channel_name = channel
        
        # Config (simple load)
        self.anim_id = DEFAULT_ANIMATION_ID
        self.load_config()

    def load_config(self):
        if CFG_FILE.exists():
            try:
                with open(CFG_FILE, 'r') as f:
                    cfg = json.load(f)
                    # On regarde si une default_image est définie, sinon on garde la constante
                    self.anim_id = cfg.get('default_image', DEFAULT_ANIMATION_ID)
            except Exception as e:
                print(f"⚠️ Erreur config: {e}")

    async def event_ready(self):
        print(f"✅ Bot connecté: {self.nick} sur {self.channel_name}")
        print("🔄 Connexion au masque...")
        try:
            await self.mask.connect()
            await self.mask.set_brightness(1)
            # Lancer l'animation par défaut au démarrage
            await self.set_default_state()
            print("✅ Masque prêt!")
        except Exception as e:
            print(f"❌ Erreur connexion masque: {e}")

    async def set_default_state(self):
        """Remet le masque dans son état par défaut (Animation)"""
        await self.mask.set_animation(self.anim_id)

    async def display_message(self, text, color=TEXT_COLOR, speed=SCROLL_SPEED, repeat=1):
        """Affiche un texte temporairement puis revient à l'animation"""
        async with self.display_lock:
            print(f"💬 Affichage: {text}")
            try:
                # 1. Configurer le style
                # Note: CompleteMaskController attend un tuple pour la couleur
                if isinstance(color, (tuple, list)):
                    self.mask.set_text_color_by_rgb(color)
                else:
                    self.mask.set_text_color(str(color))
                
                # 2. Envoyer le texte
                await self.mask.set_scrolling_text(text, scroll_mode=SCROLL_MODE, speed=speed)
                
                # 3. Attendre la fin du défilement
                # Estimation durée : (Base + Char * 0.8s) * (50/Speed)
                char_count = len(text)
                base = 5.0
                char_time = 0.8
                duration = (base + (char_count * char_time)) * (50.0 / max(1, speed))
                
                await asyncio.sleep(duration * repeat)
                
            except Exception as e:
                print(f"❌ Erreur display: {e}")
            finally:
                # 4. Retour à l'anim
                print("🔙 Retour animation")
                await self.set_default_state()

    @commands.command(name='randanim')
    async def cmd_randanim(self, ctx):
        """!randanim - Change l'animation pour une aléatoire (1-40) pendant 10s"""
        val = random.randint(1, 40)
        
        # 1. Changer l'animation (sous lock pour éviter conflit avec upload)
        async with self.display_lock:
            await self.mask.set_animation(val)
            await ctx.send(f"🎲 Animation aléatoire: {val} (10s)")
            
        # 2. Attendre 10 secondes
        await asyncio.sleep(10)
        
        # 3. Revenir à la normale (sous lock)
        async with self.display_lock:
            # On vérifie si on n'est pas déjà en train d'afficher autre chose
            # Mais avec le lock, on attendra que l'autre chose finisse.
            # C'est acceptable.
            await self.set_default_state()

    @commands.command(name='anim')
    async def cmd_anim(self, ctx, anim_id: str):
        """!anim [ID] - Change l'animation par défaut en direct"""
        try:
            val = int(anim_id)
            self.anim_id = val
            await self.set_default_state()
            await ctx.send(f"✅ Animation changée pour: {val}")
        except ValueError:
            await ctx.send("❌ ID invalide (doit être un nombre)")

    @commands.command(name='say')
    async def cmd_say(self, ctx, *, text: str):
        await self.display_message(text)

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

def main():
    bot = InternalAnimBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
