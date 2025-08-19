"""
Contrôleur de luminosité pour masque LED
Utilise la commande LIGHT découverte dans la documentation officielle
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

class BrightnessController:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    def create_brightness_command(self, brightness):
        """Crée une commande LIGHT cryptée pour contrôler la luminosité"""
        cmd_ascii = "LIGHT"
        args = brightness.to_bytes(1, 'big')
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        # Padding à 16 bytes pour AES
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
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
            print("❌ Masque LED non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask.name} ({mask.address})...")
        self.client = BleakClient(mask.address)
        await self.client.connect()
        print("✅ Connexion établie")
        return True
    
    async def set_brightness(self, brightness):
        """Définit la luminosité du masque (0-255)"""
        if not 0 <= brightness <= 255:
            print("❌ La luminosité doit être entre 0 et 255")
            return False
        
        if not self.client or not self.client.is_connected:
            print("❌ Pas de connexion au masque")
            return False
        
        command = self.create_brightness_command(brightness)
        await self.client.write_gatt_char(COMMAND_CHAR, command)
        
        percentage = int((brightness / 255) * 100)
        print(f"🔆 Luminosité réglée à {brightness}/255 ({percentage}%)")
        
        await asyncio.sleep(0.5)
        return True
    
    async def brightness_demo(self):
        """Démonstration des niveaux de luminosité"""
        print("\n🎭 DÉMONSTRATION DE LUMINOSITÉ")
        print("=" * 40)
        
        # Niveaux prédéfinis
        levels = [0, 64, 128, 192, 255]
        level_names = ["Éteint", "Faible", "Moyen", "Fort", "Maximum"]
        
        for brightness, name in zip(levels, level_names):
            print(f"\n➤ {name} ({brightness}/255)")
            await self.set_brightness(brightness)
            await asyncio.sleep(2)
        
        print("\n🔄 Retour à luminosité normale...")
        await self.set_brightness(128)
    
    async def interactive_brightness(self):
        """Mode interactif pour ajuster la luminosité"""
        print("\n🎛️  MODE INTERACTIF")
        print("=" * 40)
        print("Entrez une valeur de luminosité (0-255) ou 'q' pour quitter")
        
        while True:
            try:
                user_input = input("\nLuminosité (0-255): ").strip()
                
                if user_input.lower() == 'q':
                    break
                
                brightness = int(user_input)
                if 0 <= brightness <= 255:
                    await self.set_brightness(brightness)
                else:
                    print("❌ Valeur hors limite (0-255)")
                    
            except ValueError:
                print("❌ Valeur invalide")
            except KeyboardInterrupt:
                break
        
        print("\n👋 Mode interactif terminé")
    
    async def disconnect(self):
        """Déconnexion du masque"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté du masque")

async def main():
    """Fonction principale"""
    controller = BrightnessController()
    
    if not await controller.connect():
        return
    
    try:
        # Démonstration automatique
        await controller.brightness_demo()
        
        # Mode interactif
        await controller.interactive_brightness()
        
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé")
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    print("🔆 CONTRÔLEUR DE LUMINOSITÉ")
    print("Contrôle la luminosité du masque LED via BLE")
    asyncio.run(main())
