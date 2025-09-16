#!/usr/bin/env python3
"""
Contrôleur Principal du Masque LED v2.0
=======================================

Contrôleur unifié utilisant l'architecture modulaire :
- Module core : Communication BLE de base
- Module text : Gestion du texte et décorations  
- Module animations : Animations personnalisées
- Module config : Gestion des configurations
- Module utils : Fonctions utilitaires

Architecture modulaire pour faciliter le développement et la maintenance.
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire des modules au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.text.scrolling_controller import ScrollingTextController
from modules.animations.animation_controller import AnimationController
from modules.animations.stable_animation_controller import StableAnimationController
from modules.config.config_manager import ConfigManager
from modules.utils.image_utils import debug_print_frame

class UnifiedMaskController(ScrollingTextController):
    """
    Contrôleur unifié du masque LED v2.0
    
    Combine toutes les fonctionnalités :
    - Texte défilant avec décorations
    - Animations personnalisées
    - Gestion de configuration
    - Interface utilisateur complète
    """
    
    def __init__(self):
        super().__init__()
        
        # Modules additionnels
        self.animation_controller = AnimationController()
        self.stable_animation_controller = StableAnimationController()
        self.config_manager = ConfigManager()
        
        # Propriétés de configuration
        self.text_color = (255, 255, 255)
        self.decoration_color = (255, 255, 255)
        self.show_decorations = True
        self.decoration_style = "lines"
        
        # Mode actuel
        self.current_mode = "text"  # "text" ou "animation"
        
    async def connect(self):
        """Connexion au masque avec initialisation"""
        try:
            success = await super().connect()
            if success:
                # Connecter aussi les contrôleurs d'animation
                self.animation_controller.client = self.client
                self.stable_animation_controller.client = self.client
                
                # Configuration initiale
                await self.set_brightness(80)
                await self.set_foreground_color(255, 255, 255)
                await self.set_background_color(0, 0, 0)
                
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def apply_config(self, config: dict):
        """Applique une configuration chargée"""
        try:
            # Paramètres d'affichage
            if "display" in config:
                display = config["display"]
                if "font_size" in display:
                    self.font_size = display["font_size"]
                if "auto_fit" in display:
                    self.auto_fit = display["auto_fit"]
                if "bold_text" in display:
                    self.bold_text = display["bold_text"]
            
            # Décorations
            if "decorations" in config:
                decorations = config["decorations"]
                if "show_decorations" in decorations:
                    self.show_decorations = decorations["show_decorations"]
                if "decoration_style" in decorations:
                    self.decoration_style = decorations["decoration_style"]
                if "decoration_color" in decorations:
                    color = decorations["decoration_color"]
                    self.decoration_color = (color["r"], color["g"], color["b"])
            
            # Couleur du texte
            if "text" in config:
                text = config["text"]
                if "text_color" in text:
                    color = text["text_color"]
                    self.text_color = (color["r"], color["g"], color["b"])
            
            # Animations
            if "animations" in config:
                animations = config["animations"]
                if "fps" in animations:
                    self.animation_controller.fps = animations["fps"]
                    self.animation_controller.frame_time = 1.0 / animations["fps"]
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur application config: {e}")
            return False
    
    def export_current_config(self, filename: str = None):
        """Exporte la configuration actuelle"""
        config = self.config_manager.get_default_config()
        
        # Mettre à jour avec les valeurs actuelles
        config["display"]["font_size"] = self.font_size
        config["display"]["auto_fit"] = self.auto_fit
        config["display"]["bold_text"] = self.bold_text
        
        config["decorations"]["show_decorations"] = self.show_decorations
        config["decorations"]["decoration_style"] = self.decoration_style
        config["decorations"]["decoration_color"] = {
            "r": self.decoration_color[0],
            "g": self.decoration_color[1],
            "b": self.decoration_color[2],
            "name": self.config_manager.get_color_name(self.decoration_color)
        }
        
        config["text"]["text_color"] = {
            "r": self.text_color[0],
            "g": self.text_color[1],
            "b": self.text_color[2],
            "name": self.config_manager.get_color_name(self.text_color)
        }
        
        config["animations"]["fps"] = self.animation_controller.fps
        
        return self.config_manager.save_config(config, filename)
    
    async def display_scrolling_text(self, text: str, mode: str = "scroll_right", speed: int = 50):
        """Affiche du texte défilant avec la configuration actuelle"""
        try:
            self.current_mode = "text"
            
            # Arrêter les animations en cours
            self.animation_controller.stop_animation()
            
            # Réinitialiser l'état d'upload
            self.reset_upload_state()
            
            # Configuration des couleurs
            await self.set_foreground_color(*self.text_color)
            await self.set_background_color(0, 0, 0)
            
            # Configuration du mode et vitesse
            await self.set_mode(mode)
            await self.set_scroll_speed(speed)
            
            # Génération du bitmap
            pixel_map = self.create_text_bitmap(text)
            
            # Ajouter les décorations si activées
            if self.show_decorations:
                pixel_map = self.add_decorative_lines(pixel_map)
            
            # Encodage
            bitmap = self.encode_bitmap_for_mask(pixel_map)
            color_array = self.encode_white_color_array_for_mask(len(pixel_map))
            
            print(f"📊 Image: {len(pixel_map)} colonnes, Bitmap: {len(bitmap)} bytes")
            
            # Upload
            await self.init_upload(bitmap, color_array)
            
            # Envoi des paquets
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                await self.wait_for_response("REOK", timeout=3.0)
            
            # Finalisation
            await self.finish_upload()
            await self.wait_for_response("DATCPOK", timeout=3.0)
            
            print("✅ Texte affiché avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur affichage texte: {e}")
            self.reset_upload_state()
    
    def add_decorative_lines(self, pixels):
        """Ajoute des lignes décoratives au bitmap"""
        if not self.show_decorations:
            return pixels
            
        decorated_pixels = []
        
        for x in range(len(pixels)):
            column = pixels[x].copy()
            
            if self.decoration_style == "lines":
                column[0] = 1
                column[1] = 1
                column[14] = 1
                column[15] = 1
                
            elif self.decoration_style == "dots":
                if x % 3 == 0:
                    column[0] = 1
                    column[1] = 1
                    column[14] = 1
                    column[15] = 1
                    
            elif self.decoration_style == "blocks":
                if (x // 4) % 2 == 0:
                    column[0] = 1
                    column[1] = 1
                    column[14] = 1
                    column[15] = 1
                    
            elif self.decoration_style == "waves":
                wave_top = int(1.5 + 0.5 * abs(((x % 20) - 10) / 10))
                wave_bottom = int(14.5 - 0.5 * abs(((x % 20) - 10) / 10))
                if wave_top < 16:
                    column[wave_top] = 1
                if wave_bottom >= 0:
                    column[wave_bottom] = 1
                    
            elif self.decoration_style == "tata_pattern":
                for y in [1, 14]:
                    column[y] = 1
                if x % 5 == 0:
                    for y in [0, 15]:
                        column[y] = 1
            
            decorated_pixels.append(column)
            
        return decorated_pixels
    
    async def play_animation(self, animation_name: str, duration: float = 10.0):
        """Joue une animation stable"""
        try:
            self.current_mode = "animation"
            
            # Utiliser le contrôleur stable pour éviter les déconnexions
            self.stable_animation_controller.client = self.client
            
            # Jouer l'animation stable
            await self.stable_animation_controller.play_simple_animation(animation_name, duration)
            
        except Exception as e:
            print(f"❌ Erreur animation: {e}")
    
    def set_color(self, color_name: str):
        """Définit la couleur du texte"""
        rgb = self.config_manager.rgb_from_name(color_name)
        self.text_color = rgb
        return True
    
    def set_decoration_style(self, style: str):
        """Définit le style de décoration"""
        valid_styles = ["lines", "dots", "blocks", "waves", "tata_pattern", "none"]
        if style in valid_styles:
            self.decoration_style = style
            self.show_decorations = (style != "none")
            return True
        return False
    
    def get_status_summary(self):
        """Retourne un résumé de l'état actuel"""
        return {
            "mode": self.current_mode,
            "font_size": f"{self.font_size}px ({'AUTO' if self.auto_fit else 'FIXE'})",
            "bold": "OUI" if self.bold_text else "NON",
            "decorations": self.decoration_style.upper() if self.show_decorations else "AUCUNE",
            "color": self.config_manager.get_color_name(self.text_color),
            "connected": self.client is not None and self.client.is_connected if self.client else False
        }


