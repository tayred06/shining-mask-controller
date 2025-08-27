#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test isolé du système de couleurs sans BLE
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Classe simplifiée pour test
class SimpleColorController:
    """Version simplifiée pour tester les couleurs"""
    
    def __init__(self):
        # Couleurs
        self.text_color = (255, 255, 255)  # Blanc par défaut
        self.decoration_color = (255, 255, 255)  # Blanc par défaut
        
        # Paramètres
        self.font_size = 12
        self.show_decorations = True
        self.decoration_style = "lines"
    
    def get_color_name(self, rgb):
        """Retourne le nom de la couleur"""
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
        return color_names.get(rgb, f"RGB({rgb[0]},{rgb[1]},{rgb[2]})")
    
    def set_text_color(self, color_name):
        """Définit la couleur du texte"""
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
    
    def set_decoration_color(self, color_name):
        """Définit la couleur des décorations"""
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
    
    def create_test_bitmap(self, text="TEST"):
        """Crée un bitmap de test"""
        # Simuler un bitmap simple 64x16
        bitmap = []
        for x in range(64):
            column = [0] * 16
            
            # Ajouter des décorations (lignes)
            if self.show_decorations and self.decoration_style == "lines":
                column[0] = 1  # Ligne du haut
                column[15] = 1  # Ligne du bas
            
            # Ajouter du "texte" au milieu
            if 10 <= x <= 50:  # Zone de texte
                for y in range(4, 12):  # Hauteur du texte
                    column[y] = 1
            
            bitmap.append(column)
        
        return bitmap
    
    def encode_color_array_for_mask(self, pixel_map):
        """Génère un tableau de couleurs pour test"""
        results = bytearray()
        
        for x in range(len(pixel_map)):
            column = pixel_map[x]
            for y in range(16):
                pixel_value = column[y]
                
                if pixel_value == 1:  # Pixel allumé
                    # Déterminer si c'est du texte ou une décoration
                    is_decoration = False
                    
                    if self.show_decorations:
                        if self.decoration_style == "lines" and (y in [0, 15]):
                            is_decoration = True
                    
                    # Utiliser la couleur appropriée
                    if is_decoration:
                        r, g, b = self.decoration_color
                    else:
                        r, g, b = self.text_color
                    
                    results.extend([r, g, b])
                else:  # Pixel éteint
                    results.extend([0x00, 0x00, 0x00])  # Noir
                    
        return bytes(results)

def test_isolated_colors():
    """Test isolé du système de couleurs"""
    print("🌈 TEST ISOLÉ DU SYSTÈME DE COULEURS")
    print("=" * 45)
    
    # Créer le contrôleur
    controller = SimpleColorController()
    
    # Test 1: Couleurs par défaut
    print("\n✅ Test 1: Couleurs par défaut")
    print(f"Texte: {controller.get_color_name(controller.text_color)}")
    print(f"Déco: {controller.get_color_name(controller.decoration_color)}")
    
    # Test 2: Changement couleur texte
    print("\n✅ Test 2: Changement couleur texte")
    success = controller.set_text_color("red")
    print(f"set_text_color('red'): {success}")
    print(f"Nouvelle couleur texte: {controller.get_color_name(controller.text_color)}")
    print(f"RGB texte: {controller.text_color}")
    
    # Test 3: Changement couleur décorations
    print("\n✅ Test 3: Changement couleur décorations")
    success = controller.set_decoration_color("yellow")
    print(f"set_decoration_color('yellow'): {success}")
    print(f"Nouvelle couleur déco: {controller.get_color_name(controller.decoration_color)}")
    print(f"RGB déco: {controller.decoration_color}")
    
    # Test 4: Génération bitmap
    print("\n✅ Test 4: Génération bitmap")
    bitmap = controller.create_test_bitmap()
    print(f"Bitmap créé: {len(bitmap)} colonnes x 16 lignes")
    
    # Test 5: Génération couleurs
    print("\n✅ Test 5: Génération tableau couleurs")
    color_array = controller.encode_color_array_for_mask(bitmap)
    total_pixels = len(bitmap) * 16
    print(f"Pixels totaux: {total_pixels}")
    print(f"Bytes couleur: {len(color_array)}")
    print(f"Bytes par pixel: {len(color_array) // total_pixels}")
    
    # Test 6: Vérification des couleurs
    print("\n✅ Test 6: Vérification couleurs spécifiques")
    
    # Pixel de décoration (ligne du haut, première colonne)
    decoration_pixel_idx = 0 * 16 * 3 + 0 * 3  # Colonne 0, ligne 0
    if decoration_pixel_idx + 2 < len(color_array):
        r, g, b = color_array[decoration_pixel_idx:decoration_pixel_idx+3]
        print(f"Décoration pixel RGB: ({r}, {g}, {b})")
        if (r, g, b) == controller.decoration_color:
            print("✅ Couleur décoration CORRECTE!")
        else:
            print("❌ Couleur décoration incorrecte")
    
    # Pixel de texte (milieu)
    text_pixel_idx = 20 * 16 * 3 + 8 * 3  # Colonne 20, ligne 8
    if text_pixel_idx + 2 < len(color_array):
        r, g, b = color_array[text_pixel_idx:text_pixel_idx+3]
        print(f"Texte pixel RGB: ({r}, {g}, {b})")
        if (r, g, b) == controller.text_color:
            print("✅ Couleur texte CORRECTE!")
        else:
            print("❌ Couleur texte incorrecte")
    
    print("\n🎉 Test terminé!")
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ:")
    print(f"   🔤 Couleur texte: {controller.get_color_name(controller.text_color)} {controller.text_color}")
    print(f"   🎨 Couleur déco: {controller.get_color_name(controller.decoration_color)} {controller.decoration_color}")
    print(f"   📏 Taille bitmap: {len(bitmap)} x 16")
    print(f"   🌈 Taille couleurs: {len(color_array)} bytes")

if __name__ == "__main__":
    test_isolated_colors()
