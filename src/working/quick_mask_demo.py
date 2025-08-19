"""
Démonstration rapide des fonctionnalités du masque LED
Test des images et de la luminosité
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import random

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

class QuickMaskDemo:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    def create_image_command(self, image_id):
        """Commande pour afficher une image"""
        base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b'
        if len(base_command) < 16:
            base_command += b'\x00' * (16 - len(base_command))
        return self.cipher.encrypt(base_command)
    
    def create_brightness_command(self, brightness):
        """Commande pour définir la luminosité"""
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
        """Envoie une commande"""
        if self.client and self.client.is_connected:
            await self.client.write_gatt_char(COMMAND_CHAR, command)
            await asyncio.sleep(0.8)
    
    async def quick_demo(self):
        """Démonstration rapide"""
        print("\n🎭 DÉMONSTRATION RAPIDE")
        print("=" * 30)
        
        # Test quelques images
        images = [1, 5, 10, 15, 20]
        for img in images:
            print(f"📸 Image {img}")
            command = self.create_image_command(img)
            await self.send_command(command)
        
        # Test luminosité
        print("\n🔆 Test luminosité...")
        for brightness in [50, 150, 255, 100]:
            print(f"💡 Luminosité {brightness}")
            command = self.create_brightness_command(brightness)
            await self.send_command(command)
        
        print("✨ Démonstration terminée")
    
    async def random_show(self, duration=30):
        """Spectacle aléatoire"""
        print(f"\n🎲 SPECTACLE ALÉATOIRE ({duration}s)")
        print("=" * 30)
        
        end_time = asyncio.get_event_loop().time() + duration
        
        while asyncio.get_event_loop().time() < end_time:
            # Image aléatoire
            img = random.randint(1, 20)
            brightness = random.randint(100, 255)
            
            print(f"🎯 Image {img}, Luminosité {brightness}")
            
            await self.send_command(self.create_image_command(img))
            await asyncio.sleep(0.2)
            await self.send_command(self.create_brightness_command(brightness))
            await asyncio.sleep(random.uniform(1, 3))
        
        print("🎊 Spectacle terminé")
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Main"""
    demo = QuickMaskDemo()
    
    if await demo.connect():
        await demo.quick_demo()
        await demo.random_show(20)
        await demo.disconnect()

if __name__ == "__main__":
    print("🚀 DÉMONSTRATION MASQUE LED")
    asyncio.run(main())
