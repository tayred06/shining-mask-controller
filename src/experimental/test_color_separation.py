#!/usr/bin/env python3
"""
Test du contrôleur expérimental avec couleurs séparées
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'working'))

async def test_experimental_colors():
    """Test des couleurs séparées"""
    from color_separation_controller import ExperimentalColorController
    
    print("🧪 TEST COULEURS SÉPARÉES")
    print("=" * 50)
    
    controller = ExperimentalColorController()
    
    # Test 1: Configuration des couleurs
    print("\n1. Configuration des couleurs")
    print("-" * 30)
    
    controller.set_text_color("red")
    controller.set_decoration_color("blue")
    
    print(f"✅ Couleur texte: {controller.get_color_name(controller.text_color)}")
    print(f"✅ Couleur décorations: {controller.get_color_name(controller.decoration_color)}")
    
    # Test 2: Génération bitmap et couleurs
    print("\n2. Test génération bitmap")
    print("-" * 30)
    
    pixel_map = controller.get_text_image("TEST")
    
    if pixel_map:
        print(f"✅ Bitmap généré: {len(pixel_map)} colonnes")
        
        # Test couleurs séparées
        controller.use_separated_colors = True
        color_array_separated = controller.encode_separated_color_array_for_mask(pixel_map)
        
        # Test couleurs unifiées (mask-go)
        controller.use_separated_colors = False
        color_array_unified = controller.encode_white_color_array_for_mask(len(pixel_map))
        
        print(f"✅ Couleurs séparées: {len(color_array_separated)} bytes")
        print(f"✅ Couleurs unifiées: {len(color_array_unified)} bytes")
        
        # Analyser les couleurs séparées
        rgb_count = len(color_array_separated) // 3
        colors_found = set()
        
        for i in range(min(10, rgb_count)):  # Analyser les 10 premières colonnes
            r = color_array_separated[i*3]
            g = color_array_separated[i*3 + 1]
            b = color_array_separated[i*3 + 2]
            colors_found.add((r, g, b))
        
        print(f"✅ Couleurs détectées: {list(colors_found)}")
        
        if (255, 0, 0) in colors_found:  # Rouge pour texte
            print("✅ Couleur texte rouge détectée")
        if (0, 0, 255) in colors_found:  # Bleu pour décorations
            print("✅ Couleur décorations bleue détectée")
            
    # Test 3: Mode toggle
    print("\n3. Test basculement de mode")
    print("-" * 30)
    
    mode1 = controller.toggle_color_mode()
    print(f"✅ Mode basculé vers: {mode1}")
    
    mode2 = controller.toggle_color_mode()
    print(f"✅ Mode basculé vers: {mode2}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")
    print("\n🎯 Fonctionnalités expérimentales:")
    print("  ✅ Couleurs séparées pour texte et décorations")
    print("  ✅ Basculement entre mode séparé et mode mask-go")
    print("  ✅ Analyse automatique des zones texte/décorations")
    print("  ✅ Fallback compatible mask-go")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_experimental_colors())
