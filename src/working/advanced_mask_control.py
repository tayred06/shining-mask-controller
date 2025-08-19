"""
Contrôleur Masque LED - Version Complète avec Luminosité
Basé sur le protocole AES découvert + commande LIGHT de la doc officielle
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class MaskController:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.current_brightness = 50
        self.current_image = 1
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée selon le protocole officiel"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        # Padding à 16 bytes pour AES
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def create_image_command(self, image_id):
        """Crée une commande cryptée pour afficher une image (méthode originale)"""
        # Format découvert: b'\x06PLAY\x01' + image_id + suffixe_fixe
        base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b'
        
        # Padding pour AES
        if len(base_command) < 16:
            base_command += b'\x00' * (16 - len(base_command))
        
        return self.cipher.encrypt(base_command)
    
    def _notification_handler(self, sender, data):
        """Gestionnaire des notifications"""
        try:
            decrypted = self.cipher.decrypt(data)
            ascii_part = decrypted.rstrip(b'\x00').decode('ascii', errors='ignore')
            if ascii_part:
                print(f"📢 Masque: {ascii_part}")
        except:
            pass
    
    async def connect(self):
        """Connexion au masque"""
        print("🔍 Recherche du masque...")
        devices = await BleakScanner.discover()
        
        for device in devices:
            if device.name and "MASK" in device.name:
                print(f"✅ Connexion à {device.name}...")
                self.client = BleakClient(device.address)
                await self.client.connect()
                await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
                return True
        
        print("❌ Masque non trouvé")
        return False
    
    async def send_command(self, cmd, args=b''):
        """Envoie une commande au masque"""
        if not self.client or not self.client.is_connected:
            return False
        
        try:
            command = self.create_command(cmd, args)
            await self.client.write_gatt_char(COMMAND_CHAR, command)
            await asyncio.sleep(0.2)
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    async def set_brightness(self, level):
        """Définit la luminosité (0-255, recommandé max 100)"""
        if not (0 <= level <= 255):
            print("❌ Luminosité doit être entre 0 et 255")
            return False
        
        success = await self.send_command("LIGHT", bytes([level]))
        if success:
            self.current_brightness = level
            print(f"🔆 Luminosité: {level}/255")
        
        return success
    
    async def show_image(self, image_id, use_new_protocol=True):
        """Affiche une image (1-20)"""
        if not (1 <= image_id <= 20):
            print("❌ Image ID doit être entre 1 et 20")
            return False
        
        try:
            if use_new_protocol:
                # Nouvelle méthode avec commande DATA
                success = await self.send_command("DATA", bytes([image_id]))
            else:
                # Ancienne méthode cryptée découverte initialement
                command = self.create_image_command(image_id)
                await self.client.write_gatt_char(COMMAND_CHAR, command)
                success = True
            
            if success:
                self.current_image = image_id
                print(f"🎨 Image {image_id} affichée")
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur affichage image {image_id}: {e}")
            return False
    
    async def set_image_color(self, r, g, b):
        """Définit la couleur de l'image (RGB 0-255)"""
        success = await self.send_command("FC", bytes([1, r, g, b]))
        if success:
            print(f"🎨 Couleur: RGB({r}, {g}, {b})")
        return success
    
    async def show_image_with_settings(self, image_id, brightness=None, color=None):
        """Affiche une image avec luminosité et couleur personnalisées"""
        print(f"\n🎭 Configuration image {image_id}")
        
        # Luminosité
        if brightness is not None:
            await self.set_brightness(brightness)
        
        # Couleur
        if color is not None:
            r, g, b = color
            await self.set_image_color(r, g, b)
        
        # Image
        await self.show_image(image_id)
    
    async def brightness_demo(self):
        """Démonstration des niveaux de luminosité"""
        print("\n🌟 DÉMONSTRATION LUMINOSITÉ")
        print("=" * 50)
        
        levels = [10, 30, 50, 75, 100]
        test_image = 1
        
        for brightness in levels:
            print(f"\n🔆 Test luminosité {brightness}")
            await self.show_image_with_settings(test_image, brightness=brightness)
            await asyncio.sleep(2)
        
        print("✅ Démonstration terminée")
    
    async def color_brightness_demo(self):
        """Démonstration couleurs + luminosité"""
        print("\n🎨 DÉMONSTRATION COULEURS + LUMINOSITÉ")
        print("=" * 50)
        
        colors = [
            (255, 0, 0, "Rouge"),
            (0, 255, 0, "Vert"),
            (0, 0, 255, "Bleu"),
            (255, 255, 0, "Jaune"),
            (255, 0, 255, "Magenta"),
            (0, 255, 255, "Cyan"),
            (255, 255, 255, "Blanc")
        ]
        
        brightnesses = [25, 50, 75]
        test_image = 2
        
        for brightness in brightnesses:
            print(f"\n💡 Luminosité {brightness}:")
            
            for r, g, b, name in colors:
                print(f"  🎨 {name}")
                await self.show_image_with_settings(test_image, brightness, (r, g, b))
                await asyncio.sleep(1.5)
        
        print("✅ Démonstration couleurs terminée")
    
    async def interactive_mode(self):
        """Mode interactif complet"""
        print("\n🎮 MODE INTERACTIF")
        print("=" * 50)
        print("Commandes disponibles:")
        print("  img <1-20>     : Afficher image")
        print("  bright <0-255> : Définir luminosité")
        print("  color <r> <g> <b> : Définir couleur RGB")
        print("  demo           : Démonstration luminosité")
        print("  colors         : Démonstration couleurs")
        print("  status         : État actuel")
        print("  quit           : Quitter")
        
        while True:
            try:
                cmd = input(f"\n🎭 [{self.current_image}|{self.current_brightness}] > ").strip().lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'status':
                    print(f"📊 Image: {self.current_image}, Luminosité: {self.current_brightness}")
                elif cmd == 'demo':
                    await self.brightness_demo()
                elif cmd == 'colors':
                    await self.color_brightness_demo()
                elif cmd.startswith('img '):
                    try:
                        img_id = int(cmd.split()[1])
                        await self.show_image(img_id)
                    except (ValueError, IndexError):
                        print("❌ Usage: img <1-20>")
                elif cmd.startswith('bright '):
                    try:
                        level = int(cmd.split()[1])
                        await self.set_brightness(level)
                    except (ValueError, IndexError):
                        print("❌ Usage: bright <0-255>")
                elif cmd.startswith('color '):
                    try:
                        parts = cmd.split()
                        r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
                        await self.set_image_color(r, g, b)
                    except (ValueError, IndexError):
                        print("❌ Usage: color <r> <g> <b>")
                else:
                    print("❌ Commande inconnue")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")

