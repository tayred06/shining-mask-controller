#!/usr/bin/env python3
"""
⚡ ÉCRASEMENT IMMÉDIAT - Anti-flèche par surcharge
==================================================

Nouvelle stratégie: au lieu de cacher la flèche, on l'écrase
immédiatement avec notre contenu plus rapidement qu'elle n'apparaît.
"""

import asyncio
import sys
import os
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class InstantOverwriter(MaskTextDisplay):
    """Écrasement instantané de la flèche"""
    
    def __init__(self):
        super().__init__()
    
    async def instant_overwrite_method(self, text, color=(255, 255, 255)):
        """Méthode d'écrasement instantané"""
        print(f"⚡ ÉCRASEMENT INSTANTANÉ: '{text}'")
        
        try:
            # 1. Préparer TOUT à l'avance
            bitmap_columns = self.text_to_bitmap(text)
            if not bitmap_columns:
                return False
            
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), color)
            complete_data = bitmap_data + color_data
            
            total_len = len(bitmap_data) + len(color_data)
            bitmap_len = len(bitmap_data)
            
            # 2. Préparer TOUTES les commandes
            # DATS
            dats_cmd = bytearray([9])
            dats_cmd.extend(b"DATS")
            dats_cmd.extend(struct.pack('>H', total_len))
            dats_cmd.extend(struct.pack('>H', bitmap_len))
            dats_cmd.extend([0])
            while len(dats_cmd) < 16:
                dats_cmd.append(0)
            encrypted_dats = self.cipher.encrypt(bytes(dats_cmd))
            
            # Chunks
            max_chunk = 96
            packets = []
            bytes_sent = 0
            packet_count = 0
            
            while bytes_sent < len(complete_data):
                remaining = len(complete_data) - bytes_sent
                chunk_size = min(max_chunk, remaining)
                chunk = complete_data[bytes_sent:bytes_sent + chunk_size]
                packet = bytearray([chunk_size + 1, packet_count])
                packet.extend(chunk)
                packets.append(bytes(packet))
                bytes_sent += chunk_size
                packet_count += 1
            
            # DATCP
            datcp_cmd = bytearray([5])
            datcp_cmd.extend(b"DATCP")
            while len(datcp_cmd) < 16:
                datcp_cmd.append(0)
            encrypted_datcp = self.cipher.encrypt(bytes(datcp_cmd))
            
            print(f"⚡ Préparation terminée: {len(packets)} chunks prêts")
            
            # 3. ENVOI ULTRA-RAPIDE
            self.responses.clear()
            
            # DATS (déclenche la flèche)
            print("⚡ DATS...")
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted_dats)
            
            # Attendre DATSOK ultra rapidement
            if not await self.wait_for_response("DATSOK", 2):
                print("❌ Pas de DATSOK")
                return False
            
            print("⚡ Upload chunks ULTRA-RAPIDE...")
            # Envoyer TOUS les chunks le plus vite possible
            for i, packet in enumerate(packets):
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", packet)
                # PAS de délai - envoi immédiat
                
                # Vérification ultra-rapide
                if not await self.wait_for_response("REOK", 1):
                    print(f"❌ Pas de REOK pour chunk {i}")
                    return False
            
            print("⚡ DATCP final...")
            # DATCP immédiat
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted_datcp)
            
            if not await self.wait_for_response("DATCPOK", 2):
                print("❌ Pas de DATCPOK")
                return False
            
            # Mode d'affichage immédiat
            await self.set_display_mode(1)
            
            print("⚡ Écrasement terminé!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    async def pre_upload_distraction(self, text, color=(255, 255, 255)):
        """Méthode avec pré-distraction"""
        print(f"🎭 PRÉ-DISTRACTION + ÉCRASEMENT: '{text}'")
        
        try:
            # 1. Charger quelque chose de "neutre" d'abord
            neutral_bitmap = [[0] * 8 for _ in range(8)]  # 8 colonnes noires
            neutral_data = self.encode_bitmap(neutral_bitmap)
            neutral_colors = self.encode_colors(8, (0, 0, 0))
            
            # Upload neutre ultra-rapide (pour "préparer" le firmware)
            await self.upload_neutral_fast(neutral_data, neutral_colors)
            
            # 2. Maintenant upload du vrai contenu
            return await self.instant_overwrite_method(text, color)
            
        except Exception as e:
            print(f"❌ Erreur pré-distraction: {e}")
            return False
    
    async def upload_neutral_fast(self, bitmap_data, color_data):
        """Upload neutre ultra-rapide"""
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        self.responses.clear()
        
        # DATS neutre
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        if not await self.wait_for_response("DATSOK", 2):
            return False
        
        # Upload chunks neutre
        complete_data = bitmap_data + color_data
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
            
            if not await self.wait_for_response("REOK", 1):
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
        
        # DATCP neutre
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        return await self.wait_for_response("DATCPOK", 2)
    
    async def triple_speed_method(self, text, color=(255, 255, 255)):
        """Méthode triple vitesse - upload en parallèle"""
        print(f"🚀 TRIPLE VITESSE: '{text}'")
        
        try:
            # Configuration background ultra-rapide
            await self.set_background_color(0, 0, 0, 1)
            
            # Upload avec timeouts minimum
            success = await self.instant_overwrite_method(text, color)
            
            if success:
                print("🚀 Triple vitesse réussie!")
                return True
            
        except Exception as e:
            print(f"❌ Erreur triple vitesse: {e}")
        
        return False

async def test_overwrite_methods():
    """Test des méthodes d'écrasement"""
    print("⚡ TESTS MÉTHODES D'ÉCRASEMENT INSTANTANÉ")
    print("=" * 50)
    print("🎯 Objectif: écraser la flèche plus vite qu'elle n'apparaît")
    print()
    
    overwriter = InstantOverwriter()
    
    if await overwriter.connect():
        try:
            methods = [
                ("SPEED1", overwriter.instant_overwrite_method, (255, 0, 0)),
                ("SPEED2", overwriter.pre_upload_distraction, (0, 255, 0)),
                ("SPEED3", overwriter.triple_speed_method, (0, 0, 255)),
            ]
            
            for i, (text, method, color) in enumerate(methods, 1):
                print(f"\n{'='*50}")
                print(f"⚡ TEST {i}/3: '{text}' - MÉTHODE {i}")
                print(f"{'='*50}")
                print("👁️  REGARDEZ: la flèche est-elle visible ou écrasée?")
                
                await asyncio.sleep(1)
                
                success = await method(text, color)
                
                if success:
                    print(f"✅ Méthode {i} terminée")
                    print("❓ La flèche était-elle visible pendant l'upload?")
                else:
                    print(f"❌ Méthode {i} échouée")
                
                await asyncio.sleep(3)
            
            print(f"\n🎯 ÉVALUATION:")
            print("Quelle méthode a le mieux masqué/écrasé la flèche?")
            print("1️⃣ Écrasement instantané")
            print("2️⃣ Pré-distraction + écrasement")
            print("3️⃣ Triple vitesse")
            print()
            print("💡 Si aucune ne fonctionne, nous explorerons")
            print("   des solutions au niveau protocolaire...")
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests arrêtés")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await overwriter.disconnect()
    else:
        print("❌ Impossible de se connecter au masque")

if __name__ == "__main__":
    asyncio.run(test_overwrite_methods())
