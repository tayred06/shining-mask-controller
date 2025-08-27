#!/usr/bin/env python3
"""
Script avec lignes décoratives au-dessus et en-dessous du texte
Ajoute des effets visuels pour encadrer le texte
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class DecorativeMaskController(ScrollingMaskController):
    """Contrôleur avec lignes décoratives"""
    
    def __init__(self):
        super().__init__()
        self.font_size = 14
        self.decoration_style = "lines"  # "lines", "dots", "blocks", "waves"
        self.show_decorations = True
    
    def set_font_size(self, size):
        """Définit la taille de la police"""
        self.font_size = max(6, min(16, size))  # Limité à 16 pour laisser place aux décorations
        
    def set_decoration_style(self, style):
        """Définit le style de décoration"""
        if style in ["lines", "dots", "blocks", "waves", "none"]:
            self.decoration_style = style
            self.show_decorations = (style != "none")
    
    def add_decorative_lines(self, pixels, text_width):
        """Ajoute des lignes décoratives au bitmap"""
        if not self.show_decorations:
            return pixels
            
        height = 16
        decorated_pixels = []
        
        for x in range(len(pixels)):
            column = pixels[x].copy()
            
            if self.decoration_style == "lines":
                # Lignes pleines en haut et en bas
                column[0] = 1  # Ligne du haut
                column[1] = 1  # Double ligne
                column[14] = 1  # Ligne du bas
                column[15] = 1  # Double ligne
                
            elif self.decoration_style == "dots":
                # Points réguliers
                if x % 3 == 0:  # Un point tous les 3 pixels
                    column[0] = 1
                    column[1] = 1
                    column[14] = 1
                    column[15] = 1
                    
            elif self.decoration_style == "blocks":
                # Blocs alternés
                if (x // 4) % 2 == 0:  # Blocs de 4 pixels
                    column[0] = 1
                    column[1] = 1
                    column[14] = 1
                    column[15] = 1
                    
            elif self.decoration_style == "waves":
                # Effet de vague
                wave_top = int(1.5 + 0.5 * abs(((x % 20) - 10) / 10))  # Vague en haut
                wave_bottom = int(14.5 - 0.5 * abs(((x % 20) - 10) / 10))  # Vague en bas
                column[wave_top] = 1
                column[wave_bottom] = 1
            
            decorated_pixels.append(column)
            
        return decorated_pixels
    
    def get_text_image(self, text, width_multiplier=1.5):
        """
        Version avec lignes décoratives
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
                    font = ImageFont.truetype(font_path, self.font_size)
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
        
        # Zone réservée pour le texte (lignes 2-13 si décorations activées)
        if self.show_decorations:
            text_area_height = 12  # 16 - 4 lignes pour décorations
            text_y_start = 2
        else:
            text_area_height = 16
            text_y_start = 0
        
        # Ajustement vertical pour centrer dans la zone disponible
        text_bbox = draw.textbbox((0, 0), text, font=font)
        actual_height = text_bbox[3] - text_bbox[1]
        text_top = text_bbox[1]
        
        # Centrage dans la zone de texte disponible
        y_offset = text_y_start + (text_area_height - actual_height) // 2 - text_top
        x_offset = (total_width - text_width) // 2
        
        draw.text((x_offset, y_offset), text, fill=255, font=font)
        
        # Conversion en bitmap binaire par colonnes
        pixels = []
        for x in range(total_width):
            column = []
            for y in range(16):
                pixel = img.getpixel((x, y))
                column.append(1 if pixel > 128 else 0)
            pixels.append(column)
        
        # Ajouter les décorations
        decorated_pixels = self.add_decorative_lines(pixels, text_width)
        
        return decorated_pixels

