"""
Test avancé de texte avec animations
Version expérimentale avec effets visuels
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import random

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"

class AdvancedTextTest:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def create_text_bitmap(self, text, width=64, height=32):
        """Crée un bitmap simple pour le texte (sans PIL)"""
        # Bitmap basique avec motifs ASCII
        bitmap = []
        
        # Patterns pour quelques caractères
        patterns = {
            'A': [
                "  ███   ",
                " █   █  ",
                " █████  ",
                " █   █  ",
                " █   █  "
            ],
            'B': [
                " ████   ",
                " █   █  ",
                " ████   ",
                " █   █  ",
                " ████   "
            ],
            'C': [
                "  ███   ",
                " █      ",
                " █      ",
                " █      ",
                "  ███   "
            ],
            'E': [
                " █████  ",
                " █      ",
                " ████   ",
                " █      ",
                " █████  "
            ],
            'H': [
                " █   █  ",
                " █   █  ",
                " █████  ",
                " █   █  ",
                " █   █  "
            ],
            'L': [
                " █      ",
                " █      ",
                " █      ",
                " █      ",
                " █████  "
            ],
            'O': [
                "  ███   ",
                " █   █  ",
                " █   █  ",
                " █   █  ",
                "  ███   "
            ],
            'R': [
                " ████   ",
                " █   █  ",
                " ████   ",
                " █  █   ",
                " █   █  "
            ],
            ' ': [
                "        ",
                "        ",
                "        ",
                "        ",
                "        "
            ]
        }
        
        # Créer le bitmap
        result = []
        for row in range(5):  # 5 lignes par caractère
            line = ""
            for char in text.upper():
                if char in patterns:
                    line += patterns[char][row]
                else:
                    line += "   █    "  # Caractère par défaut
            result.append(line[:width])
        
        # Ajouter des lignes vides pour atteindre la hauteur
        while len(result) < height:
            result.append(" " * width)
        
        return result[:height]
    
    def bitmap_to_bytes(self, bitmap, color=(255, 255, 255)):
        """Convertit le bitmap en bytes pour upload"""
        data = bytearray()
        
        # En-tête couleur
        r, g, b = color
        data.extend([r, g, b, 0])
        
        # Conversion bitmap
        for row in bitmap:
            byte_row = 0
            for i, char in enumerate(row):
                if char == '█' and i < 8:
                    byte_row |= (1 << (7 - i))
            data.append(byte_row)
        
        return bytes(data)
    
    async def connect(self):
        """Connexion au masque"""
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
        print("✅ Connecté")
        return True
    
    async def upload_text_bitmap(self, bitmap_data):
        """Upload du bitmap texte"""
        # Commande DATS
        dats_cmd = self.create_command("DATS", len(bitmap_data).to_bytes(2, 'big'))
        await self.client.write_gatt_char(COMMAND_CHAR, dats_cmd)
        await asyncio.sleep(0.2)
        
        # Upload par chunks
        for i in range(0, len(bitmap_data), 20):
            chunk = bitmap_data[i:i + 20]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            await asyncio.sleep(0.1)
        
        # Finalisation
        datcp_cmd = self.create_command("DATCP")
        await self.client.write_gatt_char(COMMAND_CHAR, datcp_cmd)
        await asyncio.sleep(0.5)
    
    async def display_word(self, word, color=(255, 0, 0)):
        """Affiche un mot"""
        print(f"📝 Affichage: {word}")
        
        bitmap = self.create_text_bitmap(word)
        bitmap_data = self.bitmap_to_bytes(bitmap, color)
        
        await self.upload_text_bitmap(bitmap_data)
        print(f"✅ '{word}' affiché")
    
    async def color_animation(self, word):
        """Animation de couleur sur un mot"""
        colors = [
            (255, 0, 0),    # Rouge
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Jaune
            (0, 255, 0),    # Vert
            (0, 0, 255),    # Bleu
            (75, 0, 130),   # Indigo
            (148, 0, 211)   # Violet
        ]
        
        print(f"🌈 Animation arc-en-ciel: {word}")
        
        for color in colors:
            await self.display_word(word, color)
            await asyncio.sleep(0.8)
    
    async def word_sequence(self, words, delay=2):
        """Séquence de mots"""
        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255)
        ]
        
        for i, word in enumerate(words):
            color = colors[i % len(colors)]
            await self.display_word(word, color)
            await asyncio.sleep(delay)
    
    async def text_demo(self):
        """Démonstration complète"""
        print("\n🎭 DÉMONSTRATION TEXTE AVANCÉE")
        print("=" * 40)
        
        # Mots simples
        await self.word_sequence(["HELLO", "WORLD", "LED", "MASK"])
        
        # Animation arc-en-ciel
        await self.color_animation("COLOR")
        
        # Messages courts
        messages = ["OK", "HI", "BYE", "LOL", "WOW"]
        for msg in messages:
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            await self.display_word(msg, color)
            await asyncio.sleep(1.5)
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Main"""
    controller = AdvancedTextTest()
    
    if await controller.connect():
        try:
            await controller.text_demo()
        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé")
        finally:
            await controller.disconnect()

if __name__ == "__main__":
    print("🎨 TEST TEXTE AVANCÉ")
    print("Animations et effets de texte")
    asyncio.run(main())
