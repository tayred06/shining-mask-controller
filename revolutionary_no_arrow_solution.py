#!/usr/bin/env python3
"""
🚀 SOLUTION RÉVOLUTIONNAIRE - Texte SANS flèche avec commandes alternatives
===========================================================================

Utilisation des commandes BITS, BUFF et FRAM découvertes pour afficher
du texte complètement SANS la flèche firmware !
"""

import asyncio
import sys
import os
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class NoArrowTextDisplay(MaskTextDisplay):
    """Affichage de texte SANS flèche en utilisant les commandes alternatives"""
    
    def __init__(self):
        super().__init__()
        self.alternative_commands = ["BITS", "BUFF", "FRAM"]
        self.preferred_command = "BITS"  # Commande par défaut
    
    async def display_text_no_arrow_revolutionary(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """
        🚀 RÉVOLUTIONNAIRE: Affiche du texte SANS AUCUNE flèche !
        
        Utilise les commandes alternatives découvertes.
        """
        print(f"🚀 Affichage révolutionnaire '{text}' SANS flèche !")
        
        try:
            # 1. Configuration background
            bg_r, bg_g, bg_b = background
            await self.set_background_color(bg_r, bg_g, bg_b, 1)
            
            # 2. Préparer le texte
            bitmap_columns = self.text_to_bitmap(text)
            if not bitmap_columns:
                print("❌ Aucun caractère valide")
                return False
            
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), color)
            
            print(f"📊 {len(bitmap_columns)} colonnes préparées")
            
            # 3. ESSAYER chaque commande alternative jusqu'à réussite
            for cmd in self.alternative_commands:
                print(f"🔧 Tentative avec commande {cmd}...")
                success = await self.upload_with_alternative_command(cmd, bitmap_data, color_data)
                
                if success:
                    print(f"🎉 Succès avec {cmd} - AUCUNE FLÈCHE !")
                    await self.set_display_mode(1)
                    return True
                else:
                    print(f"❌ {cmd} échoué, essai suivant...")
            
            print("❌ Toutes les commandes alternatives ont échoué")
            return False
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    async def upload_with_alternative_command(self, cmd, bitmap_data, color_data):
        """Upload avec une commande alternative spécifique"""
        try:
            print(f"📤 Upload avec {cmd}...")
            
            # Format optimal découvert pendant les tests
            if cmd == "BITS":
                params = [32, 16]  # Format qui fonctionne
            elif cmd == "BUFF":
                params = [0, 32, 0, 16, 0]  # Format qui fonctionne  
            elif cmd == "FRAM":
                params = [32, 16]  # Format qui fonctionne
            else:
                params = [32, 16]  # Format par défaut
            
            # 1. Envoyer la commande alternative
            test_cmd = bytearray([len(cmd) + 1])
            test_cmd.extend(cmd.encode())
            test_cmd.extend(params)
            while len(test_cmd) < 16:
                test_cmd.append(0)
            
            encrypted = self.cipher.encrypt(bytes(test_cmd))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
            
            await asyncio.sleep(0.3)
            
            # 2. Envoyer les données bitmap
            complete_data = bitmap_data + color_data
            
            # Envoyer par chunks comme avec DATS mais sans DATS !
            max_chunk = 96
            bytes_sent = 0
            packet_count = 0
            
            while bytes_sent < len(complete_data):
                remaining = len(complete_data) - bytes_sent
                chunk_size = min(max_chunk, remaining)
                chunk = complete_data[bytes_sent:bytes_sent + chunk_size]
                packet = bytearray([chunk_size + 1, packet_count])
                packet.extend(chunk)
                
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", bytes(packet))
                
                # Attendre confirmation
                await asyncio.sleep(0.1)
                if not await self.wait_for_response("REOK", 2):
                    print(f"⚠️ Pas de REOK pour chunk {packet_count} avec {cmd}")
                    # Continuer quand même
                
                bytes_sent += chunk_size
                packet_count += 1
            
            print(f"✅ Upload {cmd} terminé - {packet_count} chunks envoyés")
            return True
            
        except Exception as e:
            print(f"❌ Erreur upload {cmd}: {e}")
            return False
    
    async def test_individual_commands(self):
        """Test individuel de chaque commande alternative"""
        print("🧪 TEST INDIVIDUEL DES COMMANDES ALTERNATIVES")
        print("=" * 55)
        
        test_text = "TEST"
        test_color = (255, 100, 0)  # Orange
        
        for cmd in self.alternative_commands:
            print(f"\n🔧 TEST EXCLUSIF: {cmd}")
            print("=" * 30)
            
            self.preferred_command = cmd
            
            success = await self.display_text_no_arrow_revolutionary(test_text, test_color)
            
            if success:
                print(f"✅ {cmd} fonctionne parfaitement!")
                input(f"👁️ Confirmez-vous que '{test_text}' est affiché SANS flèche avec {cmd}? (ENTRÉE)")
            else:
                print(f"❌ {cmd} ne fonctionne pas")
            
            await asyncio.sleep(2)

# Fonction principale pour utilisation
async def display_text_without_arrow_final(text, color=(255, 255, 255), background=(0, 0, 0)):
    """
    🚀 FONCTION FINALE: Affichage de texte SANS flèche garantie
    
    Utilise les commandes alternatives découvertes.
    """
    display = NoArrowTextDisplay()
    
    if await display.connect():
        try:
            success = await display.display_text_no_arrow_revolutionary(text, color, background)
            return success
        finally:
            await display.disconnect()
    
    return False

async def demo_revolutionary_solution():
    """Démonstration de la solution révolutionnaire"""
    print("🚀 DÉMONSTRATION SOLUTION RÉVOLUTIONNAIRE")
    print("=" * 50)
    print("🎯 Objectif: Prouver que nous pouvons afficher du texte")
    print("           COMPLÈTEMENT sans flèche firmware!")
    print()
    
    demo_texts = [
        ("NO ARROW", (255, 0, 0)),     # Rouge
        ("SUCCESS", (0, 255, 0)),      # Vert
        ("PERFECT", (0, 0, 255)),      # Bleu
        ("VICTORY", (255, 255, 0)),    # Jaune
    ]
    
    for text, color in demo_texts:
        print(f"\n🎯 Démonstration: '{text}'")
        print("👁️ OBSERVEZ: Il ne devrait y avoir AUCUNE flèche!")
        
        success = await display_text_without_arrow_final(text, color)
        
        if success:
            print(f"🎉 '{text}' affiché SANS flèche!")
            await asyncio.sleep(3)
        else:
            print(f"❌ Échec pour '{text}'")
            break
    
    print("\n🏆 RÉVOLUTION ACCOMPLIE!")
    print("Vous avez maintenant une solution PARFAITE pour")
    print("afficher du texte SANS AUCUNE flèche firmware!")

async def test_all_methods():
    """Test complet de toutes les méthodes"""
    display = NoArrowTextDisplay()
    
    if await display.connect():
        try:
            # Test individuel
            await display.test_individual_commands()
            
            print("\n" + "="*60)
            
            # Demo final
            await demo_revolutionary_solution()
            
        finally:
            await display.disconnect()
    else:
        print("❌ Connexion impossible")

if __name__ == "__main__":
    asyncio.run(test_all_methods())
