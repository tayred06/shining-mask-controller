#!/usr/bin/env python3
"""
🎮 Uploader Simplifié d'Images Texte pour Contrôleur Clavier
============================================================

Au lieu d'uploader des images bitmap complexes, ce script utilise
le système de texte existant pour créer des "images" simples et rapides
avec des caractères ASCII et symboles Unicode.

Cette approche fonctionne mieux avec le protocole BLE existant.
"""

import asyncio
import sys
import os

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class SimpleTextImageUploader:
    """
    Uploader simplifié qui crée des "images" à partir de texte
    Compatible avec le système BLE existant
    """
    
    def __init__(self):
        self.controller = MaskTextDisplay()
        self.test_patterns = self.create_simple_patterns()
    
    def create_simple_patterns(self):
        """
        Crée 20 patterns texte simples pour remplacer les images
        """
        patterns = [
            # Images 1-5: Émotions de base
            {"name": "Sourire", "text": ":)", "color": (255, 255, 0)},      # Jaune
            {"name": "Neutre", "text": ":|", "color": (255, 255, 255)},     # Blanc
            {"name": "Triste", "text": ":(", "color": (0, 100, 255)},       # Bleu
            {"name": "Surpris", "text": ":O", "color": (255, 100, 0)},      # Orange
            {"name": "Colère", "text": ">:(", "color": (255, 0, 0)},        # Rouge
            
            # Images 6-10: Émotions avancées (pour clignotement)
            {"name": "Clin œil", "text": ";)", "color": (255, 255, 0)},     # Pour clignotement
            {"name": "Endormi", "text": "-_-", "color": (100, 100, 100)},   # Pour clignotement
            {"name": "Cœur", "text": "<3", "color": (255, 0, 100)},         # Rose
            {"name": "Cool", "text": "B)", "color": (0, 255, 255)},         # Cyan
            {"name": "Étourdi", "text": "@_@", "color": (255, 0, 255)},     # Magenta
            
            # Images 11-15: Symboles et formes
            {"name": "Étoile", "text": "*", "color": (255, 255, 0)},        # Jaune
            {"name": "Carré", "text": "■", "color": (255, 255, 255)},       # Blanc
            {"name": "Rond", "text": "●", "color": (0, 255, 0)},            # Vert
            {"name": "Plus", "text": "+", "color": (255, 0, 0)},            # Rouge
            {"name": "Diamant", "text": "♦", "color": (0, 100, 255)},       # Bleu
            
            # Images 16-20: Texte et effets
            {"name": "OK", "text": "OK", "color": (0, 255, 0)},             # Vert
            {"name": "Non", "text": "NO", "color": (255, 0, 0)},            # Rouge
            {"name": "Oui", "text": "YES", "color": (0, 255, 0)},           # Vert
            {"name": "Aide", "text": "?", "color": (255, 255, 0)},          # Jaune
            {"name": "Exclamation", "text": "!", "color": (255, 100, 0)},    # Orange
        ]
        
        return patterns
    
    async def upload_text_pattern(self, pattern_id, pattern):
        """Upload un pattern texte comme 'image'"""
        try:
            print(f"📝 Upload pattern {pattern_id}: {pattern['name']} = '{pattern['text']}'")
            
            # Afficher le texte avec la couleur directement
            await self.controller.display_text(pattern['text'], color=pattern['color'])
            
            print(f"✅ Pattern {pattern_id} ({pattern['name']}) uploadé!")
            
            # Petit délai pour voir le résultat
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur pattern {pattern_id}: {e}")
            return False
    
    async def demo_all_patterns(self):
        """Démo de tous les patterns"""
        print("🎮 === DÉMO DES PATTERNS TEXTE ===")
        print("Simulation des 20 images du projet shining-mask")
        print("-" * 50)
        
        # Connexion
        try:
            await self.controller.connect()
            print("✅ Connecté au masque!")
        except Exception as e:
            print(f"❌ Connexion impossible: {e}")
            return False
        
        # Test de chaque pattern
        success_count = 0
        for i, pattern in enumerate(self.test_patterns, 1):
            print(f"\n🔄 Test {i}/20...")
            if await self.upload_text_pattern(i, pattern):
                success_count += 1
            else:
                print(f"❌ Échec pattern {i}")
        
        # Déconnexion
        await self.controller.disconnect()
        
        # Rapport final
        print(f"\n🎯 === RAPPORT FINAL ===")
        print(f"Patterns testés: {success_count}/20")
        
        if success_count >= 15:  # Au moins 15 sur 20
            print("🎉 SUCCESS! Votre masque est prêt!")
            print("🎮 Les 'images' texte sont disponibles pour le contrôleur clavier!")
            return True
        else:
            print(f"⚠️ Seulement {success_count} patterns fonctionnels")
            return False
    
    def show_patterns_list(self):
        """Affiche la liste des patterns disponibles"""
        print("📋 === PATTERNS DISPONIBLES ===")
        print("Ces 'images' texte remplacent les 20 images du projet shining-mask:")
        print("-" * 60)
        
        for i, pattern in enumerate(self.test_patterns, 1):
            r, g, b = pattern['color']
            color_name = self.get_color_name(r, g, b)
            print(f"Image {i:2d}: {pattern['name']:12} = '{pattern['text']:4}' ({color_name})")
        
        print("\n🎮 Mapping clavier:")
        print("Q W E R T  → Images 1-5   (Émotions de base)")
        print("A S D F G  → Images 6-10  (Émotions avancées)")  
        print("Z X C V B  → Images 11-15 (Symboles)")
        print("Images 16-20 disponibles pour extension")
    
    def get_color_name(self, r, g, b):
        """Retourne le nom de la couleur"""
        if r > 200 and g > 200 and b < 50:
            return "Jaune"
        elif r > 200 and g < 50 and b < 50:
            return "Rouge"
        elif r < 50 and g > 200 and b < 50:
            return "Vert"
        elif r < 50 and g < 50 and b > 200:
            return "Bleu"
        elif r > 200 and g > 200 and b > 200:
            return "Blanc"
        elif r < 100 and g < 100 and b < 100:
            return "Gris"
        else:
            return "Mixte"

async def main():
    """Point d'entrée principal"""
    print("🎮 === UPLOADER PATTERNS TEXTE SIMPLIFIÉ ===")
    print("Alternative simple aux images bitmap complexes")
    print("-" * 50)
    
    uploader = SimpleTextImageUploader()
    
    while True:
        print("\nOptions disponibles:")
        print("1. 📋 Voir la liste des patterns")
        print("2. 🎬 Démo de tous les patterns")
        print("3. 🎯 Test d'un pattern spécifique")
        print("4. ❌ Quitter")
        
        try:
            choice = input("\n🎯 Votre choix (1-4): ").strip()
            
            if choice == '1':
                uploader.show_patterns_list()
                
            elif choice == '2':
                print("\n🎬 Lancement de la démo complète...")
                await uploader.demo_all_patterns()
                
            elif choice == '3':
                uploader.show_patterns_list()
                pattern_id = input("\n📝 ID du pattern à tester (1-20): ").strip()
                try:
                    pid = int(pattern_id)
                    if 1 <= pid <= 20:
                        pattern = uploader.test_patterns[pid-1]
                        await uploader.controller.connect()
                        await uploader.upload_text_pattern(pid, pattern)
                        await uploader.controller.disconnect()
                    else:
                        print("❌ ID invalide (1-20)")
                except ValueError:
                    print("❌ ID invalide")
                    
            elif choice == '4':
                print("\n👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide. Utilisez 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n⚠️ Interruption par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())
