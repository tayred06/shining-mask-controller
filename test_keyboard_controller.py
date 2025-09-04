#!/usr/bin/env python3
"""
Test simple du contrôleur clavier
"""
import asyncio
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, '/Users/mathieu/my-python-project/src')

from keyboard_controller import KeyboardMaskController

async def test_keyboard_controller():
    """Test simple sans clavier réel"""
    print("🚀 Test du contrôleur clavier")
    
    controller = KeyboardMaskController()
    
    # Test de connexion
    print("🔄 Test de connexion...")
    if await controller.connect():
        print("✅ Connexion réussie!")
        
        # Test d'envoi d'image
        print("🎬 Test d'envoi d'image préchargée...")
        await controller.send_preloaded_image(1)
        await asyncio.sleep(1)
        
        await controller.send_preloaded_image(5)
        await asyncio.sleep(1)
        
        print("🎨 Test de changement de couleur...")
        await controller.handle_color_change('red')
        await asyncio.sleep(1)
        
        await controller.handle_color_change('blue')
        await asyncio.sleep(1)
        
        print("✅ Tests terminés!")
        
    else:
        print("❌ Connexion échouée")
    
    if controller.client:
        await controller.client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(test_keyboard_controller())
    except KeyboardInterrupt:
        print("\n👋 Test interrompu")
    except Exception as e:
        print(f"❌ Erreur: {e}")
