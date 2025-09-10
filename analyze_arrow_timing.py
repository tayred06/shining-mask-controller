#!/usr/bin/env python3
"""
🔍 ANALYSE FLÈCHE - Détection précise du moment d'apparition
===============================================================

Investigation pour comprendre exactement quand et comment
la flèche apparaît dans le processus d'upload.
"""

import asyncio
import sys
import os
import struct
import time

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class ArrowAnalyzer(MaskTextDisplay):
    """Analyseur pour détecter l'apparition de la flèche"""
    
    def __init__(self):
        super().__init__()
        self.step_delay = 1.0  # Délai entre chaque étape
    
    async def analyze_arrow_timing(self, text="TEST"):
        """Analyse étape par étape pour détecter quand la flèche apparaît"""
        print("🔍 ANALYSE DÉTAILLÉE DE L'APPARITION DE LA FLÈCHE")
        print("=" * 60)
        print("👁️  REGARDEZ LE MASQUE et DITES-MOI à quelle étape la flèche apparaît!")
        print()
        
        try:
            # Préparer les données
            bitmap_columns = self.text_to_bitmap(text)
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), (255, 0, 0))
            total_len = len(bitmap_data) + len(color_data)
            bitmap_len = len(bitmap_data)
            
            print(f"📊 Données préparées: {len(bitmap_columns)} colonnes")
            input("🔎 ÉTAPE 0: Masque au repos - Appuyez sur ENTRÉE pour continuer...")
            
            # ÉTAPE 1: Configuration background
            print("\n🔎 ÉTAPE 1: Configuration du background...")
            print("👁️  Y a-t-il une flèche MAINTENANT?")
            await self.set_background_color(0, 0, 0, 1)
            await asyncio.sleep(self.step_delay)
            input("Appuyez sur ENTRÉE si PAS de flèche, ou CTRL+C si flèche visible...")
            
            # ÉTAPE 2: Préparation DATS
            print("\n🔎 ÉTAPE 2: Préparation commande DATS...")
            print("👁️  Y a-t-il une flèche MAINTENANT?")
            
            dats_cmd = bytearray([9])
            dats_cmd.extend(b"DATS")
            dats_cmd.extend(struct.pack('>H', total_len))
            dats_cmd.extend(struct.pack('>H', bitmap_len))
            dats_cmd.extend([0])
            while len(dats_cmd) < 16:
                dats_cmd.append(0)
            
            encrypted_dats = self.cipher.encrypt(bytes(dats_cmd))
            print(f"📦 DATS préparé: {len(encrypted_dats)} bytes")
            await asyncio.sleep(self.step_delay)
            input("Appuyez sur ENTRÉE si PAS de flèche, ou CTRL+C si flèche visible...")
            
            # ÉTAPE 3: Envoi DATS
            print("\n🔎 ÉTAPE 3: ENVOI de la commande DATS...")
            print("👁️  🚨 ATTENTION: C'est ICI que la flèche pourrait apparaître!")
            
            self.responses.clear()
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted_dats)
            print("📤 DATS envoyé!")
            
            await asyncio.sleep(0.5)  # Laisser le temps à la flèche d'apparaître
            input("🔥 FLÈCHE VISIBLE MAINTENANT? (ENTRÉE=non, CTRL+C=oui)")
            
            # ÉTAPE 4: Attente DATSOK
            print("\n🔎 ÉTAPE 4: Attente de DATSOK...")
            if await self.wait_for_response("DATSOK", 5):
                print("📨 DATSOK reçu")
                await asyncio.sleep(self.step_delay)
                input("Flèche toujours visible? (ENTRÉE=non, CTRL+C=oui)")
            else:
                print("❌ Pas de DATSOK")
                return
            
            # ÉTAPE 5: Préparation chunks
            print("\n🔎 ÉTAPE 5: Préparation des chunks de données...")
            complete_data = bitmap_data + color_data
            print(f"📦 {len(complete_data)} bytes à envoyer en chunks")
            await asyncio.sleep(self.step_delay)
            input("Flèche toujours visible? (ENTRÉE=non, CTRL+C=oui)")
            
            # ÉTAPE 6: Envoi chunks (un par un avec pause)
            max_chunk = 96
            bytes_sent = 0
            packet_count = 0
            
            while bytes_sent < len(complete_data):
                remaining = len(complete_data) - bytes_sent
                chunk_size = min(max_chunk, remaining)
                chunk = complete_data[bytes_sent:bytes_sent + chunk_size]
                packet = bytearray([chunk_size + 1, packet_count])
                packet.extend(chunk)
                
                print(f"\n🔎 ÉTAPE 6.{packet_count + 1}: Envoi chunk {packet_count + 1}")
                print(f"📦 {chunk_size} bytes")
                
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", bytes(packet))
                
                await asyncio.sleep(0.3)
                input(f"Chunk {packet_count + 1} envoyé - Flèche visible? (ENTRÉE=non, CTRL+C=oui)")
                
                if not await self.wait_for_response("REOK", 3):
                    print("❌ Pas de REOK")
                    return
                
                print("📨 REOK reçu")
                bytes_sent += chunk_size
                packet_count += 1
            
            # ÉTAPE 7: DATCP
            print("\n🔎 ÉTAPE 7: Envoi DATCP (finalisation)...")
            datcp_cmd = bytearray([5])
            datcp_cmd.extend(b"DATCP")
            while len(datcp_cmd) < 16:
                datcp_cmd.append(0)
            
            encrypted_datcp = self.cipher.encrypt(bytes(datcp_cmd))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted_datcp)
            print("📤 DATCP envoyé")
            
            await asyncio.sleep(0.5)
            input("DATCP envoyé - Flèche toujours visible? (ENTRÉE=non, CTRL+C=oui)")
            
            # ÉTAPE 8: DATCPOK et finalisation
            if await self.wait_for_response("DATCPOK", 5):
                print("📨 DATCPOK reçu")
                print("\n🔎 ÉTAPE 8: Finalisation...")
                await self.set_display_mode(1)
                print("🎭 Mode d'affichage activé")
                
                await asyncio.sleep(self.step_delay)
                input("Upload terminé - Flèche encore visible? (ENTRÉE=non, CTRL+C=oui)")
            
            print("\n🎉 ANALYSE TERMINÉE!")
            print("✅ Si vous êtes arrivé ici, nous savons maintenant")
            print("   à quelle étape précise la flèche apparaît!")
            
        except KeyboardInterrupt:
            print(f"\n🔥 FLÈCHE DÉTECTÉE à cette étape!")
            print("💡 Maintenant nous pouvons cibler précisément le problème!")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    async def test_minimal_dats_only(self):
        """Test minimal: juste DATS pour voir si ça déclenche la flèche"""
        print("\n🧪 TEST MINIMAL: DATS seulement")
        print("=" * 40)
        print("👁️  Ce test envoie JUSTE la commande DATS")
        print("    pour voir si elle seule déclenche la flèche")
        
        try:
            input("Appuyez sur ENTRÉE pour envoyer DATS...")
            
            # DATS minimal
            dats_cmd = bytearray([9])
            dats_cmd.extend(b"DATS")
            dats_cmd.extend(struct.pack('>H', 100))  # Taille bidon
            dats_cmd.extend(struct.pack('>H', 50))   # Bitmap bidon
            dats_cmd.extend([0])
            while len(dats_cmd) < 16:
                dats_cmd.append(0)
            
            encrypted = self.cipher.encrypt(bytes(dats_cmd))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
            
            print("📤 DATS envoyé!")
            await asyncio.sleep(2)
            
            input("🔥 FLÈCHE VISIBLE après DATS? (ENTRÉE=non, CTRL+C=oui)")
            print("✅ Pas de flèche avec DATS seul")
            
        except KeyboardInterrupt:
            print("🔥 FLÈCHE confirmée avec DATS!")

async def run_analysis():
    """Lance l'analyse complète"""
    analyzer = ArrowAnalyzer()
    
    if await analyzer.connect():
        try:
            # Test minimal d'abord
            await analyzer.test_minimal_dats_only()
            
            # Puis analyse complète
            await analyzer.analyze_arrow_timing()
            
        finally:
            await analyzer.disconnect()
    else:
        print("❌ Connexion impossible")

if __name__ == "__main__":
    print("🔍 DÉTECTEUR DE FLÈCHE - Investigation précise")
    print("=" * 50)
    print("Ce programme va analyser EXACTEMENT quand la flèche apparaît")
    print("Suivez les instructions et dites-moi quand vous voyez la flèche!")
    print()
    
    asyncio.run(run_analysis())
