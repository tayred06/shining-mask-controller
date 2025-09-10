#!/usr/bin/env python3
"""
🚨 CORRECTION URGENTE - Fix du problème de flèche bloquée
========================================================

Retour à une solution stable qui évite les blocages
tout en minimisant la visibilité de la flèche.
"""

import asyncio
import sys
import os

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class StableArrowFix(MaskTextDisplay):
    """Solution stable pour minimiser la flèche sans blocage"""
    
    def __init__(self):
        super().__init__()
        self.default_brightness = 150
    
    async def display_text_stable_minimal_arrow(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """
        🛡️ SOLUTION STABLE: Flèche minimisée sans risque de blocage
        
        Approche: Luminosité faible (pas 0) + upload rapide
        """
        print(f"🛡️ Affichage stable '{text}' avec flèche minimisée...")
        
        try:
            # 1. Configuration background
            bg_r, bg_g, bg_b = background
            await self.set_background_color(bg_r, bg_g, bg_b, 1)
            
            # 2. Réduire luminosité à 10 (visible mais très faible)
            print("🔅 Luminosité réduite (anti-flèche)...")
            cmd = self.create_command("LIGHT", bytes([10]))  # 10 au lieu de 0
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await asyncio.sleep(0.2)
            
            # 3. Upload NORMAL avec DATS (pas d'expérimentation)
            print("📤 Upload standard...")
            success = await self.display_text(text, color)
            
            # 4. Restaurer luminosité IMMÉDIATEMENT
            print("💡 Restauration luminosité...")
            cmd = self.create_command("LIGHT", bytes([self.default_brightness]))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            
            if success:
                print(f"✅ '{text}' affiché - flèche minimisée et stable")
                return True
            else:
                print(f"❌ Échec upload pour '{text}'")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            # TOUJOURS restaurer la luminosité en cas d'erreur
            try:
                cmd = self.create_command("LIGHT", bytes([self.default_brightness]))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
                print("🔧 Luminosité restaurée après erreur")
            except:
                print("⚠️ Impossible de restaurer luminosité")
            return False
    
    async def display_text_ultra_fast(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """
        ⚡ Alternative: Upload ultra-rapide pour flèche très brève
        """
        print(f"⚡ Affichage ultra-rapide '{text}'...")
        
        try:
            # Configuration
            bg_r, bg_g, bg_b = background
            await self.set_background_color(bg_r, bg_g, bg_b, 1)
            
            # Préparer données à l'avance
            bitmap_columns = self.text_to_bitmap(text)
            if not bitmap_columns:
                return False
            
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), color)
            
            # Upload avec timeouts réduits au minimum
            success = await self.upload_minimal_delay(bitmap_data, color_data)
            
            if success:
                await self.set_display_mode(1)
                print(f"✅ '{text}' affiché ultra-rapidement")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erreur ultra-rapide: {e}")
            return False
    
    async def upload_minimal_delay(self, bitmap_data, color_data):
        """Upload avec délais minimums"""
        import struct
        
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
        
        if not await self.wait_for_response("DATSOK", 2):
            return False
        
        # Chunks ultra-rapides
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
            
            # Pas de délai entre chunks
            if not await self.wait_for_response("REOK", 1):
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
        
        return await self.wait_for_response("DATCPOK", 2)

# Fonction principale corrigée
async def display_text_fixed(text, color=(255, 255, 255), background=(0, 0, 0), method="stable"):
    """
    🛡️ FONCTION CORRIGÉE: Affichage avec flèche minimisée SANS blocage
    
    Args:
        method: "stable" (luminosité 10) ou "fast" (upload rapide)
    """
    display = StableArrowFix()
    
    if await display.connect():
        try:
            if method == "stable":
                success = await display.display_text_stable_minimal_arrow(text, color, background)
            else:  # method == "fast"
                success = await display.display_text_ultra_fast(text, color, background)
            
            return success
        finally:
            await display.disconnect()
    
    return False

async def test_corrected_solution():
    """Test de la solution corrigée"""
    print("🛡️ TEST SOLUTION CORRIGÉE - Anti-blocage")
    print("=" * 45)
    print("🎯 Objectif: Flèche minimisée SANS blocage du masque")
    print()
    
    # Test méthode stable
    print("1️⃣ TEST MÉTHODE STABLE (luminosité 10)")
    success1 = await display_text_fixed("STABLE", (255, 0, 0), method="stable")
    if success1:
        print("✅ Méthode stable fonctionne")
        await asyncio.sleep(3)
    else:
        print("❌ Méthode stable échoue")
    
    # Test méthode rapide
    print("\n2️⃣ TEST MÉTHODE RAPIDE (upload ultra-fast)")
    success2 = await display_text_fixed("RAPID", (0, 255, 0), method="fast")
    if success2:
        print("✅ Méthode rapide fonctionne")
        await asyncio.sleep(3)
    else:
        print("❌ Méthode rapide échoue")
    
    print(f"\n🎯 RÉSULTATS:")
    if success1:
        print("🛡️ RECOMMANDATION: Utilisez la méthode STABLE")
        print("   → Luminosité 10, flèche très discrète, pas de blocage")
    elif success2:
        print("⚡ RECOMMANDATION: Utilisez la méthode RAPIDE")
        print("   → Upload ultra-rapide, flèche brève")
    else:
        print("❌ Problème de connexion ou firmware")

if __name__ == "__main__":
    asyncio.run(test_corrected_solution())
