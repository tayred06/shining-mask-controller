#!/usr/bin/env python3
"""
Contrôleur Clavier pour Masque LED - Inspiré de shining-mask
===========================================================

Contrôle en temps réel du masque LED avec le clavier :
- Images préchargées (1-20) contrôlées par les touches numériques
- Animations avec les touches fléchées
- Expressions et émotions avec les lettres
- Mode gaming avec WASD
- Effets spéciaux avec les touches fonction

Inspiré du projet shawnrancatore/shining-mask mais avec clavier au lieu de Wii Nunchuck
"""

import asyncio
import sys
import os
import time
import random
import threading
from queue import Queue

# Configuration du clavier
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    print("⚠️ Module 'keyboard' non trouvé. Installation...")
    os.system("pip install keyboard")
    try:
        import keyboard
        KEYBOARD_AVAILABLE = True
    except ImportError:
        KEYBOARD_AVAILABLE = False
        print("❌ Impossible d'installer le module keyboard")

# Ajouter le répertoire des modules au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.text.scrolling_controller import ScrollingTextController
from modules.animations.stable_animation_controller import StableAnimationController
from modules.config.config_manager import ConfigManager

class KeyboardMaskController(ScrollingTextController):
    """
    Contrôleur du masque LED via clavier - Version gaming/interactive
    
    Inspiré de shining-mask mais utilise le clavier pour :
    - Sélectionner des images préchargées (1-20)
    - Contrôler des animations en temps réel
    - Changer d'expressions et d'émotions
    - Mode gaming interactif
    """
    
    def __init__(self):
        super().__init__()
        
        # Contrôleurs additionnels
        self.animation_controller = StableAnimationController()
        self.config_manager = ConfigManager()
        
        # État du contrôleur
        self.current_image = 1
        self.current_mode = "image"  # "image", "animation", "text", "gaming"
        self.is_running = False
        self.can_blink = True
        self.auto_blink_enabled = True
        
        # Commandes clavier en attente
        self.command_queue = Queue()
        
        # Mapping des commandes clavier
        self.setup_keyboard_mapping()
        
        # Images préchargées (simulées comme dans shining-mask)
        self.preloaded_images = self.generate_image_commands()
        
        print("🎮 Contrôleur Clavier initialisé!")
        print("📋 Appuyez sur 'h' pour l'aide")

    def generate_image_commands(self):
        """Génère les commandes pour 20 images préchargées (comme shining-mask)"""
        images = []
        for i in range(1, 21):
            # Format : PLAY + image_id (comme dans le repo original)
            command = f"PLAY{i:02d}".encode()
            images.append(command)
        return images
    
    def setup_keyboard_mapping(self):
        """Configure le mapping des touches clavier"""
        if not KEYBOARD_AVAILABLE:
            return
            
        # Images préchargées (1-20)
        for i in range(1, 10):
            keyboard.on_press_key(str(i), lambda e, img=i: self.queue_command('image', img))
        
        # Images 10-20 avec Shift+0-9 + q
        keyboard.on_press_key('0', lambda e: self.queue_command('image', 10))
        keyboard.add_hotkey('shift+1', lambda: self.queue_command('image', 11))
        keyboard.add_hotkey('shift+2', lambda: self.queue_command('image', 12))
        keyboard.add_hotkey('shift+3', lambda: self.queue_command('image', 13))
        keyboard.add_hotkey('shift+4', lambda: self.queue_command('image', 14))
        keyboard.add_hotkey('shift+5', lambda: self.queue_command('image', 15))
        keyboard.add_hotkey('shift+6', lambda: self.queue_command('image', 16))
        keyboard.add_hotkey('shift+7', lambda: self.queue_command('image', 17))
        keyboard.add_hotkey('shift+8', lambda: self.queue_command('image', 18))
        keyboard.add_hotkey('shift+9', lambda: self.queue_command('image', 19))
        keyboard.add_hotkey('shift+0', lambda: self.queue_command('image', 20))
        
        # Animations avec les flèches
        keyboard.on_press_key('up', lambda e: self.queue_command('animation', 'pulse'))
        keyboard.on_press_key('down', lambda e: self.queue_command('animation', 'wave'))
        keyboard.on_press_key('left', lambda e: self.queue_command('animation', 'fire'))
        keyboard.on_press_key('right', lambda e: self.queue_command('animation', 'rain'))
        keyboard.on_press_key('space', lambda e: self.queue_command('animation', 'matrix'))
        
        # Expressions et émotions
        keyboard.on_press_key('s', lambda e: self.queue_command('expression', 'smile'))  # Sourire
        keyboard.on_press_key('f', lambda e: self.queue_command('expression', 'frown'))  # Froncement
        keyboard.on_press_key('w', lambda e: self.queue_command('expression', 'wink'))   # Clin d'œil
        keyboard.on_press_key('b', lambda e: self.queue_command('action', 'blink'))      # Clignotement
        keyboard.on_press_key('r', lambda e: self.queue_command('action', 'random'))     # Image aléatoire
        
        # Couleurs rapides
        keyboard.add_hotkey('ctrl+r', lambda: self.queue_command('color', 'red'))
        keyboard.add_hotkey('ctrl+g', lambda: self.queue_command('color', 'green'))
        keyboard.add_hotkey('ctrl+b', lambda: self.queue_command('color', 'blue'))
        keyboard.add_hotkey('ctrl+w', lambda: self.queue_command('color', 'white'))
        
        # Modes spéciaux
        keyboard.on_press_key('m', lambda e: self.queue_command('mode', 'cycle'))        # Cycle modes
        keyboard.on_press_key('p', lambda e: self.queue_command('action', 'pause'))      # Pause
        keyboard.on_press_key('c', lambda e: self.queue_command('action', 'clear'))      # Effacer
        
        # Contrôles système
        keyboard.on_press_key('h', lambda e: self.show_help())
        keyboard.on_press_key('esc', lambda e: self.queue_command('system', 'quit'))
        
        print("⌨️ Mapping clavier configuré!")
    
    def queue_command(self, command_type: str, value):
        """Ajoute une commande à la queue"""
        self.command_queue.put((command_type, value))
    
    def show_help(self):
        """Affiche l'aide des commandes clavier"""
        help_text = """
🎮 === CONTRÔLEUR CLAVIER MASQUE LED ===

📸 IMAGES PRÉCHARGÉES:
   1-9        → Images 1-9
   0          → Image 10  
   Shift+1-9  → Images 11-19
   Shift+0    → Image 20

🎬 ANIMATIONS:
   ↑          → Pulse (pulsation)
   ↓          → Wave (vague)
   ←          → Fire (feu)
   →          → Rain (pluie) 
   SPACE      → Matrix

😊 EXPRESSIONS:
   S          → Smile (sourire)
   F          → Frown (froncement)
   W          → Wink (clin d'œil)
   B          → Blink (clignotement)
   R          → Random (aléatoire)

🎨 COULEURS:
   Ctrl+R     → Rouge
   Ctrl+G     → Vert
   Ctrl+B     → Bleu
   Ctrl+W     → Blanc

⚙️ CONTRÔLES:
   M          → Cycle modes
   P          → Pause
   C          → Effacer
   H          → Cette aide
   ESC        → Quitter

🎯 MODE ACTUEL: {self.current_mode.upper()}
📸 IMAGE ACTUELLE: {self.current_image}
"""
        print(help_text)
    
    async def connect(self):
        """Connexion au masque avec initialisation"""
        try:
            success = await super().connect()
            if success:
                # Connecter le contrôleur d'animation
                self.animation_controller.client = self.client
                
                print("✅ Masque connecté!")
                print("🎮 Contrôleur clavier prêt!")
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    async def send_preloaded_image(self, image_id: int):
        """Envoie une commande d'image préchargée (comme shining-mask)"""
        try:
            if 1 <= image_id <= 20:
                command = self.preloaded_images[image_id - 1]
                await self.send_command(command)
                self.current_image = image_id
                print(f"📸 Image {image_id} envoyée")
                return True
            else:
                print(f"❌ Image {image_id} invalide (1-20)")
                return False
        except Exception as e:
            print(f"❌ Erreur envoi image: {e}")
            return False
    
    async def trigger_blink_sequence(self):
        """Séquence de clignotement automatique (inspiré de shining-mask)"""
        if not self.can_blink:
            return
            
        try:
            self.can_blink = False
            
            # Séquence : ouverts → mi-fermés → fermés → mi-fermés → ouverts
            blink_sequence = [6, 7, 7, 6]  # IDs d'images pour le clignotement
            
            for img_id in blink_sequence:
                await self.send_preloaded_image(img_id)
                await asyncio.sleep(1/12)  # 12 FPS comme dans l'original
            
            # Retourner à l'image précédente
            await self.send_preloaded_image(self.current_image)
            
            # Autoriser un nouveau clignotement dans 1 seconde
            await asyncio.sleep(1.0)
            self.can_blink = True
            
        except Exception as e:
            print(f"❌ Erreur clignotement: {e}")
            self.can_blink = True
    
    async def auto_blink_loop(self):
        """Boucle de clignotement automatique (comme dans shining-mask)"""
        while self.is_running:
            try:
                if self.auto_blink_enabled and self.can_blink:
                    # 4% de chance de cligner (comme dans l'original)
                    if random.randint(0, 100) < 4:
                        await self.trigger_blink_sequence()
                
                await asyncio.sleep(0.1)  # Vérifier toutes les 100ms
                
            except Exception as e:
                print(f"❌ Erreur auto-blink: {e}")
                await asyncio.sleep(1.0)
    
    async def process_commands(self):
        """Traite les commandes du clavier en continu"""
        while self.is_running:
            try:
                if not self.command_queue.empty():
                    command_type, value = self.command_queue.get()
                    
                    if command_type == 'image':
                        await self.send_preloaded_image(value)
                        
                    elif command_type == 'animation':
                        print(f"🎬 Animation: {value}")
                        await self.animation_controller.play_simple_animation(value, 5.0)
                        
                    elif command_type == 'expression':
                        await self.handle_expression(value)
                        
                    elif command_type == 'action':
                        await self.handle_action(value)
                        
                    elif command_type == 'color':
                        await self.handle_color_change(value)
                        
                    elif command_type == 'mode':
                        self.handle_mode_change(value)
                        
                    elif command_type == 'system':
                        if value == 'quit':
                            self.is_running = False
                            break
                
                await asyncio.sleep(0.05)  # 20 FPS pour la réactivité
                
            except Exception as e:
                print(f"❌ Erreur traitement commande: {e}")
                await asyncio.sleep(0.1)
    
    async def handle_expression(self, expression: str):
        """Gère les expressions faciales"""
        expression_map = {
            'smile': [2, 3, 4],      # Images de sourire
            'frown': [8, 9, 10],     # Images de froncement
            'wink': [5, 6, 5]        # Séquence de clin d'œil
        }
        
        if expression in expression_map:
            sequence = expression_map[expression]
            for img_id in sequence:
                await self.send_preloaded_image(img_id)
                await asyncio.sleep(0.2)
    
    async def handle_action(self, action: str):
        """Gère les actions spéciales"""
        if action == 'blink':
            await self.trigger_blink_sequence()
            
        elif action == 'random':
            random_img = random.randint(1, 20)
            await self.send_preloaded_image(random_img)
            
        elif action == 'pause':
            self.auto_blink_enabled = not self.auto_blink_enabled
            status = "activé" if self.auto_blink_enabled else "désactivé"
            print(f"⏸️ Auto-blink {status}")
            
        elif action == 'clear':
            await self.send_command(b"CLEAR")
            print("🗑️ Écran effacé")
    
    async def handle_color_change(self, color: str):
        """Change la couleur du masque"""
        color_map = {
            'red': "FCFF0000",
            'green': "FC00FF00", 
            'blue': "FC0000FF",
            'white': "FCFFFFFF"
        }
        
        if color in color_map:
            await self.send_command(color_map[color].encode())
            print(f"🎨 Couleur: {color}")
    
    def handle_mode_change(self, mode_action: str):
        """Change le mode de fonctionnement"""
        if mode_action == 'cycle':
            modes = ['image', 'animation', 'text', 'gaming']
            current_idx = modes.index(self.current_mode)
            self.current_mode = modes[(current_idx + 1) % len(modes)]
            print(f"🔄 Mode: {self.current_mode}")
    
    async def run(self):
        """Boucle principale du contrôleur"""
        if not KEYBOARD_AVAILABLE:
            print("❌ Module keyboard non disponible")
            return
            
        # Connexion au masque
        if not await self.connect():
            print("❌ Impossible de se connecter au masque")
            return
        
        self.is_running = True
        
        try:
            print("🚀 Contrôleur clavier démarré!")
            print("📋 Appuyez sur 'h' pour l'aide, ESC pour quitter")
            
            # Démarrer les tâches parallèles
            tasks = [
                asyncio.create_task(self.process_commands()),
                asyncio.create_task(self.auto_blink_loop())
            ]
            
            # Attendre que l'une des tâches se termine
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n⚠️ Interruption clavier")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        finally:
            self.is_running = False
            if self.client:
                await self.client.disconnect()
            print("👋 Contrôleur arrêté")

async def main():
    """Point d'entrée principal"""
    controller = KeyboardMaskController()
    await controller.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
