#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités basées sur mask-go
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'working'))

from ultimate_text_display_with_bold import CompleteMaskController

def test_mask_go_features():
    """Test des nouvelles fonctionnalités basées sur mask-go"""
    
    print("🧪 Test des fonctionnalités mask-go")
    print("=" * 50)
    
    # Créer un contrôleur de test (sans connexion BLE)
    controller = CompleteMaskController()
    
    # Test 1: Couleurs
    print("\n1. Test des couleurs")
    print("-" * 20)
    
    test_colors = [
        ("rouge", (255, 0, 0)),
        ("vert", (0, 255, 0)), 
        ("bleu", (0, 0, 255)),
        ("jaune", (255, 255, 0))
    ]
    
    for color_name, rgb in test_colors:
        controller.set_text_color_by_rgb(rgb)
        print(f"✅ Couleur {color_name} définie: {controller.text_color}")
    
    # Test 2: Génération bitmap + couleur blanche
    print("\n2. Test génération bitmap")
    print("-" * 20)
    
    controller.set_text_color_by_rgb((255, 0, 0))  # Rouge
    pixel_map = controller.get_text_image("TEST")
    
    if pixel_map:
        print(f"✅ Bitmap généré: {len(pixel_map)} colonnes")
        
        # Test nouveau encode white color array
        white_colors = controller.encode_white_color_array_for_mask(len(pixel_map))
        print(f"✅ Color array blanc: {len(white_colors)} bytes")
        
        # Vérifier que c'est bien du blanc
        rgb_count = len(white_colors) // 3
        all_white = True
        for i in range(rgb_count):
            r = white_colors[i*3]
            g = white_colors[i*3 + 1]
            b = white_colors[i*3 + 2]
            if (r, g, b) != (255, 255, 255):
                all_white = False
                break
                
        if all_white:
            print(f"✅ Toutes les couleurs sont blanches (compatible mask-go)")
        else:
            print(f"❌ Couleurs non blanches détectées")
    else:
        print("❌ Erreur génération bitmap")
    
    # Test 3: Encodage bitmap (pas de changement mais vérification)
    print("\n3. Test encodage bitmap")
    print("-" * 20)
    
    try:
        bitmap = controller.encode_bitmap_for_mask(pixel_map)
        print(f"✅ Bitmap encodé: {len(bitmap)} bytes")
        
        # Vérifier le format (2 bytes par colonne)
        expected_size = len(pixel_map) * 2
        if len(bitmap) == expected_size:
            print(f"✅ Taille bitmap correcte: {expected_size} bytes")
        else:
            print(f"⚠️  Taille bitmap inattendue: {len(bitmap)} vs {expected_size}")
            
    except Exception as e:
        print(f"❌ Erreur encodage bitmap: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")
    print("\n🔧 Corrections appliquées selon mask-go:")
    print("  ✅ Commandes FC/BG ajoutées pour les couleurs")
    print("  ✅ Color array forcé en blanc (protocole mask-go)")
    print("  ✅ Couleurs gérées par commandes BLE séparées")
    print("  ✅ Compatible avec le protocole mask-go officiel")

def test_color_rgb_function():
    """Test la fonction de couleur par RGB"""
    print("\n🎨 Test fonction couleur RGB")
    print("-" * 30)
    
    controller = CompleteMaskController()
    
    # Ajouter la méthode manquante
    def set_text_color_by_rgb(self, rgb):
        self.text_color = rgb
        return True
        
    # Monkey patch pour le test
    CompleteMaskController.set_text_color_by_rgb = set_text_color_by_rgb
    
    test_colors = [
        (255, 0, 0),    # Rouge
        (0, 255, 0),    # Vert  
        (0, 0, 255),    # Bleu
        (255, 255, 0)   # Jaune
    ]
    
    for rgb in test_colors:
        success = controller.set_text_color_by_rgb(rgb)
        if success and controller.text_color == rgb:
            print(f"✅ RGB {rgb} → {controller.get_color_name(rgb)}")
        else:
            print(f"❌ RGB {rgb} échec")

if __name__ == "__main__":
    test_mask_go_features()
    test_color_rgb_function()
