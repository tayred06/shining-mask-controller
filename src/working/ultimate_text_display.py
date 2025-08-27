#!/usr/bin/env python3
"""
Script complet avec auto-ajustement ET décorations
Combine les fonctionnalités des deux scripts précédents
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.        # État actuel
        print("📊 ÉTAT ACTUEL:")
        auto_status = "AUTO" if self.mask.auto_fit else f"FIXE ({self.mask.font_size}px)"
        deco_status = self.mask.decoration_style.upper() if self.mask.show_decorations else "AUCUNE"
        bold_status = "OUI" if self.mask.bold_text else "NON"
        
        print(f"   🔤 Police: {auto_status}")
        print(f"   🎨 Décorations: {deco_status}")
        print(f"   💪 Texte gras: {bold_status}")
        print(f"   🎬 Mode: {current_mode}")
        print(f"   ⚡ Vitesse: {current_speed}")
        if last_text:
            print(f"   📱 Dernier texte: '{last_text}'")
        print()th.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class CompleteMaskController(ScrollingMaskController):
    """Contrôleur complet avec auto-ajustement et décorations"""
    
    def __init__(self):
        super().__init__()
        self.font_size = 14
        self.auto_fit = True
        self.decoration_style = "lines"
        self.show_decorations = True
        self.bold_text = False  # Nouvelle option pour texte en gras
    
    def set_font_size(self, size):
        """Définit la taille de la police"""
        if self.show_decorations:
            self.font_size = max(6, min(14, size))  # Limité pour les décorations
        else:
            self.font_size = max(6, min(32, size))
        
    def set_auto_fit(self, enabled):
        """Active/désactive l'auto-ajustement"""
        self.auto_fit = enabled
        
    def set_decoration_style(self, style):
        """Définit le style de décoration"""
        if style in ["lines", "dots", "blocks", "waves", "none"]:
            self.decoration_style = style
            self.show_decorations = (style != "none")
    
    def set_bold(self, enabled):
        """Active/désactive le texte en gras"""
        self.bold_text = enabled
    
    def find_optimal_font_size(self, text):
        """Trouve la taille de police optimale"""
        from PIL import Image, ImageDraw, ImageFont
        
        max_height = 12 if self.show_decorations else 15  # Laisser place aux décorations
        max_size = 14 if self.show_decorations else self.font_size
        
        for test_size in range(max_size, 6, -1):
            try:
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if self.bold_text else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "arial.ttf"
                ]
                
                font = None
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, test_size)
                        break
                    except:
                        continue
                        
                if font is None:
                    font = ImageFont.load_default()
                
                dummy_img = Image.new('L', (1, 1))
                dummy_draw = ImageDraw.Draw(dummy_img)
                bbox = dummy_draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                
                if text_height <= max_height:
                    return test_size
                    
            except Exception:
                continue
        
        return 8
    
    def add_decorative_lines(self, pixels, text_width):
        """Ajoute des lignes décoratives au bitmap"""
        if not self.show_decorations:
            return pixels
            
        height = 16
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
            
            decorated_pixels.append(column)
            
        return decorated_pixels
    
    def get_text_image(self, text, width_multiplier=1.5):
        """Version complète avec auto-ajustement, décorations et texte gras"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Déterminer la taille de police
            if self.auto_fit:
                optimal_size = self.find_optimal_font_size(text)
                actual_font_size = optimal_size
                if optimal_size != self.font_size:
                    print(f"🔧 Auto-ajustement: {self.font_size}px → {optimal_size}px")
            else:
                actual_font_size = self.font_size
            
            # Choix de la police avec support du gras
            font_paths = [
                "/System/Library/Fonts/Arial Bold.ttf" if self.bold_text else "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if self.bold_text else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "arialbd.ttf" if self.bold_text else "arial.ttf"
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, actual_font_size)
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
        
        total_width = int(text_width * width_multiplier)
        
        # Création de l'image
        img = Image.new('L', (total_width, 16), 0)
        draw = ImageDraw.Draw(img)
        
        # Zone de texte selon les décorations
        if self.show_decorations:
            text_area_height = 12
            text_y_start = 2
        else:
            text_area_height = 16
            text_y_start = 0
        
        # Positionnement du texte
        text_bbox = draw.textbbox((0, 0), text, font=font)
        actual_height = text_bbox[3] - text_bbox[1]
        text_top = text_bbox[1]
        
        y_offset = text_y_start + (text_area_height - actual_height) // 2 - text_top
        x_offset = (total_width - text_width) // 2
        
        # Dessiner le texte
        draw.text((x_offset, y_offset), text, fill=255, font=font)
        
        # Effet gras par superposition si activé
        if self.bold_text:
            # Superposer le texte légèrement décalé pour effet gras
            draw.text((x_offset + 1, y_offset), text, fill=255, font=font)
            # Optionnel: ajouter d'autres décalages pour plus d'épaisseur
            draw.text((x_offset, y_offset + 1), text, fill=255, font=font)
            draw.text((x_offset + 1, y_offset + 1), text, fill=255, font=font)
        
        # Conversion en bitmap
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

class UltimateTextDisplay:
    def __init__(self):
        self.mask = CompleteMaskController()
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
        """Affiche le texte sur le masque avec confirmation visuelle"""
        if not self.connected:
            return
            
        try:
            await self.mask.set_scrolling_text(text, mode, speed)
            print(f"✅ Texte affiché sur le masque!")
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
    
    def clear_screen(self):
        """Efface l'écran de manière compatible"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_interface(self, current_mode, current_speed, last_text=""):
        """Affiche l'interface utilisateur avec l'état actuel"""
        self.clear_screen()
        
        print("🚀 MASQUE LED - Interface Complète")
        print("=" * 60)
        
        # État actuel
        print("� ÉTAT ACTUEL:")
        auto_status = "AUTO" if self.mask.auto_fit else f"FIXE ({self.mask.font_size}px)"
        deco_status = self.mask.decoration_style.upper() if self.mask.show_decorations else "AUCUNE"
        
        print(f"   🔤 Police: {auto_status}")
        print(f"   🎨 Décorations: {deco_status}")
        print(f"   🎬 Mode: {current_mode}")
        print(f"   ⚡ Vitesse: {current_speed}")
        if last_text:
            print(f"   📱 Dernier texte: '{last_text}'")
        print()
        
        # Commandes disponibles
        print("💡 COMMANDES DISPONIBLES:")
        print("   📝 [texte]        - Afficher le texte")
        print("   ⚡ speed:X        - Changer vitesse (0-255)")
        print("   🎬 mode:X         - Mode (scroll_left/scroll_right/blink/steady)")
        print("   🔤 size:X         - Taille forcée (6-14px avec déco, 6-32px sans)")
        print("   🧠 auto:on/off    - Auto-ajustement de police")
        print("   🎨 deco:X         - Décorations (lines/dots/blocks/waves/none)")
        print("   📊 info           - Afficher cet état")
        print("   🚪 quit           - Quitter")
        print("=" * 60)
    
    def input_thread(self):
        """Thread pour la saisie utilisateur avec interface propre"""
        current_mode = "scroll_right"
        current_speed = 50
        last_text = ""
        
        # Affichage initial
        self.display_interface(current_mode, current_speed)
        
        while self.running:
            try:
                user_input = input(f"\n💬 Commande: ").strip()
                
                if not user_input:
                    self.display_interface(current_mode, current_speed, last_text)
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
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Vitesse changée: {current_speed}")
                        # Mettre à jour le masque avec le dernier texte si disponible
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                        continue
                    except ValueError:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Format invalide (ex: speed:80)")
                        continue
                        
                elif user_input.startswith('mode:'):
                    new_mode = user_input.split(':')[1].strip()
                    if new_mode in ['scroll_left', 'scroll_right', 'blink', 'steady']:
                        current_mode = new_mode
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Mode changé: {current_mode}")
                        # Mettre à jour le masque avec le dernier texte si disponible
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                        continue
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Mode invalide (scroll_left/scroll_right/blink/steady)")
                        continue
                
                elif user_input.startswith('size:'):
                    try:
                        new_size = int(user_input.split(':')[1])
                        old_size = self.mask.font_size
                        self.mask.set_font_size(new_size)
                        self.mask.set_auto_fit(False)
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Taille changée: {old_size}px → {self.mask.font_size}px (auto désactivé)")
                        # Mettre à jour le masque avec le dernier texte si disponible
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                        continue
                    except ValueError:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Format invalide (ex: size:12)")
                        continue
                
                elif user_input.startswith('auto:'):
                    setting = user_input.split(':')[1].strip().lower()
                    if setting in ['on', 'true', '1']:
                        self.mask.set_auto_fit(True)
                        self.display_interface(current_mode, current_speed, last_text)
                        print("✅ Auto-ajustement activé")
                        # Mettre à jour le masque avec le dernier texte si disponible
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    elif setting in ['off', 'false', '0']:
                        self.mask.set_auto_fit(False)
                        self.display_interface(current_mode, current_speed, last_text)
                        print("✅ Auto-ajustement désactivé")
                        # Mettre à jour le masque avec le dernier texte si disponible
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Utilisez 'auto:on' ou 'auto:off'")
                    continue
                
                elif user_input.startswith('deco:'):
                    new_style = user_input.split(':')[1].strip()
                    if new_style in ["lines", "dots", "blocks", "waves", "none"]:
                        old_style = self.mask.decoration_style if self.mask.show_decorations else "none"
                        self.mask.set_decoration_style(new_style)
                        new_display = self.mask.decoration_style if self.mask.show_decorations else "none"
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Décoration changée: {old_style} → {new_display}")
                        # Mettre à jour le masque avec le dernier texte si disponible
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Style invalide (lines/dots/blocks/waves/none)")
                    continue
                
                elif user_input.lower() in ['info', 'status']:
                    self.display_interface(current_mode, current_speed, last_text)
                    print("📊 Interface rafraîchie!")
                    continue
                
                # Texte normal à afficher
                else:
                    last_text = user_input
                    self.display_interface(current_mode, current_speed, last_text)
                    print(f"📤 Envoi du texte: '{user_input}'...")
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
        """Boucle principale"""
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
                print(f"❌ Erreur: {e}")
                await asyncio.sleep(1)
        
        try:
            await self.mask.disconnect()
            print("\n👋 Déconnecté du masque. Au revoir!")
        except:
            pass

async def main():
    """Point d'entrée principal"""
    display = UltimateTextDisplay()
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
