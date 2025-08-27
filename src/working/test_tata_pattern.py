#!/usr/bin/env python3
"""
Test du nouveau style de décoration tata_pattern
Reproduit exactement le motif du fichier Tata
"""

from PIL import Image, ImageDraw

def create_tata_pattern_preview():
    """Crée un aperçu du pattern tata_pattern"""
    width = 64
    height = 16
    
    # Créer une image noire
    img = Image.new('RGB', (width, height), (0, 0, 0))
    
    # Couleur de décoration (blanc pour la visibilité)
    decoration_color = (255, 255, 255)
    
    # Appliquer le pattern tata exact
    for y in range(height):
        for x in range(width):
            if y == 0:
                # Ligne 1: points continus
                img.putpixel((x, y), decoration_color)
            elif y == 1:
                # Ligne 2: espaces avec points isolés à intervalles réguliers
                if x % 8 == 4:  # Points espacés tous les 8 pixels, décalés de 4
                    img.putpixel((x, y), decoration_color)
            elif y == 2:
                # Ligne 3: points continus à nouveau
                img.putpixel((x, y), decoration_color)
            # Répéter le motif tous les 3 pixels en hauteur
            elif y % 3 == 0:
                # Points continus
                img.putpixel((x, y), decoration_color)
            elif y % 3 == 1:
                # Points espacés
                if x % 8 == 4:
                    img.putpixel((x, y), decoration_color)
            elif y % 3 == 2:
                # Points continus
                img.putpixel((x, y), decoration_color)
    
    return img

def display_pattern_analysis():
    """Affiche l'analyse du pattern"""
    print("=" * 60)
    print("🎨 NOUVEAU STYLE DE DÉCORATION: tata_pattern")
    print("=" * 60)
    print()
    print("📋 DESCRIPTION:")
    print("   Reproduit exactement le motif du fichier Tata")
    print("   Chaque point (.) du fichier correspond à une LED allumée")
    print()
    print("🔄 MOTIF RÉPÉTITIF (tous les 3 pixels en hauteur):")
    print("   Ligne Y%3=0: ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●")
    print("   Ligne Y%3=1:     ●       ●       ●       ●       ●")
    print("   Ligne Y%3=2: ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●")
    print()
    print("📐 DIMENSIONS:")
    print("   - Largeur: 64 pixels (toute la largeur du masque)")
    print("   - Hauteur: 16 pixels (toute la hauteur du masque)")
    print("   - Points isolés: espacés de 8 pixels, décalés de 4")
    print()
    print("🎯 UTILISATION:")
    print("   Dans l'interface, tapez: deco:tata_pattern")
    print("   Puis envoyez votre texte pour voir le motif appliqué")
    print()
    print("🌈 COULEURS:")
    print("   Utilisez decocolor:X pour changer la couleur du motif")
    print("   (red, green, blue, yellow, white, cyan, magenta, etc.)")
    print("=" * 60)

if __name__ == "__main__":
    print("🔄 Génération de l'aperçu du pattern tata...")
    
    # Créer l'aperçu
    img = create_tata_pattern_preview()
    
    # Sauvegarder l'aperçu
    output_path = "/Users/mathieu/my-python-project/src/working/tata_pattern_preview.png"
    
    # Agrandir pour la visibilité (x8)
    large_img = img.resize((512, 128), Image.NEAREST)
    large_img.save(output_path)
    
    print(f"✅ Aperçu sauvegardé: {output_path}")
    print("📏 Image agrandie 8x pour la visibilité")
    
    # Afficher l'analyse
    display_pattern_analysis()
    
    print("\n✨ Le style tata_pattern est maintenant disponible!")
    print("🚀 Lancez ultimate_text_display_with_bold.py et testez-le!")
