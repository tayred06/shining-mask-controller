#!/usr/bin/env python3
"""
Test rapide pour l'animation pulse
"""
import asyncio
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, '/Users/mathieu/my-python-project/src')

from unified_controller import UnifiedMaskController

async def test_pulse():
    controller = UnifiedMaskController()
    
    try:
        # Connexion
        print("🔄 Connexion...")
        if await controller.connect():
            print("✅ Connecté!")
            
            # Test animation pulse courte
            print("🎬 Test animation pulse...")
            await controller.play_animation("pulse", duration=3.0)  # 3 secondes seulement
            print("✅ Test terminé!")
            
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if controller.client:
            await controller.client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_pulse())
