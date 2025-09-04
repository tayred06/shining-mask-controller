#!/usr/bin/env python3
"""
Test simple du contrôleur clavier simplifié
"""
import asyncio
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, '/Users/mathieu/my-python-project/src')

from simplified_keyboard_controller import SimplifiedKeyboardController

async def test_simplified_controller():
    """Test du contrôleur simplifié"""
    print("🚀 Test du contrôleur clavier simplifié")
    
    controller = SimplifiedKeyboardController()
    
    # Test de connexion
    if await controller.connect():
        print("✅ Connexion réussie!")
        
        # Test des patterns texte
        print("� Test des patterns texte...")
        for i in [1, 3, 5, 7, 9]:
            await controller.send_text_pattern(i)
            print(f"   Pattern {i} affiché")
            await asyncio.sleep(0.5)
        
        # Test de clignotement
        print("👁️ Test du clignotement...")
        await controller.trigger_blink_sequence()
        
        # Test des couleurs
        print("🎨 Test des couleurs...")
        colors = ['red', 'green', 'blue', 'white']
        for color in colors:
            await controller.handle_color_change(color)
            print(f"   Couleur {color}")
            await asyncio.sleep(0.5)
        
        print("✅ Tests terminés!")
        
        # Afficher l'aide
        controller.show_help()
        
    else:
        print("❌ Connexion échouée")
    
    if controller.client:
        await controller.client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(test_simplified_controller())
    except KeyboardInterrupt:
        print("\n👋 Test interrompu")
    except Exception as e:
        print(f"❌ Erreur: {e}")