class MaskInterface:
    """Interface utilisateur pour le contrôleur unifié"""
    
    def __init__(self):
        self.controller = UnifiedMaskController()
        self.command_queue = Queue()
        self.running = True
        self.connected = False
        
    async def connect_mask(self):
        """Connexion initiale au masque"""
        try:
            print("🔄 Connexion au masque...")
            self.connected = await self.controller.connect()
            if self.connected:
                print("✅ Masque connecté!")
            else:
                print("❌ Échec de la connexion")
            return self.connected
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def clear_screen(self):
        """Efface l'écran"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_interface(self, current_mode="scroll_right", current_speed=50, last_text=""):
        """Affiche l'interface utilisateur"""
        self.clear_screen()
        
        print("🚀 MASQUE LED v2.0 - Interface Unifiée")
        print("=" * 60)
        
        # État actuel
        status = self.controller.get_status_summary()
        print("📊 ÉTAT ACTUEL:")
        print(f"   🔗 Connecté: {'OUI' if status['connected'] else 'NON'}")
        print(f"   🎭 Mode: {status['mode'].upper()}")
        print(f"   🔤 Police: {status['font_size']}")
        print(f"   💪 Gras: {status['bold']}")
        print(f"   🎨 Décorations: {status['decorations']}")
        print(f"   🌈 Couleur: {status['color']}")
        print(f"   🎬 Défilement: {current_mode}")
        print(f"   ⚡ Vitesse: {current_speed}")
        if last_text:
            print(f"   📱 Dernier texte: '{last_text}'")
        print()
        
        # Commandes disponibles
        print("💡 COMMANDES DISPONIBLES:")
        print("   📝 TEXTE:")
        print("      [texte]        - Afficher le texte")
        print("      speed:X        - Vitesse (0-255)")
        print("      mode:X         - Mode (scroll_left/scroll_right/blink/steady)")
        print("      size:X         - Taille police (6-32px)")
        print("      auto:on/off    - Auto-ajustement")
        print("      bold:on/off    - Texte gras")
        print("      color:X        - Couleur (red/green/blue/etc)")
        print("      deco:X         - Décorations (lines/dots/blocks/waves/tata_pattern/none)")
        print()
        print("   🎬 ANIMATIONS:")
        print("      anim:pulse     - Animation pulsation")
        print("      anim:wave      - Animation vague")
        print("      anim:fire      - Animation feu")
        print("      anim:rain      - Animation pluie")
        print("      anim:matrix    - Animation Matrix")
        print("      stop           - Arrêter animation")
        print()
        print("   ⚙️ CONFIGURATION:")
        print("      export         - Exporter config")
        print("      export:nom     - Exporter avec nom")
        print("      import:nom     - Importer config")
        print("      configs        - Lister configs")
        print("      profile:nom    - Créer profil")
        print("      profiles       - Lister profils")
        print()
        print("   📊 info           - Rafraîchir interface")
        print("   🚪 quit           - Quitter")
        print()
        print("🌈 COULEURS: red, green, blue, yellow, white, cyan, magenta, orange, violet, rose")
        print("=" * 60)
    
    def input_thread(self):
        """Thread pour la saisie utilisateur"""
        current_mode = "scroll_right"
        current_speed = 50
        last_text = ""
        
        self.display_interface(current_mode, current_speed)
        
        while self.running:
            try:
                user_input = input(f"\n💬 Commande: ").strip()
                
                if not user_input:
                    self.display_interface(current_mode, current_speed, last_text)
                    continue
                
                # Analyser la commande
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.running = False
                    self.command_queue.put(('quit', None))
                    break
                
                elif user_input.startswith('speed:'):
                    try:
                        new_speed = int(user_input.split(':')[1])
                        current_speed = max(0, min(255, new_speed))
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Vitesse: {current_speed}")
                        if last_text:
                            self.command_queue.put(('text', (last_text, current_mode, current_speed)))
                    except ValueError:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Format: speed:80")
                    continue
                
                elif user_input.startswith('mode:'):
                    new_mode = user_input.split(':')[1].strip()
                    if new_mode in ['scroll_left', 'scroll_right', 'blink', 'steady']:
                        current_mode = new_mode
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Mode: {current_mode}")
                        if last_text:
                            self.command_queue.put(('text', (last_text, current_mode, current_speed)))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Modes: scroll_left/scroll_right/blink/steady")
                    continue
                
                elif user_input.startswith('anim:'):
                    anim_name = user_input.split(':')[1].strip()
                    self.command_queue.put(('animation', anim_name))
                    self.display_interface(current_mode, current_speed, last_text)
                    print(f"🎬 Lancement animation: {anim_name}")
                    continue
                
                elif user_input == 'stop':
                    self.command_queue.put(('stop_animation', None))
                    self.display_interface(current_mode, current_speed, last_text)
                    print("⏹️ Arrêt des animations")
                    continue
                
                # Décorations (ex: deco:tata_pattern)
                elif user_input.startswith('deco:'):
                    style = user_input.split(':', 1)[1].strip()
                    if self.controller.set_decoration_style(style):
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Décorations: {style}")
                        # Ré-appliquer sur le dernier texte si présent
                        if last_text:
                            self.command_queue.put(('text', (last_text, current_mode, current_speed)))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Style invalide. Valeurs: lines/dots/blocks/waves/tata_pattern/none")
                    continue

                # ... Autres commandes (config, export, etc.) ...
                
                else:
                    # Texte à afficher
                    last_text = user_input
                    self.command_queue.put(('text', (user_input, current_mode, current_speed)))
                    self.display_interface(current_mode, current_speed, last_text)
                    print(f"📤 Envoi: '{user_input}'")
                
            except (KeyboardInterrupt, EOFError):
                self.running = False
                self.command_queue.put(('quit', None))
                break
    
    async def main_loop(self):
        """Boucle principale"""
        if not await self.connect_mask():
            return
        
        # Démarrer le thread d'interface
        input_thread = threading.Thread(target=self.input_thread, daemon=True)
        input_thread.start()
        
        while self.running:
            try:
                if not self.command_queue.empty():
                    command, data = self.command_queue.get_nowait()
                    
                    if command == 'quit':
                        break
                    elif command == 'text':
                        text, mode, speed = data
                        await self.controller.display_scrolling_text(text, mode, speed)
                    elif command == 'animation':
                        await self.controller.play_animation(data, duration=10.0)
                    elif command == 'stop_animation':
                        self.controller.animation_controller.stop_animation()
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                await asyncio.sleep(1)
        
        try:
            await self.controller.disconnect()
            print("\n👋 Déconnecté. Au revoir!")
        except:
            pass


async def main():
    """Point d'entrée principal"""
    interface = MaskInterface()
    try:
        await interface.main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