class DecorativeTextDisplay:
    def __init__(self):
        self.mask = DecorativeMaskController()
        self.text_queue = Queue()
        self.running = True
        self.connected = False
        
    async def connect_mask(self):
        """Connexion initiale au masque"""
        try:
            print("🔄 Connexion au masque...")
            await self.mask.connect()
            await self.mask.set_brightness(80)
            await self.mask.set_background_color(0, 0, 0)
            await self.mask.set_foreground_color(255, 255, 255)
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
            deco_info = f"({self.mask.decoration_style})" if self.mask.show_decorations else "(sans déco)"
            print(f"📱 Affichage: '{text}' {deco_info}")
            await self.mask.set_scrolling_text(text, mode, speed)
            print("✅ Texte mis à jour!")
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
    
    def input_thread(self):
        """Thread pour la saisie utilisateur avec décorations"""
        print("\n🎨 MASQUE LED - Affichage avec décorations")
        print("=" * 55)
        print("📝 Tapez votre texte et appuyez sur Entrée")
        print("🎨 Des lignes décoratives encadrent le texte")
        print("💡 Commandes spéciales:")
        print("   'quit' ou 'exit' - Quitter")
        print("   'speed:X' - Changer vitesse (ex: speed:80)")
        print("   'mode:X' - Changer mode (scroll_left/scroll_right/blink/steady)")
        print("   'size:X' - Changer taille (6-16px, ex: size:12)")
        print("   'deco:X' - Style déco (lines/dots/blocks/waves/none)")
        print("   'info' - Afficher paramètres actuels")
        print("=" * 55)
        print("🎨 Styles de décoration disponibles:")
        print("   lines - Lignes pleines en haut et bas")
        print("   dots - Points réguliers")
        print("   blocks - Blocs alternés")
        print("   waves - Effet de vague")
        print("   none - Pas de décoration")
        print("=" * 55)
        
        current_mode = "scroll_right"
        current_speed = 50
        
        while self.running:
            try:
                deco_display = self.mask.decoration_style if self.mask.show_decorations else "none"
                user_input = input(f"\n💬 Texte ({self.mask.font_size}px, {deco_display}): ").strip()
                
                if not user_input:
                    continue
                    
                # Commandes spéciales
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.running = False
                    self.text_queue.put(('quit', None, None))
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
                        print(f"🔤 Taille changée: {old_size}px → {self.mask.font_size}px")
                        if new_size > 16:
                            print("⚠️  Taille limitée à 16px pour laisser place aux décorations")
                        continue
                    except ValueError:
                        print("❌ Format de taille invalide (ex: size:12)")
                        continue
                
                elif user_input.startswith('deco:'):
                    new_style = user_input.split(':')[1].strip()
                    old_style = self.mask.decoration_style if self.mask.show_decorations else "none"
                    self.mask.set_decoration_style(new_style)
                    new_display = self.mask.decoration_style if self.mask.show_decorations else "none"
                    print(f"🎨 Style de décoration changé: {old_style} → {new_display}")
                    continue
                
                elif user_input.lower() == 'info':
                    print(f"📊 Paramètres actuels:")
                    print(f"   🔤 Taille police: {self.mask.font_size}px")
                    print(f"   🎨 Décoration: {self.mask.decoration_style if self.mask.show_decorations else 'none'}")
                    print(f"   🎬 Mode: {current_mode}")
                    print(f"   ⚡ Vitesse: {current_speed}")
                    continue
                
                # Texte normal à afficher
                self.text_queue.put((user_input, current_mode, current_speed))
                
            except KeyboardInterrupt:
                self.running = False
                self.text_queue.put(('quit', None, None))
                break
            except EOFError:
                self.running = False
                self.text_queue.put(('quit', None, None))
                break
    
    async def main_loop(self):
        """Boucle principale pour traiter les textes"""
        if not await self.connect_mask():
            return
        
        input_thread = threading.Thread(target=self.input_thread, daemon=True)
        input_thread.start()
        
        while self.running:
            try:
                if not self.text_queue.empty():
                    text, mode, speed = self.text_queue.get_nowait()
                    
                    if text == 'quit':
                        break
                    
                    await self.display_text(text, mode, speed)
                
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Erreur dans la boucle principale: {e}")
                await asyncio.sleep(1)
        
        try:
            await self.mask.disconnect()
            print("\n👋 Déconnecté du masque. Au revoir!")
        except:
            pass

async def main():
    """Point d'entrée principal"""
    display = DecorativeTextDisplay()
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
