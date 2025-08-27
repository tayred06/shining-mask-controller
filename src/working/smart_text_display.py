#!/usr/bin/env python3
"""
Script avec auto-ajustement de la taille de police pour le masque LED
Adapte automatiquement la taille pour éviter la coupure
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class AutoFitMaskController(ScrollingMaskController):
    """Contrôleur avec ajustement automatique de la taille de police"""
    
    def __init__(self):
        super().__init__()
        self.font_size = 14  # Taille par défaut
        self.auto_fit = True  # Mode auto-ajustement
    
    def set_font_size(self, size):
        """Définit la taille de la police"""
        self.font_size = max(6, min(32, size))
        
    def set_auto_fit(self, enabled):
        """Active/désactive l'auto-ajustement"""
        self.auto_fit = enabled
        
    def find_optimal_font_size(self, text):
        """Trouve la taille de police optimale pour le texte"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Tester différentes tailles de police
        for test_size in range(self.font_size, 6, -1):  # Décrémenter depuis la taille actuelle
            try:
                # Charger la police
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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
                
                # Tester la taille
                dummy_img = Image.new('L', (1, 1))
                dummy_draw = ImageDraw.Draw(dummy_img)
                bbox = dummy_draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                
                # Si ça rentre dans 16 pixels avec un peu de marge
                if text_height <= 15:  # Laisser 1 pixel de marge
                    return test_size
                    
            except Exception:
                continue
        
        # Si rien ne fonctionne, retourner une taille très petite
        return 8
    
    def get_text_image(self, text, width_multiplier=1.5):
        """
        Version avec auto-ajustement de la taille de police
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Déterminer la taille de police à utiliser
            if self.auto_fit:
                optimal_size = self.find_optimal_font_size(text)
                actual_font_size = optimal_size
                print(f"🔧 Auto-ajustement: {self.font_size}px → {optimal_size}px")
            else:
                actual_font_size = self.font_size
            
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "arial.ttf"  # Windows
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
        
        # Pour le défilement, on crée une image plus large
        total_width = int(text_width * width_multiplier)
        
        # Création de l'image 16 pixels de hauteur
        img = Image.new('L', (total_width, 16), 0)
        draw = ImageDraw.Draw(img)
        
        # Alignement vertical optimisé
        text_bbox = draw.textbbox((0, 0), text, font=font)
        actual_height = text_bbox[3] - text_bbox[1]
        text_top = text_bbox[1]
        
        # Centrage vertical parfait
        y_offset = (16 - actual_height) // 2 - text_top
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
        
        return pixels

class SmartTextDisplay:
    def __init__(self):
        self.mask = AutoFitMaskController()
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
            auto_status = "AUTO" if self.mask.auto_fit else f"{self.mask.font_size}px"
            print(f"📱 Affichage: '{text}' (police: {auto_status})")
            await self.mask.set_scrolling_text(text, mode, speed)
            print("✅ Texte mis à jour!")
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
    
    def input_thread(self):
        """Thread pour la saisie utilisateur avec auto-ajustement"""
        print("\n🎮 MASQUE LED - Affichage intelligent")
        print("=" * 50)
        print("📝 Tapez votre texte et appuyez sur Entrée")
        print("🧠 La taille de police s'ajuste automatiquement")
        print("💡 Commandes spéciales:")
        print("   'quit' ou 'exit' - Quitter")
        print("   'speed:X' - Changer vitesse (ex: speed:80)")
        print("   'mode:X' - Changer mode (scroll_left/scroll_right/blink/steady)")
        print("   'size:X' - Forcer une taille (ex: size:20)")
        print("   'auto:on' - Activer auto-ajustement")
        print("   'auto:off' - Désactiver auto-ajustement")
        print("   'info' - Afficher paramètres actuels")
        print("=" * 50)
        
        current_mode = "scroll_right"
        current_speed = 50
        
        while self.running:
            try:
                auto_indicator = "AUTO" if self.mask.auto_fit else f"{self.mask.font_size}px"
                user_input = input(f"\n💬 Texte ({auto_indicator}): ").strip()
                
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
                        self.mask.set_font_size(new_size)
                        self.mask.set_auto_fit(False)  # Désactiver l'auto quand on force
                        print(f"🔤 Taille forcée: {self.mask.font_size}px (auto désactivé)")
                        continue
                    except ValueError:
                        print("❌ Format de taille invalide (ex: size:18)")
                        continue
                
                elif user_input.startswith('auto:'):
                    setting = user_input.split(':')[1].strip().lower()
                    if setting in ['on', 'true', '1']:
                        self.mask.set_auto_fit(True)
                        print("🧠 Auto-ajustement activé")
                    elif setting in ['off', 'false', '0']:
                        self.mask.set_auto_fit(False)
                        print("🔧 Auto-ajustement désactivé")
                    else:
                        print("❌ Utilisez 'auto:on' ou 'auto:off'")
                    continue
                
                elif user_input.lower() == 'info':
                    print(f"📊 Paramètres actuels:")
                    if self.mask.auto_fit:
                        print(f"   🧠 Auto-ajustement: ACTIVÉ (base: {self.mask.font_size}px)")
                    else:
                        print(f"   🔤 Taille fixe: {self.mask.font_size}px")
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
    display = SmartTextDisplay()
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
