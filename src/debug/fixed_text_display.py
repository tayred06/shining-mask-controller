#!/usr/bin/env python3

import asyncio
import struct
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration BLE
SERVICE_UUID = "D44BC439-ABFD-45A2-B575-925416129600"
COMMAND_CHAR = "D44BC439-ABFD-45A2-B575-925416129600"  
UPLOAD_CHAR = "D44BC439-ABFD-45A2-B575-92541612960A"
NOTIFY_CHAR = "D44BC439-ABFD-45A2-B575-925416129601"

# Clé de chiffrement
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')

class FixedTextDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
        
        # Police corrigée - exactement 8x16 pixels, pas d'espaces parasites
        self.font_patterns = {
            'H': [
                "█      █",
                "█      █", 
                "█      █",
                "█      █",
                "█      █",
                "████████",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "        ",
                "        ",
                "        "
            ],
            'E': [
                "████████",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "███████ ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "████████",
                "        ",
                "        ",
                "        ",
                "        "
            ],
            'L': [
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "████████",
                "        ",
                "        ",
                "        ",
                "        "
            ],
            'O': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        ",
                "        "
            ],
            'W': [
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█  ██  █",
                "█  ██  █",
                "█ ████ █",
                "█ ████ █",
                "██    ██",
                "██    ██",
                "█      █",
                "        ",
                "        ",
                "        ",
                "        "
            ],
            'R': [
                "███████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "███████ ",
                "█ ███   ",
                "█  ██   ",
                "█   █   ",
                "█   ██  ",
                "█    █  ",
                "█     ██",
                "        ",
                "        ",
                "        ",
                "        "
            ],
            'D': [
                "██████  ",
                "█     █ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█     █ ",
                "██████  ",
                "        ",
                "        ",
                "        ",
                "        "
            ],
            ' ': [
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
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
    
    def _notification_handler(self, sender, data):
        response = data.decode('utf-8', errors='ignore')
        self.responses.append(response)
        self.notification_event.set()
        print(f"📨 {response}")
    
    def create_command(self, cmd, data=b''):
        payload = cmd.encode() + data
        if len(payload) < 16:
            payload += b'\x00' * (16 - len(payload))
        elif len(payload) > 16:
            payload = payload[:16]
        
        return self.cipher.encrypt(payload)
    
    async def connect(self):
        print("🔍 Recherche du masque...")
        devices = await BleakScanner.discover()
        
        mask = None
        for device in devices:
            if device.name and "MASK" in device.name:
                mask = device
                break
        
        if not mask:
            print("❌ Masque non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask.name}...")
        self.client = BleakClient(mask.address)
        await self.client.connect()
        
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        print("✅ Connecté")
        return True
    
    def text_to_bitmap_fixed(self, text):
        """Version corrigée de conversion texte vers bitmap"""
        print(f"\n🔍 Conversion '{text}' vers bitmap...")
        columns = []
        
        for char_idx, char in enumerate(text.upper()):
            if char in self.font_patterns:
                pattern = self.font_patterns[char]
                print(f"  Caractère '{char}' (pos {char_idx})")
                
                # Vérification: chaque ligne doit faire exactement 8 caractères
                for row_idx, row in enumerate(pattern):
                    if len(row) != 8:
                        print(f"    ⚠️  Ligne {row_idx}: {len(row)} chars au lieu de 8: '{row}'")
                
                # Conversion en colonnes
                for col_idx in range(8):
                    column = []
                    for row_idx in range(16):  # Toujours 16 lignes
                        if row_idx < len(pattern) and col_idx < len(pattern[row_idx]):
                            pixel = 1 if pattern[row_idx][col_idx] == '█' else 0
                        else:
                            pixel = 0
                        column.append(pixel)
                    
                    columns.append(column)
                    
                    # Debug pour les premières colonnes
                    if char_idx == 0 and col_idx < 3:
                        pixel_str = ''.join(['█' if p else ' ' for p in column[:8]])
                        print(f"    Col {col_idx}: {pixel_str}")
        
        print(f"📊 Total: {len(columns)} colonnes générées")
        return columns
    
    def encode_bitmap_fixed(self, bitmap):
        """Version corrigée d'encodage bitmap"""
        encoded = bytearray()
        
        for i, column in enumerate(bitmap):
            # Vérification: chaque colonne doit avoir exactement 16 pixels
            if len(column) != 16:
                print(f"⚠️  Colonne {i}: {len(column)} pixels au lieu de 16")
                column = column[:16] + [0] * (16 - len(column))  # Ajuste si nécessaire
            
            # Encodage little-endian
            val = 0
            for j, pixel in enumerate(column):
                if pixel == 1:
                    val |= (1 << j)
            
            # Debug pour les premières colonnes
            if i < 5:
                pixels_str = ''.join(['█' if p else ' ' for p in column[:8]])
                print(f"  Col {i}: {pixels_str} -> 0x{val:04x}")
            
            encoded.extend(struct.pack('<H', val))
        
        print(f"📦 Bitmap: {len(encoded)} bytes")
        return bytes(encoded)
    
    async def wait_for_response(self, expected, timeout=10):
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            for i, response in enumerate(self.responses):
                if expected in response:
                    self.responses.pop(i)
                    return True
            
            try:
                await asyncio.wait_for(self.notification_event.wait(), timeout=0.5)
                self.notification_event.clear()
            except asyncio.TimeoutError:
                continue
        
        return False
    
    async def set_background_color(self, r, g, b, enable=1):
        cmd = self.create_command("BG", bytes([enable, r, g, b]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🌑 Background: RGB({r},{g},{b})")
    
    async def set_display_mode(self, mode):
        cmd = self.create_command("MODE", bytes([mode]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🎭 Mode: {mode}")
    
    async def display_text_fixed(self, text, color=(255, 255, 255)):
        """Version corrigée d'affichage texte"""
        print(f"\n📝 Affichage CORRIGÉ: '{text}'")
        
        # 1. Background noir
        await self.set_background_color(0, 0, 0, 1)
        
        # 2. Conversion bitmap avec vérifications
        bitmap = self.text_to_bitmap_fixed(text)
        bitmap_data = self.encode_bitmap_fixed(bitmap)
        
        # 3. Couleurs 
        r, g, b = color
        colors = bytes([r, g, b] * len(bitmap))
        
        print(f"📊 Upload: {len(bitmap)} colonnes, {len(bitmap_data)}B bitmap, {len(colors)}B couleurs")
        
        # 4. Upload séquence
        # DATS
        cmd = self.create_command("DATS", struct.pack('<HH', len(bitmap_data), len(colors)))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await self.wait_for_response("OK")
        
        # Upload bitmap par chunks de 16 bytes
        chunk_size = 16
        for i in range(0, len(bitmap_data), chunk_size):
            chunk = bitmap_data[i:i+chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            await self.wait_for_response("OK")
        
        # Upload couleurs par chunks de 16 bytes
        for i in range(0, len(colors), chunk_size):
            chunk = colors[i:i+chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            await self.wait_for_response("OK")
        
        # DATCP
        cmd = self.create_command("DATCP")
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await self.wait_for_response("OK")
        
        # 5. Mode d'affichage
        await self.set_display_mode(1)
        
        print(f"✅ '{text}' affiché avec bitmap corrigé!")
    
    async def run_test(self):
        if not await self.connect():
            return
        
        try:
            print("\n" + "="*50)
            print("🔧 TEST AFFICHAGE CORRIGÉ")
            print("="*50)
            
            # Test avec des textes simples
            test_texts = ["HELLO", "WORLD", "LED"]
            
            for text in test_texts:
                await self.display_text_fixed(text)
                await asyncio.sleep(3)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client:
                await self.client.disconnect()
                print("🔌 Déconnecté")

async def main():
    display = FixedTextDisplay()
    await display.run_test()

if __name__ == "__main__":
    print("🔧 TEST AFFICHAGE PIXELS CORRIGÉ")
    asyncio.run(main())
