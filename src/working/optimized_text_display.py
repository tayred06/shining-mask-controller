#!/usr/bin/env python3

import asyncio
import struct
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration BLE
SERVICE_UUID = "d44bc439-abfd-45a2-b575-925416129600"
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

# Clé de chiffrement découverte
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')

class OptimizedMaskDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
        
        # Police optimisée 8x16 - patterns courts pour éviter les gros uploads
        self.font_patterns = {
            'H': [
                "█      █", "█      █", "█      █", "█      █", 
                "████████", "█      █", "█      █", "█      █", 
                "█      █", "█      █", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'E': [
                "████████", "█       ", "█       ", "█       ", 
                "███████ ", "█       ", "█       ", "█       ", 
                "█       ", "████████", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'L': [
                "█       ", "█       ", "█       ", "█       ", 
                "█       ", "█       ", "█       ", "█       ", 
                "█       ", "████████", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'O': [
                " ██████ ", "█      █", "█      █", "█      █", 
                "█      █", "█      █", "█      █", "█      █", 
                "█      █", " ██████ ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'W': [
                "█      █", "█      █", "█      █", "█  ██  █", 
                "█  ██  █", "█ ████ █", "█ ████ █", "██    ██", 
                "█      █", "        ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'R': [
                "███████ ", "█      █", "█      █", "█      █", 
                "███████ ", "█ ██    ", "█  ██   ", "█   █   ", 
                "█    ██ ", "        ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'D': [
                "██████  ", "█     █ ", "█      █", "█      █", 
                "█      █", "█      █", "█      █", "█      █", 
                "█     █ ", "██████  ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'I': [
                "████████", "   █    ", "   █    ", "   █    ", 
                "   █    ", "   █    ", "   █    ", "   █    ", 
                "   █    ", "████████", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'M': [
                "██    ██", "███  ███", "████████", "█ ████ █", 
                "█  ██  █", "█      █", "█      █", "█      █", 
                "█      █", "        ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'A': [
                "  ████  ", " █    █ ", "█      █", "█      █", 
                "████████", "█      █", "█      █", "█      █", 
                "█      █", "        ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'S': [
                " ███████", "█       ", "█       ", "█       ", 
                " ██████ ", "       █", "       █", "       █", 
                "       █", "███████ ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            'K': [
                "█     ██", "█    █  ", "█   █   ", "█  █    ", 
                "███     ", "█  █    ", "█   █   ", "█    █  ", 
                "█     ██", "        ", "        ", "        ",
                "        ", "        ", "        ", "        "
            ],
            ' ': [
                "        ", "        ", "        ", "        ", 
                "        ", "        ", "        ", "        ", 
                "        ", "        ", "        ", "        ",
                "        ", "        ", "        ", "        "
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
    
    def text_to_bitmap(self, text):
        """Conversion optimisée texte vers bitmap"""
        columns = []
        
        for char in text.upper():
            if char in self.font_patterns:
                pattern = self.font_patterns[char]
                
                # 8 colonnes par caractère, 16 lignes exactement
                for col_idx in range(8):
                    column = []
                    for row_idx in range(16):
                        if row_idx < len(pattern) and col_idx < len(pattern[row_idx]):
                            pixel = 1 if pattern[row_idx][col_idx] == '█' else 0
                        else:
                            pixel = 0
                        column.append(pixel)
                    columns.append(column)
        
        return columns
    
    def encode_bitmap(self, bitmap):
        """Encodage bitmap optimisé"""
        encoded = bytearray()
        
        for column in bitmap:
            val = 0
            for j, pixel in enumerate(column[:16]):
                if pixel == 1:
                    val |= (1 << j)
            
            encoded.extend(struct.pack('<H', val))
        
        return bytes(encoded)
    
    async def wait_for_response(self, expected, timeout=5):
        """Attente réponse avec timeout réduit"""
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            for i, response in enumerate(self.responses):
                if expected in response:
                    self.responses.pop(i)
                    return True
            
            try:
                await asyncio.wait_for(self.notification_event.wait(), timeout=0.3)
                self.notification_event.clear()
            except asyncio.TimeoutError:
                continue
        
        return False
    
    async def upload_with_delays(self, bitmap_data, colors):
        """Upload avec délais pour éviter les déconnexions"""
        chunk_size = 16
        
        print(f"📊 Upload: {len(bitmap_data)}B bitmap, {len(colors)}B couleurs")
        
        # DATS
        cmd = self.create_command("DATS", struct.pack('<HH', len(bitmap_data), len(colors)))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        if not await self.wait_for_response("OK"):
            print("❌ DATS timeout")
            return False
        
        # Upload bitmap avec délais
        print("📤 Upload bitmap...")
        for i in range(0, len(bitmap_data), chunk_size):
            chunk = bitmap_data[i:i+chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            
            if not await self.wait_for_response("OK"):
                print(f"❌ Bitmap chunk {i//chunk_size} timeout")
                return False
            
            # Petit délai entre chunks pour éviter la surcharge
            await asyncio.sleep(0.05)
        
        # Upload couleurs avec délais
        print("🎨 Upload couleurs...")
        for i in range(0, len(colors), chunk_size):
            chunk = colors[i:i+chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            
            if not await self.wait_for_response("OK"):
                print(f"❌ Color chunk {i//chunk_size} timeout")
                return False
            
            await asyncio.sleep(0.05)
        
        # DATCP
        cmd = self.create_command("DATCP")
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        if not await self.wait_for_response("OK"):
            print("❌ DATCP timeout")
            return False
        
        return True
    
    async def display_text_optimized(self, text, color=(255, 255, 255)):
        """Affichage texte optimisé avec gestion des erreurs"""
        print(f"\n📝 Affichage OPTIMISÉ: '{text}'")
        
        # Limite la longueur pour éviter les problèmes
        if len(text) > 8:
            print(f"⚠️ Texte tronqué à 8 caractères: '{text[:8]}'")
            text = text[:8]
        
        try:
            # 1. Background noir
            cmd = self.create_command("BG", bytes([1, 0, 0, 0]))
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            print("🌑 Background noir configuré")
            
            # 2. Bitmap
            bitmap = self.text_to_bitmap(text)
            bitmap_data = self.encode_bitmap(bitmap)
            
            # 3. Couleurs
            r, g, b = color
            colors = bytes([r, g, b] * len(bitmap))
            
            # 4. Upload avec gestion d'erreurs
            if not await self.upload_with_delays(bitmap_data, colors):
                print("❌ Erreur upload")
                return False
            
            # 5. Mode d'affichage
            cmd = self.create_command("MODE", bytes([1]))
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            print("🎭 Mode appliqué")
            
            print(f"✅ '{text}' affiché avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
            return False
    
    async def demo_optimized(self):
        """Démo avec gestion optimisée"""
        if not await self.connect():
            return
        
        try:
            print("\n" + "="*50)
            print("🚀 DÉMO AFFICHAGE OPTIMISÉ")
            print("="*50)
            
            # Tests progressifs
            tests = [
                ("HI", (255, 255, 255)),      # Blanc
                ("LED", (255, 0, 0)),         # Rouge
                ("MASK", (0, 255, 0)),        # Vert
                ("HELLO", (0, 0, 255)),       # Bleu
                ("WORLD", (255, 255, 0))      # Jaune
            ]
            
            for text, color in tests:
                success = await self.display_text_optimized(text, color)
                if success:
                    await asyncio.sleep(2)
                else:
                    print(f"⚠️ Échec pour '{text}', on continue...")
                    await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Erreur démo: {e}")
        finally:
            if self.client and self.client.is_connected:
                await self.client.disconnect()
                print("🔌 Déconnecté")

async def main():
    display = OptimizedMaskDisplay()
    await display.demo_optimized()

if __name__ == "__main__":
    print("🚀 AFFICHAGE TEXTE OPTIMISÉ")
    asyncio.run(main())
