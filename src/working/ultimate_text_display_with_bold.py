#!/usr/bin/env python3
"""
Script complet avec auto-ajustement, décorations ET texte gras
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class CompleteMaskController(ScrollingMaskController):
    """Contrôleur complet avec toutes les fonctionnalités incluant les couleurs"""
    
    def __init__(self):
        super().__init__()
        
        # Nouvelles propriétés de couleur
        self.text_color = (255, 255, 255)  # Blanc par défaut
        self.decoration_color = (255, 255, 255)  # Blanc par défaut
        
        # Propriétés existantes
        self.font_size = 12
        self.auto_fit = True
        self.show_decorations = True
        self.decoration_style = "lines"
        self.bold_text = False
    
    def reset_upload_state(self):
        """Réinitialise complètement l'état d'upload"""
        self.upload_running = False
        if hasattr(self, 'upload_in_progress'):
            self.upload_in_progress = False
        if hasattr(self, '_upload_task') and self._upload_task:
            self._upload_task.cancel()
            self._upload_task = None
        if hasattr(self, 'current_upload'):
            self.current_upload = None
        print("🔄 État d'upload réinitialisé")
    
    async def set_scrolling_text(self, text, scroll_mode='scroll_left', speed=50, width_multiplier=1.2):
        """
        Version avec couleurs personnalisées compatible mask-go
        """
        print(f"Affichage défilant: '{text}' (mode: {scroll_mode}, vitesse: {speed})")
        
        try:
            # Réinitialisation complète de l'état d'upload
            self.reset_upload_state()
            
            # 1. Configuration des couleurs selon le protocole mask-go
            await self.set_text_front_color(self.text_color)
            await self.set_text_background_color((0, 0, 0))  # Fond noir
            
            # 2. Configuration du mode et de la vitesse
            await self.set_mode(scroll_mode)
            await asyncio.sleep(0.3)
            await self.set_scroll_speed(speed)
            await asyncio.sleep(0.3)  # Attente avant upload pour éviter saturation
            
            # 3. Génération de l'image avec espace pour le défilement
            pixel_map = self.get_text_image(text, width_multiplier)
            
            # 4. Encodage du bitmap
            bitmap = self.encode_bitmap_for_mask(pixel_map)
            
            # 5. Génération des couleurs (blanc pour compatibilité avec mask-go)
            color_array = self.encode_white_color_array_for_mask(len(pixel_map))
            
            print(f"Image: {len(pixel_map)} colonnes, Bitmap: {len(bitmap)} bytes")
            
            # 6. Upload
            await self.init_upload(bitmap, color_array)
            
            # 7. Envoi des paquets avec attente de confirmation
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                await self.wait_for_response("REOK", timeout=3.0)
                
            # 8. Finalisation
            await self.finish_upload()
            await self.wait_for_response("DATCPOK", timeout=3.0)
            
            print("✅ Texte défilant configuré avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur upload: {e}")
            # Réinitialisation complète en cas d'erreur
            self.reset_upload_state()
            import traceback
            traceback.print_exc()
    
    async def set_text_front_color(self, rgb_color):
        """Configure la couleur de premier plan selon le protocole mask-go (commande FC)"""
        try:
            r, g, b = rgb_color
            command = f"FC".encode('utf-8')
            
            # Format: 06FC<enable> <RR> <GG> <BB>
            data = bytearray([6])  # Longueur
            data.extend(command)
            data.append(1)  # Enable = 1
            data.append(r)
            data.append(g) 
            data.append(b)
            
            await self.send_command(data)
            print(f"🎨 Couleur avant-plan configurée: RGB({r}, {g}, {b})")
            
        except Exception as e:
            print(f"❌ Erreur config couleur avant-plan: {e}")
    
    async def set_text_background_color(self, rgb_color):
        """Configure la couleur d'arrière-plan selon le protocole mask-go (commande BG)"""
        try:
            r, g, b = rgb_color
            command = f"BG".encode('utf-8')
            
            # Format: 06BG<enable> <RR> <GG> <BB>
            data = bytearray([6])  # Longueur
            data.extend(command)
            data.append(1)  # Enable = 1
            data.append(r)
            data.append(g)
            data.append(b)
            
            await self.send_command(data)
            print(f"🌑 Couleur arrière-plan configurée: RGB({r}, {g}, {b})")
            
        except Exception as e:
            print(f"❌ Erreur config couleur arrière-plan: {e}")
    
    def encode_white_color_array_for_mask(self, columns):
        """Génère un tableau de couleurs blanches selon mask-go"""
        results = bytearray()
        for i in range(columns):
            results.extend([0xFF, 0xFF, 0xFF])  # RGB blanc pour chaque colonne
        return bytes(results)
    
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
        if style in ["lines", "dots", "blocks", "waves", "blocks_pattern", "tata_pattern", "tata_line_pattern", "none"]:
            self.decoration_style = style
            self.show_decorations = (style != "none")
    
    def set_bold(self, enabled):
        """Active/désactive le texte en gras"""
        self.bold_text = enabled
    
    def set_decoration_color(self, color_name):
        """Définit la couleur des décorations par nom"""
        colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 165, 0),
            "magenta": (255, 0, 255),
            "cyan": (0, 255, 255),
            "orange": (255, 165, 0),
            "violet": (128, 0, 128),
            "rose": (255, 192, 203)
        }
        
        if color_name.lower() in colors:
            self.decoration_color = colors[color_name.lower()]
            return True
        return False
    
    def set_text_color(self, color_name):
        """Définit la couleur du texte par nom"""
        colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 165, 0),
            "magenta": (255, 0, 255),
            "cyan": (0, 255, 255),
            "orange": (255, 165, 0),
            "violet": (128, 0, 128),
            "rose": (255, 192, 203)
        }
        
        if color_name.lower() in colors:
            self.text_color = colors[color_name.lower()]
            return True
        return False
    
    def set_text_color_by_rgb(self, rgb):
        """Définit la couleur du texte par RGB"""
        self.text_color = rgb
        return True
    
    def get_color_name(self, rgb):
        """Retourne le nom de la couleur à partir du RGB"""
        color_names = {
            (255, 255, 255): "BLANC",
            (255, 0, 0): "ROUGE",
            (0, 255, 0): "VERT", 
            (0, 0, 255): "BLEU",
            (255, 165, 0): "JAUNE",
            (255, 0, 255): "MAGENTA",
            (0, 255, 255): "CYAN",
            (255, 165, 0): "ORANGE",
            (128, 0, 128): "VIOLET",
            (255, 192, 203): "ROSE"
        }
        return color_names.get(rgb, f"RGB({rgb[0]},{rgb[1]},{rgb[2]})")
    
    def export_config(self, filename=None):
        """Exporte la configuration actuelle vers un fichier JSON"""
        import json
        from datetime import datetime
        
        config = {
            "metadata": {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "description": "Configuration du masque LED"
            },
            "display": {
                "font_size": self.font_size,
                "auto_fit": self.auto_fit,
                "bold_text": self.bold_text
            },
            "scrolling": {
                "default_mode": "scroll_right",
                "default_speed": 50
            },
            "decorations": {
                "show_decorations": self.show_decorations,
                "decoration_style": self.decoration_style,
                "decoration_color": {
                    "r": self.decoration_color[0],
                    "g": self.decoration_color[1], 
                    "b": self.decoration_color[2],
                    "name": self.get_color_name(self.decoration_color)
                }
            },
            "text": {
                "text_color": {
                    "r": self.text_color[0],
                    "g": self.text_color[1],
                    "b": self.text_color[2],
                    "name": self.get_color_name(self.text_color)
                }
            }
        }
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mask_config_{timestamp}.json"
        
        # Sauvegarder dans le dossier working
        config_path = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, config_path
        except Exception as e:
            return False, str(e)
    
    def import_config(self, filename):
        """Importe une configuration depuis un fichier JSON"""
        import json
        
        # Chercher le fichier dans le dossier working
        config_path = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(config_path):
            # Essayer le chemin absolu
            config_path = filename
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Restaurer les paramètres d'affichage
            if "display" in config:
                display = config["display"]
                if "font_size" in display:
                    self.set_font_size(display["font_size"])
                if "auto_fit" in display:
                    self.set_auto_fit(display["auto_fit"])
                if "bold_text" in display:
                    self.set_bold(display["bold_text"])
            
            # Restaurer les décorations
            if "decorations" in config:
                decorations = config["decorations"]
                if "decoration_style" in decorations:
                    self.set_decoration_style(decorations["decoration_style"])
                if "decoration_color" in decorations:
                    color = decorations["decoration_color"]
                    self.decoration_color = (color["r"], color["g"], color["b"])
            
            # Restaurer la couleur du texte
            if "text" in config:
                text = config["text"]
                if "text_color" in text:
                    color = text["text_color"]
                    self.text_color = (color["r"], color["g"], color["b"])
            
            return True, config.get("metadata", {}).get("description", "Configuration importée")
        except Exception as e:
            return False, str(e)
    
    def list_config_files(self):
        """Liste les fichiers de configuration disponibles"""
        config_dir = os.path.dirname(__file__)
        config_files = []
        
        for filename in os.listdir(config_dir):
            if filename.startswith("mask_config_") and filename.endswith(".json"):
                config_files.append(filename)
        
        return sorted(config_files, reverse=True)  # Plus récents en premier
    
    def find_optimal_font_size(self, text):
        """Trouve la taille de police optimale"""
        from PIL import Image, ImageDraw, ImageFont
        
        max_height = 12 if self.show_decorations else 15
        max_size = 14 if self.show_decorations else self.font_size
        
        for test_size in range(max_size, 6, -1):
            try:
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
        """Génère uniquement le bitmap (sans image RGB) pour le masque"""
        # Imports sécurisés
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("❌ PIL manquant!")
            return []

        try:
            # Charger la police
            font_paths = [
                "ScienceGothic.ttf",
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "arial.ttf"
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
                
        except Exception as e:
            print(f"⚠️ Erreur police: {e}")
            font = ImageFont.load_default()

        # 1. Forcer majuscules
        text = text.upper()

        # 2. Calculer la largeur avec espacement
        char_spacing = 2  # Espace entre les lettres (en pixels)
        
        # Initialiser dummy_draw pour les calculs
        dummy_img = Image.new('L', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        total_text_width = 0
        char_widths = []
        
        for char in text:
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            w = bbox[2] - bbox[0]
            char_widths.append(w)
            total_text_width += w + char_spacing
            
        if char_widths:
            total_text_width -= char_spacing # Retirer le dernier espace
            
        text_height = 12 # Hauteur max estimée
        
        # Largeur totale de l'image (avec marge pour défilement)
        total_width = int(total_text_width * width_multiplier)
        if total_width < 32: total_width = 32 # Minimum vital
        
        # Création de l'image en noir et blanc pour bitmap
        img = Image.new('L', (total_width, 16), 0)  # Fond noir
        draw = ImageDraw.Draw(img)
        
        # Zone de texte selon les décorations
        if self.show_decorations:
            text_area_height = 12
            text_y_start = 2
        else:
            text_area_height = 16
            text_y_start = 0
        
        # Positionnement du texte (centré horizontalement dans l'image large)
        x_cursor = (total_width - total_text_width) // 2
        
        # Dessiner lettre par lettre avec espacement
        for i, char in enumerate(text):
            bbox = draw.textbbox((0, 0), char, font=font)
            char_h = bbox[3] - bbox[1]
            char_top = bbox[1]
            
            # Centrage vertical
            y_pos = text_y_start + (text_area_height - char_h) // 2 - char_top
            
            draw.text((x_cursor, y_pos), char, fill=255, font=font)
            
            # Effet gras par superposition si activé
            if self.bold_text:
                draw.text((x_cursor + 1, y_pos), char, fill=255, font=font)
                draw.text((x_cursor, y_pos + 1), char, fill=255, font=font)
                draw.text((x_cursor + 1, y_pos + 1), char, fill=255, font=font)
            
            x_cursor += char_widths[i] + char_spacing
        
        # Ajouter les décorations directement sur le bitmap
        if self.show_decorations:
            self.add_decorative_lines_to_bitmap(img, total_width)
        
        # Conversion directe en bitmap pour le masque
        pixels = []
        for x in range(total_width):
            column = []
            for y in range(16):
                pixel_value = img.getpixel((x, y))
                column.append(1 if pixel_value > 0 else 0)
            pixels.append(column)
        
        return pixels
    
    def add_decorative_lines_to_bitmap(self, img, width):
        """Ajoute des décorations directement sur le bitmap noir et blanc"""
        for x in range(width):
            if self.decoration_style == "lines":
                for y in [0, 1, 14, 15]:
                    img.putpixel((x, y), 255)
                    
            elif self.decoration_style == "dots":
                if x % 3 == 0:
                    for y in [0, 1, 14, 15]:
                        img.putpixel((x, y), 255)
                        
            elif self.decoration_style == "blocks":
                if (x // 4) % 2 == 0:
                    for y in [0, 1, 14, 15]:
                        img.putpixel((x, y), 255)
                        
            elif self.decoration_style == "waves":
                wave_top = int(1.5 + 0.5 * abs(((x % 20) - 10) / 10))
                wave_bottom = int(14.5 - 0.5 * abs(((x % 20) - 10) / 10))
                if 0 <= wave_top < 16:
                    img.putpixel((x, wave_top), 255)
                if 0 <= wave_bottom < 16:
                    img.putpixel((x, wave_bottom), 255)
                    
            elif self.decoration_style == "blocks_pattern":
                # Pattern en blocs comme dans BLOCKS_PATTERN_SUCCESS.md
                for y in range(16):  # Hauteur fixe du masque
                    if (x // 4) % 2 == 0 and (y // 2) % 2 == 0:
                        if img.getpixel((x, y)) == 0:  # Seulement sur fond noir
                            img.putpixel((x, y), 255)
                            
            elif self.decoration_style == "tata_pattern":
                for y in [1, 14]:
                    img.putpixel((x, y), 255)
                if x % 5 == 0:
                    for y in [0, 15]:
                        img.putpixel((x, y), 255)
                            
            elif self.decoration_style == "tata_line_pattern":
                # Pattern avec 10 points au début et à la fin de chaque ligne
                for y in [0, 15]:
                    should_light = False
                    
                    if x < 10:
                        # 10 premiers points (0-9): toujours allumés
                        should_light = True
                    elif x >= 54:
                        # 10 derniers points (54-63): toujours allumés
                        should_light = True
                    else:
                        # Zone milieu (10-53): motif répétitif de 16 pixels
                        middle_pos = (x - 10) % 16
                        
                        if middle_pos < 10:
                            # 10 points continus
                            should_light = True
                        elif middle_pos == 10 or middle_pos == 11:
                            # 2 espaces
                            should_light = False
                        elif middle_pos == 12 or middle_pos == 13:
                            # 2 points
                            should_light = True
                        elif middle_pos == 14 or middle_pos == 15:
                            # 2 espaces
                            should_light = False
                    
                    if should_light and img.getpixel((x, y)) == 0:
                        img.putpixel((x, y), 255)

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
        print("📊 ÉTAT ACTUEL:")
        auto_status = "AUTO" if self.mask.auto_fit else f"FIXE ({self.mask.font_size}px)"
        deco_status = self.mask.decoration_style.upper() if self.mask.show_decorations else "AUCUNE"
        bold_status = "OUI" if self.mask.bold_text else "NON"
        text_color_name = self.mask.get_color_name(self.mask.text_color)
        
        print(f"   🔤 Police: {auto_status}")
        print(f"   🎨 Décorations: {deco_status}")
        print(f"   💪 Texte gras: {bold_status}")
        print(f"   🌈 Couleur: {text_color_name}")
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
        print("   🎨 deco:X         - Décorations (lines/dots/blocks/waves/blocks_pattern/tata_pattern/tata_line_pattern/none)")
        print("   💪 bold:on/off    - Texte en gras")
        print("   🌈 color:X        - Couleur (red/green/blue/yellow/white/etc)")
        print("   💾 export         - Exporter la config actuelle")
        print("   💾 export:nom.json - Exporter avec nom personnalisé")
        print("   📥 import:nom.json - Importer une configuration")
        print("   📁 configs        - Lister les configs disponibles")
        print("   �📊 info           - Afficher cet état")
        print("   🚪 quit           - Quitter")
        print()
        print("🌈 COULEURS DISPONIBLES:")
        print("   red, green, blue, yellow, white, cyan, magenta, orange, violet, rose")
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
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    elif setting in ['off', 'false', '0']:
                        self.mask.set_auto_fit(False)
                        self.display_interface(current_mode, current_speed, last_text)
                        print("✅ Auto-ajustement désactivé")
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Utilisez 'auto:on' ou 'auto:off'")
                    continue
                
                elif user_input.startswith('deco:'):
                    new_style = user_input.split(':')[1].strip()
                    if new_style in ["lines", "dots", "blocks", "waves", "blocks_pattern", "tata_pattern", "tata_line_pattern", "none"]:
                        old_style = self.mask.decoration_style if self.mask.show_decorations else "none"
                        self.mask.set_decoration_style(new_style)
                        new_display = self.mask.decoration_style if self.mask.show_decorations else "none"
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Décoration changée: {old_style} → {new_display}")
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Style invalide (lines/dots/blocks/waves/blocks_pattern/tata_pattern/tata_line_pattern/none)")
                    continue
                
                elif user_input.startswith('bold:'):
                    setting = user_input.split(':')[1].strip().lower()
                    if setting in ['on', 'true', '1']:
                        self.mask.set_bold(True)
                        self.display_interface(current_mode, current_speed, last_text)
                        print("✅ Texte gras activé")
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    elif setting in ['off', 'false', '0']:
                        self.mask.set_bold(False)
                        self.display_interface(current_mode, current_speed, last_text)
                        print("✅ Texte gras désactivé")
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print("❌ Utilisez 'bold:on' ou 'bold:off'")
                    continue
                
                elif user_input.startswith('color:'):
                    color_name = user_input.split(':')[1].strip().lower()
                    old_color = self.mask.get_color_name(self.mask.text_color)
                    if self.mask.set_text_color(color_name):
                        new_color = self.mask.get_color_name(self.mask.text_color)
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"✅ Couleur changée: {old_color} → {new_color}")
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        self.display_interface(current_mode, current_speed, last_text)
                        print(f"❌ Couleur inconnue: {color_name}")
                        print("🌈 Couleurs disponibles: red, green, blue, yellow, white, cyan, magenta, orange, violet, rose")
                    continue
                
                elif user_input.lower() in ['info', 'status']:
                    self.display_interface(current_mode, current_speed, last_text)
                    print("📊 Interface rafraîchie!")
                    continue
                
                elif user_input.startswith('export:'):
                    filename = user_input.split(':', 1)[1].strip() if ':' in user_input else None
                    success, result = self.mask.export_config(filename)
                    self.display_interface(current_mode, current_speed, last_text)
                    if success:
                        print(f"✅ Configuration exportée: {result}")
                    else:
                        print(f"❌ Erreur d'export: {result}")
                    continue
                
                elif user_input == 'export':
                    success, result = self.mask.export_config()
                    self.display_interface(current_mode, current_speed, last_text)
                    if success:
                        print(f"✅ Configuration exportée: {result}")
                    else:
                        print(f"❌ Erreur d'export: {result}")
                    continue
                
                elif user_input.startswith('import:'):
                    filename = user_input.split(':', 1)[1].strip()
                    old_state = f"{self.mask.font_size}px, {self.mask.decoration_style}, {self.mask.get_color_name(self.mask.text_color)}"
                    success, result = self.mask.import_config(filename)
                    self.display_interface(current_mode, current_speed, last_text)
                    if success:
                        new_state = f"{self.mask.font_size}px, {self.mask.decoration_style}, {self.mask.get_color_name(self.mask.text_color)}"
                        print(f"✅ Configuration importée: {result}")
                        print(f"📋 Avant: {old_state}")
                        print(f"📋 Après: {new_state}")
                        if last_text:
                            self.text_queue.put((last_text, current_mode, current_speed))
                    else:
                        print(f"❌ Erreur d'import: {result}")
                    continue
                
                elif user_input == 'configs':
                    configs = self.mask.list_config_files()
                    self.display_interface(current_mode, current_speed, last_text)
                    print("📁 CONFIGURATIONS DISPONIBLES:")
                    if configs:
                        for i, config in enumerate(configs, 1):
                            print(f"   {i}. {config}")
                        print("\n💡 Utilisez 'import:nom_du_fichier.json' pour importer")
                    else:
                        print("   Aucune configuration sauvegardée")
                    print("💾 Utilisez 'export' ou 'export:nom.json' pour sauvegarder")
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
