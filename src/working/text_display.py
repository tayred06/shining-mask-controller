"""
Afficheur de texte pour masque LED
Version simple et efficace pour afficher du texte statique et défilant
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"

class TextDisplay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.width = 64
        self.height = 32
        
        # Patterns de caractères 8x8 pixels
        self.char_patterns = {
            'A': [
                "  ████  ",
                " █    █ ",
                "█      █",
                "████████",
                "█      █",
                "█      █",
                "█      █",
                "        "
            ],
            'B': [
                "███████ ",
                "█      █",
                "█      █",
                "███████ ",
                "█      █",
                "█      █",
                "███████ ",
                "        "
            ],
            'C': [
                " ██████ ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                " ██████ ",
                "        "
            ],
            'D': [
                "██████  ",
                "█     █ ",
                "█      █",
                "█      █",
                "█      █",
                "█     █ ",
                "██████  ",
                "        "
            ],
            'E': [
                "████████",
                "█       ",
                "█       ",
                "██████  ",
                "█       ",
                "█       ",
                "████████",
                "        "
            ],
            'F': [
                "████████",
                "█       ",
                "█       ",
                "██████  ",
                "█       ",
                "█       ",
                "█       ",
                "        "
            ],
            'G': [
                " ██████ ",
                "█       ",
                "█       ",
                "█   ████",
                "█      █",
                "█      █",
                " ██████ ",
                "        "
            ],
            'H': [
                "█      █",
                "█      █",
                "█      █",
                "████████",
                "█      █",
                "█      █",
                "█      █",
                "        "
            ],
            'I': [
                "████████",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "████████",
                "        "
            ],
            'J': [
                "████████",
                "      █ ",
                "      █ ",
                "      █ ",
                "      █ ",
                "█     █ ",
                " ██████ ",
                "        "
            ],
            'K': [
                "█     █ ",
                "█    █  ",
                "█   █   ",
                "█ █     ",
                "█   █   ",
                "█    █  ",
                "█     █ ",
                "        "
            ],
            'L': [
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "█       ",
                "████████",
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
                "        "
            ],
            'O': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "        "
            ],
            'P': [
                "███████ ",
                "█      █",
                "█      █",
                "███████ ",
                "█       ",
                "█       ",
                "█       ",
                "        "
            ],
            'Q': [
                " ██████ ",
                "█      █",
                "█      █",
                "█      █",
                "█   █  █",
                "█    █ █",
                " ██████ ",
                "       █"
            ],
            'R': [
                "███████ ",
                "█      █",
                "█      █",
                "███████ ",
                "█   █   ",
                "█    █  ",
                "█     █ ",
                "        "
            ],
            'S': [
                " ██████ ",
                "█       ",
                "█       ",
                " ██████ ",
                "       █",
                "       █",
                " ██████ ",
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
                "        "
            ],
            'U': [
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " ██████ ",
                "        "
            ],
            'V': [
                "█      █",
                "█      █",
                "█      █",
                "█      █",
                " █    █ ",
                "  █  █  ",
                "   ██   ",
                "        "
            ],
            'W': [
                "█      █",
                "█      █",
                "█      █",
                "█  ██  █",
                "█ █  █ █",
                "██    ██",
                "█      █",
                "        "
            ],
            'X': [
                "█      █",
                " █    █ ",
                "  █  █  ",
                "   ██   ",
                "  █  █  ",
                " █    █ ",
                "█      █",
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
                "        "
            ],
            'Z': [
                "████████",
                "      █ ",
                "     █  ",
                "   ██   ",
                "  █     ",
                " █      ",
                "████████",
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
                "        "
            ],
            '!': [
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "   ██   ",
                "        ",
                "   ██   ",
                "        "
            ],
            '?': [
                " ██████ ",
                "█      █",
                "      █ ",
                "    ██  ",
                "   █    ",
                "        ",
                "   █    ",
                "        "
            ],
            '0': [
                " ██████ ",
                "█     █ ",
                "█    █ █",
                "█   █  █",
                "█ █    █",
                " █     █",
                " ██████ ",
                "        "
            ],
            '1': [
                "   █    ",
                "  ██    ",
                "   █    ",
                "   █    ",
                "   █    ",
                "   █    ",
                " ██████ ",
                "        "
            ],
            '2': [
                " ██████ ",
                "█      █",
                "       █",
                " ██████ ",
                "█       ",
                "█       ",
                "████████",
                "        "
            ],
            '3': [
                " ██████ ",
                "       █",
                "       █",
                " ██████ ",
                "       █",
                "       █",
                " ██████ ",
                "        "
            ],
            '4': [
                "█     █ ",
                "█     █ ",
                "█     █ ",
                "████████",
                "      █ ",
                "      █ ",
                "      █ ",
                "        "
            ],
            '5': [
                "████████",
                "█       ",
                "█       ",
                "███████ ",
                "       █",
                "       █",
                "███████ ",
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
    
    def text_to_bitmap(self, text, start_pos=0):
        """Convertit le texte en bitmap 64x32"""
        # Créer un bitmap vide
        bitmap = []
        for y in range(32):
            bitmap.append(['0'] * 64)
        
        # Position de départ pour centrer verticalement
        start_y = 12  # Centre vertical (32-8)/2 = 12
        
        # Dessiner chaque caractère
        x_pos = start_pos
        for char in text.upper():
            if char in self.char_patterns and x_pos < 64:
                pattern = self.char_patterns[char]
                
                # Dessiner le caractère
                for y, row in enumerate(pattern):
                    if start_y + y < 32:
                        for x, pixel in enumerate(row):
                            if x_pos + x < 64 and pixel == '█':
                                bitmap[start_y + y][x_pos + x] = '1'
                
                x_pos += 8  # Largeur d'un caractère
        
        return bitmap
    
    def bitmap_to_data(self, bitmap, color=(255, 255, 255)):
        """Convertit le bitmap en données pour upload"""
        data = bytearray()
        
        # En-tête couleur RGB
        r, g, b = color
        data.extend([r, g, b, 0])  # RGB + padding
        
        # Conversion bitmap en bytes
        for row in bitmap:
            for i in range(0, len(row), 8):
                byte_val = 0
                for j in range(8):
                    if i + j < len(row) and row[i + j] == '1':
                        byte_val |= (1 << (7 - j))
                data.append(byte_val)
        
        return bytes(data)
    
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
            print("❌ Masque LED non trouvé")
            print("💡 Vérifiez que le masque est allumé et en mode appairage")
            return False
        
        print(f"🔗 Connexion à {mask.name}...")
        self.client = BleakClient(mask.address)
        await self.client.connect()
        print("✅ Connecté au masque")
        return True
    
    async def upload_bitmap(self, bitmap_data):
        """Upload du bitmap vers le masque"""
        if not self.client or not self.client.is_connected:
            print("❌ Pas de connexion au masque")
            return False
        
        try:
            # Commande DATS pour démarrer l'upload
            dats_cmd = self.create_command("DATS", len(bitmap_data).to_bytes(2, 'big'))
            await self.client.write_gatt_char(COMMAND_CHAR, dats_cmd)
            await asyncio.sleep(0.2)
            
            # Upload des données par chunks de 20 bytes
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
            
        except Exception as e:
            print(f"❌ Erreur upload: {e}")
            return False
    
    async def display_text(self, text, color=(255, 255, 255)):
        """Affiche du texte statique sur le masque"""
        print(f"📝 Affichage: '{text}'")
        
        # Générer le bitmap
        bitmap = self.text_to_bitmap(text)
        bitmap_data = self.bitmap_to_data(bitmap, color)
        
        # Upload vers le masque
        success = await self.upload_bitmap(bitmap_data)
        
        if success:
            print(f"✅ Texte '{text}' affiché avec succès")
        else:
            print(f"❌ Erreur lors de l'affichage de '{text}'")
        
        return success
    
    async def scroll_text(self, text, color=(255, 255, 255), speed=0.3):
        """Fait défiler le texte horizontalement"""
        print(f"📜 Défilement: '{text}'")
        
        text_width = len(text) * 8
        total_steps = text_width + 64  # Largeur texte + largeur écran
        
        for step in range(total_steps):
            scroll_pos = -step * 2  # Vitesse de défilement
            
            bitmap = self.text_to_bitmap(text, scroll_pos)
            bitmap_data = self.bitmap_to_data(bitmap, color)
            
            success = await self.upload_bitmap(bitmap_data)
            if not success:
                print("❌ Erreur pendant le défilement")
                break
            
            await asyncio.sleep(speed)
            
            # Afficher progression
            if step % 10 == 0:
                progress = int((step / total_steps) * 100)
                print(f"📍 Défilement: {progress}%")
        
        print("✅ Défilement terminé")
    
    async def text_demo(self):
        """Démonstration des capacités texte"""
        print("\n🎭 DÉMONSTRATION TEXTE")
        print("=" * 30)
        
        # Messages avec différentes couleurs
        messages = [
            ("HELLO", (255, 0, 0)),      # Rouge
            ("WORLD", (0, 255, 0)),      # Vert
            ("LED", (0, 0, 255)),        # Bleu
            ("MASK", (255, 255, 0)),     # Jaune
            ("OK", (255, 0, 255)),       # Magenta
        ]
        
        # Affichage statique
        for msg, color in messages:
            await self.display_text(msg, color)
            await asyncio.sleep(2)
        
        # Défilement
        await self.scroll_text("MASQUE LED FONCTIONNE PARFAITEMENT", (0, 255, 255), 0.2)
    
    async def interactive_mode(self):
        """Mode interactif pour saisir du texte"""
        print("\n💬 MODE INTERACTIF")
        print("=" * 25)
        print("Commandes:")
        print("  text <message>  - Afficher un message")
        print("  scroll <message> - Faire défiler un message")
        print("  demo            - Démonstration")
        print("  quit            - Quitter")
        print()
        
        while True:
            try:
                cmd = input("texte> ").strip()
                
                if cmd.lower() == 'quit' or cmd.lower() == 'q':
                    break
                elif cmd.lower() == 'demo':
                    await self.text_demo()
                elif cmd.startswith('text '):
                    message = cmd[5:].upper()
                    if message:
                        await self.display_text(message, (255, 255, 255))
                elif cmd.startswith('scroll '):
                    message = cmd[7:].upper()
                    if message:
                        await self.scroll_text(message, (0, 255, 0), 0.2)
                elif cmd == 'help' or cmd == 'h':
                    print("Commandes: text <msg>, scroll <msg>, demo, quit")
                else:
                    print("❌ Commande inconnue. Tapez 'help' pour l'aide")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\n👋 Mode interactif terminé")
    
    async def disconnect(self):
        """Déconnexion du masque"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("🔌 Déconnecté du masque")

async def main():
    """Fonction principale"""
    print("📝 AFFICHEUR DE TEXTE MASQUE LED")
    print("Affichage et défilement de texte personnalisé")
    print("=" * 40)
    
    display = TextDisplay()
    
    if not await display.connect():
        print("\n💡 Conseils:")
        print("- Vérifiez que le masque est allumé")
        print("- Assurez-vous qu'il est en mode appairage")
        print("- Rapprochez-vous du masque")
        return
    
    try:
        # Démonstration initiale
        print("\n🧪 Test initial...")
        await display.display_text("HELLO", (255, 0, 0))
        await asyncio.sleep(2)
        
        # Mode interactif
        await display.interactive_mode()
        
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
