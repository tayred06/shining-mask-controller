#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple du style blocks_pattern sans BLE
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

def create_tata_pattern():
    """Créer un motif inspiré du fichier Tata"""
    print("🎨 CRÉATION MOTIF TATA")
    print("=" * 25)
    
    # Créer une image test
    width, height = 80, 16
    img = Image.new('RGB', (width, height), (0, 0, 0))  # Fond noir
    
    # Couleurs
    decoration_color = (255, 255, 0)  # Jaune
    text_color = (255, 255, 255)      # Blanc
    
    # Appliquer le motif blocks_pattern
    for x in range(width):
        # Ligne du haut : blocs complets
        if x % 8 < 6:  # 6 pixels pleins, 2 espaces
            for y in [0, 1]:
                img.putpixel((x, y), decoration_color)
        
        # Ligne du bas : blocs complets
        if x % 8 < 6:  # 6 pixels pleins, 2 espaces
            for y in [14, 15]:
                img.putpixel((x, y), decoration_color)
        
        # Motif vertical : colonnes espacées comme dans Tata
        if x % 12 == 0 or x % 12 == 6:  # Colonnes verticales
            for y in range(2, 14):
                img.putpixel((x, y), decoration_color)
    
    # Ajouter du texte au centre
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    text = "TATA"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = 4  # Zone de texte entre les décorations
    
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    # Sauvegarder l'aperçu agrandi
    preview_img = img.resize((width * 8, height * 8), Image.NEAREST)
    preview_img.save("blocks_pattern_demo.png")
    
    print(f"📸 Aperçu créé: blocks_pattern_demo.png")
    print(f"📏 Taille: {width}x{height} → {preview_img.width}x{preview_img.height}")
    
    # Afficher un aperçu ASCII
    print(f"\n👀 APERÇU ASCII:")
    for y in range(height):
        line = ""
        for x in range(min(width, 40)):  # Limiter la largeur
            pixel = img.getpixel((x, y))
            if pixel == (0, 0, 0):      # Noir
                line += " "
            elif pixel == decoration_color:  # Jaune (décorations)
                line += "█"
            else:                        # Blanc (texte)
                line += "▓"
        print(f"Y{y:2d}: {line}")
    
    return img

def compare_with_original():
    """Comparer avec le motif original du fichier Tata"""
    print(f"\n🆚 COMPARAISON AVEC TATA ORIGINAL")
    print("=" * 35)
    
    # Lire le fichier Tata original
    try:
        with open("../Tata", "r", encoding="utf-8") as f:
            tata_lines = f.readlines()[:5]  # Premières lignes
        
        print("📄 Motif original Tata:")
        for i, line in enumerate(tata_lines):
            clean_line = line.rstrip()[:40]  # Limiter la largeur
            print(f"   {clean_line}")
            
    except Exception as e:
        print(f"❌ Impossible de lire le fichier Tata: {e}")
    
    print(f"\n🎨 Notre motif blocks_pattern:")
    print("   (Voir l'image blocks_pattern_demo.png)")

if __name__ == "__main__":
    # Créer le motif
    img = create_tata_pattern()
    
    # Comparer
    compare_with_original()
    
    print(f"\n✅ Test terminé!")
    print(f"🎯 Utilisez 'deco:blocks_pattern' dans votre script pour l'activer!")
