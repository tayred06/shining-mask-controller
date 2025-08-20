#!/usr/bin/env python3
"""
Test simple pour vérifier que le texte s'affiche correctement
avec l'implémentation mask-go compatible
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour importer mask_go_compatible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mask_go_compatible import MaskGoCompatible

async def test_text_display():
    mask = MaskGoCompatible()
    
    try:
        print("=== Test d'affichage de texte avec implémentation mask-go ===")
        
        # Connexion
        await mask.connect()
        
        # Configuration basique
        await mask.set_mode(1)  # Mode steady
        await mask.set_brightness(80)  # Luminosité élevée pour un bon contraste
        await mask.set_background_color(0, 0, 0)  # Fond noir
        
        # Test avec le texte problématique
        test_text = "SALUT"
        print(f"\nTest avec '{test_text}':")
        print("- Si le texte apparaît en entier et bien formé, le problème est résolu !")
        print("- Si le texte apparaît coupé en deux, il reste du travail à faire")
        
        await mask.set_text(test_text)
        
        # Attendre pour observer
        print("\nTexte affiché ! Vérifiez sur le masque...")
        await asyncio.sleep(5)
        
        # Test avec un texte plus long
        test_text2 = "Hello World"
        print(f"\nTest avec '{test_text2}':")
        await mask.set_text(test_text2)
        
        print("\nTexte affiché ! Observation terminée.")
        await asyncio.sleep(3)
        
        print("\n✅ Tests terminés avec succès !")
        print("Si les textes s'affichent correctement, l'implémentation mask-go a résolu le problème !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mask.disconnect()

if __name__ == "__main__":
    asyncio.run(test_text_display())
