#!/usr/bin/env python3
"""
🎯 SOLUTION FINALE - Envoi de texte SANS flèche upload
======================================================

Intégration de la méthode de masquage par luminosité dans 
votre système de contrôle clavier principal.
"""

import asyncio
import sys
import os

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class NoArrowTextDisplay(MaskTextDisplay):
    """Affichage de texte SANS flèche firmware visible"""
    
    def __init__(self):
        super().__init__()
        self.default_brightness = 150
        self.is_display_hidden = False
    
    async def hide_display(self):
        """Cache l'affichage (luminosité 0)"""
        if not self.is_display_hidden:
            cmd = self.create_command("LIGHT", bytes([0]))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            self.is_display_hidden = True
            await asyncio.sleep(0.2)
    
    async def show_display(self):
        """Révèle l'affichage (luminosité normale)"""
        if self.is_display_hidden:
            cmd = self.create_command("LIGHT", bytes([self.default_brightness]))
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            self.is_display_hidden = False
            await asyncio.sleep(0.2)
    
    async def display_text_no_arrow(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """
        Affiche du texte SANS flèche upload visible
        
        Args:
            text: Texte à afficher
            color: Couleur RGB du texte (tuple)
            background: Couleur RGB du fond (tuple)
            
        Returns:
            bool: True si succès
        """
        print(f"📝 Affichage '{text}' SANS flèche...")
        
        try:
            # 1. MASQUER l'affichage AVANT upload
            await self.hide_display()
            
            # 2. Préparer le background
            bg_r, bg_g, bg_b = background
            if background != (0, 0, 0):
                await self.set_background_color(bg_r, bg_g, bg_b, 1)
            else:
                await self.set_background_color(0, 0, 0, 1)
            
            # 3. Générer et encoder le texte
            bitmap_columns = self.text_to_bitmap(text)
            if not bitmap_columns:
                print("❌ Aucun caractère valide")
                await self.show_display()
                return False
            
            bitmap_data = self.encode_bitmap(bitmap_columns)
            color_data = self.encode_colors(len(bitmap_columns), color)
            
            # 4. Upload INVISIBLE (firmware ne sait pas qu'on regarde!)
            success = await self.upload_data_invisible(bitmap_data, color_data)
            
            if success:
                # 5. RÉVÉLER le résultat final
                await self.show_display()
                await asyncio.sleep(0.3)
                await self.set_display_mode(1)
                print(f"🎉 '{text}' affiché - flèche était invisible!")
                return True
            else:
                await self.show_display()
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            await self.show_display()  # Toujours restaurer
            return False
    
    async def upload_data_invisible(self, bitmap_data, color_data):
        """Upload avec affichage masqué (aucune flèche visible)"""
        import struct
        
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        self.responses.clear()
        
        # DATS invisible
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        if not await self.wait_for_response("DATSOK", 5):
            return False
        
        # Upload chunks invisibles
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
            
            if not await self.wait_for_response("REOK", 3):
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
        
        # DATCP invisible
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
        
        return await self.wait_for_response("DATCPOK", 5)
    
    async def set_brightness(self, level):
        """Définit la luminosité par défaut"""
        self.default_brightness = max(1, min(255, level))
        if not self.is_display_hidden:
            await self.brightness(self.default_brightness)

# Fonction principale pour votre usage
async def display_text_without_arrow(text, color=(255, 255, 255), background=(0, 0, 0), brightness=150):
    """
    🎯 FONCTION PRINCIPALE: Affiche du texte SANS flèche upload
    
    Usage simple:
        await display_text_without_arrow("HELLO", (255, 0, 0))  # Rouge
        await display_text_without_arrow("WORLD", (0, 255, 0))  # Vert
    """
    display = NoArrowTextDisplay()
    
    if await display.connect():
        try:
            await display.set_brightness(brightness)
            success = await display.display_text_no_arrow(text, color, background)
            return success
        finally:
            await display.disconnect()
    
    return False

# Tests de validation
async def test_solution():
    """Test de la solution finale"""
    print("🎯 TEST SOLUTION FINALE - Texte sans flèche")
    print("=" * 45)
    
    tests = [
        ("PERFECT", (255, 0, 255)),   # Magenta
        ("NO ARROW", (255, 255, 0)),  # Jaune
        ("CLEAN", (0, 255, 255)),     # Cyan
    ]
    
    for text, color in tests:
        print(f"\n🧪 Test: '{text}'")
        success = await display_text_without_arrow(text, color)
        if success:
            print(f"✅ '{text}' affiché avec succès (sans flèche)")
            await asyncio.sleep(2)
        else:
            print(f"❌ Échec pour '{text}'")
    
    print("\n🎉 Solution prête pour intégration!")

if __name__ == "__main__":
    asyncio.run(test_solution())
