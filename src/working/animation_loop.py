#!/usr/bin/env python3
"""
Script pour créer une animation en boucle avec les 7 images custom.
Fait défiler les images 1 à 7 en boucle pour créer une animation fluide.
"""

import asyncio
import sys
import os

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ultimate_text_display_with_bold import CompleteMaskController
except ImportError:
    # Fallback si on est exécuté depuis la racine
    sys.path.append(os.path.join(os.getcwd(), 'src', 'working'))
    from ultimate_text_display_with_bold import CompleteMaskController

class AnimationLooper(CompleteMaskController):
    async def show_image(self, image_num, bank=1):
        """
        Affiche une image/animation prédéfinie du masque.
        bank 0 = Animations système (pré-enregistrées)
        bank 1 = Animations personnalisées (uploadées)
        """
        try:
            # Construction de la commande "PLAY"
            # Format: [Length] [Command String] [Bank] [ImageID]
            cmd_str = "PLAY"
            args = bytes([bank, image_num])
            
            payload = bytearray()
            payload.append(len(cmd_str) + len(args))
            payload.extend(cmd_str.encode('ascii'))
            payload.extend(args)
            
            await self.send_command(payload)
            return True
        except Exception as e:
            print(f"❌ Erreur lors du lancement de l'animation {image_num}: {e}")
            return False

async def main():
    controller = AnimationLooper()
    
    print("\n🎬 ANIMATION EN BOUCLE - 7 IMAGES CUSTOM")
    print("==========================================")
    print("Ce script fait défiler les 7 images custom en boucle.")
    
    print("\n🔄 Connexion au masque en cours...")
    try:
        await controller.connect()
        print("✅ Masque connecté avec succès !")
    except Exception as e:
        print(f"❌ Impossible de se connecter au masque : {e}")
        print("Assurez-vous que le masque est allumé et à proximité.")
        return

    # Paramètres de l'animation
    num_images = 7  # Nombre d'images custom
    delay = 0.05  # Délai entre chaque image (en secondes) - ajustez pour la vitesse
    
    print(f"\n▶️  Démarrage de l'animation ({num_images} images, {delay}s par image)")
    print("Appuyez sur Ctrl+C pour arrêter.\n")
    
    try:
        frame_count = 0
        while True:
            for image_id in range(1, num_images + 1):
                await controller.show_image(image_id, bank=1)
                await asyncio.sleep(delay)
                frame_count += 1
                
                # Afficher un compteur toutes les 10 frames
                if frame_count % 10 == 0:
                    print(f"🎞️  Frame {frame_count} (Image {image_id}/7)")
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Animation arrêtée après {frame_count} frames.")
    except Exception as e:
        print(f"\n❌ Erreur pendant l'animation : {e}")
    finally:
        # Déconnexion propre
        if controller.client:
            await controller.disconnect()
            print("🔌 Déconnecté du masque.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAu revoir ! 👋")
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
