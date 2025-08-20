#!/usr/bin/env python3

import asyncio
import struct
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "D44BC439-ABFD-45A2-B575-925416129600"
COMMAND_CHAR = "D44BC439-ABFD-45A2-B575-925416129600"
UPLOAD_CHAR = "D44BC439-ABFD-45A2-B575-92541612960A"
NOTIFY_CHAR = "D44BC439-ABFD-45A2-B575-925416129601"

class PixelDiagnostic:
    def __init__(self):
        self.client = None
        self.responses = []
        self.notification_event = asyncio.Event()
        
        # Font simplifié pour diagnostic
        self.simple_font = {
            'H': [
                "█      █",
                "█      █", 
                "█      █",
                "█      █",
                "████████",
                "█      █",
                "█      █",
                "█      █",
                "        ",
                "        "
            ],
            'I': [
                "████████",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "████████",
                "        ",
                "        "
            ]
        }
    
    def _notification_handler(self, sender, data):
        """Gestionnaire des notifications"""
        response = data.decode('utf-8', errors='ignore')
        self.responses.append(response)
        self.notification_event.set()
        print(f"📨 {response}")
    
    def create_command(self, cmd, data=b''):
        """Crée une commande chiffrée"""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        
        key = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
        
        payload = cmd.encode() + data
        if len(payload) < 16:
            payload += b'\x00' * (16 - len(payload))
        elif len(payload) > 16:
            payload = payload[:16]
        
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(payload) + encryptor.finalize()
    
    async def connect(self):
        """Connexion au masque"""
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
    
    def test_bitmap_alignment(self, text):
        """Test l'alignement des pixels"""
        print(f"\n🔍 Diagnostic pour: '{text}'")
        columns = []
        
        for i, char in enumerate(text.upper()):
            if char in self.simple_font:
                pattern = self.simple_font[char]
                print(f"\nCaractère '{char}' (position {i}):")
                
                # Affiche le pattern pour vérification visuelle
                for row_idx, row in enumerate(pattern):
                    print(f"Row {row_idx:2d}: {row}")
                
                # Convertit en colonnes
                for col_idx in range(8):
                    column = []
                    for row_idx in range(len(pattern)):
                        if col_idx < len(pattern[row_idx]) and pattern[row_idx][col_idx] == '█':
                            column.append(1)
                        else:
                            column.append(0)
                    
                    # Complète à 16 pixels si nécessaire
                    while len(column) < 16:
                        column.append(0)
                    
                    columns.append(column)
                    print(f"Col {col_idx}: {column[:10]}...")  # Affiche les 10 premiers
        
        print(f"\n📊 Total colonnes générées: {len(columns)}")
        return columns
    
    def encode_bitmap_debug(self, bitmap):
        """Encode avec debug"""
        encoded = bytearray()
        
        for i, column in enumerate(bitmap):
            val = 0
            for j, pixel in enumerate(column[:16]):
                if pixel == 1:
                    val |= (1 << j)
            
            # Debug: affiche la valeur de chaque colonne
            if i < 10:  # Premières colonnes seulement
                print(f"Col {i}: pixels={column[:8]} -> val=0x{val:04x}")
            
            encoded.extend(struct.pack('<H', val))
        
        print(f"📦 Bitmap encodé: {len(encoded)} bytes")
        return bytes(encoded)
    
    async def test_simple_pattern(self):
        """Test avec un pattern très simple"""
        print("\n🧪 Test pattern simple...")
        
        # Pattern simple: ligne verticale
        simple_bitmap = []
        for col in range(8):  # Une seule lettre
            column = [1] * 8 + [0] * 8  # 8 pixels allumés en haut
            simple_bitmap.append(column)
        
        bitmap_data = self.encode_bitmap_debug(simple_bitmap)
        
        # Upload
        await self.upload_bitmap(bitmap_data, len(simple_bitmap))
        
        # Mode d'affichage
        cmd = self.create_command("MODE", bytes([1]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print("🎭 Pattern simple affiché")
    
    async def upload_bitmap(self, bitmap_data, num_columns):
        """Upload bitmap avec diagnostic"""
        colors = bytes([255, 255, 255] * num_columns)  # Blanc
        
        print(f"📊 Upload: {num_columns} colonnes, {len(bitmap_data)}B bitmap, {len(colors)}B couleurs")
        
        # DATS
        cmd = self.create_command("DATS", struct.pack('<HH', len(bitmap_data), len(colors)))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await self.wait_for_response("OK")
        
        # Upload bitmap par chunks
        chunk_size = 16
        for i in range(0, len(bitmap_data), chunk_size):
            chunk = bitmap_data[i:i+chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            await self.wait_for_response("OK")
        
        # Upload couleurs par chunks
        for i in range(0, len(colors), chunk_size):
            chunk = colors[i:i+chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            await self.wait_for_response("OK")
        
        # DATCP
        cmd = self.create_command("DATCP")
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await self.wait_for_response("OK")
    
    async def wait_for_response(self, expected, timeout=5):
        """Attend une réponse"""
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
    
    async def test_text_display(self, text):
        """Test complet d'affichage"""
        bitmap = self.test_bitmap_alignment(text)
        bitmap_data = self.encode_bitmap_debug(bitmap)
        
        # Background noir
        cmd = self.create_command("BG", bytes([1, 0, 0, 0]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print("🌑 Background noir configuré")
        
        # Upload
        await self.upload_bitmap(bitmap_data, len(bitmap))
        
        # Mode d'affichage
        cmd = self.create_command("MODE", bytes([1]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"✅ '{text}' affiché")
    
    async def run_diagnostic(self):
        """Lance le diagnostic complet"""
        if not await self.connect():
            return
        
        print("\n" + "="*50)
        print("🔧 DIAGNOSTIC PIXELS LED MASK")
        print("="*50)
        
        try:
            # Test 1: Pattern très simple
            await self.test_simple_pattern()
            await asyncio.sleep(2)
            
            # Test 2: Texte simple
            await self.test_text_display("HI")
            await asyncio.sleep(2)
            
            # Test 3: Un seul caractère
            await self.test_text_display("H")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        finally:
            if self.client:
                await self.client.disconnect()
                print("🔌 Déconnecté")

async def main():
    diagnostic = PixelDiagnostic()
    await diagnostic.run_diagnostic()

if __name__ == "__main__":
    print("🧪 DIAGNOSTIC AFFICHAGE PIXELS")
    asyncio.run(main())
