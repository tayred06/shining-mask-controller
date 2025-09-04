#!/usr/bin/env python3
"""
Animation pulse simple utilisant seulement les commandes de couleur
"""
import asyncio
import sys
import os
import math
import time

# Ajouter le chemin du projet
sys.path.insert(0, '/Users/mathieu/my-python-project/src')

from modules.core.base_controller import BaseMaskController

async def simple_pulse_animation():
    controller = BaseMaskController()
    
    try:
        # Connexion
        print("🔄 Connexion...")
        if await controller.connect():
            print("✅ Connecté!")
            
            # Animation pulse simple avec changement de couleur
            print("🎬 Animation pulse simple...")
            duration = 3.0
            start_time = time.time()
            
            while (time.time() - start_time) < duration:
                current_time = time.time() - start_time
                
                # Calculer l'intensité du pulse
                pulse_intensity = (math.sin(current_time * 2 * math.pi) + 1) / 2
                
                # Changer la luminosité en modifiant la couleur
                brightness = int(255 * pulse_intensity)
                
                # Envoyer commande de couleur au lieu d'une image
                color_command = f"FC{brightness:02X}{brightness:02X}{brightness:02X}"
                await controller.send_command(color_command.encode())
                
                # Attendre 100ms entre les changements
                await asyncio.sleep(0.1)
            
            # Remettre en blanc
            await controller.send_command("FCFFFFFF".encode())
            print("✅ Animation terminée!")
            
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
    asyncio.run(simple_pulse_animation())
