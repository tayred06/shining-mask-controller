#!/usr/bin/env python3
"""
Version expérimentale avec couleurs séparées pour texte et décorations
Basée sur ultimate_text_display_with_bold.py qui fonctionne
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'working'))

from scrolling_text_controller import ScrollingMaskController

class ExperimentalColorController(ScrollingMaskController):
    """Contrôleur expérimental avec couleurs séparées pour texte et décorations"""
    
    def __init__(self):
        super().__init__()
        self.text_color = (255, 255, 255)
        self.decoration_color = (255, 255, 255)
        self.font_size = 12
        self.auto_fit = True
        self.show_decorations = True
        self.decoration_style = "lines"
        self.bold_text = False
        self.use_separated_colors = True  # Mode couleurs séparées
    
    async def set_scrolling_text(self, text):
        """Configure le texte avec couleurs séparées selon le mode actuel"""
        try:
            print(f"🧪 Affichage expérimental: '{text}' (mode: {self.scroll_mode}, vitesse: {self.scroll_speed})")
            
            # Réinitialisation de l'état d'upload avant chaque nouvelle opération
            if hasattr(self, 'upload_in_progress'):
                self.upload_in_progress = False
            if hasattr(self, '_upload_task') and self._upload_task:
                self._upload_task.cancel()
                self._upload_task = None
            
            if self.use_separated_colors:
                print("🎨 Mode couleurs séparées activé")
                
                # Configuration du mode
                print(f"Mode configuré: {self.scroll_mode}")
                await self.set_scroll_mode(self.scroll_mode)
                
                # Configuration de la vitesse
                print(f"Vitesse de défilement: {self.scroll_speed}")
                await self.set_scroll_speed(self.scroll_speed)
                
                # Auto-ajustement de la taille
                original_size = self.font_size
                optimized_size = self.auto_fit_text(text)
                if optimized_size != original_size:
                    print(f"🔧 Auto-ajustement: {original_size}px → {optimized_size}px")
                
                # Génération de l'image avec décorations
                img = self.create_text_image(text)
                bitmap = self.convert_to_bitmap(img)
                
                # Couleurs séparées avec analyse des zones
                color_array = self.encode_separated_color_array_for_mask(img)
                
                # Upload des données
                await self.init_upload(bitmap, color_array)
                print("✅ Texte expérimental configuré avec succès!")
                
            else:
                # Mode compatible mask-go (FC/BG)
                print("🎨 Mode mask-go activé")
                await super().set_scrolling_text(text)
                print("✅ Texte mask-go configuré avec succès!")
                
        except Exception as e:
            print(f"❌ Erreur upload: {e}")
            # Réinitialisation en cas d'erreur
            if hasattr(self, 'upload_in_progress'):
                self.upload_in_progress = False
            if hasattr(self, '_upload_task') and self._upload_task:
                self._upload_task.cancel()
                self._upload_task = None
    
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
    
    def encode_separated_color_array_for_mask(self, pixel_map):
        """🧪 EXPÉRIMENTAL: Génère un tableau de couleurs avec support des couleurs séparées"""
        results = bytearray()
        
        # Utiliser l'image RGB stockée si disponible
        if hasattr(self, '_current_rgb_image') and self._current_rgb_image:
            img = self._current_rgb_image
            width, height = img.size
            
            for x in range(len(pixel_map)):
                column = pixel_map[x]
                # Analyser la colonne pour déterminer s'il y a du texte et/ou des décorations
                has_text = False
                has_decoration = False
                
                # Vérifier si cette colonne contient du texte (zone centrale)
                text_area_start = 2 if self.show_decorations else 0
                text_area_end = 14 if self.show_decorations else 16
                
                for y in range(text_area_start, text_area_end):
                    if y < len(column) and column[y] == 1:
                        has_text = True
                        break
                
                # Vérifier si cette colonne contient des décorations
                if self.show_decorations:
                    for y in [0, 1, 14, 15]:  # Zones de décorations
                        if y < len(column) and column[y] == 1:
                            has_decoration = True
                            break
                
                # Déterminer la couleur à utiliser pour cette colonne
                if has_decoration and not has_text:
                    # Colonne avec seulement des décorations
                    r, g, b = self.decoration_color
                elif has_text and not has_decoration:
                    # Colonne avec seulement du texte
                    r, g, b = self.text_color
                elif has_text and has_decoration:
                    # Colonne mixte : priorité au texte
                    r, g, b = self.text_color
                    print(f"🔀 Colonne {x}: mixte texte+déco, utilise couleur texte")
                else:
                    # Colonne vide : blanc
                    r, g, b = (255, 255, 255)
                
                results.extend([r, g, b])
        else:
            # Fallback : méthode simple par analyse des décorations
            for x in range(len(pixel_map)):
                column = pixel_map[x]
                
                # Déterminer si c'est une zone de décoration
                is_decoration_column = False
                
                if self.show_decorations:
                    if self.decoration_style == "lines":
                        # Décorations sur les lignes 0, 1, 14, 15
                        is_decoration_column = any(column[y] == 1 for y in [0, 1, 14, 15] if y < len(column))
                    elif self.decoration_style == "dots" and (x % 3 == 0):
                        is_decoration_column = any(column[y] == 1 for y in [0, 1, 14, 15] if y < len(column))
                    elif self.decoration_style == "blocks" and ((x // 4) % 2 == 0):
                        is_decoration_column = any(column[y] == 1 for y in [0, 1, 14, 15] if y < len(column))
                
                # Vérifier s'il y a du texte dans la zone centrale
                has_text_in_center = any(column[y] == 1 for y in range(2, 14) if y < len(column))
                
                if is_decoration_column and not has_text_in_center:
                    # Colonne de décoration pure
                    r, g, b = self.decoration_color
                elif has_text_in_center:
                    # Colonne avec du texte (priorité)
                    r, g, b = self.text_color
                else:
                    # Colonne vide ou indéterminée
                    r, g, b = (255, 255, 255)
                
                results.extend([r, g, b])
                    
        return bytes(results)
    
    # Méthodes de configuration des couleurs
    def set_decoration_color(self, color_name):
        """Définit la couleur des décorations par nom"""
        colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
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
            "yellow": (255, 255, 0),
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
    
    def set_decoration_color_by_rgb(self, rgb):
        """Définit la couleur des décorations par RGB"""
        self.decoration_color = rgb
        return True
    
    def get_color_name(self, rgb):
        """Retourne le nom de la couleur à partir du RGB"""
        color_names = {
            (255, 255, 255): "BLANC",
            (255, 0, 0): "ROUGE",
            (0, 255, 0): "VERT", 
            (0, 0, 255): "BLEU",
            (255, 255, 0): "JAUNE",
            (255, 0, 255): "MAGENTA",
            (0, 255, 255): "CYAN",
            (255, 165, 0): "ORANGE",
            (128, 0, 128): "VIOLET",
            (255, 192, 203): "ROSE"
        }
        return color_names.get(rgb, f"RGB{rgb}")
    
    def toggle_color_mode(self):
        """Bascule entre mode couleurs séparées et mode compatible mask-go"""
        self.use_separated_colors = not self.use_separated_colors
        mode_name = "couleurs séparées" if self.use_separated_colors else "compatible mask-go"
        print(f"🔄 Mode basculé vers: {mode_name}")
        return mode_name
    
    # Inclure toutes les autres méthodes du contrôleur principal...
    # (copiées depuis ultimate_text_display_with_bold.py)
    
    def set_font_size(self, size):
        """Définit la taille de la police"""
        if self.show_decorations:
            self.font_size = max(6, min(14, size))  # Limité pour les décorations
        else:
            self.font_size = max(6, min(32, size))  # Plus large sans décorations
    
    def find_optimal_font_size(self, text):
        """Trouve la taille de police optimale pour le texte"""
        from PIL import ImageFont, ImageDraw, Image
        
        # Zone disponible selon les décorations
        if self.show_decorations:
            max_height = 12  # Hauteur réduite avec décorations
            max_size = 14
            min_size = 6
        else:
            max_height = 16  # Pleine hauteur sans décorations
            max_size = 32
            min_size = 6
        
        # Test des tailles de police
        for size in range(max_size, min_size - 1, -1):
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
            except:
                continue
                
            # Test avec une image temporaire
            test_img = Image.new('RGB', (200, 16))
            draw = ImageDraw.Draw(test_img)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_height = bbox[3] - bbox[1]
            
            if text_height <= max_height:
                return size
                
        return min_size
    
    def get_text_image(self, text, width_multiplier=1.5):
        """Version expérimentale qui génère l'image avec gestion des couleurs"""
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
            
            # Charger la police
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "arial.ttf"
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
        dummy_img = Image.new('RGB', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        total_width = int(text_width * width_multiplier)
        
        # Création de l'image en couleur
        img = Image.new('RGB', (total_width, 16), (0, 0, 0))  # Fond noir
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
        
        # Dessiner le texte avec la couleur spécifiée
        draw.text((x_offset, y_offset), text, fill=self.text_color, font=font)
        
        # Effet gras par superposition si activé
        if self.bold_text:
            draw.text((x_offset + 1, y_offset), text, fill=self.text_color, font=font)
            draw.text((x_offset, y_offset + 1), text, fill=self.text_color, font=font)
            draw.text((x_offset + 1, y_offset + 1), text, fill=self.text_color, font=font)
        
        # Ajouter les décorations colorées directement sur l'image
        if self.show_decorations:
            self.add_colored_decorations(img, total_width)
        
        # Stocker l'image RGB pour l'encodage des couleurs
        self._current_rgb_image = img
        
        # Conversion en bitmap pour transmission au masque
        pixels = []
        for x in range(total_width):
            column = []
            for y in range(16):
                pixel = img.getpixel((x, y))
                # Détection de pixel coloré : tout pixel non-noir est considéré comme allumé
                if isinstance(pixel, tuple):
                    r, g, b = pixel
                    # Un pixel est allumé s'il n'est pas complètement noir
                    is_lit = (r > 0 or g > 0 or b > 0)
                else:
                    is_lit = pixel > 0
                
                column.append(1 if is_lit else 0)
            pixels.append(column)
        
        return pixels
    
    def add_colored_decorations(self, img, width):
        """Ajoute des décorations colorées avec la couleur de décoration"""
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        if self.decoration_style == "lines":
            # Lignes horizontales en haut et en bas
            for x in range(width):
                draw.point((x, 0), fill=self.decoration_color)
                draw.point((x, 1), fill=self.decoration_color)
                draw.point((x, 14), fill=self.decoration_color)
                draw.point((x, 15), fill=self.decoration_color)
                
        elif self.decoration_style == "dots":
            # Points espacés
            for x in range(0, width, 3):
                draw.point((x, 0), fill=self.decoration_color)
                draw.point((x, 1), fill=self.decoration_color)
                draw.point((x, 14), fill=self.decoration_color)
                draw.point((x, 15), fill=self.decoration_color)
                
        # Ajouter d'autres styles si nécessaire...

    # Méthodes héritées nécessaires (simplifiées pour le test)
    def encode_bitmap_for_mask(self, pixel_map):
        """Encode le bitmap selon le format mask-go"""
        # Utiliser la méthode de la classe parent ou une version simplifiée
        results = bytearray()
        for column in pixel_map:
            val = 0
            for y, pixel in enumerate(column):
                if pixel == 1:
                    if y < 8:
                        val |= (1 << (7 - y))
                    else:
                        val |= (1 << (23 - y))
            
            # Encoder en little endian comme mask-go
            results.extend(val.to_bytes(2, 'little'))
        
        return bytes(results)

# Interface utilisateur simplifiée pour tester
async def main():
    """Interface de test pour le contrôleur expérimental"""
    print("🧪 CONTRÔLEUR EXPÉRIMENTAL - Couleurs Séparées")
    print("=" * 60)
    
    controller = ExperimentalColorController()
    
    try:
        # Connexion au masque
        print("🔄 Connexion au masque...")
        await controller.connect()
        print("✅ Masque connecté!")
        
        # Interface simple
        while True:
            print("\n🎯 COMMANDES EXPÉRIMENTALES:")
            print("  📝 text:MESSAGE       - Afficher du texte")
            print("  🎨 textcolor:COLOR    - Couleur du texte")
            print("  🎯 decocolor:COLOR    - Couleur des décorations")
            print("  🔄 mode              - Basculer mode couleurs")
            print("  🚪 quit              - Quitter")
            print("  📊 status            - État actuel")
            
            cmd = input("\n💬 Commande: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "mode":
                mode = controller.toggle_color_mode()
                print(f"✅ Mode: {mode}")
            elif cmd == "status":
                mode = "couleurs séparées" if controller.use_separated_colors else "compatible mask-go"
                print(f"📊 Mode: {mode}")
                print(f"🎨 Couleur texte: {controller.get_color_name(controller.text_color)}")
                print(f"🎯 Couleur décorations: {controller.get_color_name(controller.decoration_color)}")
            elif cmd.startswith("text:"):
                text = cmd[5:]
                await controller.set_scrolling_text(text)
            elif cmd.startswith("textcolor:"):
                color = cmd[10:]
                if controller.set_text_color(color):
                    print(f"✅ Couleur texte: {controller.get_color_name(controller.text_color)}")
                else:
                    print(f"❌ Couleur inconnue: {color}")
            elif cmd.startswith("decocolor:"):
                color = cmd[10:]
                if controller.set_decoration_color(color):
                    print(f"✅ Couleur décorations: {controller.get_color_name(controller.decoration_color)}")
                else:
                    print(f"❌ Couleur inconnue: {color}")
            else:
                print("❌ Commande inconnue")
                
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if controller.client:
            await controller.client.disconnect()
        print("👋 Au revoir!")

if __name__ == "__main__":
    asyncio.run(main())
