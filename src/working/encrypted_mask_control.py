"""
Contrôleur de masque LED avec protocole AES crypté
Version simplifiée pour tests rapides
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration découverte
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class EncryptedMaskController:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    def create_image_command(self, image_id):
        """Crée une commande cryptée pour afficher une image"""
        base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b'
        
        if len(base_command) < 16:
            base_command += b'\x00' * (16 - len(base_command))
        
        return self.cipher.encrypt(base_command)
    
    def create_brightness_command(self, brightness):
        """Crée une commande LIGHT pour la luminosité"""
        cmd_ascii = "LIGHT"
        args = brightness.to_bytes(1, 'big')
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
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
    
    async def send_command(self, command):
        """Envoie une commande cryptée"""
        if not self.client or not self.client.is_connected:
            print("❌ Pas de connexion")
            return
        
        await self.client.write_gatt_char(COMMAND_CHAR, command)
        await asyncio.sleep(0.5)
    
    async def set_image(self, image_id):
        """Affiche une image"""
        if not 1 <= image_id <= 20:
            print("❌ Image doit être entre 1 et 20")
            return
        
        command = self.create_image_command(image_id)
        await self.send_command(command)
        print(f"📸 Image {image_id} envoyée")
    
    async def set_brightness(self, brightness):
        """Définit la luminosité"""
        if not 0 <= brightness <= 255:
            print("❌ Luminosité doit être entre 0 et 255")
            return
        
        command = self.create_brightness_command(brightness)
        await self.send_command(command)
        print(f"🔆 Luminosité {brightness} envoyée")
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test rapide"""
    controller = EncryptedMaskController()
    
    if await controller.connect():
        # Test image
        await controller.set_image(5)
        await asyncio.sleep(2)
        
        # Test luminosité
        await controller.set_brightness(100)
        await asyncio.sleep(2)
        
        await controller.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
