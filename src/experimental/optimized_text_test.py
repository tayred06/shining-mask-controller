"""
Afficheur de texte OPTIMISÉ avec timing amélioré
Version basée sur mask-go avec corrections des notifications
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct

# Configuration validée
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class OptimizedTextDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.upload_running = False
        self.responses = []  # Queue des réponses
        self.notification_event = asyncio.Event()
        
        # Patterns simplifiés 5x12 pour test (plus petit)
        self.simple_chars = {
            'H': [
                "█   █",
                "█   █", 
                "█   █",
                "█████",
                "█   █",
                "█   █",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     "
            ],
            'I': [
                "█████",
                "  █  ",
                "  █  ",
                "  █  ",
                "  █  ",
                "█████",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     "
            ],
            ' ': [
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
                "     "
            ]
        }
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def _notification_handler(self, sender, data):
        """Gestionnaire amélioré des notifications"""
        try:
            decrypted = self.cipher.decrypt(data)
            str_len = decrypted[0]
            if str_len > 0 and str_len < len(decrypted):
                response = decrypted[1:str_len+1].decode('ascii', errors='ignore')
                self.responses.append(response)
                self.notification_event.set()
                print(f"📨 Réponse: {response}")
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    async def connect(self):
        """Connexion avec notifications"""
        print("🔍 Recherche du masque...")
        devices = await BleakScanner.discover()
        
        mask = None
        for device in devices:
            if "MASK" in (device.name or ""):
                mask = device
                break
        
        if not mask:
            print("❌ Masque non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask.name}...")
        self.client = BleakClient(mask.address)
        await self.client.connect()
        
        # Activer les notifications
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        
        print("✅ Connecté avec notifications")
        return True
    
    def text_to_simple_bitmap(self, text):
        """Version simplifiée pour test"""
        columns = []
        
        for char in text.upper():
            if char in self.simple_chars:
                pattern = self.simple_chars[char]
                
                # 5 colonnes par caractère
                for col_idx in range(5):
                    column = []
                    for row_idx in range(12):  # 12 pixels seulement
                        if col_idx < len(pattern[row_idx]) and pattern[row_idx][col_idx] == '█':
                            column.append(1)
                        else:
                            column.append(0)
                    # Étendre à 16 pixels
                    while len(column) < 16:
                        column.append(0)
                    columns.append(column)
        
        return columns
    
    def encode_bitmap_for_mask(self, bitmap):
        """Encode bitmap selon mask-go (simplifié)"""
        encoded = bytearray()
        
        for column in bitmap:
            # Convertir la colonne en 2 bytes
            val = 0
            for j, pixel in enumerate(column[:16]):  # Max 16 pixels
                if pixel == 1:
                    val |= (1 << j)
            
            # 2 bytes par colonne (little endian)
            encoded.extend(struct.pack('<H', val))
        
        return bytes(encoded)
    
    def encode_color_array(self, num_columns, color=(255, 255, 255)):
        """Array de couleurs (3 bytes RGB par colonne)"""
        r, g, b = color
        colors = bytearray()
        
        for _ in range(num_columns):
            colors.extend([r, g, b])
        
        return bytes(colors)
    
    async def wait_for_specific_response(self, expected, timeout=10):
        """Attend une réponse spécifique avec timeout amélioré"""
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Vérifier les réponses déjà reçues
            for i, response in enumerate(self.responses):
                if expected in response:
                    # Supprimer la réponse utilisée
                    self.responses.pop(i)
                    return True
            
            # Attendre une nouvelle notification
            try:
                await asyncio.wait_for(self.notification_event.wait(), timeout=0.5)
                self.notification_event.clear()
            except asyncio.TimeoutError:
                continue
        
        print(f"❌ Timeout pour {expected} après {timeout}s")
        return False
    
    async def simple_upload_test(self, text="HI"):
        """Test simplifié d'upload"""
        print(f"\n📝 Test upload simple: '{text}'")
        
        # Créer un bitmap minimal
        bitmap_columns = self.text_to_simple_bitmap(text)
        if not bitmap_columns:
            print("❌ Pas de bitmap")
            return False
        
        bitmap_data = self.encode_bitmap_for_mask(bitmap_columns)
        color_data = self.encode_color_array(len(bitmap_columns), (0, 255, 0))
        
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        print(f"📊 Bitmap: {bitmap_len}B, Couleurs: {len(color_data)}B, Total: {total_len}B")
        
        # ÉTAPE 1: DATS
        self.responses.clear()
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        
        print("📤 Envoi DATS...")
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_specific_response("DATSOK", 5):
            return False
        
        print("✅ DATSOK reçu")
        
        # ÉTAPE 2: Upload des données (un seul chunk pour simplicité)
        complete_data = bitmap_data + color_data
        
        if len(complete_data) <= 96:  # Un seul chunk
            packet = bytearray([len(complete_data) + 1, 0])  # count=0 pour premier chunk
            packet.extend(complete_data)
            
            print(f"📤 Upload chunk unique: {len(complete_data)} bytes")
            await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
            
            if not await self.wait_for_specific_response("REOK", 5):
                return False
            
            print("✅ REOK reçu")
        else:
            print("❌ Données trop grandes pour ce test")
            return False
        
        # ÉTAPE 3: DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        
        print("📤 Envoi DATCP...")
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_specific_response("DATCPOK", 5):
            return False
        
        print("✅ DATCPOK reçu - Upload terminé!")
        return True
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test simple et rapide"""
    print("🧪 TEST UPLOAD TEXTE SIMPLIFIÉ")
    print("=" * 35)
    
    display = OptimizedTextDisplay()
    
    if await display.connect():
        try:
            # Test avec "HI" (très simple)
            success = await display.simple_upload_test("HI")
            
            if success:
                print("\n🎉 SUCCESS! Le protocole fonctionne!")
                
                # Attendre un peu puis faire un autre test
                await asyncio.sleep(2)
                await display.simple_upload_test("I")
            
        except KeyboardInterrupt:
            print("\n⏹️ Test interrompu")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await display.disconnect()
    else:
        print("💡 Vérifiez que le masque est allumé")

if __name__ == "__main__":
    asyncio.run(main())
