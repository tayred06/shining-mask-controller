#!/usr/bin/env python3
"""
🔥 MÉTHODES RADICALES - Élimination totale des flèches
=======================================================

Tests de méthodes plus agressives pour masquer complètement
la flèche firmware pendant l'upload.
"""

import asyncio
import sys
import os
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class RadicalArrowKiller(MaskTextDisplay):
    """Méthodes radicales pour éliminer les flèches"""
    
    def __init__(self):
        super().__init__()
    
    async def method_1_ultra_fast_hide(self, text, color=(255, 255, 255)):
        """Méthode 1: Cache ultra-rapide avec fond noir total"""
        print("🔥 MÉTHODE 1: Ultra-fast hide")
        
        try:
            # 1. Fond noir immédiat + luminosité 0
            await self.set_background_color(0, 0, 0, 1)
            await asyncio.sleep(0.1)
            
            cmd = self.create_command("LIGHT", bytes([0]))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await asyncio.sleep(0.05)  # Plus rapide
            
            # 2. Upload ultra-rapide
            success = await self.upload_text_fast(text, color)
            
            # 3. Révélation immédiate
            cmd = self.create_command("LIGHT", bytes([200]))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            
            if success:
                await self.set_display_mode(1)
                print("✅ Méthode 1 terminée")
                return True
            
        except Exception as e:
            print(f"❌ Erreur méthode 1: {e}")
        
        return False
    
    async def method_2_mode_switching(self, text, color=(255, 255, 255)):
        """Méthode 2: Commutation de mode avant upload"""
        print("🔥 MÉTHODE 2: Mode switching")
        
        try:
            # 1. Passer en mode 0 (éteint?)
            await self.set_display_mode(0)
            await asyncio.sleep(0.2)
            
            # 2. Upload en mode éteint
            success = await self.upload_text_fast(text, color)
            
            # 3. Révélation par mode 1
            if success:
                await asyncio.sleep(0.1)
                await self.set_display_mode(1)
                print("✅ Méthode 2 terminée")
                return True
            
        except Exception as e:
            print(f"❌ Erreur méthode 2: {e}")
        
        return False
    
    async def method_3_background_flood(self, text, color=(255, 255, 255)):
        """Méthode 3: Inondation background + luminosité minimum"""
        print("🔥 MÉTHODE 3: Background flood")
        
        try:
            # 1. Fond noir total
            await self.set_background_color(0, 0, 0, 1)
            await asyncio.sleep(0.1)
            
            # 2. Luminosité au minimum absolu
            cmd = self.create_command("LIGHT", bytes([1]))  # 1 au lieu de 0
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await asyncio.sleep(0.2)
            
            # 3. Upload
            success = await self.upload_text_fast(text, color)
            
            # 4. Révélation progressive
            if success:
                for brightness in [50, 100, 150]:
                    cmd = self.create_command("LIGHT", bytes([brightness]))
                    await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
                    await asyncio.sleep(0.1)
                
                await self.set_display_mode(1)
                print("✅ Méthode 3 terminée")
                return True
            
        except Exception as e:
            print(f"❌ Erreur méthode 3: {e}")
        
        return False
    
    async def method_4_distraction_technique(self, text, color=(255, 255, 255)):
        """Méthode 4: Technique de distraction - affichage rapide d'autre chose"""
        print("🔥 MÉTHODE 4: Distraction technique")
        
        try:
            # 1. Afficher un point noir pour "distraire"
            bitmap_columns = [[0] * 8]  # Une colonne noire
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(1, (0, 0, 0))
            
            # Upload distraction rapide
            await self.upload_data_direct(bitmap_data, color_data)
            await self.set_display_mode(1)
            await asyncio.sleep(0.1)
            
            # 2. Maintenant upload du vrai texte (avec luminosité 0)
            cmd = self.create_command("LIGHT", bytes([0]))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await asyncio.sleep(0.1)
            
            success = await self.upload_text_fast(text, color)
            
            # 3. Révélation
            if success:
                cmd = self.create_command("LIGHT", bytes([150]))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
                await self.set_display_mode(1)
                print("✅ Méthode 4 terminée")
                return True
            
        except Exception as e:
            print(f"❌ Erreur méthode 4: {e}")
        
        return False
    
    async def method_5_background_camouflage(self, text, color=(255, 255, 255)):
        """Méthode 5: Camouflage - fond de même couleur que la flèche"""
        print("🔥 MÉTHODE 5: Background camouflage")
        
        try:
            # 1. Fond blanc (même couleur que flèche?)
            await self.set_background_color(255, 255, 255, 1)
            await asyncio.sleep(0.2)
            
            # 2. Upload avec fond blanc
            success = await self.upload_text_fast(text, color)
            
            # 3. Retour fond noir + révélation
            if success:
                await self.set_background_color(0, 0, 0, 1)
                await self.set_display_mode(1)
                print("✅ Méthode 5 terminée")
                return True
            
        except Exception as e:
            print(f"❌ Erreur méthode 5: {e}")
        
        return False
    
    async def upload_text_fast(self, text, color):
        """Upload optimisé pour vitesse"""
        bitmap_columns = self.text_to_bitmap(text)
        if not bitmap_columns:
            return False
        
        bitmap_data = self.encode_bitmap(bitmap_columns)
        color_data = self.encode_colors(len(bitmap_columns), color)
        
        return await self.upload_data_direct(bitmap_data, color_data)
    
    async def upload_data_direct(self, bitmap_data, color_data):
        """Upload direct optimisé"""
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        self.responses.clear()
        
        # DATS
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        if not await self.wait_for_response("DATSOK", 3):
            return False
        
        # Upload chunks
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
            
            if not await self.wait_for_response("REOK", 2):
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
        
        # DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        return await self.wait_for_response("DATCPOK", 3)

