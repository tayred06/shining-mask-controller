"""
Script principal pour contrôler le masque LED
Point d'entrée principal du projet
"""

import asyncio
import sys
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration du protocole
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class MaskMain:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    def create_image_command(self, image_id):
        """Crée une commande pour afficher une image"""
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
        print("🔍 Recherche du masque LED...")
        devices = await BleakScanner.discover()
        
        mask = None
        for device in devices:
            if "MASK" in (device.name or ""):
                mask = device
                break
        
        if not mask:
            print("❌ Aucun masque LED trouvé")
            print("💡 Vérifiez que le masque est allumé et en mode appairage")
            return False
        
        print(f"🔗 Connexion à {mask.name} ({mask.address})...")
        
        try:
            self.client = BleakClient(mask.address)
            await self.client.connect()
            print("✅ Connexion établie avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def send_command(self, command, description=""):
        """Envoie une commande au masque"""
        if not self.client or not self.client.is_connected:
            print("❌ Pas de connexion au masque")
            return False
        
        try:
            await self.client.write_gatt_char(COMMAND_CHAR, command)
            if description:
                print(f"📤 {description}")
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            print(f"❌ Erreur d'envoi: {e}")
            return False
    
    async def set_image(self, image_id):
        """Affiche une image sur le masque"""
        if not 1 <= image_id <= 20:
            print("❌ L'ID d'image doit être entre 1 et 20")
            return False
        
        command = self.create_image_command(image_id)
        return await self.send_command(command, f"Image {image_id} envoyée")
    
    async def set_brightness(self, brightness):
        """Définit la luminosité du masque"""
        if not 0 <= brightness <= 255:
            print("❌ La luminosité doit être entre 0 et 255")
            return False
        
        command = self.create_brightness_command(brightness)
        percentage = int((brightness / 255) * 100)
        return await self.send_command(command, f"Luminosité {brightness}/255 ({percentage}%)")
    
    async def interactive_mode(self):
        """Mode interactif pour contrôler le masque"""
        print("\n🎮 MODE INTERACTIF")
        print("=" * 40)
        print("Commandes disponibles:")
        print("  img <1-20>     - Afficher une image")
        print("  bright <0-255> - Définir la luminosité")
        print("  demo           - Démonstration automatique")
        print("  quit           - Quitter")
        print()
        
        while True:
            try:
                cmd = input("masque> ").strip().lower()
                
                if cmd == "quit" or cmd == "q":
                    break
                elif cmd == "demo":
                    await self.demo_sequence()
                elif cmd.startswith("img "):
                    try:
                        image_id = int(cmd.split()[1])
                        await self.set_image(image_id)
                    except (IndexError, ValueError):
                        print("❌ Usage: img <1-20>")
                elif cmd.startswith("bright "):
                    try:
                        brightness = int(cmd.split()[1])
                        await self.set_brightness(brightness)
                    except (IndexError, ValueError):
                        print("❌ Usage: bright <0-255>")
                elif cmd == "help" or cmd == "h":
                    print("Commandes: img <1-20>, bright <0-255>, demo, quit")
                else:
                    print("❌ Commande inconnue. Tapez 'help' pour l'aide")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\n👋 Mode interactif terminé")
    
    async def demo_sequence(self):
        """Séquence de démonstration"""
        print("\n🎭 DÉMONSTRATION")
        print("Cycle d'images avec différentes luminosités...")
        
        for i in range(1, 6):
            await self.set_image(i)
            await asyncio.sleep(1)
            
            brightness = 50 + (i * 40)
            await self.set_brightness(brightness)
            await asyncio.sleep(2)
        
        print("✨ Démonstration terminée")
    
    async def disconnect(self):
        """Déconnexion du masque"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté du masque")

async def main():
    """Fonction principale"""
    print("🎭 CONTRÔLEUR MASQUE LED")
    print("Projet de contrôle via Bluetooth Low Energy")
    print("=" * 40)
    
    mask = MaskMain()
    
    if not await mask.connect():
        print("\n💡 Conseils de dépannage:")
        print("- Vérifiez que le masque est allumé")
        print("- Assurez-vous qu'il est en mode appairage") 
        print("- Redémarrez le Bluetooth si nécessaire")
        return
    
    try:
        # Test initial
        print("\n🧪 Test de connexion...")
        await mask.set_image(1)
        await mask.set_brightness(128)
        
        # Mode interactif
        await mask.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
    finally:
        await mask.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)
