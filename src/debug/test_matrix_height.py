#!/usr/bin/env python3

import asyncio
import struct
import sys
sys.path.append('/Users/mathieu/my-python-project/src/working')
from complete_text_display import MaskTextDisplay

class MatrixTester(MaskTextDisplay):
    def __init__(self):
        super().__init__()
    
    def create_test_pattern_8bit(self, width=8):
        """Crée un pattern de test pour 8 bits de hauteur"""
        columns = []
        for col in range(width):
            # Pattern simple: ligne horizontale au milieu
            column = [0, 0, 0, 1, 1, 1, 0, 0]  # 8 bits seulement
            # Compléter à 16 bits avec des zéros
            column.extend([0] * 8)
            columns.append(column)
        return columns
    
    def create_test_pattern_vertical_line(self, width=8):
        """Crée une ligne verticale simple"""
        columns = []
        for col in range(width):
            if col == width // 2:  # Colonne du milieu
                column = [1] * 8 + [0] * 8  # Ligne verticale sur 8 bits
            else:
                column = [0] * 16
            columns.append(column)
        return columns
    
    def create_single_pixel(self, row=3, col=3):
        """Crée un seul pixel allumé à la position donnée"""
        columns = []
        for c in range(8):
            column = [0] * 16
            if c == col and row < 8:  # Seulement dans les 8 premières lignes
                column[row] = 1
            columns.append(column)
        return columns
    
    async def test_matrix_heights(self):
        """Test différentes configurations de matrice"""
        print("🔬 TEST HAUTEURS DE MATRICE")
        print("=" * 50)
        
        if not await self.connect():
            return
        
        try:
            # Test 1: Pattern horizontal 8-bit
            print("\n--- Test 1: Ligne horizontale (8 bits) ---")
            bitmap = self.create_test_pattern_8bit(8)
            await self.upload_test_pattern(bitmap, "Ligne horizontale")
            await asyncio.sleep(3)
            
            # Test 2: Ligne verticale
            print("\n--- Test 2: Ligne verticale ---")
            bitmap = self.create_test_pattern_vertical_line(8)
            await self.upload_test_pattern(bitmap, "Ligne verticale")
            await asyncio.sleep(3)
            
            # Test 3: Pixel unique
            print("\n--- Test 3: Pixel unique ---")
            bitmap = self.create_single_pixel(3, 3)
            await self.upload_test_pattern(bitmap, "Pixel unique")
            await asyncio.sleep(3)
            
            # Test 4: Pattern très simple - barre en haut
            print("\n--- Test 4: Barre en haut (ligne 0) ---")
            bitmap = []
            for col in range(8):
                column = [1, 0, 0, 0, 0, 0, 0, 0] + [0] * 8
                bitmap.append(column)
            await self.upload_test_pattern(bitmap, "Barre en haut")
            await asyncio.sleep(3)
            
            # Test 5: Pattern très simple - barre en bas
            print("\n--- Test 5: Barre en bas (ligne 7) ---")
            bitmap = []
            for col in range(8):
                column = [0, 0, 0, 0, 0, 0, 0, 1] + [0] * 8
                bitmap.append(column)
            await self.upload_test_pattern(bitmap, "Barre en bas")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client:
                await self.client.disconnect()
                print("🔌 Déconnecté")
    
    async def upload_test_pattern(self, bitmap, description):
        """Upload un pattern de test"""
        print(f"📤 Upload: {description}")
        
        # Afficher le pattern dans la console
        print("🖥️  Pattern:")
        for row in range(8):  # Seulement 8 lignes
            line = ""
            for col_idx, column in enumerate(bitmap):
                if column[row] == 1:
                    line += "██"
                else:
                    line += "  "
            print(f"│{line}│")
        
        # Background noir
        await self.set_background_color(0, 0, 0, 1)
        
        # Encoder et envoyer
        bitmap_data = self.encode_bitmap(bitmap)
        colors = bytes([255, 255, 255] * len(bitmap))  # Blanc
        
        print(f"📊 {len(bitmap)} colonnes, {len(bitmap_data)}B bitmap")
        
        # DATS
        cmd = self.create_command("DATS", struct.pack('<HH', len(bitmap_data), len(colors)))
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        await self.wait_for_response("OK")
        
        # Upload bitmap
        chunk_size = 16
        for i in range(0, len(bitmap_data), chunk_size):
            chunk = bitmap_data[i:i+chunk_size]
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
            await self.wait_for_response("OK")
        
        # Upload couleurs
        for i in range(0, len(colors), chunk_size):
            chunk = colors[i:i+chunk_size]
            await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
            await self.wait_for_response("OK")
        
        # DATCP
        cmd = self.create_command("DATCP")
        await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        await self.wait_for_response("OK")
        
        # Mode
        await self.set_display_mode(1)
        
        print(f"✅ {description} envoyé")

async def main():
    tester = MatrixTester()
    await tester.test_matrix_heights()

if __name__ == "__main__":
    print("🔬 DIAGNOSTIC MATRICE LED - PROBLÈME COUPURE")
    asyncio.run(main())
