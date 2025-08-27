#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du système de décorations colorées
Démontre les nouvelles fonctionnalités de couleur sans masque physique
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class ColorTestController(ScrollingMaskController):
    """Contrôleur de test pour les décorations colorées"""
    
    def __init__(self):
        # Initialiser sans BLE
        self.encryption_key = "32672f7974ad43451d9c6c894a0e8764"
        self.mask = None
        self.connected = False
        
        # Paramètres de texte
        self.current_mode = "scroll_left"
        self.current_speed = 50
        self.last_text = ""
        
        # Nouvelles propriétés de couleur
        self.text_color = (255, 255, 255)  # Blanc par défaut
        self.decoration_color = (255, 255, 255)  # Blanc par défaut
        
        # Paramètres existants
        self.font_size = 12
        self.auto_fit = True
        self.show_decorations = True
        self.decoration_style = "lines"
        self.bold_text = False
        
    def get_color_name(self, rgb_color):
        """Obtenir le nom d'une couleur à partir de ses valeurs RGB"""
        colors = {
            (255, 255, 255): "BLANC",
            (255, 0, 0): "ROUGE", 
            (0, 255, 0): "VERT",
            (0, 0, 255): "BLEU",
            (255, 255, 0): "JAUNE",
            (0, 255, 255): "CYAN",
            (255, 0, 255): "MAGENTA",
            (255, 165, 0): "ORANGE",
            (238, 130, 238): "VIOLET",
            (255, 192, 203): "ROSE"
        }
        return colors.get(rgb_color, "CUSTOM")
    
    def set_text_color(self, color_name):
        """Définir la couleur du texte"""
        colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0), 
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "violet": (238, 130, 238),
            "rose": (255, 192, 203)
        }
        
        if color_name.lower() in colors:
            self.text_color = colors[color_name.lower()]
            return True
        return False
    
    def set_decoration_color(self, color_name):
        """Définir la couleur des décorations"""
        colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0), 
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "violet": (238, 130, 238),
            "rose": (255, 192, 203)
        }
        
        if color_name.lower() in colors:
            self.decoration_color = colors[color_name.lower()]
            return True
        return False
    
    def generate_colored_image(self, text):
        """Générer une image colorée avec texte et décorations"""
        # Paramètres de l'affichage
        width, height = 64, 16
        
        # Créer une image RGB
        img = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            # Charger une police système
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.font_size)
        except:
            # Fallback sur la police par défaut
            font = ImageFont.load_default()
        
        # Calculer la position du texte pour le centrage
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Dessiner le texte avec la couleur choisie
        draw.text((x, y), text, font=font, fill=self.text_color)
        
        # Ajouter du texte en gras si activé
        if self.bold_text:
            # Superposition légère pour l'effet gras
            draw.text((x + 1, y), text, font=font, fill=self.text_color)
            draw.text((x, y + 1), text, font=font, fill=self.text_color)
        
        # Ajouter les décorations colorées
        if self.show_decorations and self.decoration_style != "none":
            self.add_colored_decorations(img, draw)
        
        return img
    
    def add_colored_decorations(self, img, draw):
        """Ajouter des décorations colorées à l'image"""
        width, height = img.size
        
        if self.decoration_style == "lines":
            # Lignes horizontales colorées
            draw.line([(0, 0), (width-1, 0)], fill=self.decoration_color, width=1)
            draw.line([(0, height-1), (width-1, height-1)], fill=self.decoration_color, width=1)
            
        elif self.decoration_style == "dots":
            # Points colorés aux coins et milieux
            for x in range(0, width, 8):
                draw.ellipse([x, 0, x+1, 1], fill=self.decoration_color)
                draw.ellipse([x, height-2, x+1, height-1], fill=self.decoration_color)
                
        elif self.decoration_style == "blocks":
            # Blocs colorés aux coins
            draw.rectangle([0, 0, 2, 2], fill=self.decoration_color)
            draw.rectangle([width-3, 0, width-1, 2], fill=self.decoration_color)
            draw.rectangle([0, height-3, 2, height-1], fill=self.decoration_color)
            draw.rectangle([width-3, height-3, width-1, height-1], fill=self.decoration_color)
            
        elif self.decoration_style == "waves":
            # Motif ondulé coloré
            for x in range(0, width, 4):
                y_top = 1 if (x // 4) % 2 == 0 else 0
                y_bottom = height - 2 if (x // 4) % 2 == 0 else height - 1
                draw.point((x, y_top), fill=self.decoration_color)
                draw.point((x, y_bottom), fill=self.decoration_color)
    
    def save_preview(self, text, filename="preview.png"):
        """Sauvegarder un aperçu de l'image générée"""
        img = self.generate_colored_image(text)
        
        # Agrandir l'image pour la visibilité (facteur 8)
        preview_img = img.resize((img.width * 8, img.height * 8), Image.NEAREST)
        preview_img.save(filename)
        print(f"📸 Aperçu sauvegardé: {filename}")
        return preview_img

def main():
    """Test du système de couleurs"""
    controller = ColorTestController()
    
    print("🌈 TEST DU SYSTÈME DE DÉCORATIONS COLORÉES")
    print("=" * 50)
    
    # Test 1: Texte blanc avec décorations rouges
    print("\n🔴 Test 1: Texte blanc avec lignes rouges")
    controller.set_text_color("white")
    controller.set_decoration_color("red")
    controller.decoration_style = "lines"
    controller.save_preview("HELLO", "test1_white_text_red_lines.png")
    
    # Test 2: Texte vert avec points bleus
    print("\n🔵 Test 2: Texte vert avec points bleus")
    controller.set_text_color("green")
    controller.set_decoration_color("blue")
    controller.decoration_style = "dots"
    controller.save_preview("WORLD", "test2_green_text_blue_dots.png")
    
    # Test 3: Texte jaune avec blocs cyan
    print("\n🔶 Test 3: Texte jaune avec blocs cyan")
    controller.set_text_color("yellow")
    controller.set_decoration_color("cyan")
    controller.decoration_style = "blocks"
    controller.save_preview("TEST", "test3_yellow_text_cyan_blocks.png")
    
    # Test 4: Texte magenta avec vagues orange
    print("\n🟠 Test 4: Texte magenta avec vagues orange")
    controller.set_text_color("magenta")
    controller.set_decoration_color("orange")
    controller.decoration_style = "waves"
    controller.save_preview("COLOR", "test4_magenta_text_orange_waves.png")
    
    # Test 5: Texte gras rouge avec lignes violettes
    print("\n🟣 Test 5: Texte gras rouge avec lignes violettes")
    controller.set_text_color("red")
    controller.set_decoration_color("violet")
    controller.decoration_style = "lines"
    controller.bold_text = True
    controller.save_preview("BOLD", "test5_bold_red_text_violet_lines.png")
    
    print("\n✅ Tous les tests terminés!")
    print("📁 Fichiers d'aperçu générés dans le répertoire courant")
    
    # Afficher l'état final
    print(f"\n📊 État final:")
    print(f"   📝 Couleur texte: {controller.get_color_name(controller.text_color)}")
    print(f"   🎨 Couleur décorations: {controller.get_color_name(controller.decoration_color)}")
    print(f"   🎯 Style décorations: {controller.decoration_style}")
    print(f"   💪 Texte gras: {'ON' if controller.bold_text else 'OFF'}")

if __name__ == "__main__":
    main()
