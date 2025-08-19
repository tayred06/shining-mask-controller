"""
Contrôleur de texte réel pour masque LED
Version corrigée avec gestion des bitmaps et couleurs
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"

class RealTextController:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.width = 64
        self.height = 32
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def text_to_bitmap(self, text, color=(255, 255, 255), scroll_pos=0):
        """Convertit le texte en bitmap pour le masque"""
        # Créer une image plus large pour le défilement
        img_width = max(200, len(text) * 12)
        img = Image.new('RGB', (img_width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            # Essayer d'utiliser une police système
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Dessiner le texte
        draw.text((10 - scroll_pos, 8), text, fill=color, font=font)
        
        # Redimensionner à la taille du masque
        img = img.resize((self.width, self.height))
        
        # Convertir en bitmap monochrome
        bitmap = np.array(img.convert('L'))
        
        # Seuil pour noir/blanc
        bitmap = (bitmap > 128).astype(np.uint8)
        
        return bitmap, color
    
    def bitmap_to_data(self, bitmap, color):
        """Convertit le bitmap en données pour le masque"""
        # Conversion en format attendu par le masque
        data = bytearray()
        
        # En-tête avec couleur RGB
        r, g, b = color
        data.extend([r, g, b, 0])  # RGB + padding
        
        # Données bitmap (pack bits par octets)
        for row in bitmap:
            for i in range(0, len(row), 8):
                byte_val = 0
                for j in range(8):
                    if i + j < len(row) and row[i + j]:
                        byte_val |= (1 << (7 - j))
                data.append(byte_val)
        
        return bytes(data)
    
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
        print("✅ Connecté")
        return True
    
    async def upload_bitmap(self, bitmap_data):
        """Upload du bitmap via DATS"""
        if not self.client or not self.client.is_connected:
            return False
        
        # Commande DATS pour upload
        dats_cmd = self.create_command("DATS", len(bitmap_data).to_bytes(2, 'big'))
        await self.client.write_gatt_char(COMMAND_CHAR, dats_cmd)
        await asyncio.sleep(0.2)
        
        # Upload des données par chunks
        chunk_size = 20
        for i in range(0, len(bitmap_data), chunk_size):
            chunk = bitmap_data[i:i + chunk_size]
            await self.client.write_gatt_char(UPLOAD_CHAR, chunk)
            await asyncio.sleep(0.1)
        
        # Finalisation avec DATCP
        datcp_cmd = self.create_command("DATCP")
        await self.client.write_gatt_char(COMMAND_CHAR, datcp_cmd)
        await asyncio.sleep(0.5)
        
        return True
    
    async def display_text(self, text, color=(255, 0, 0)):
        """Affiche du texte statique"""
        print(f"📝 Affichage: '{text}'")
        
        bitmap, final_color = self.text_to_bitmap(text, color)
        bitmap_data = self.bitmap_to_data(bitmap, final_color)
        
        success = await self.upload_bitmap(bitmap_data)
        if success:
            print("✅ Texte affiché")
        else:
            print("❌ Erreur d'affichage")
        
        return success
    
    async def scroll_text(self, text, color=(0, 255, 0), speed=0.5):
        """Fait défiler le texte horizontalement"""
        print(f"📜 Défilement: '{text}'")
        
        # Calculer la largeur du texte
        text_width = len(text) * 8
        
        for scroll_pos in range(0, text_width + self.width, 4):
            print(f"📍 Position {scroll_pos}/{text_width + self.width}")
            
            bitmap, final_color = self.text_to_bitmap(text, color, scroll_pos)
            bitmap_data = self.bitmap_to_data(bitmap, final_color)
            
            await self.upload_bitmap(bitmap_data)
            await asyncio.sleep(speed)
            
            if scroll_pos > text_width:
                break
        
        print("✅ Défilement terminé")
    
    async def text_demo(self):
        """Démonstration des capacités texte"""
        print("\n🎭 DÉMONSTRATION TEXTE")
        print("=" * 30)
        
        # Texte statique
        await self.display_text("HELLO", (255, 0, 0))
        await asyncio.sleep(3)
        
        await self.display_text("WORLD", (0, 255, 0))
        await asyncio.sleep(3)
        
        # Texte défilant
        await self.scroll_text("MASQUE LED FONCTIONNE!", (0, 0, 255), 0.3)
        
        # Messages colorés
        messages = [
            ("ROUGE", (255, 0, 0)),
            ("VERT", (0, 255, 0)),
            ("BLEU", (0, 0, 255)),
            ("JAUNE", (255, 255, 0)),
            ("VIOLET", (255, 0, 255))
        ]
        
        for msg, color in messages:
            await self.display_text(msg, color)
            await asyncio.sleep(2)
    
    async def interactive_text(self):
        """Mode interactif pour le texte"""
        print("\n💬 MODE TEXTE INTERACTIF")
        print("Tapez votre texte (ou 'quit' pour sortir)")
        
        while True:
            try:
                text = input("\nTexte> ").strip()
                
                if text.lower() == 'quit':
                    break
                
                if text:
                    # Couleur aléatoire
                    import random
                    color = (
                        random.randint(100, 255),
                        random.randint(100, 255),
                        random.randint(100, 255)
                    )
                    
                    if len(text) > 8:
                        await self.scroll_text(text, color)
                    else:
                        await self.display_text(text, color)
                
            except KeyboardInterrupt:
                break
        
        print("\n👋 Mode texte terminé")
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Main"""
    controller = RealTextController()
    
    if await controller.connect():
        try:
            await controller.text_demo()
            await controller.interactive_text()
        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé")
        finally:
            await controller.disconnect()

if __name__ == "__main__":
    print("📝 CONTRÔLEUR TEXTE MASQUE LED")
    print("Affichage et défilement de texte")
    asyncio.run(main())
