"""
AFFICHEUR DE TEXTE FINAL - VERSION COMPLÈTE
Protocole d'upload de texte FONCTIONNEL basé sur mask-go
Support des caractères complets avec chunking intelligent
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct
import time

# Configuration validée
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class MaskTextDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
        
        # Police complète 8x16 pixels - CORRIGÉE
        self.font_patterns = {
            'A': [
                "  ████  ",
                " █    █ ",
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
                "        ",
                "        ",
                "        "
            ],
            'B': [
                "███████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "███████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "███████ ",
                "        ",
                "        ",
                "        "
            ],
            'C': [
                " ███████",
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
                " ███████",
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
                "█      █",
                "█     █ ",
                "██████  ",
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
                "█       ",
                "████████",
                "        ",
                "        ",
                "        "
            ],
            'F': [
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
                "        ",
                "        ",
                "        "
            ],
            'G': [
                " ███████",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█   ████",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ███████",
                "        ",
                "        ",
                "        "
            ],
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
            'I': [
                "████████",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "████████",
                "        ",
                "        ",
                "        "
            ],
            'J': [
                "████████",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "█     █ ",
                "█     █ ",
                "█     █ ",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            'K': [
                "█     █ ",
                "█    █  ",
                "█   █   ",
                "█  █    ",
                "█ █     ",
                "██      ",
                "█ █     ",
                "█  █    ",
                "█   █   ",
                "█    █  ",
                "█     █ ",
                "█      █",
                "█      █",
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
                "█       ",
                "████████",
                "        ",
                "        ",
                "        "
            ],
            'M': [
                "█      █",
                "██    ██",
                "█ █  █ █",
                "█  ██  █",
                "█      █",
                "█      █",
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
            'N': [
                "█      █",
                "██     █",
                "█ █    █",
                "█  █   █",
                "█   █  █",
                "█    █ █",
                "█     ██",
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
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            'P': [
                "███████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "███████ ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "        ",
                "        ",
                "        "
            ],
            'Q': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█   █  █",
                "█    █ █",
                "█     ██",
                " ██████ ",
                "       █",
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
                "█  █    ",
                "█   █   ",
                "█    █  ",
                "█     █ ",
                "█      █",
                "█      █",
                "█      █",
                "        ",
                "        ",
                "        "
            ],
            'S': [
                " ███████",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                " ██████ ",
                "       █",
                "       █",
                "       █",
                "       █",
                "       █",
                "       █",
                "███████ ",
                "        ",
                "        ",
                "        "
            ],
            'T': [
                "████████",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "        ",
                "        ",
                "        "
            ],
            'U': [
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
                "        ",
                "        ",
                "        "
            ],
            'V': [
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " █    █ ",
                " █    █ ",
                "  █  █  ",
                "  █  █  ",
                "   ██   ",
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
                "█      █",
                "█      █",
                "█  ██  █",
                "█ █  █ █",
                "█ █  █ █",
                "██    ██",
                "█      █",
                "█      █",
                "        ",
                "        ",
                "        "
            ],
            'X': [
                "█      █",
                " █    █ ",
                "  █  █  ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "  █  █  ",
                " █    █ ",
                "█      █",
                "█      █",
                "█      █",
                "        ",
                "        ",
                "        "
            ],
            'Y': [
                "█      █",
                " █    █ ",
                "  █  █  ",
                "   ██   ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "        ",
                "        ",
                "        "
            ],
            'Z': [
                "████████",
                "      █ ",
                "     █  ",
                "    █   ",
                "   █    ",
                "  █     ",
                " █      ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "████████",
                "        ",
                "        ",
                "        "
            ],
            '0': [
                " ██████ ",
                "█      █",
                "█     ██",
                "█    █ █",
                "█   █  █",
                "█  █   █",
                "█ █    █",
                "██     █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            '1': [
                "   █    ",
                "  ██    ",
                " █ █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "████████",
                "        ",
                "        ",
                "        "
            ],
            '2': [
                " ██████ ",
                "█      █",
                "       █",
                "       █",
                "       █",
                "      █ ",
                "     █  ",
                "    █   ",
                "   █    ",
                "  █     ",
                " █      ",
                "█       ",
                "████████",
                "        ",
                "        ",
                "        "
            ],
            '3': [
                " ██████ ",
                "█      █",
                "       █",
                "       █",
                "       █",
                " ██████ ",
                "       █",
                "       █",
                "       █",
                "       █",
                "       █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            '4': [
                "      █ ",
                "     ██ ",
                "    █ █ ",
                "   █  █ ",
                "  █   █ ",
                " █    █ ",
                "█     █ ",
                "████████",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "        ",
                "        ",
                "        "
            ],
            '5': [
                "████████",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "███████ ",
                "       █",
                "       █",
                "       █",
                "       █",
                "       █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            '6': [
                " ██████ ",
                "█      █",
                "█       ",
                "█       ",
                "█       ",
                "███████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            '7': [
                "████████",
                "       █",
                "      █ ",
                "     █  ",
                "    █   ",
                "   █    ",
                "  █     ",
                " █      ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "        ",
                "        ",
                "        "
            ],
            '8': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            '9': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ███████",
                "       █",
                "       █",
                "       █",
                "█      █",
                " ██████ ",
                "        ",
                "        ",
                "        "
            ],
            '!': [
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "        ",
                "        ",
                "   ██   ",
                "   ██   ",
                "        ",
                "        ",
                "        "
            ],
            '?': [
                " ██████ ",
                "█      █",
                "       █",
                "       █",
                "      █ ",
                "     █  ",
                "    █   ",
                "   █    ",
                "   █    ",
                "        ",
                "        ",
                "   █    ",
                "   █    ",
                "        ",
                "        ",
                "        "
            ],
            '.': [
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
                "   ██   ",
                "   ██   ",
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
            ],
            '-': [
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "        ",
                "████████",
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
    
    def text_to_bitmap(self, text):
        """Convertit le texte en bitmap - VERSION CORRIGÉE"""
        columns = []
        
        for char in text.upper():
            if char in self.font_patterns:
                pattern = self.font_patterns[char]
                
                # Vérification: le pattern doit avoir exactement 16 lignes
                if len(pattern) != 16:
                    print(f"⚠️ Pattern '{char}': {len(pattern)} lignes au lieu de 16")
                    # Ajuste le pattern
                    while len(pattern) < 16:
                        pattern.append("        ")
                    pattern = pattern[:16]
                
                # 8 colonnes par caractère
                for col_idx in range(8):
                    column = []
                    for row_idx in range(16):
                        # Vérification: chaque ligne doit faire 8 caractères
                        if len(pattern[row_idx]) < 8:
                            line = pattern[row_idx] + " " * (8 - len(pattern[row_idx]))
                        else:
                            line = pattern[row_idx][:8]
                        
                        if line[col_idx] == '█':
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
    
    async def wait_for_response(self, expected, timeout=10):
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
        """Définit la couleur de background"""
        # Commande BG découverte dans mask-go: 06BG<enable><r><g><b>
        cmd = self.create_command("BG", bytes([enable, r, g, b]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🌟 Background: RGB({r},{g},{b}) {'activé' if enable else 'désactivé'}")
    
    async def set_display_mode(self, mode):
        """Définit le mode d'affichage (CRUCIAL!)"""
        # mode: 1=steady, 2=blink, 3=scroll left, 4=scroll right, 5=steady
        cmd = self.create_command("MODE", bytes([mode]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🎭 Mode: {mode}")
    
    async def display_text(self, text, color=(255, 255, 255), background=(0, 0, 0)):
        """Affiche du texte avec couleur de background personnalisée"""
        print(f"\n📝 Affichage: '{text}'")
        
        # 1. Définir le background en premier
        bg_r, bg_g, bg_b = background
        if background != (0, 0, 0):  # Si ce n'est pas noir par défaut
            print(f"🌟 Configuration background RGB({bg_r},{bg_g},{bg_b})")
            await self.set_background_color(bg_r, bg_g, bg_b, 1)
        else:
            print("🌑 Configuration background noir")
            await self.set_background_color(0, 0, 0, 1)  # Background noir
        
        await asyncio.sleep(0.5)  # Délai pour appliquer le background
        
        # 2. Créer le bitmap
        bitmap_columns = self.text_to_bitmap(text)
        if not bitmap_columns:
            print("❌ Aucun caractère valide")
            return False
        
        bitmap_data = self.encode_bitmap(bitmap_columns)
        color_data = self.encode_colors(len(bitmap_columns), color)
        
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        print(f"📊 {len(bitmap_columns)} colonnes, {bitmap_len}B bitmap, {len(color_data)}B couleurs")
        
        # ÉTAPE 1: Initialiser avec DATS
        self.responses.clear()
        
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATSOK", 5):
            print("❌ Pas de DATSOK")
            return False
        
        # ÉTAPE 2: Upload des données par chunks
        complete_data = bitmap_data + color_data
        max_chunk = 96  # Taille sûre
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
        
        # ÉTAPE 3: Finaliser avec DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATCPOK", 5):
            print("❌ Pas de DATCPOK")
            return False
        
        # CRUCIAL: Définir le mode d'affichage après l'upload!
        print("🎭 Application du mode d'affichage...")
        await asyncio.sleep(0.5)  # Petit délai
        await self.set_display_mode(1)  # 1 = steady (affichage fixe)
        
        print(f"✅ '{text}' affiché avec succès!")
        return True
    
    async def brightness(self, level):
        """Contrôle la luminosité"""
        cmd = self.create_command("LIGHT", bytes([level]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"💡 Luminosité: {level}")
    
    async def show_image(self, image_num):
        """Affiche une image prédéfinie"""
        cmd = self.create_command("PLAY", bytes([image_num]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🖼️ Image: {image_num}")
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def demo():
    """Démonstration complète"""
    print("🎭 AFFICHEUR DE TEXTE LED MASK")
    print("Protocole complet fonctionnel")
    print("=" * 40)
    
    mask = MaskTextDisplay()
    
    if await mask.connect():
        try:
            # Régler la luminosité
            await mask.brightness(100)
            await asyncio.sleep(1)
            
            # Messages de démonstration avec backgrounds noirs
            messages = [
                ("HELLO", (255, 0, 0), (0, 0, 0)),      # Rouge sur noir
                ("WORLD", (0, 255, 0), (0, 0, 0)),      # Vert sur noir  
                ("LED MASK", (0, 0, 255), (0, 0, 0)),   # Bleu sur noir
                ("SUCCESS!", (255, 255, 0), (0, 0, 0)), # Jaune sur noir
                ("2024", (255, 0, 255), (0, 0, 0)),     # Magenta sur noir
                ("PYTHON", (0, 255, 255), (0, 0, 0))    # Cyan sur noir
            ]
            
            for text, color, bg_color in messages:
                success = await mask.display_text(text, color, bg_color)
                if success:
                    await asyncio.sleep(3)  # Laisser le temps de voir
                else:
                    print(f"❌ Échec pour '{text}'")
                    break
            
            print("\n🎉 Démonstration terminée!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await mask.disconnect()
    else:
        print("💡 Vérifiez que le masque est allumé")

if __name__ == "__main__":
    asyncio.run(demo())
