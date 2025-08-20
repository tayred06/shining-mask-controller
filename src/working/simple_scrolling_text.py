#!/usr/bin/env python3
"""
Script simple pour afficher du texte défilant sur le masque LED
Usage: python simple_scrolling_text.py "Votre texte ici"
"""

import asyncio
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

async def display_scrolling_text(text, mode="scroll_right", speed=50):
    """
    Affiche du texte défilant de manière simple
    
    Args:
        text: Texte à afficher
        mode: Mode de défilement ('scroll_left', 'scroll_right', 'blink', 'steady')
        speed: Vitesse (0-255, plus haut = plus rapide)
    """
    mask = ScrollingMaskController()
    
    try:
        print(f"🔄 Affichage de '{text}' en mode {mode}...")
        
        # Connexion
        await mask.connect()
        
        # Configuration
        await mask.set_brightness(80)
        await mask.set_background_color(0, 0, 0)  # Fond noir
        await mask.set_foreground_color(255, 255, 255)  # Texte blanc
        
        # Affichage du texte défilant
        await mask.set_scrolling_text(text, mode, speed)
        
        print(f"✅ Texte '{text}' affiché en mode {mode}!")
        print("Le texte défile maintenant sur votre masque.")
        
        # Garder le script actif pour observer le défilement
        print("\nAppuyez sur Ctrl+C pour arrêter...")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mask.disconnect()
        print("Déconnecté du masque")

async def interactive_mode():
    """Mode interactif pour tester différents textes et modes"""
    mask = ScrollingMaskController()
    
    try:
        await mask.connect()
        await mask.set_brightness(80)
        await mask.set_background_color(0, 0, 0)
        await mask.set_foreground_color(255, 255, 255)
        
        print("\n🎮 Mode interactif - Texte défilant")
        print("Modes disponibles:")
        print("  1. scroll_left   - Défilement vers la gauche")
        print("  2. scroll_right  - Défilement vers la droite") 
        print("  3. blink         - Texte clignotant")
        print("  4. steady        - Texte fixe")
        print("\nTapez 'quit' pour quitter\n")
        
        while True:
            try:
                # Demander le texte
                text = input("Texte à afficher: ").strip()
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not text:
                    continue
                
                # Demander le mode
                print("\nMode (scroll_left/scroll_right/blink/steady) [scroll_left]: ", end="")
                mode = input().strip() or "scroll_left"
                
                if mode not in ['scroll_left', 'scroll_right', 'blink', 'steady']:
                    print(f"Mode '{mode}' non reconnu, utilisation de 'scroll_left'")
                    mode = 'scroll_left'
                
                # Demander la vitesse
                print("Vitesse (0-255) [50]: ", end="")
                speed_input = input().strip()
                try:
                    speed = int(speed_input) if speed_input else 50
                    speed = max(0, min(255, speed))  # Limiter entre 0 et 255
                except ValueError:
                    speed = 50
                    print("Vitesse invalide, utilisation de 50")
                
                # Afficher le texte
                print(f"\n🔄 Affichage de '{text}' (mode: {mode}, vitesse: {speed})")
                await mask.set_scrolling_text(text, mode, speed)
                print("✅ Texte affiché! Entrez un nouveau texte ou 'quit' pour arrêter\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    finally:
        await mask.disconnect()
        print("Au revoir!")

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1:
        # Mode ligne de commande
        text = " ".join(sys.argv[1:])
        
        # Options par défaut
        mode = "scroll_left"
        speed = 50
        
        # Vérifier les options
        if "--mode" in sys.argv:
            mode_index = sys.argv.index("--mode")
            if mode_index + 1 < len(sys.argv):
                mode = sys.argv[mode_index + 1]
                # Retirer les options des arguments
                text = " ".join([arg for i, arg in enumerate(sys.argv[1:], 1) 
                               if i not in [mode_index, mode_index + 1]])
        
        if "--speed" in sys.argv:
            speed_index = sys.argv.index("--speed")
            if speed_index + 1 < len(sys.argv):
                try:
                    speed = int(sys.argv[speed_index + 1])
                except ValueError:
                    speed = 50
                # Retirer les options des arguments
                text = " ".join([arg for i, arg in enumerate(sys.argv[1:], 1) 
                               if i not in [speed_index, speed_index + 1]])
        
        asyncio.run(display_scrolling_text(text, mode, speed))
    else:
        # Mode interactif
        print("Usage: python simple_scrolling_text.py \"Votre texte\"")
        print("   ou: python simple_scrolling_text.py \"Texte\" --mode scroll_right --speed 70")
        print("\nLancement du mode interactif...\n")
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()
