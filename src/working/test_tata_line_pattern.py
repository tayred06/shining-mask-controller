#!/usr/bin/env python3
"""
Test du nouveau style tata_line_pattern
Basé sur la ligne spécifique: "..........  ..  ..  ..........  ..  ..  .........."
"""

from PIL import Image, ImageDraw

def create_tata_line_pattern_preview():
    """Crée un aperçu du pattern tata_line_pattern"""
    width = 64
    height = 16
    
    # Créer une image noire
    img = Image.new('RGB', (width, height), (0, 0, 0))
    
    # Couleur de décoration (blanc pour la visibilité)
    decoration_color = (255, 255, 255)
    
    # Appliquer le pattern tata_line seulement sur les lignes de décoration
    for y in [0, 1, 14, 15]:
        for x in range(width):
            # Calculer la position dans le cycle de 16 pixels (10+2+2+2 = 16)
            pos_in_cycle = x % 16
            should_light = False
            
            if pos_in_cycle < 10:
                # 10 premiers pixels: points continus
                should_light = True
            elif pos_in_cycle == 10 or pos_in_cycle == 11:
                # 2 espaces
                should_light = False
            elif pos_in_cycle == 12 or pos_in_cycle == 13:
                # 2 points
                should_light = True
            elif pos_in_cycle == 14 or pos_in_cycle == 15:
                # 2 espaces
                should_light = False
            
            if should_light:
                img.putpixel((x, y), decoration_color)
    
    return img

def display_pattern_analysis():
    """Affiche l'analyse du pattern"""
    print("=" * 70)
    print("🎨 NOUVEAU STYLE DE DÉCORATION: tata_line_pattern")
    print("=" * 70)
    print()
    print("📋 DESCRIPTION:")
    print("   Basé sur la ligne spécifique du fichier Tata:")
    print('   "..........  ..  ..  ..........  ..  ..  .........."')
    print()
    print("🔄 STRUCTURE DU MOTIF (cycle de 16 pixels):")
    print("   Pixels 0-9  : ●●●●●●●●●● (10 points continus)")
    print("   Pixels 10-11:           (2 espaces)")
    print("   Pixels 12-13: ●●        (2 points)")
    print("   Pixels 14-15:           (2 espaces)")
    print("   → Répétition du cycle")
    print()
    print("📐 VISUALISATION (64 pixels de large):")
    pattern = ""
    for x in range(64):
        pos_in_cycle = x % 16
        if pos_in_cycle < 10:
            pattern += "●"
        elif pos_in_cycle == 10 or pos_in_cycle == 11:
            pattern += " "
        elif pos_in_cycle == 12 or pos_in_cycle == 13:
            pattern += "●"
        elif pos_in_cycle == 14 or pos_in_cycle == 15:
            pattern += " "
    print(f"   {pattern}")
    print()
    print("🎯 ZONES D'APPLICATION:")
    print("   - Lignes 0, 1 (haut)")
    print("   - Lignes 14, 15 (bas)")
    print("   - Zone texte (2-13) libre")
    print()
    print("🎯 UTILISATION:")
    print("   Dans l'interface, tapez: deco:tata_line_pattern")
    print("   Puis envoyez votre texte pour voir le motif appliqué")
    print()
    print("🌈 COULEURS:")
    print("   Utilisez decocolor:X pour changer la couleur du motif")
    print("   (red, green, blue, yellow, white, cyan, magenta, etc.)")
    print("=" * 70)

if __name__ == "__main__":
    print("🔄 Génération de l'aperçu du pattern tata_line...")
    
    # Créer l'aperçu
    img = create_tata_line_pattern_preview()
    
    # Sauvegarder l'aperçu
    output_path = "/Users/mathieu/my-python-project/src/working/tata_line_pattern_preview.png"
    
    # Agrandir pour la visibilité (x8)
    large_img = img.resize((512, 128), Image.NEAREST)
    large_img.save(output_path)
    
    print(f"✅ Aperçu sauvegardé: {output_path}")
    print("📏 Image agrandie 8x pour la visibilité")
    
    # Afficher l'analyse
    display_pattern_analysis()
    
    print("\n✨ Le style tata_line_pattern est maintenant disponible!")
    print("🚀 Testez-le avec: deco:tata_line_pattern")
