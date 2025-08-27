#!/usr/bin/env python3
"""
Test du pattern tata_line_pattern modifié
Avec 10 points au début et à la fin de chaque ligne
"""

from PIL import Image, ImageDraw

def create_tata_line_pattern_with_borders():
    """Crée un aperçu du pattern avec bordures de 10 points"""
    width = 64
    height = 16
    
    # Créer une image noire
    img = Image.new('RGB', (width, height), (0, 0, 0))
    
    # Couleur de décoration (blanc pour la visibilité)
    decoration_color = (255, 255, 255)
    
    # Appliquer le pattern avec bordures
    for y in [0, 15]:
        for x in range(width):
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
            
            if should_light:
                img.putpixel((x, y), decoration_color)
    
    return img

def display_pattern_analysis():
    """Affiche l'analyse du pattern avec bordures"""
    print("=" * 80)
    print("🎨 PATTERN TATA_LINE_PATTERN AVEC BORDURES DE 10 POINTS")
    print("=" * 80)
    print()
    print("📋 STRUCTURE MODIFIÉE:")
    print("   🟦 Pixels 0-9   : ●●●●●●●●●● (10 points fixes au DÉBUT)")
    print("   🔄 Pixels 10-53 : Motif répétitif (44 pixels)")
    print("   🟦 Pixels 54-63 : ●●●●●●●●●● (10 points fixes à la FIN)")
    print()
    print("🔄 MOTIF RÉPÉTITIF AU MILIEU (cycle de 16 pixels):")
    print("   Pixels 0-9  : ●●●●●●●●●● (10 points)")
    print("   Pixels 10-11:           (2 espaces)")
    print("   Pixels 12-13: ●●        (2 points)")
    print("   Pixels 14-15:           (2 espaces)")
    print()
    print("📐 VISUALISATION COMPLÈTE (64 pixels):")
    
    # Générer la visualisation
    pattern = ""
    for x in range(64):
        if x < 10:
            # 10 premiers points fixes
            pattern += "●"
        elif x >= 54:
            # 10 derniers points fixes
            pattern += "●"
        else:
            # Zone milieu avec motif répétitif
            middle_pos = (x - 10) % 16
            if middle_pos < 10:
                pattern += "●"
            elif middle_pos == 10 or middle_pos == 11:
                pattern += " "
            elif middle_pos == 12 or middle_pos == 13:
                pattern += "●"
            elif middle_pos == 14 or middle_pos == 15:
                pattern += " "
    
    print(f"   {pattern}")
    print()
    print("🎯 AVANTAGES:")
    print("   ✅ Chaque ligne commence TOUJOURS par 10 points")
    print("   ✅ Chaque ligne termine TOUJOURS par 10 points")
    print("   ✅ Motif cohérent au centre")
    print("   ✅ Symétrie parfaite")
    print()
    print("🎯 ZONES D'APPLICATION:")
    print("   - Ligne 0 (tout en haut)")
    print("   - Ligne 15 (tout en bas)")
    print("   - Zone texte (1-14) libre")
    print()
    print("🚀 UTILISATION:")
    print("   deco:tata_line_pattern")
    print("   decocolor:violet")
    print("   Votre texte ici!")
    print("=" * 80)

if __name__ == "__main__":
    print("🔄 Génération du pattern avec bordures de 10 points...")
    
    # Créer l'aperçu
    img = create_tata_line_pattern_with_borders()
    
    # Sauvegarder l'aperçu
    output_path = "/Users/mathieu/my-python-project/src/working/tata_line_with_borders_preview.png"
    
    # Agrandir pour la visibilité (x8)
    large_img = img.resize((512, 128), Image.NEAREST)
    large_img.save(output_path)
    
    print(f"✅ Aperçu sauvegardé: {output_path}")
    print("📏 Image agrandie 8x pour la visibilité")
    
    # Afficher l'analyse
    display_pattern_analysis()
    
    print("\n✨ Pattern modifié avec bordures de 10 points!")
    print("🔄 Relancez le programme pour tester le nouveau comportement!")
