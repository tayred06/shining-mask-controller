#!/usr/bin/env python3
"""
🎯 SOLUTION FINALE DE COMPROMIS - Flèche minimisée
==================================================

Puisque la flèche firmware ne peut pas être complètement éliminée,
cette solution la rend aussi discrète que possible.
"""

import asyncio
import sys
import os
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class MinimizedArrowDisplay(MaskTextDisplay):
    """Affichage avec flèche minimisée au maximum"""
    
    def __init__(self):
        super().__init__()
        self.default_brightness = 150
    
    async def display_text_minimal_arrow(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """
        Affiche du texte avec la flèche la moins visible possible
        
        Stratégie de minimisation:
        1. Luminosité très faible pendant upload
        2. Upload ultra-rapide
        3. Révélation immédiate du contenu
        4. Feedback utilisateur optimisé
        """
        print(f"🎯 Affichage '{text}' avec flèche minimisée...")
        
        try:
            # 1. Préparer tout à l'avance pour upload ultra-rapide
            bitmap_columns = self.text_to_bitmap(text)
            if not bitmap_columns:
                print("❌ Aucun caractère valide")
                return False
            
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), color)
            
            # 2. Configuration initiale
            bg_r, bg_g, bg_b = background
            await self.set_background_color(bg_r, bg_g, bg_b, 1)
            
            # 3. RÉDUIRE la luminosité au MINIMUM (pas 0, mais très faible)
            print("🔅 Luminosité minimale pendant upload...")
            cmd = self.create_command("LIGHT", bytes([1]))  # 1 = minimum visible
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await asyncio.sleep(0.1)
            
            # 4. Upload ULTRA-RAPIDE avec feedback minimal
            print("⚡ Upload ultra-rapide...")
            success = await self.ultra_fast_upload(bitmap_data, color_data)
            
            if success:
                # 5. Révélation IMMÉDIATE du contenu
                print("💡 Révélation du contenu...")
                cmd = self.create_command("LIGHT", bytes([self.default_brightness]))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
                
                await asyncio.sleep(0.1)
                await self.set_display_mode(1)
                
                print(f"✅ '{text}' affiché (flèche minimisée)")
                return True
            else:
                # Restaurer luminosité même en cas d'échec
                cmd = self.create_command("LIGHT", bytes([self.default_brightness]))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            # Toujours restaurer la luminosité
            try:
                cmd = self.create_command("LIGHT", bytes([self.default_brightness]))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            except:
                pass
            return False
    
    async def ultra_fast_upload(self, bitmap_data, color_data):
        """Upload optimisé pour vitesse maximale"""
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        self.responses.clear()
        
        # DATS avec timeout réduit
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        # Attente DATSOK ultra-rapide
        if not await self.wait_for_response("DATSOK", 2):
            return False
        
        # Upload chunks avec délai minimum
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
            
            # Timeout ultra-court
            if not await self.wait_for_response("REOK", 1):
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
        
        # DATCP final
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        return await self.wait_for_response("DATCPOK", 2)
    
    async def set_brightness(self, level):
        """Configure la luminosité par défaut"""
        self.default_brightness = max(1, min(255, level))

# Fonction principale simplifiée
async def display_text_best_effort(text, color=(255, 255, 255), background=(0, 0, 0), brightness=150):
    """
    🎯 FONCTION PRINCIPALE: Meilleur effort pour minimiser la flèche
    
    Cette fonction fait de son mieux pour rendre la flèche aussi
    discrète que possible, mais ne peut pas la supprimer complètement.
    """
    display = MinimizedArrowDisplay()
    
    if await display.connect():
        try:
            await display.set_brightness(brightness)
            success = await display.display_text_minimal_arrow(text, color, background)
            return success
        finally:
            await display.disconnect()
    
    return False

async def test_compromise_solution():
    """Test de la solution de compromis"""
    print("🎯 TEST SOLUTION DE COMPROMIS - Flèche minimisée")
    print("=" * 50)
    print("⚠️  ATTENTION: Cette solution ne peut PAS éliminer")
    print("   complètement la flèche (limitation firmware)")
    print("   Mais elle la rend aussi discrète que possible!")
    print()
    
    tests = [
        ("BEST", (255, 100, 0)),    # Orange
        ("EFFORT", (0, 255, 100)),  # Vert-cyan
        ("MINIMAL", (255, 0, 150)), # Rose
        ("ARROW", (100, 100, 255)), # Bleu clair
    ]
    
    for text, color in tests:
        print(f"\n🧪 Test: '{text}'")
        print("👁️  Observez: la flèche devrait être TRÈS discrète")
        
        success = await display_text_best_effort(text, color)
        
        if success:
            print(f"✅ '{text}' affiché avec flèche minimisée")
            await asyncio.sleep(2)
        else:
            print(f"❌ Échec pour '{text}'")
    
    print("\n📋 CONCLUSION:")
    print("✅ Flèche rendue aussi discrète que possible")
    print("⚠️  Élimination complète impossible (firmware)")
    print("🎯 Solution optimale dans les contraintes existantes")

if __name__ == "__main__":
    asyncio.run(test_compromise_solution())
