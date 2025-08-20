"""
Afficheur de texte SIMPLE et SÉCURISÉ pour masque LED
Version qui utilise des méthodes fiables sans risquer de bloquer le masque
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import time

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

class SafeTextDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        
        # Mapping des lettres vers des images du masque (1-20)
        # Utilisation des images prédéfinies pour simuler du texte
        self.letter_to_image = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
            'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
            'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
            'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20
        }
        
        # Messages prédéfinis avec séquences d'images
        self.predefined_messages = {
            'HELLO': [8, 5, 12, 12, 15],  # H-E-L-L-O
            'HI': [8, 9],                 # H-I
            'OK': [15, 11],               # O-K  
            'YES': [25, 5, 19],           # Y-E-S (25 = image spéciale)
            'NO': [14, 15],               # N-O
            'ON': [15, 14],               # O-N
            'OFF': [15, 6, 6],            # O-F-F
            'GO': [7, 15],                # G-O
            'STOP': [19, 20, 15, 16],     # S-T-O-P
        }
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def create_image_command(self, image_id):
        """Crée une commande pour afficher une image (méthode fiable)"""
        base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b'
        if len(base_command) < 16:
            base_command += b'\x00' * (16 - len(base_command))
        return self.cipher.encrypt(base_command)
    
    def create_brightness_command(self, brightness):
        """Commande pour la luminosité"""
        cmd_ascii = "LIGHT"
        args = brightness.to_bytes(1, 'big')
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        return self.cipher.encrypt(command)
    
    def create_color_command(self, r, g, b):
        """Commande pour changer la couleur"""
        command = b'\x05FC\x00' + r.to_bytes(1, 'big') + g.to_bytes(1, 'big') + b.to_bytes(1, 'big')
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        return self.cipher.encrypt(command)
    
    async def connect(self):
        """Connexion sécurisée au masque"""
        print("🔍 Recherche du masque LED...")
        devices = await BleakScanner.discover()
        
        mask = None
        for device in devices:
            if "MASK" in (device.name or ""):
                mask = device
                break
        
        if not mask:
            print("❌ Masque LED non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask.name}...")
        try:
            self.client = BleakClient(mask.address)
            await self.client.connect()
            
            # Test de connexion avec une commande sûre
            test_cmd = self.create_brightness_command(100)
            await self.client.write_gatt_char(COMMAND_CHAR, test_cmd)
            await asyncio.sleep(0.5)
            
            print("✅ Connecté et testé avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def send_safe_command(self, command, description=""):
        """Envoie une commande de manière sécurisée"""
        if not self.client or not self.client.is_connected:
            print("❌ Pas de connexion")
            return False
        
        try:
            await self.client.write_gatt_char(COMMAND_CHAR, command)
            if description:
                print(f"📤 {description}")
            await asyncio.sleep(0.8)  # Délai plus long pour la sécurité
            return True
        except Exception as e:
            print(f"❌ Erreur envoi: {e}")
            return False
    
    async def display_image(self, image_id):
        """Affiche une image prédéfinie (méthode 100% fiable)"""
        if not 1 <= image_id <= 20:
            print(f"❌ Image {image_id} invalide (1-20)")
            return False
        
        command = self.create_image_command(image_id)
        return await self.send_safe_command(command, f"Image {image_id}")
    
    async def set_color(self, r, g, b):
        """Change la couleur du masque"""
        command = self.create_color_command(r, g, b)
        return await self.send_safe_command(command, f"Couleur RGB({r},{g},{b})")
    
    async def set_brightness(self, brightness):
        """Change la luminosité"""
        if not 0 <= brightness <= 255:
            print("❌ Luminosité doit être 0-255")
            return False
        
        command = self.create_brightness_command(brightness)
        return await self.send_safe_command(command, f"Luminosité {brightness}")
    
    async def display_text_safe(self, text):
        """Affiche du texte en utilisant des images prédéfinies"""
        text = text.upper().strip()
        
        if text in self.predefined_messages:
            print(f"📝 Affichage message prédéfini: '{text}'")
            images = self.predefined_messages[text]
            
            for i, img_id in enumerate(images):
                if 1 <= img_id <= 20:  # Sécurité
                    await self.display_image(img_id)
                    await asyncio.sleep(1.5)
            
            print(f"✅ Message '{text}' affiché")
            return True
        
        # Affichage lettre par lettre pour texte custom
        print(f"📝 Affichage lettre par lettre: '{text}'")
        displayed_any = False
        
        for char in text:
            if char in self.letter_to_image:
                img_id = self.letter_to_image[char]
                if await self.display_image(img_id):
                    displayed_any = True
                await asyncio.sleep(1.2)
            elif char == ' ':
                # Pause pour l'espace
                await asyncio.sleep(0.8)
            else:
                print(f"⚠️ Caractère '{char}' non supporté")
        
        if displayed_any:
            print(f"✅ Texte '{text}' affiché (partiel)")
        else:
            print(f"❌ Aucun caractère de '{text}' n'a pu être affiché")
        
        return displayed_any
    
    async def text_animation(self, text, color=(255, 255, 255)):
        """Animation de texte avec couleurs"""
        print(f"🎭 Animation: '{text}' en RGB{color}")
        
        # Définir la couleur
        r, g, b = color
        await self.set_color(r, g, b)
        await asyncio.sleep(0.5)
        
        # Afficher le texte
        await self.display_text_safe(text)
    
    async def rainbow_text(self, text):
        """Affiche le texte avec des couleurs arc-en-ciel"""
        colors = [
            (255, 0, 0),    # Rouge
            (255, 127, 0),  # Orange  
            (255, 255, 0),  # Jaune
            (0, 255, 0),    # Vert
            (0, 0, 255),    # Bleu
            (75, 0, 130),   # Indigo
            (148, 0, 211)   # Violet
        ]
        
        print(f"🌈 Texte arc-en-ciel: '{text}'")
        
        for i, color in enumerate(colors):
            print(f"🎨 Couleur {i+1}/7: RGB{color}")
            await self.text_animation(text, color)
            await asyncio.sleep(1)
    
    async def demo_safe(self):
        """Démonstration sécurisée"""
        print("\n🎭 DÉMONSTRATION SÉCURISÉE")
        print("=" * 35)
        
        # Messages prédéfinis
        print("\n📋 Messages prédéfinis:")
        for msg in ['HELLO', 'HI', 'OK', 'GO']:
            await self.display_text_safe(msg)
            await asyncio.sleep(2)
        
        # Test couleurs
        print("\n🎨 Test des couleurs:")
        colors = [
            ((255, 0, 0), "Rouge"),
            ((0, 255, 0), "Vert"), 
            ((0, 0, 255), "Bleu"),
            ((255, 255, 0), "Jaune")
        ]
        
        for color, name in colors:
            print(f"🎨 {name}")
            await self.set_color(*color)
            await self.display_image(1)  # Image 1 comme test
            await asyncio.sleep(2)
        
        # Test luminosité
        print("\n💡 Test luminosité:")
        for brightness in [50, 150, 255, 100]:
            await self.set_brightness(brightness)
            await self.display_image(5)
            await asyncio.sleep(1.5)
    
    async def interactive_safe(self):
        """Mode interactif sécurisé"""
        print("\n🎮 MODE INTERACTIF SÉCURISÉ")
        print("=" * 30)
        print("Commandes disponibles:")
        print("  msg <text>     - Afficher un message")
        print("  img <1-20>     - Afficher une image")
        print("  color <r g b>  - Changer couleur RGB")
        print("  bright <0-255> - Changer luminosité")
        print("  rainbow <text> - Texte arc-en-ciel")
        print("  demo           - Démonstration")
        print("  quit           - Quitter")
        print()
        
        while True:
            try:
                cmd = input("masque> ").strip()
                
                if cmd.lower() in ['quit', 'q', 'exit']:
                    break
                elif cmd.lower() == 'demo':
                    await self.demo_safe()
                elif cmd.startswith('msg '):
                    text = cmd[4:].strip()
                    if text:
                        await self.display_text_safe(text)
                elif cmd.startswith('img '):
                    try:
                        img_id = int(cmd[4:].strip())
                        await self.display_image(img_id)
                    except ValueError:
                        print("❌ Format: img <1-20>")
                elif cmd.startswith('color '):
                    try:
                        parts = cmd[6:].split()
                        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                        await self.set_color(r, g, b)
                    except (ValueError, IndexError):
                        print("❌ Format: color <r g b> (0-255)")
                elif cmd.startswith('bright '):
                    try:
                        brightness = int(cmd[7:].strip())
                        await self.set_brightness(brightness)
                    except ValueError:
                        print("❌ Format: bright <0-255>")
                elif cmd.startswith('rainbow '):
                    text = cmd[8:].strip()
                    if text:
                        await self.rainbow_text(text)
                elif cmd in ['help', 'h']:
                    print("msg <text>, img <1-20>, color <r g b>, bright <0-255>, rainbow <text>, demo, quit")
                else:
                    print("❌ Commande inconnue. Tapez 'help'")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\n👋 Mode interactif terminé")
    
    async def disconnect(self):
        """Déconnexion sécurisée"""
        if self.client and self.client.is_connected:
            # Remettre en état stable avant déconnexion
            await self.set_brightness(100)
            await self.display_image(1)
            await self.client.disconnect()
            print("🔌 Déconnecté en sécurité")

async def main():
    """Fonction principale sécurisée"""
    print("📝 AFFICHEUR DE TEXTE SÉCURISÉ")
    print("Version qui ne risque PAS de bloquer le masque")
    print("=" * 45)
    
    display = SafeTextDisplay()
    
    if not await display.connect():
        print("\n💡 Conseils:")
        print("- Vérifiez que le masque est allumé")
        print("- Rapprochez-vous du masque")
        print("- Essayez emergency_reset.py si bloqué")
        return
    
    try:
        # Test initial
        print("\n🧪 Test de base...")
        await display.display_text_safe("HI")
        await asyncio.sleep(2)
        
        # Mode interactif
        await display.interactive_safe()
        
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        await display.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