async def test_radical_methods():
    """Test des méthodes radicales"""
    print("🔥 TESTS MÉTHODES RADICALES ANTI-FLÈCHE")
    print("=" * 50)
    print("👀 OBSERVEZ ATTENTIVEMENT: quelle méthode cache le mieux la flèche?")
    print()
    
    killer = RadicalArrowKiller()
    
    if await killer.connect():
        try:
            methods = [
                ("ULTRA", killer.method_1_ultra_fast_hide),
                ("SWITCH", killer.method_2_mode_switching),
                ("FLOOD", killer.method_3_background_flood),
                ("TRICK", killer.method_4_distraction_technique),
                ("CAMO", killer.method_5_background_camouflage),
            ]
            
            for i, (text, method) in enumerate(methods, 1):
                print(f"\n{'='*50}")
                print(f"🧪 TEST {i}/5: MÉTHODE {i} - '{text}'")
                print(f"{'='*50}")
                print("👁️  REGARDEZ LE MASQUE MAINTENANT!")
                
                await asyncio.sleep(1)
                
                success = await method(text, (255, 100, 0))  # Orange
                
                if success:
                    print(f"✅ Méthode {i} terminée - La flèche était-elle visible?")
                else:
                    print(f"❌ Méthode {i} échouée")
                
                await asyncio.sleep(3)  # Observer le résultat
            
            print(f"\n🎯 ÉVALUATION FINALE:")
            print("Quelle méthode a le mieux masqué la flèche?")
            print("1️⃣ Ultra-fast hide")
            print("2️⃣ Mode switching") 
            print("3️⃣ Background flood")
            print("4️⃣ Distraction technique")
            print("5️⃣ Background camouflage")
            print()
            print("💡 Si aucune ne fonctionne parfaitement,")
            print("   nous devrons explorer d'autres pistes...")
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests arrêtés")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await killer.disconnect()
    else:
        print("❌ Impossible de se connecter au masque")

if __name__ == "__main__":
    asyncio.run(test_radical_methods())
