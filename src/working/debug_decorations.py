#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de débogage pour vérifier les couleurs des décorations
"""

import sys
import os

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultimate_text_display_with_bold import CompleteMaskController

def debug_decoration_colors():
    """Debug des couleurs de décorations"""
    print("🔍 DEBUG COULEURS DÉCORATIONS")
    print("=" * 35)
    
    controller = CompleteMaskController()
    
    # Configuration
    controller.set_text_color("white")
    controller.set_decoration_color("red")
    controller.decoration_style = "lines"
    controller.show_decorations = True
    
    print(f"📊 Configuration:")
    print(f"   Texte: {controller.get_color_name(controller.text_color)} {controller.text_color}")
    print(f"   Déco: {controller.get_color_name(controller.decoration_color)} {controller.decoration_color}")
    print(f"   Style: {controller.decoration_style}")
    print(f"   Visible: {controller.show_decorations}")
    
    # Générer les données
    print(f"\n🔧 Génération...")
    pixel_map = controller.get_text_image("TEST")
    print(f"   Pixel map: {len(pixel_map)} colonnes")
    
    # Vérifier si l'image RGB est stockée
    has_rgb = hasattr(controller, '_current_rgb_image')
    print(f"   Image RGB stockée: {has_rgb}")
    
    if has_rgb:
        img = controller._current_rgb_image
        print(f"   Taille image: {img.size}")
        
        # Vérifier quelques pixels de décoration
        print(f"\n🎨 Vérification pixels décorations:")
        for x in [0, 10, 20]:
            for y in [0, 15]:  # Lignes de décoration
                if x < img.size[0] and y < img.size[1]:
                    pixel = img.getpixel((x, y))
                    print(f"   Pixel ({x},{y}): {pixel}")
    
    # Générer le tableau de couleurs
    color_array = controller.encode_color_array_for_mask(pixel_map)
    print(f"\n📊 Tableau couleurs: {len(color_array)} bytes")
    
    # Analyser les premières couleurs
    print(f"\n🌈 Premières couleurs:")
    for i in range(0, min(30, len(color_array)), 3):
        r, g, b = color_array[i], color_array[i+1], color_array[i+2]
        pixel_num = i // 3
        x = pixel_num // 16
        y = pixel_num % 16
        print(f"   Pixel {pixel_num} ({x},{y}): RGB({r},{g},{b})")
        
        if r == 255 and g == 0 and b == 0:
            print(f"     ✅ ROUGE détecté (décoration)")
        elif r == 255 and g == 255 and b == 255:
            print(f"     ✅ BLANC détecté (texte)")
        elif r == 0 and g == 0 and b == 0:
            print(f"     ⚫ NOIR (fond)")
        else:
            print(f"     ❓ Autre couleur")

if __name__ == "__main__":
    debug_decoration_colors()
