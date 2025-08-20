"""
Afficheur de texte avec background noir
Utilise la commande BG pour définir le background
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class TextDisplayBlackBackground:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
        
        # Police simplifiée pour test
        self.font_patterns = {
            'H': [
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "██████",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "      "
            ],
            'E': [
                "██████",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█████ ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "██████",
                "██████",
                "      "
            ],
            'L': [
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "█     ",
                "██████",
                "██████",
                "      "
            ],
            'O': [
                " ████ ",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                "█    █",
                " ████ ",
                "      "
            ],
            ' ': [
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      ",
                "      "
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
        """Gestionnaire des notifications"""
        try:
            decrypted = self.cipher.decrypt(data)
            str_len = decrypted[0]
            if str_len > 0 and str_len < len(decrypted):
                response = decrypted[1:str_len+1].decode('ascii', errors='ignore')
                self.responses.append(response)
                self.notification_event.set()
                print(f"📨 {response}")
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    async def connect(self):
        """Connexion au masque"""
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
        
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        
        print("✅ Connecté")
        return True
    
    async def wait_for_response(self, expected, timeout=5):
        """Attend une réponse spécifique"""
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
        """Définit la couleur de background (NOUVELLE FONCTION!)"""
        # Commande BG découverte dans mask-go
        cmd = self.create_command("BG", bytes([enable, r, g, b]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🌟 Background: RGB({r},{g},{b}) {'activé' if enable else 'désactivé'}")
    
    async def set_display_mode(self, mode):
        """Définit le mode d'affichage"""
        cmd = self.create_command("MODE", bytes([mode]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🎭 Mode: {mode}")
    
    def text_to_bitmap(self, text):
        """Convertit le texte en bitmap"""
        columns = []
        
        for char in text.upper():
            if char in self.font_patterns:
                pattern = self.font_patterns[char]
                
                # 6 colonnes par caractère
                for col_idx in range(6):
                    column = []
                    for row_idx in range(16):
                        if col_idx < len(pattern[row_idx]) and pattern[row_idx][col_idx] == '█':
                            column.append(1)
                        else:
                            column.append(0)
                    columns.append(column)
        
        return columns
    
    def encode_bitmap(self, bitmap):
        """Encode bitmap pour le masque"""
        encoded = bytearray()
        
        for column in bitmap:
            val = 0
            for j, pixel in enumerate(column[:16]):
                if pixel == 1:
                    val |= (1 << j)
            
            encoded.extend(struct.pack('<H', val))
        
        return bytes(encoded)
    
    def encode_colors(self, num_columns, color=(255, 255, 255)):
        """Encode les couleurs"""
        r, g, b = color
        colors = bytearray()
        
        for _ in range(num_columns):
            colors.extend([r, g, b])
        
        return bytes(colors)
    
    async def display_text_with_black_background(self, text, text_color=(255, 255, 255)):
        """Affiche du texte avec background noir"""
        print(f"\n📝 Affichage: '{text}' avec background noir")
        
        # 1. DÉFINIR LE BACKGROUND NOIR EN PREMIER
        print("🌟 Configuration background noir...")
        await self.set_background_color(0, 0, 0, 1)  # RGB(0,0,0) = noir, enable=1
        await asyncio.sleep(0.5)
        
        # 2. Créer le bitmap
        bitmap_columns = self.text_to_bitmap(text)
        if not bitmap_columns:
            print("❌ Aucun caractère valide")
            return False
        
        bitmap_data = self.encode_bitmap(bitmap_columns)
        color_data = self.encode_colors(len(bitmap_columns), text_color)
        
        total_len = len(bitmap_data) + len(color_data)
        
        print(f"📊 {len(bitmap_columns)} colonnes, {len(bitmap_data)}B bitmap, {len(color_data)}B couleurs")
        
        # 3. Upload bitmap
        self.responses.clear()
        
        # DATS
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', len(bitmap_data)))
        dats_cmd.extend([0])
        
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATSOK"):
            print("❌ Pas de DATSOK")
            return False
        
        # Upload des données
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
            
            await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
            
            if not await self.wait_for_response("REOK", 3):
                print(f"❌ Pas de REOK pour chunk {packet_count}")
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
        
        # DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATCPOK"):
            print("❌ Pas de DATCPOK")
            return False
        
        # 4. Appliquer le mode d'affichage
        print("🎭 Application du mode d'affichage...")
        await asyncio.sleep(0.5)
        await self.set_display_mode(1)  # Mode steady
        
        print(f"✅ '{text}' affiché avec background noir!")
        return True
    
    async def test_background_colors(self):
        """Test différentes couleurs de background"""
        print("\n🎨 TEST DIFFÉRENTS BACKGROUNDS")
        print("=" * 35)
        
        backgrounds = [
            (0, 0, 0, "Noir"),
            (255, 0, 0, "Rouge"),
            (0, 255, 0, "Vert"),
            (0, 0, 255, "Bleu"),
            (0, 0, 0, "Retour au noir")
        ]
        
        for r, g, b, name in backgrounds:
            print(f"🌟 Background {name}")
            await self.set_background_color(r, g, b, 1)
            await asyncio.sleep(2)
        
        # Puis afficher du texte avec background noir
        await self.display_text_with_black_background("HELLO", (255, 255, 0))
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test avec background noir"""
    print("🌑 AFFICHAGE TEXTE - BACKGROUND NOIR")
    print("Utilise la commande BG découverte dans mask-go")
    print("=" * 45)
    
    display = TextDisplayBlackBackground()
    
    if await display.connect():
        try:
            # Tester différents backgrounds puis texte
            await display.test_background_colors()
            
            await asyncio.sleep(3)
            
            # Texte avec différentes couleurs sur fond noir
            texts = [
                ("HELLO", (255, 0, 0)),    # Rouge
                ("WORLD", (0, 255, 0)),    # Vert
                ("LED", (0, 0, 255))       # Bleu
            ]
            
            for text, color in texts:
                await display.display_text_with_black_background(text, color)
                await asyncio.sleep(3)
            
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
