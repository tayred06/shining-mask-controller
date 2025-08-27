#!/usr/bin/env python3
"""
Diagnostic des couleurs - Test pour vérifier la transmission des couleurs
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultimate_text_display_with_bold import CompleteMaskController

async def test_color_transmission():
    """Test diagnostic des couleurs"""
    print("🔬 DIAGNOSTIC DES COULEURS")
    print("=" * 50)
    
    mask = CompleteMaskController()
    
    try:
        print("🔄 Connexion au masque...")
        await mask.connect()
        await mask.set_brightness(80)
        print("✅ Connecté!")
        
        # Test 1: Couleurs de base
        colors_to_test = [
            ("red", "ROUGE"),
            ("green", "VERT"), 
            ("blue", "BLEU"),
            ("yellow", "JAUNE"),
            ("white", "BLANC")
        ]
        
        for color_key, color_name in colors_to_test:
            print(f"\n🎨 Test couleur {color_name}")
            
            # Définir la couleur
            success = mask.set_text_color(color_key)
            print(f"   Couleur définie: {success}")
            print(f"   RGB interne: {mask.text_color}")
            
            # Générer l'image avec cette couleur
            print(f"   Génération image avec texte 'TEST {color_name}'...")
            pixel_map = mask.get_text_image(f"TEST {color_name}")
            
            # Vérifier que l'image RGB est créée
            if hasattr(mask, '_current_rgb_image') and mask._current_rgb_image:
                img = mask._current_rgb_image
                print(f"   Image RGB créée: {img.size}")
                
                # Vérifier quelques pixels pour voir leurs couleurs
                width, height = img.size
                sample_pixels = []
                for x in range(min(10, width)):
                    for y in range(2, min(14, height)):  # Zone de texte
                        pixel = img.getpixel((x, y))
                        if pixel != (0, 0, 0):  # Pas noir (fond)
                            sample_pixels.append(pixel)
                            break
                    if sample_pixels:
                        break
                
                if sample_pixels:
                    print(f"   Couleur échantillon: {sample_pixels[0]}")
                else:
                    print("   ⚠️  Aucun pixel coloré trouvé")
            else:
                print("   ❌ Pas d'image RGB créée")
            
            # Encoder les couleurs
            print("   Encodage des couleurs...")
            color_array = mask.encode_color_array_for_mask(pixel_map)
            
            # Vérifier les premières couleurs non-noires dans le tableau
            sample_colors = []
            for i in range(0, min(len(color_array), 300), 3):
                r, g, b = color_array[i], color_array[i+1], color_array[i+2]
                if (r, g, b) != (0, 0, 0):
                    sample_colors.append((r, g, b))
                if len(sample_colors) >= 3:
                    break
            
            print(f"   Couleurs encodées échantillon: {sample_colors}")
            
            # Envoyer au masque
            print("   Envoi au masque...")
            await mask.set_scrolling_text(f"TEST {color_name}", "steady", 0)
            
            print(f"   ✅ {color_name} envoyé - Vérifiez le masque!")
            
            # Attendre confirmation utilisateur
            input(f"   Pressez Entrée quand vous avez vérifié la couleur {color_name}...")
        
        print("\n📊 RÉSUMÉ DU DIAGNOSTIC:")
        print("1. Vérifiez que chaque couleur s'affiche correctement sur le masque")
        print("2. Si toutes les couleurs apparaissent en blanc:")
        print("   - Le problème vient du masque lui-même")
        print("   - Ou du firmware qui ignore les couleurs")
        print("3. Si certaines couleurs fonctionnent:")
        print("   - Le problème vient de l'encodage de ces couleurs spécifiques")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        try:
            await mask.disconnect()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_color_transmission())
