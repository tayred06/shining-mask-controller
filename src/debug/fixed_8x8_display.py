#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/Users/mathieu/my-python-project/src/working')
from complete_text_display import MaskTextDisplay

class FixedMaskDisplay(MaskTextDisplay):
    def __init__(self):
        super().__init__()
        
        # Police corrigée 8x8 pixels (au lieu de 8x16)
        self.font_patterns_8x8 = {
            'O': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ "
            ],
            'I': [
                "████████",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "████████"
            ],
            'H': [
                "██    ██",
                "██    ██",
                "██    ██",
                "████████",
                "████████",
                "██    ██",
                "██    ██",
                "██    ██"
            ],
            'L': [
                "██      ",
                "██      ",
                "██      ",
                "██      ",
                "██      ",
                "██      ",
                "██      ",
                "████████"
            ],
            'E': [
                "████████",
                "██      ",
                "██      ",
                "██████  ",
                "██████  ",
                "██      ",
                "██      ",
                "████████"
            ],
            ' ': [
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        "
            ]
        }
    
    def text_to_bitmap_8x8(self, text):
        """Conversion bitmap 8x8 au lieu de 8x16"""
        columns = []
        
        for char in text.upper():
            if char in self.font_patterns_8x8:
                pattern = self.font_patterns_8x8[char]
                
                # 8 colonnes par caractère, 8 lignes seulement
                for col_idx in range(8):
                    column = []
                    for row_idx in range(8):  # Seulement 8 lignes!
                        if row_idx < len(pattern) and col_idx < len(pattern[row_idx]):
                            pixel = 1 if pattern[row_idx][col_idx] == '█' else 0
                        else:
                            pixel = 0
                        column.append(pixel)
                    
                    # Compléter à 16 avec des zéros (pour compatibilité)
                    column.extend([0] * 8)
                    columns.append(column)
        
        return columns
    
    def afficher_bitmap_console_8x8(self, text):
        """Affiche le bitmap 8x8 dans la console"""
        print(f"\n🖥️  APERÇU CONSOLE 8x8 DE '{text}':")
        print("=" * 40)
        
        bitmap = self.text_to_bitmap_8x8(text)
        
        # Afficher seulement les 8 premières lignes
        for row in range(8):
            line = ""
            for col_idx, column in enumerate(bitmap):
                if row < len(column):
                    if column[row] == 1:
                        line += "██"
                    else:
                        line += "  "
                else:
                    line += "  "
            print(f"│{line}│")
        
        print("=" * 40)
        print(f"📊 Dimensions: {len(bitmap)} colonnes x 8 lignes")
    
    async def display_text_8x8(self, text, color=(255, 255, 255)):
        """Affiche du texte avec bitmap 8x8"""
        print(f"\n📝 Affichage 8x8: '{text}'")
        
        # Aperçu console
        self.afficher_bitmap_console_8x8(text)
        
        # Background noir
        await self.set_background_color(0, 0, 0, 1)
        
        # Bitmap 8x8
        bitmap = self.text_to_bitmap_8x8(text)
        bitmap_data = self.encode_bitmap(bitmap)
        
        # Couleurs
        r, g, b = color
        colors = bytes([r, g, b] * len(bitmap))
        
        print(f"📊 Upload: {len(bitmap)} colonnes, {len(bitmap_data)}B bitmap, {len(colors)}B couleurs")
        
        # Upload
        cmd = self.create_command("DATS", struct.pack('<HH', len(bitmap_data), len(colors)))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        await self.wait_for_response("OK")
        
        chunk_size = 16
        for i in range(0, len(bitmap_data), chunk_size):
            chunk = bitmap_data[i:i+chunk_size]
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
            await self.wait_for_response("OK")
        
        for i in range(0, len(colors), chunk_size):
            chunk = colors[i:i+chunk_size]
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
            await self.wait_for_response("OK")
        
        cmd = self.create_command("DATCP")
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        await self.wait_for_response("OK")
        
        # Mode d'affichage
        await self.set_display_mode(1)
        
        print(f"✅ '{text}' affiché en 8x8!")

async def test_8x8():
    """Test avec bitmap 8x8"""
    print("🔧 TEST BITMAP 8x8 - CORRECTION RÉPÉTITION")
    
    display = FixedMaskDisplay()
    if not await display.connect():
        print("❌ Connexion impossible")
        return
    
    try:
        # Test avec différents textes
        tests = ["O", "OO", "HI", "HELLO"]
        
        for text in tests:
            await display.display_text_8x8(text)
            await asyncio.sleep(4)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if display.client:
            await display.client.disconnect()
            print("🔌 Déconnecté")

if __name__ == "__main__":
    import struct
    asyncio.run(test_8x8())