async def main():
    controller = MaskController()
    
    print("🎭 CONTRÔLEUR MASQUE LED COMPLET")
    print("🔆 Nouvelle fonctionnalité: Contrôle de luminosité !")
    print("=" * 60)
    
    if not await controller.connect():
        return
    
    try:
        # Test de base
        print("\n🧪 Test initial...")
        await controller.set_brightness(50)
        await controller.show_image(1)
        
        choice = input("\n❓ Voyez-vous l'image ? (o/n): ").strip().lower()
        
        if choice.startswith('o'):
            print("🎉 Parfait ! Contrôle avec luminosité opérationnel !")
            
            mode = input("""
🎮 Mode souhaité ?
1. Démonstration luminosité
2. Démonstration couleurs + luminosité  
3. Mode interactif complet
Choix (1/2/3): """).strip()
            
            if mode == "1":
                await controller.brightness_demo()
            elif mode == "2":
                await controller.color_brightness_demo()
            elif mode == "3":
                await controller.interactive_mode()
        else:
            print("❌ Problème d'affichage")
    
    except KeyboardInterrupt:
        print("\n⏹️ Arrêté")
    
    finally:
        if controller.client and controller.client.is_connected:
            await controller.client.disconnect()
            print("🔌 Déconnecté")

if __name__ == "__main__":
    asyncio.run(main())
