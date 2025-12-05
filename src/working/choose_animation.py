#!/usr/bin/env python3
"""
Script pour choisir une animation pré-enregistrée sur le masque.
Permet de sélectionner une animation par son numéro sans avoir à saisir de texte.
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

class AnimationSelector(CompleteMaskController):
    async def show_image(self, image_num, bank=0):
        """
        Affiche une image/animation prédéfinie du masque.
        bank 0 = Animations système (pré-enregistrées)
        bank 1 = Animations personnalisées (uploadées)
        """
        try:
            # Construction de la commande "PLAY"
            # Format: [Length] [Command String] [Bank] [ImageID]
            # D'après les analyses, PLAY prend souvent 2 arguments : Bank et ID
            cmd_str = "PLAY"
            args = bytes([bank, image_num])
            
            payload = bytearray()
            payload.append(len(cmd_str) + len(args)) # Devrait être 6
            payload.extend(cmd_str.encode('ascii'))
            payload.extend(args)
            
            await self.send_command(payload)
            bank_name = "Système" if bank == 0 else "Custom"
            print(f"🖼️  Animation #{image_num} ({bank_name}) lancée !")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du lancement de l'animation {image_num}: {e}")
            return False

async def main():
    controller = AnimationSelector()
    
    print("\n🎭 SÉLECTEUR D'ANIMATIONS PRÉ-ENREGISTRÉES")
    print("===========================================")
    print("Ce script permet de lancer les animations stockées dans la mémoire du masque.")
    
    print("\n🔄 Connexion au masque en cours...")
    try:
        await controller.connect()
        print("✅ Masque connecté avec succès !")
    except Exception as e:
        print(f"❌ Impossible de se connecter au masque : {e}")
        print("Assurez-vous que le masque est allumé et à proximité.")
        return

    current_bank = 0 # 0 = Système, 1 = Custom

    while True:
        print("\n-------------------------------------------")
        bank_name = "SYSTÈME (Pré-enregistré)" if current_bank == 0 else "CUSTOM (Uploadé)"
        print(f"Mode actuel : {bank_name}")
        print("Commandes :")
        print(" - <nombre> : Lancer l'animation n° <nombre>")
        print(" - 's' ou 'sys' : Passer en mode Système")
        print(" - 'c' ou 'custom' : Passer en mode Custom")
        print(" - 'q' ou 'exit' : Quitter")
        
        choice = input("\nVotre choix > ").strip().lower()
        
        if choice in ['q', 'exit', 'quit']:
            print("Au revoir ! 👋")
            break
            
        if choice in ['s', 'sys', 'system']:
            current_bank = 0
            print("✅ Mode basculé sur : SYSTÈME")
            continue
            
        if choice in ['c', 'custom']:
            current_bank = 1
            print("✅ Mode basculé sur : CUSTOM")
            continue
            
        if not choice:
            continue
            
        try:
            anim_id = int(choice)
            if anim_id < 0 or anim_id > 255:
                print("⚠️  Le numéro doit être compris entre 0 et 255.")
                continue
                
            print(f"⏳ Envoi de la commande pour l'animation #{anim_id} (Bank {current_bank})...")
            await controller.show_image(anim_id, bank=current_bank)
            
        except ValueError:
            print("❌ Commande non reconnue. Entrez un nombre ou une commande.")
        except Exception as e:
            print(f"❌ Erreur inattendue : {e}")

    # Déconnexion propre
    if controller.client:
        await controller.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nArrêt du programme. Au revoir ! 👋")
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
