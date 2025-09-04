#!/usr/bin/env python3
"""
🎮 Launcher pour le Contrôleur Clavier Masque LED
================================================

Script de démarrage simplifié inspiré de shining-mask
"""

import sys
import os

def main():
    print("🎮 === CONTRÔLEUR CLAVIER MASQUE LED ===")
    print("Inspiré du projet shining-mask de shawnrancatore")
    print("Remplace la manette Wii par un contrôle clavier\n")
    
    print("Options disponibles:")
    print("1. 🎯 Contrôleur interactif (recommandé)")
    print("2. 🧪 Test automatisé")
    print("3. 📋 Aide et documentation")
    print("4. ❌ Quitter")
    
    while True:
        try:
            choice = input("\n🎯 Votre choix (1-4): ").strip()
            
            if choice == '1':
                print("\n🚀 Lancement du contrôleur interactif...")
                print("📋 Appuyez sur 'H' dans le contrôleur pour l'aide")
                print("⚠️  Permissions root peuvent être requises pour le clavier")
                os.system(f"{sys.executable} src/simplified_keyboard_controller.py")
                break
                
            elif choice == '2':
                print("\n🧪 Lancement des tests automatisés...")
                os.system(f"{sys.executable} test_simplified_controller.py")
                break
                
            elif choice == '3':
                print("\n📋 Documentation du contrôleur clavier:")
                print("-" * 50)
                show_help()
                
            elif choice == '4':
                print("\n👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide. Utilisez 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

def show_help():
    """Affiche l'aide complète"""
    help_text = """
🎮 CONTRÔLEUR CLAVIER MASQUE LED

📸 IMAGES PRÉCHARGÉES (comme shining-mask):
   Q W E R T  →  Images 1-5
   A S D F G  →  Images 6-10  
   Z X C V B  →  Images 11-15

🎬 ANIMATIONS:
   ↑ (Haut)      →  Pulse (pulsation)
   ↓ (Bas)       →  Wave (vague)
   ← (Gauche)    →  Fire (feu)
   → (Droite)    →  Rain (pluie)
   SPACE         →  Matrix

🎭 ACTIONS SPÉCIALES:
   ENTER         →  Clignotement manuel
   BACKSPACE     →  Image aléatoire (comme bouton C Wii)
   TAB           →  Effacer écran

🎨 COULEURS RAPIDES:
   Shift+R       →  Rouge
   Shift+G       →  Vert
   Shift+B       →  Bleu
   Shift+W       →  Blanc

⚙️ CONTRÔLES SYSTÈME:
   H             →  Aide dans le contrôleur
   ESC           →  Quitter

🎯 FONCTIONNALITÉS HÉRITÉES DE SHINING-MASK:
   • 20 emplacements d'images préchargées
   • Clignotement automatique (4% chance/100ms)
   • Séquences d'animation à 12 FPS
   • Communication BLE chiffrée AES-128
   • Gestion d'erreurs et reconnexion

🔧 ARCHITECTURE:
   • src/simplified_keyboard_controller.py  - Contrôleur principal
   • src/modules/                          - Modules de base
   • test_simplified_controller.py         - Tests automatisés

📋 DOCUMENTATION COMPLÈTE:
   Voir KEYBOARD_CONTROLLER_README.md
"""
    print(help_text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
