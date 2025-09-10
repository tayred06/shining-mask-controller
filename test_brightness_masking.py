#!/usr/bin/env python3
"""
🔇 MÉTHODE LUMINOSITÉ OPTIMISÉE - Anti-Flèche Firmware
=====================================================

Implémentation optimisée de la méthode luminosité pour masquer
la flèche hardcodée du firmware pendant l'upload.
"""

import asyncio
import sys
import os
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class BrightnessHiddenUpload(MaskTextDisplay):
    """Version modifiée avec masquage par luminosité"""
    
    def __init__(self):
        super().__init__()
        self.saved_brightness = 150  # Luminosité par défaut
    
    async def hide_display_during_upload(self):
        """Cache l'affichage en réduisant la luminosité à 0"""
        print("🔇 Masquage de l'affichage (luminosité 0)...")
        cmd = self.create_command("LIGHT", bytes([0]))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        await asyncio.sleep(0.3)  # Laisser le temps de s'appliquer
    
    async def restore_display_after_upload(self):
        """Restaure l'affichage avec la luminosité normale"""
        print(f"💡 Restauration de l'affichage (luminosité {self.saved_brightness})...")
        cmd = self.create_command("LIGHT", bytes([self.saved_brightness]))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        await asyncio.sleep(0.2)
    
    async def display_text_hidden_upload(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """Affiche du texte avec upload masqué par luminosité"""
        print(f"\n📝 Affichage avec upload masqué: '{text}'")
        
        try:
            # 1. MASQUER l'affichage AVANT tout
            await self.hide_display_during_upload()
            
            # 2. Configuration background (invisible car luminosité 0)
            bg_r, bg_g, bg_b = background
            if background != (0, 0, 0):
                await self.set_background_color(bg_r, bg_g, bg_b, 1)
            else:
                await self.set_background_color(0, 0, 0, 1)
            
            # 3. Générer bitmap
            bitmap_columns = self.text_to_bitmap(text)
            if not bitmap_columns:
                print("❌ Aucun caractère valide")
                await self.restore_display_after_upload()
                return False
            
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), color)
            
            total_len = len(bitmap_data) + len(color_data)
            bitmap_len = len(bitmap_data)
            
            print(f"📊 {len(bitmap_columns)} colonnes, {bitmap_len}B bitmap, {len(color_data)}B couleurs")
            
            # 4. Upload COMPLET avec affichage masqué (flèche invisible!)
            self.responses.clear()
            
            # DATS
            dats_cmd = bytearray([9])
            dats_cmd.extend(b"DATS")
            dats_cmd.extend(struct.pack('>H', total_len))
            dats_cmd.extend(struct.pack('>H', bitmap_len))
            dats_cmd.extend([0])
            while len(dats_cmd) < 16:
                dats_cmd.append(0)
            
            print("📤 DATS (flèche masquée par luminosité 0)...")
            encrypted = self.cipher.encrypt(bytes(dats_cmd))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
            
            if not await self.wait_for_response("DATSOK", 5):
                print("❌ Pas de DATSOK")
                await self.restore_display_after_upload()
                return False
            
            # Upload chunks (toujours invisible)
            complete_data = bitmap_data + color_data
            max_chunk = 96
            bytes_sent = 0
            packet_count = 0
            
            print("📦 Upload chunks (invisibles)...")
            while bytes_sent < len(complete_data):
                remaining = len(complete_data) - bytes_sent
                chunk_size = min(max_chunk, remaining)
                chunk = complete_data[bytes_sent:bytes_sent + chunk_size]
                packet = bytearray([chunk_size + 1, packet_count])
                packet.extend(chunk)
                
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", bytes(packet))
                
                if not await self.wait_for_response("REOK", 3):
                    print(f"❌ Pas de REOK pour chunk {packet_count}")
                    await self.restore_display_after_upload()
                    return False
                
                bytes_sent += chunk_size
                packet_count += 1
            
            # DATCP (finalisation invisible)
            datcp_cmd = bytearray([5])
            datcp_cmd.extend(b"DATCP")
            while len(datcp_cmd) < 16:
                datcp_cmd.append(0)
            
            print("📤 DATCP (finalisation invisible)...")
            encrypted = self.cipher.encrypt(bytes(datcp_cmd))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
            
            if not await self.wait_for_response("DATCPOK", 5):
                print("❌ Pas de DATCPOK")
                await self.restore_display_after_upload()
                return False
            
            # 5. RÉVÉLER le résultat final
            print("✨ Révélation du texte final...")
            await self.restore_display_after_upload()
            
            # 6. Confirmer le mode d'affichage
            await asyncio.sleep(0.5)
            await self.set_display_mode(1)
            
            print(f"🎉 '{text}' affiché SANS flèche visible (masquée par luminosité)!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            # Toujours restaurer la luminosité en cas d'erreur
            await self.restore_display_after_upload()
            return False

async def test_brightness_masking():
    """Test de la méthode de masquage par luminosité"""
    print("🔇 TEST MÉTHODE LUMINOSITÉ OPTIMISÉE")
    print("=" * 45)
    print("Concept: Upload complètement invisible, puis révélation du résultat")
    print()
    
    display = BrightnessHiddenUpload()
    
    if await display.connect():
        try:
            # Définir une luminosité de base
            print("💡 Configuration luminosité de base...")
            await display.brightness(150)
            await asyncio.sleep(1)
            
            # Tests avec différents textes
            test_cases = [
                ("HIDDEN", (255, 0, 0)),      # Rouge
                ("UPLOAD", (0, 255, 0)),      # Vert  
                ("MAGIC", (0, 0, 255)),       # Bleu
                ("DONE", (255, 255, 0)),      # Jaune
            ]
            
            for i, (text, color) in enumerate(test_cases, 1):
                print(f"\n{'='*50}")
                print(f"🧪 TEST {i}/4: '{text}'")
                print(f"{'='*50}")
                
                print("👀 OBSERVEZ: L'upload devrait être COMPLÈTEMENT INVISIBLE!")
                print("⏳ Puis le texte apparaît d'un coup à la fin")
                
                await asyncio.sleep(1)
                
                success = await display.display_text_hidden_upload(text, color)
                
                if success:
                    print(f"✅ Test {i} réussi - Flèche était-elle invisible? (OUI attendu)")
                    await asyncio.sleep(3)  # Observer le résultat
                else:
                    print(f"❌ Test {i} échoué")
                    break
            
            print(f"\n🎯 ÉVALUATION:")
            print("Si vous n'avez VU AUCUNE FLÈCHE pendant les uploads,")
            print("alors cette méthode FONCTIONNE parfaitement!")
            print()
            print("🔧 Cette méthode peut être intégrée dans votre système existant")
            print("   pour éliminer définitivement la flèche firmware!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Test arrêté")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await display.disconnect()
    else:
        print("❌ Impossible de se connecter au masque")

if __name__ == "__main__":
    asyncio.run(test_brightness_masking())
