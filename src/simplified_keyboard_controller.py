#!/usr/bin/env python3
"""
Contrôleur Clavier Simplifié pour Masque LED 
===========================================

Version simplifiée inspirée de shining-mask avec contrôles clavier basiques.
Utilise les lettres et touches spéciales au lieu des chiffres pour éviter les conflits.
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
    print("✅ Module keyboard disponible")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ Module keyboard non disponible")

# Ajouter le répertoire des modules au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.text.scrolling_controller import ScrollingTextController
from modules.animations.stable_animation_controller import StableAnimationController
from modules.config.config_manager import ConfigManager

class SimplifiedKeyboardController(ScrollingTextController):
    """
    Contrôleur clavier simplifié pour le masque LED
    
    Basé sur le projet shining-mask mais avec contrôles clavier simplifiés :
    - Q,W,E,R,T = Images 1-5
    - A,S,D,F,G = Images 6-10  
    - Z,X,C,V,B = Images 11-15
    - Flèches = Animations
    - Touches fonction = Effets spéciaux
    """
    
    def __init__(self):
        super().__init__()
        
        # Contrôleurs additionnels
        self.animation_controller = StableAnimationController()
        self.config_manager = ConfigManager()
        
        # État du contrôleur
        self.current_image = 1
        self.is_running = False
        self.can_blink = True
        self.auto_blink_enabled = True
        
        # Commandes en attente
        self.command_queue = Queue()
        
        # Images préchargées remplacées par patterns texte
        self.text_patterns = self.generate_text_patterns()
        
        # Importer le contrôleur de texte pour l'affichage
        from modules.text.scrolling_controller import ScrollingTextController
        self.text_controller = ScrollingTextController()
        
        print("🎮 Contrôleur Clavier Simplifié initialisé!")

    def generate_text_patterns(self):
        """Génère les 20 patterns texte pour remplacer les images préchargées"""
        patterns = [
            # Images 1-5: Émotions de base (Q W E R T)
            {"text": ":)", "color": (255, 255, 0)},      # 1 - Q - Sourire
            {"text": ":|", "color": (255, 255, 255)},     # 2 - W - Neutre
            {"text": ":(", "color": (0, 100, 255)},       # 3 - E - Triste
            {"text": ":O", "color": (255, 100, 0)},       # 4 - R - Surpris
            {"text": ">:(", "color": (255, 0, 0)},        # 5 - T - Colère
            
            # Images 6-10: Émotions avancées (A S D F G)
            {"text": ";)", "color": (255, 255, 0)},       # 6 - A - Clin œil (clignotement)
            {"text": "-_-", "color": (100, 100, 100)},   # 7 - S - Endormi (clignotement)
            {"text": "<3", "color": (255, 0, 100)},       # 8 - D - Cœur
            {"text": "B)", "color": (0, 255, 255)},       # 9 - F - Cool
            {"text": "X_X", "color": (255, 0, 255)},      # 10 - G - Étourdi
            
            # Images 11-15: Symboles (Z X C V B)
            {"text": "*", "color": (255, 255, 0)},        # 11 - Z - Étoile
            {"text": "o", "color": (255, 255, 255)},      # 12 - X - Rond (remplace ■)
            {"text": "O", "color": (0, 255, 0)},          # 13 - C - Grand rond
            {"text": "+", "color": (255, 0, 0)},          # 14 - V - Plus
            {"text": "?", "color": (255, 255, 0)},        # 15 - B - Question
            
            # Images 16-20: Texte et effets (extension)
            {"text": "OK", "color": (0, 255, 0)},         # 16 - OK
            {"text": "NO", "color": (255, 0, 0)},         # 17 - Non
            {"text": "YES", "color": (0, 255, 0)},        # 18 - Oui
            {"text": "!", "color": (255, 100, 0)},        # 19 - Exclamation
            {"text": "HI", "color": (0, 255, 255)},       # 20 - Salut
        ]
        
        return patterns
    
    def setup_keyboard_hooks(self):
        """Configure les hooks clavier de manière simplifiée"""
        if not KEYBOARD_AVAILABLE:
            return False
            
        try:
            # Images ligne 1 (QWERT = images 1-5)
            keyboard.add_hotkey('q', lambda: self.queue_command('image', 1))
            keyboard.add_hotkey('w', lambda: self.queue_command('image', 2))
            keyboard.add_hotkey('e', lambda: self.queue_command('image', 3))
            keyboard.add_hotkey('r', lambda: self.queue_command('image', 4))
            keyboard.add_hotkey('t', lambda: self.queue_command('image', 5))
            
            # Images ligne 2 (ASDFG = images 6-10)
            keyboard.add_hotkey('a', lambda: self.queue_command('image', 6))
            keyboard.add_hotkey('s', lambda: self.queue_command('image', 7))
            keyboard.add_hotkey('d', lambda: self.queue_command('image', 8))
            keyboard.add_hotkey('f', lambda: self.queue_command('image', 9))
            keyboard.add_hotkey('g', lambda: self.queue_command('image', 10))
            
            # Images ligne 3 (ZXCVB = images 11-15)
            keyboard.add_hotkey('z', lambda: self.queue_command('image', 11))
            keyboard.add_hotkey('x', lambda: self.queue_command('image', 12))
            keyboard.add_hotkey('c', lambda: self.queue_command('image', 13))
            keyboard.add_hotkey('v', lambda: self.queue_command('image', 14))
            keyboard.add_hotkey('b', lambda: self.queue_command('image', 15))
            
            # Animations avec flèches
            keyboard.add_hotkey('up', lambda: self.queue_command('animation', 'pulse'))
            keyboard.add_hotkey('down', lambda: self.queue_command('animation', 'wave'))
            keyboard.add_hotkey('left', lambda: self.queue_command('animation', 'fire'))
            keyboard.add_hotkey('right', lambda: self.queue_command('animation', 'rain'))
            keyboard.add_hotkey('space', lambda: self.queue_command('animation', 'matrix'))
            
            # Actions spéciales
            keyboard.add_hotkey('enter', lambda: self.queue_command('action', 'blink'))
            keyboard.add_hotkey('backspace', lambda: self.queue_command('action', 'random'))
            keyboard.add_hotkey('tab', lambda: self.queue_command('action', 'clear'))
            
            # Couleurs avec Shift+lettre
            keyboard.add_hotkey('shift+r', lambda: self.queue_command('color', 'red'))
            keyboard.add_hotkey('shift+g', lambda: self.queue_command('color', 'green'))
            keyboard.add_hotkey('shift+b', lambda: self.queue_command('color', 'blue'))
            keyboard.add_hotkey('shift+w', lambda: self.queue_command('color', 'white'))
            
            # Contrôle
            keyboard.add_hotkey('h', lambda: self.show_help())
            keyboard.add_hotkey('esc', lambda: self.queue_command('system', 'quit'))
            
            print("⌨️ Hooks clavier configurés!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur configuration clavier: {e}")
            return False
    
    def queue_command(self, command_type: str, value):
        """Ajoute une commande à la queue"""
        self.command_queue.put((command_type, value))
        print(f"🎯 Commande: {command_type} = {value}")
    
    def show_help(self):
        """Affiche l'aide des commandes"""
        help_text = f"""
🎮 === CONTRÔLEUR CLAVIER MASQUE LED ===

� PATTERNS TEXTE (remplacent les images):
   Q W E R T  → :) :| :( :O >:(
   A S D F G  → ;) -_- <3 B) X_X  
   Z X C V B  → * o O + ?

🎬 ANIMATIONS:
   ↑          → Pulse
   ↓          → Wave  
   ←          → Fire
   →          → Rain
   SPACE      → Matrix

🎭 ACTIONS:
   ENTER      → Clignotement
   BACKSPACE  → Pattern aléatoire
   TAB        → Réinitialiser

🎨 COULEURS:
   Shift+R    → Rouge
   Shift+G    → Vert
   Shift+B    → Bleu  
   Shift+W    → Blanc

⚙️ CONTRÔLES:
   H          → Cette aide
   ESC        → Quitter

🎯 PATTERN ACTUEL: {self.current_image}
🔗 STATUT: {'Connecté' if self.client and self.client.is_connected else 'Déconnecté'}
"""
        print(help_text)
    
    async def connect(self):
        """Connexion au masque"""
        try:
            success = await super().connect()
            if success:
                self.animation_controller.client = self.client
                print("✅ Masque connecté!")
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    async def send_text_pattern(self, pattern_id: int):
        """Affiche un pattern texte à la place d'une image préchargée"""
        try:
            if 1 <= pattern_id <= 20:
                pattern = self.text_patterns[pattern_id - 1]
                
                # Utiliser le système de texte existant pour afficher
                # (mais nous devons d'abord nous assurer que client est disponible)
                if not self.client or not self.client.is_connected:
                    print("❌ Non connecté au masque")
                    return False
                
                # Temporairement, on utilise notre contrôleur de texte
                from working.complete_text_display import MaskTextDisplay
                temp_controller = MaskTextDisplay()
                temp_controller.client = self.client  # Réutiliser la connexion existante
                
                await temp_controller.display_text(pattern['text'], color=pattern['color'])
                
                self.current_image = pattern_id
                print(f"� Pattern {pattern_id} ('{pattern['text']}') affiché")
                return True
            else:
                print(f"❌ Pattern {pattern_id} invalide (1-20)")
                return False
        except Exception as e:
            print(f"❌ Erreur affichage pattern: {e}")
            return False
    
    async def trigger_blink_sequence(self):
        """Séquence de clignotement avec patterns texte"""
        if not self.can_blink:
            return
            
        try:
            self.can_blink = False
            print("👁️ Clignotement...")
            
            # Séquence de clignotement avec les patterns texte appropriés
            blink_sequence = [6, 7, 7, 6]  # Patterns "clin œil" et "endormi"
            
            for pattern_id in blink_sequence:
                await self.send_text_pattern(pattern_id)
                await asyncio.sleep(1/12)  # 12 FPS comme l'original
            
            # Retourner au pattern précédent
            await self.send_text_pattern(self.current_image)
            
            # Délai avant prochain clignotement
            await asyncio.sleep(1.0)
            self.can_blink = True
            
        except Exception as e:
            print(f"❌ Erreur clignotement: {e}")
            self.can_blink = True
    
    async def auto_blink_loop(self):
        """Boucle de clignotement automatique"""
        while self.is_running:
            try:
                if self.auto_blink_enabled and self.can_blink:
                    # 4% de chance de cligner (comme shining-mask)
                    if random.randint(0, 100) < 4:
                        await self.trigger_blink_sequence()
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Erreur auto-blink: {e}")
                await asyncio.sleep(1.0)
    
    async def process_commands(self):
        """Traite les commandes du clavier"""
        while self.is_running:
            try:
                if not self.command_queue.empty():
                    command_type, value = self.command_queue.get()
                    
                    if command_type == 'image':
                        await self.send_text_pattern(value)
                        
                    elif command_type == 'animation':
                        print(f"🎬 Animation: {value}")
                        await self.animation_controller.play_simple_animation(value, 3.0)
                        
                    elif command_type == 'action':
                        await self.handle_action(value)
                        
                    elif command_type == 'color':
                        await self.handle_color_change(value)
                        
                    elif command_type == 'system':
                        if value == 'quit':
                            print("👋 Arrêt demandé")
                            self.is_running = False
                            break
                
                await asyncio.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                print(f"❌ Erreur traitement: {e}")
                await asyncio.sleep(0.1)
    
    async def handle_action(self, action: str):
        """Gère les actions spéciales"""
        if action == 'blink':
            await self.trigger_blink_sequence()
            
        elif action == 'random':
            random_pattern = random.randint(1, 15)  # Limité aux patterns mappés
            await self.send_text_pattern(random_pattern)
            print(f"🎲 Pattern aléatoire: {random_pattern}")
            
        elif action == 'clear':
            # Afficher un pattern vide ou effacer
            await self.send_text_pattern(2)  # Pattern neutre ":|"
            print("🗑️ Affichage réinitialisé")
    
    async def handle_color_change(self, color: str):
        """Change la couleur"""
        color_map = {
            'red': "FCFF0000",
            'green': "FC00FF00", 
            'blue': "FC0000FF",
            'white': "FCFFFFFF"
        }
        
        if color in color_map:
            await self.send_command(color_map[color].encode())
            print(f"🎨 Couleur: {color}")
    
    async def run(self):
        """Boucle principale"""
        # Connexion
        if not await self.connect():
            print("❌ Impossible de se connecter au masque")
            return
        
        # Configuration clavier
        if not self.setup_keyboard_hooks():
            print("❌ Impossible de configurer le clavier")
            return
        
        self.is_running = True
        
        try:
            print("🚀 Contrôleur clavier démarré!")
            self.show_help()
            
            # Démarrer les tâches parallèles
            await asyncio.gather(
                self.process_commands(),
                self.auto_blink_loop()
            )
            
        except KeyboardInterrupt:
            print("\n⚠️ Interruption")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        finally:
            self.is_running = False
            if self.client:
                await self.client.disconnect()
            print("👋 Contrôleur arrêté")

async def main():
    """Point d'entrée"""
    if not KEYBOARD_AVAILABLE:
        print("❌ Module keyboard requis:")
        print("   pip install keyboard")
        return
    
    controller = SimplifiedKeyboardController()
    await controller.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
