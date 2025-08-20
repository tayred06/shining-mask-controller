"""
Afficheur de texte CORRIGÉ basé sur mask-go
Utilise le format bitmap réel du masque (16 pixels hauteur)
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct

# Configuration validée par mask-go
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class CorrectTextDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.upload_running = False
        self.response_received = False
        self.last_response = ""
        
        # Format confirmé par mask-go : 16 pixels de hauteur (pas 32!)
        self.mask_height = 16
        
        # Patterns 8x16 pour caractères (format correct)
        self.char_patterns = {
            'A': [
                "  ████  ",
                " █    █ ",
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
                "█      █",
                "█      █",
                "█      █",
                "        "
            ],
            'H': [
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
                "█      █",
                "█      █",
                "█      █",
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
                "█       ",
                "█       ",
                "████████",
                "████████",
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
                "█       ",
                "█       ",
                "████████",
                "████████",
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
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
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
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        # Padding à 16 bytes
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def _notification_handler(self, sender, data):
        """Gestionnaire de notifications (format mask-go)"""
        try:
            decrypted = self.cipher.decrypt(data)
            str_len = decrypted[0]
            if str_len > 0 and str_len < len(decrypted):
                response = decrypted[1:str_len+1].decode('ascii', errors='ignore')
                self.last_response = response
                self.response_received = True
                print(f"📨 Réponse masque: {response}")
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
        
        # Activer les notifications (essentiel pour l'upload)
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        
        print("✅ Connecté avec notifications")
        return True
    
    def text_to_bitmap(self, text):
        """Convertit le texte en bitmap format mask-go"""
        columns = []
        
        for char in text.upper():
            if char in self.char_patterns:
                pattern = self.char_patterns[char]
                
                # Créer 8 colonnes pour ce caractère
                for col_idx in range(8):
                    column = []
                    for row_idx in range(16):  # 16 pixels de hauteur
                        if col_idx < len(pattern[row_idx]) and pattern[row_idx][col_idx] == '█':
                            column.append(1)
                        else:
                            column.append(0)
                    columns.append(column)
        
        return columns
    
    def encode_bitmap_for_mask(self, bitmap):
        """Encode bitmap selon le format mask-go"""
        encoded = bytearray()
        
        for column in bitmap:
            if len(column) != 16:
                print(f"❌ Erreur: colonne doit avoir 16 pixels, pas {len(column)}")
                continue
            
            # Encoder selon le format mask-go
            val = 0
            for j, pixel in enumerate(column):
                if pixel == 1:
                    if j == 0:
                        val = val | 128
                    elif j == 1:
                        val = val | 64
                    elif j == 2:
                        val = val | 32
                    elif j == 3:
                        val = val | 16
                    elif j == 4:
                        val = val | 8
                    elif j == 5:
                        val = val | 4
                    elif j == 6:
                        val = val | 2
                    elif j == 7:
                        val = val | 1
                    elif j == 8:
                        val = val | 32768
                    elif j == 9:
                        val = val | 16384
                    elif j == 10:
                        val = val | 8192
                    elif j == 11:
                        val = val | 4096
                    elif j == 12:
                        val = val | 2048
                    elif j == 13:
                        val = val | 1024
                    elif j == 14:
                        val = val | 512
                    elif j == 15:
                        val = val | 256
            
            # 2 bytes par colonne (little endian)
            encoded.extend(struct.pack('<H', val))
        
        return bytes(encoded)
    
    def encode_color_array_for_mask(self, num_columns, color=(255, 255, 255)):
        """Encode array de couleurs (3 bytes RGB par colonne)"""
        r, g, b = color
        colors = bytearray()
        
        for _ in range(num_columns):
            colors.extend([r, g, b])
        
        return bytes(colors)
    
    async def wait_for_response(self, expected_response, timeout=5):
        """Attend une réponse spécifique du masque"""
        self.response_received = False
        for _ in range(timeout * 10):  # 10 checks par seconde
            if self.response_received and expected_response in self.last_response:
                return True
            await asyncio.sleep(0.1)
        return False
    
    async def init_upload(self, bitmap_data, color_data):
        """Initialise l'upload (commande DATS)"""
        if self.upload_running:
            print("❌ Upload déjà en cours")
            return False
        
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        # Commande DATS selon mask-go
        dats_cmd = bytearray([9])  # Longueur
        dats_cmd.extend(b"DATS")   # Commande
        dats_cmd.extend(struct.pack('>H', total_len))    # Longueur totale (big endian)
        dats_cmd.extend(struct.pack('>H', bitmap_len))   # Longueur bitmap (big endian)
        dats_cmd.extend([0])       # Padding
        
        # Padding à 16 bytes
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        
        print(f"📤 DATS: total={total_len}, bitmap={bitmap_len}")
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        # Attendre DATSOK
        if await self.wait_for_response("DATSOK"):
            print("✅ DATSOK reçu, upload autorisé")
            self.upload_running = True
            return True
        else:
            print("❌ Timeout DATSOK")
            return False
    
    async def upload_data_chunks(self, complete_data):
        """Upload des données par chunks"""
        max_chunk = 98  # mask-go utilise max 98 bytes de données par packet
        bytes_sent = 0
        packet_count = 0
        
        while bytes_sent < len(complete_data):
            # Calculer la taille du chunk
            remaining = len(complete_data) - bytes_sent
            chunk_size = min(max_chunk, remaining)
            
            # Extraire le chunk
            chunk = complete_data[bytes_sent:bytes_sent + chunk_size]
            
            # Créer le packet : [len][count][data]
            packet = bytearray([chunk_size + 1, packet_count])
            packet.extend(chunk)
            
            print(f"📤 Chunk {packet_count}: {chunk_size} bytes")
            await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
            
            # Attendre REOK
            if not await self.wait_for_response("REOK", 3):
                print(f"❌ Timeout REOK pour chunk {packet_count}")
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
        
        print(f"✅ Tous les chunks envoyés ({packet_count} packets)")
        return True
    
    async def finish_upload(self):
        """Finalise l'upload (commande DATCP)"""
        datcp_cmd = bytearray([5])  # Longueur
        datcp_cmd.extend(b"DATCP") # Commande
        
        # Padding à 16 bytes
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        
        print("📤 DATCP (finalisation)")
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        # Attendre DATCPOK
        if await self.wait_for_response("DATCPOK"):
            print("✅ DATCPOK reçu, upload terminé")
            self.upload_running = False
            return True
        else:
            print("❌ Timeout DATCPOK")
            return False
    
    async def display_text(self, text, color=(255, 255, 255)):
        """Affiche du texte en utilisant le protocole mask-go"""
        print(f"📝 Affichage texte: '{text}'")
        
        # Créer le bitmap
        bitmap_columns = self.text_to_bitmap(text)
        if not bitmap_columns:
            print("❌ Impossible de créer le bitmap")
            return False
        
        # Encoder selon le format mask-go
        bitmap_data = self.encode_bitmap_for_mask(bitmap_columns)
        color_data = self.encode_color_array_for_mask(len(bitmap_columns), color)
        
        print(f"📊 Bitmap: {len(bitmap_data)} bytes, Couleurs: {len(color_data)} bytes")
        
        # Processus d'upload complet
        if not await self.init_upload(bitmap_data, color_data):
            return False
        
        complete_data = bitmap_data + color_data
        
        if not await self.upload_data_chunks(complete_data):
            return False
        
        if not await self.finish_upload():
            return False
        
        print(f"✅ Texte '{text}' affiché avec succès!")
        return True
    
    async def test_simple(self):
        """Test simple du protocole"""
        print("\n🧪 TEST PROTOCOLE MASK-GO")
        print("=" * 30)
        
        # Test avec "HELLO"
        success = await self.display_text("HELLO", (255, 0, 0))
        
        if success:
            await asyncio.sleep(3)
            # Test avec un autre mot
            await self.display_text("LED", (0, 255, 0))
        
        return success
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test du protocole basé sur mask-go"""
    print("📝 AFFICHEUR TEXTE - PROTOCOLE MASK-GO")
    print("Basé sur le repository GitHub mask-go")
    print("=" * 45)
    
    display = CorrectTextDisplay()
    
    if await display.connect():
        try:
            await display.test_simple()
        except KeyboardInterrupt:
            print("\n⏹️ Test interrompu")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
        finally:
            await display.disconnect()
    else:
        print("💡 Vérifiez que le masque est allumé et proche")

if __name__ == "__main__":
    asyncio.run(main())
