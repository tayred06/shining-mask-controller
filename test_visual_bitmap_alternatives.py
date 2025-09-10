#!/usr/bin/env python3
"""
🔍 TEST VISUEL BITMAP ALTERNATIVES - Observation attentive
===========================================================

Test approfondi des commandes bitmap alternatives avec 
observation visuelle pour détecter tout affichage sans flèche.
"""

import asyncio
import sys
import os
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class BitmapAlternativeTester(MaskTextDisplay):
    """Testeur pour les commandes bitmap alternatives"""
    
    def __init__(self):
        super().__init__()
    
    async def test_bitmap_command_visual(self, cmd, description):
        """Test visuel d'une commande bitmap avec observation"""
        print(f"\n🔍 TEST VISUEL: {cmd} ({description})")
        print("=" * 50)
        
        # Préparer des données bitmap simples
        simple_bitmap = [
            [255, 0, 0, 0, 0, 0, 255, 0],  # Points rouges
            [0, 255, 0, 0, 0, 255, 0, 0],  # Points verts
            [0, 0, 255, 0, 255, 0, 0, 0],  # Points bleus
            [0, 0, 0, 255, 0, 0, 0, 0],    # Point blanc centre
        ]
        
        # Test avec différentes structures de données
        test_variations = [
            ("Format 1", [0, 32, 0, 16, 0]),  # Taille standard
            ("Format 2", [32, 16]),           # Taille simple  
            ("Format 3", [1, 1, 1, 1]),       # Minimal
            ("Format 4", [255, 255, 0, 0]),   # Couleurs max
        ]
        
        for variation_name, params in test_variations:
            print(f"\n📱 {variation_name}: {params}")
            
            try:
                # Construire la commande
                test_cmd = bytearray([len(cmd) + 1])
                test_cmd.extend(cmd.encode())
                test_cmd.extend(params)
                while len(test_cmd) < 16:
                    test_cmd.append(0)
                
                print(f"📤 Envoi: {test_cmd.hex()}")
                
                # Chiffrer et envoyer
                encrypted = self.cipher.encrypt(bytes(test_cmd))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
                
                # Observer pendant 2 secondes
                await asyncio.sleep(2)
                
                # Vérifier réponse
                if self.responses:
                    response = self.responses[-1]
                    print(f"📨 Réponse: {response}")
                else:
                    print("📨 Aucune réponse")
                
                # DEMANDER À L'UTILISATEUR
                user_input = input("👁️  VOYEZ-VOUS quelque chose d'affiché? (o/n/flèche): ").lower()
                
                if user_input == 'o':
                    print(f"🎉 {cmd} FONCTIONNE! Affichage détecté!")
                    arrow_input = input("🔍 Y a-t-il une FLÈCHE visible? (o/n): ").lower()
                    
                    if arrow_input == 'n':
                        print(f"🚀 SOLUTION TROUVÉE! {cmd} affiche SANS flèche!")
                        await self.test_bitmap_command_deeper(cmd, params)
                        return True
                    else:
                        print(f"⚠️ {cmd} affiche mais avec flèche")
                
                elif user_input == 'flèche':
                    print(f"⚠️ {cmd} montre juste la flèche")
                else:
                    print(f"❌ {cmd} - variation {variation_name} sans effet")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Erreur avec {cmd}: {e}")
        
        return False
    
    async def test_bitmap_command_deeper(self, cmd, working_params):
        """Test approfondi d'une commande qui fonctionne"""
        print(f"\n🔬 TEST APPROFONDI DE {cmd}")
        print("=" * 40)
        
        # Test avec vraies données bitmap
        print("📝 Test avec données bitmap réelles...")
        
        # Créer un simple pattern
        bitmap_columns = [
            [255, 0, 255, 0, 255, 0, 255, 0],  # Rayures
            [0, 255, 0, 255, 0, 255, 0, 255],
            [255, 255, 0, 0, 255, 255, 0, 0],
            [0, 0, 255, 255, 0, 0, 255, 255],
        ]
        
        # Encoder
        bitmap_data = self.encode_bitmap(bitmap_columns)
        
        try:
            # Test 1: Juste les paramètres
            test_cmd = bytearray([len(cmd) + 1])
            test_cmd.extend(cmd.encode())
            test_cmd.extend(working_params)
            while len(test_cmd) < 16:
                test_cmd.append(0)
            
            encrypted = self.cipher.encrypt(bytes(test_cmd))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
            
            await asyncio.sleep(1)
            print("📤 Commande envoyée")
            
            # Test 2: Envoyer des données sur le canal data
            if len(bitmap_data) > 0:
                print("📦 Envoi données bitmap sur canal data...")
                chunk = bitmap_data[:16]  # Premier chunk
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
                
                await asyncio.sleep(1)
                user_input = input("👁️ Maintenant, voyez-vous quelque chose? (o/n): ").lower()
                
                if user_input == 'o':
                    print(f"🎉 {cmd} + données fonctionne!")
                    return True
            
        except Exception as e:
            print(f"❌ Erreur test approfondi: {e}")
        
        return False
    
    async def test_all_promising_commands(self):
        """Test de toutes les commandes prometteuses"""
        print("🎯 TEST COMPLET COMMANDES BITMAP ALTERNATIVES")
        print("=" * 55)
        print("👁️ IMPORTANT: Regardez ATTENTIVEMENT le masque!")
        print("   Même un petit point ou changement est significatif")
        print()
        
        # Commandes à tester en priorité
        promising_commands = [
            ("BITS", "Bitmap bits"),
            ("MAPS", "Bitmap maps"),  
            ("DATA", "Data command"),
            ("BUFF", "Buffer command"),
            ("FRAM", "Frame buffer"),
            ("VRAM", "Video RAM"),
            ("DRAW", "Draw command"),
            ("SHOW", "Show command"),
            ("DISP", "Display command"),
            ("REND", "Render command"),
        ]
        
        successful_commands = []
        
        for cmd, desc in promising_commands:
            print(f"\n{'='*60}")
            print(f"🧪 COMMANDE: {cmd}")
            print(f"{'='*60}")
            
            success = await self.test_bitmap_command_visual(cmd, desc)
            
            if success:
                successful_commands.append(cmd)
                print(f"✅ {cmd} ajouté aux commandes réussies!")
            
            # Pause entre tests
            await asyncio.sleep(2)
        
        # Résumé
        print(f"\n🎯 RÉSUMÉ DES TESTS")
        print("=" * 25)
        
        if successful_commands:
            print("🎉 COMMANDES QUI FONCTIONNENT:")
            for cmd in successful_commands:
                print(f"  ✅ {cmd}")
            print()
            print("🚀 Nous avons trouvé des alternatives à DATS!")
        else:
            print("❌ Aucune commande alternative trouvée")
            print("   La flèche DATS reste inévitable")
        
        return successful_commands

async def run_visual_bitmap_test():
    """Lance le test visuel complet"""
    tester = BitmapAlternativeTester()
    
    if await tester.connect():
        try:
            print("🔍 DÉTECTION VISUELLE - COMMANDES BITMAP")
            print("=" * 45)
            print("Ce test va vérifier si certaines commandes")
            print("peuvent afficher du contenu SANS la flèche DATS")
            print()
            print("⚠️ ATTENTION: Regardez le masque très attentivement!")
            input("Appuyez sur ENTRÉE quand vous êtes prêt...")
            
            successful = await tester.test_all_promising_commands()
            
            if successful:
                print("\n🎉 SOLUTION ALTERNATIVE TROUVÉE!")
                print(f"Les commandes {successful} peuvent remplacer DATS!")
            else:
                print("\n😔 Aucune alternative trouvée")
                print("La solution de compromis reste la meilleure option")
            
        except KeyboardInterrupt:
            print("\n⏹️ Test arrêté par l'utilisateur")
        finally:
            await tester.disconnect()
    else:
        print("❌ Connexion impossible")

if __name__ == "__main__":
    asyncio.run(run_visual_bitmap_test())
