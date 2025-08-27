#!/usr/bin/env python3
"""
Script avec contrôle de la taille de police pour le masque LED
Permet de changer la taille du texte affiché
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class CustomFontMaskController(ScrollingMaskController):
    """Extension du contrôleur avec support de tailles de police personnalisées"""
    
    def __init__(self):
        super().__init__()
        self.font_size = 14  # Taille par défaut
    
    def set_font_size(self, size):
        """Définit la taille de la police"""
        self.font_size = max(6, min(32, size))  # Limiter entre 6 et 32 pixels
        
    def get_text_image(self, text, width_multiplier=1.5):
        """
        Version modifiée avec taille de police personnalisable
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "arial.ttf"  # Windows
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, self.font_size)  # Utilise la taille personnalisée
                    break
                except:
                    continue
                    
            if font is None:
                font = ImageFont.load_default()
                
        except:
            from PIL import ImageFont
            font = ImageFont.load_default()

        # Calcul de la largeur du texte
        dummy_img = Image.new('L', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Pour le défilement, on crée une image plus large
        total_width = int(text_width * width_multiplier)
        
        # Création de l'image 16 pixels de hauteur
        img = Image.new('L', (total_width, 16), 0)
        draw = ImageDraw.Draw(img)
        
        # Ajustement vertical amélioré pour éviter la coupure
        # On utilise la bbox complète pour un meilleur alignement
        text_bbox = draw.textbbox((0, 0), text, font=font)
        actual_height = text_bbox[3] - text_bbox[1]
        text_top = text_bbox[1]  # Décalage du haut
        
        # Calculer la position verticale pour centrer le texte visible
        if actual_height <= 16:
            # Texte normal, centrage standard
            y_offset = (16 - actual_height) // 2 - text_top
        else:
            # Texte trop grand, on privilégie la partie haute (plus lisible)
            y_offset = -text_top + 1  # Petit décalage pour éviter la coupure du haut
        
        x_offset = (total_width - text_width) // 2
        draw.text((x_offset, y_offset), text, fill=255, font=font)
        
        # Conversion en bitmap binaire par colonnes (identique à l'original)
        pixels = []
        for x in range(total_width):
            column = []
            for y in range(16):
                pixel = img.getpixel((x, y))
                column.append(1 if pixel > 128 else 0)
            pixels.append(column)
        
        return pixels

class LiveTextDisplayWithFont:
    def __init__(self):
        self.mask = CustomFontMaskController()
        self.text_queue = Queue()
        self.running = True
        self.connected = False
        
    async def connect_mask(self):
        """Connexion initiale au masque"""
        try:
            print("🔄 Connexion au masque...")
            await self.mask.connect()
            await self.mask.set_brightness(80)
            await self.mask.set_background_color(0, 0, 0)  # Fond noir
            await self.mask.set_foreground_color(255, 255, 255)  # Texte blanc
            self.connected = True
            print("✅ Masque connecté et configuré!")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def display_text(self, text, mode="scroll_right", speed=50):
        """Affiche le texte sur le masque"""
        if not self.connected:
            return
            
        try:
            print(f"📱 Affichage: '{text}' (taille: {self.mask.font_size}px)")
            await self.mask.set_scrolling_text(text, mode, speed)
            print("✅ Texte mis à jour!")
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
    
    def input_thread(self):
        """Thread pour la saisie utilisateur avec support de taille de police"""
        print("\n🎮 MASQUE LED - Affichage avec contrôle de police")
        print("=" * 55)
        print("📝 Tapez votre texte et appuyez sur Entrée")
        print("🔄 Le texte s'affichera immédiatement sur le masque")
        print("💡 Commandes spéciales:")
        print("   'quit' ou 'exit' - Quitter")
        print("   'speed:X' - Changer vitesse (ex: speed:80)")
        print("   'mode:X' - Changer mode (scroll_left/scroll_right/blink/steady)")
        print("   'size:X' - Changer taille police (ex: size:20)")
        print("   'info' - Afficher paramètres actuels")
        print("=" * 55)
        
        current_mode = "scroll_right"
        current_speed = 50
        
        while self.running:
            try:
                user_input = input(f"\n💬 Texte (police {self.mask.font_size}px): ").strip()
                
                if not user_input:
                    continue
                    
                # Commandes spéciales
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.running = False
                    self.text_queue.put(('quit', None, None, None))
                    break
                    
                elif user_input.startswith('speed:'):
                    try:
                        new_speed = int(user_input.split(':')[1])
                        current_speed = max(0, min(255, new_speed))
                        print(f"⚡ Vitesse changée: {current_speed}")
                        continue
                    except ValueError:
                        print("❌ Format de vitesse invalide (ex: speed:80)")
                        continue
                        
                elif user_input.startswith('mode:'):
                    new_mode = user_input.split(':')[1].strip()
                    if new_mode in ['scroll_left', 'scroll_right', 'blink', 'steady']:
                        current_mode = new_mode
                        print(f"🎬 Mode changé: {current_mode}")
                        continue
                    else:
                        print("❌ Mode invalide. Utilisez: scroll_left/scroll_right/blink/steady")
                        continue
                
                elif user_input.startswith('size:'):
                    try:
                        new_size = int(user_input.split(':')[1])
                        old_size = self.mask.font_size
                        self.mask.set_font_size(new_size)
                        print(f"🔤 Taille de police changée: {old_size}px → {self.mask.font_size}px")
                        if new_size < 6:
                            print("⚠️  Taille minimale: 6px")
                        elif new_size > 32:
                            print("⚠️  Taille maximale: 32px")
                        continue
                    except ValueError:
                        print("❌ Format de taille invalide (ex: size:18)")
                        continue
                
                elif user_input.lower() == 'info':
                    print(f"📊 Paramètres actuels:")
                    print(f"   🔤 Taille police: {self.mask.font_size}px")
                    print(f"   🎬 Mode: {current_mode}")
                    print(f"   ⚡ Vitesse: {current_speed}")
                    continue
                
                # Texte normal à afficher
                self.text_queue.put((user_input, current_mode, current_speed, self.mask.font_size))
                
            except KeyboardInterrupt:
                self.running = False
                self.text_queue.put(('quit', None, None, None))
                break
            except EOFError:
                self.running = False
                self.text_queue.put(('quit', None, None, None))
                break
    
    async def main_loop(self):
        """Boucle principale pour traiter les textes"""
        # Connexion au masque
        if not await self.connect_mask():
            return
        
        # Démarrer le thread de saisie
        input_thread = threading.Thread(target=self.input_thread, daemon=True)
        input_thread.start()
        
        # Boucle de traitement des textes
        while self.running:
            try:
                # Vérifier s'il y a du nouveau texte (non-bloquant)
                if not self.text_queue.empty():
                    result = self.text_queue.get_nowait()
                    
                    if len(result) == 4:
                        text, mode, speed, font_size = result
                    else:
                        text, mode, speed = result
                        font_size = None
                    
                    if text == 'quit':
                        break
                    
                    await self.display_text(text, mode, speed)
                
                # Petite pause pour éviter la surcharge CPU
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Erreur dans la boucle principale: {e}")
                await asyncio.sleep(1)
        
        # Nettoyage
        try:
            await self.mask.disconnect()
            print("\n👋 Déconnecté du masque. Au revoir!")
        except:
            pass

async def main():
    """Point d'entrée principal"""
    display = LiveTextDisplayWithFont()
    try:
        await display.main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
