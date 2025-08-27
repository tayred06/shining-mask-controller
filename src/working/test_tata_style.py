#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du nouveau style "blocks_pattern" inspiré du fichier Tata
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultimate_text_display_with_bold import CompleteMaskController

def create_tata_preview():
    """Créer un aperçu du style blocks_pattern"""
    print("🎨 CRÉATION DU STYLE BLOCKS_PATTERN")
    print("=" * 40)
    
    controller = CompleteMaskController()
    
    # Configuration du style Tata
    controller.set_text_color("white")
    controller.set_decoration_color("red")
    controller.decoration_style = "blocks_pattern"
    controller.show_decorations = True
    controller.bold_text = False
    
    # Génération d'un exemple
    text = "TATA STYLE"
    print(f"📝 Génération du texte: '{text}'")
    
    # Créer l'image
    img = controller.generate_colored_image(text)
    
    if img:
        # Agrandir pour la visibilité (facteur 10)
        preview_img = img.resize((img.width * 10, img.height * 10), Image.NEAREST)
        preview_img.save("tata_style_preview.png")
        print(f"📸 Aperçu sauvegardé: tata_style_preview.png")
        print(f"📏 Taille: {img.width}x{img.height} → {preview_img.width}x{preview_img.height}")
        
        # Analyser le motif
        analyze_pattern(img)
    else:
        print("❌ Erreur lors de la génération")

def analyze_pattern(img):
    """Analyser le motif généré"""
    print("\n🔍 ANALYSE DU MOTIF:")
    
    width, height = img.size
    print(f"📐 Dimensions: {width}x{height}")
    
    # Analyser la première ligne (décoration du haut)
    top_line = []
    for x in range(min(width, 32)):  # Limiter à 32 pixels pour l'affichage
        pixel = img.getpixel((x, 0))
        if pixel != (0, 0, 0):  # Pas noir
            top_line.append("█")
        else:
            top_line.append(" ")
    
    print(f"🔝 Ligne du haut: {''.join(top_line)}")
    
    # Analyser une ligne du milieu
    middle_line = []
    for x in range(min(width, 32)):
        pixel = img.getpixel((x, 8))  # Milieu
        if pixel != (0, 0, 0):  # Pas noir
            middle_line.append("█")
        else:
            middle_line.append(" ")
    
    print(f"⚡ Ligne milieu: {''.join(middle_line)}")
    
    # Analyser la ligne du bas
    bottom_line = []
    for x in range(min(width, 32)):
        pixel = img.getpixel((x, 15))
        if pixel != (0, 0, 0):  # Pas noir
            bottom_line.append("█")
        else:
            bottom_line.append(" ")
    
    print(f"🔻 Ligne du bas: {''.join(bottom_line)}")

def create_comparison():
    """Créer une comparaison des styles"""
    print("\n🆚 COMPARAISON DES STYLES")
    print("=" * 30)
    
    controller = CompleteMaskController()
    controller.set_text_color("white")
    controller.set_decoration_color("cyan")
    
    styles = ["lines", "dots", "blocks", "waves", "blocks_pattern"]
    
    for style in styles:
        print(f"\n🎨 Style: {style}")
        controller.decoration_style = style
        controller.show_decorations = True
        
        # Générer l'image
        img = controller.generate_colored_image("DEMO")
        
        if img:
            # Sauvegarder
            filename = f"style_{style}_demo.png"
            preview_img = img.resize((img.width * 8, img.height * 8), Image.NEAREST)
            preview_img.save(filename)
            print(f"💾 Sauvegardé: {filename}")
            
            # Aperçu ASCII de la première ligne
            ascii_preview = []
            for x in range(min(img.width, 20)):
                pixel = img.getpixel((x, 0))
                ascii_preview.append("█" if pixel != (0, 0, 0) else "·")
            print(f"👀 Aperçu: {''.join(ascii_preview)}")

if __name__ == "__main__":
    # Test principal
    create_tata_preview()
    
    # Comparaison
    create_comparison()
    
    print(f"\n🎉 Tests terminés!")
    print(f"📁 Fichiers générés dans le répertoire courant")
    print(f"🎯 Utilisez 'deco:blocks_pattern' dans votre script !")
