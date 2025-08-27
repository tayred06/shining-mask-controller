#!/usr/bin/env python3
"""
Test de diagnostic pour l'encodage des couleurs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'working'))

from ultimate_text_display_with_bold import MaskController

def test_color_encoding():
    """Test l'encodage des couleurs pour chaque couleur"""
    
    print("🧪 Test d'encodage des couleurs")
    print("=" * 50)
    
    # Créer un contrôleur de test (sans connexion BLE)
    controller = MaskController()
    
    # Test des couleurs principales
    test_colors = ['white', 'red', 'green', 'blue', 'yellow']
    
    for color_name in test_colors:
        print(f"\n🎨 Test couleur: {color_name.upper()}")
        print("-" * 30)
        
        # Définir la couleur
        success = controller.set_text_color(color_name)
        if not success:
            print(f"❌ Erreur: Couleur {color_name} non reconnue")
            continue
            
        print(f"✅ Couleur définie: {controller.text_color}")
        
        # Générer une image de test simple
        controller.generate_rgb_image_for_text("TEST")
        
        if hasattr(controller, '_current_rgb_image') and controller._current_rgb_image:
            img = controller._current_rgb_image
            width, height = img.size
            print(f"📐 Image générée: {width}x{height}")
            
            # Vérifier les pixels colorés dans l'image
            colored_pixels = 0
            sample_colors = set()
            
            for x in range(width):
                for y in range(height):
                    pixel = img.getpixel((x, y))
                    if pixel != (0, 0, 0):  # Pas noir
                        colored_pixels += 1
                        sample_colors.add(pixel)
            
            print(f"🔍 Pixels colorés trouvés: {colored_pixels}")
            print(f"🎨 Couleurs échantillons: {list(sample_colors)[:3]}")
            
            # Test de l'encodage
            pixel_map = controller.create_simple_bitmap("TEST")
            color_array = controller.encode_color_array_for_mask(pixel_map)
            
            print(f"📊 Taille bitmap: {len(pixel_map)} colonnes")
            print(f"📊 Taille color_array: {len(color_array)} bytes")
            
            # Analyser les couleurs dans le color_array
            rgb_colors = []
            for i in range(0, len(color_array), 3):
                if i + 2 < len(color_array):
                    r = color_array[i]
                    g = color_array[i + 1] 
                    b = color_array[i + 2]
                    if (r, g, b) != (0, 0, 0):
                        rgb_colors.append((r, g, b))
            
            unique_colors = list(set(rgb_colors))
            print(f"🔬 Couleurs dans color_array: {unique_colors[:3]}")
            
            # Vérifier si la couleur attendue est présente
            expected_color = controller.text_color
            if expected_color in unique_colors:
                print(f"✅ Couleur attendue {expected_color} TROUVÉE")
            else:
                print(f"❌ Couleur attendue {expected_color} MANQUANTE")
                if unique_colors:
                    print(f"⚠️  Couleur présente à la place: {unique_colors[0]}")
        else:
            print("❌ Aucune image RGB générée")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

if __name__ == "__main__":
    test_color_encoding()
