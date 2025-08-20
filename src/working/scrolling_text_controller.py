#!/usr/bin/env python3
"""
Contrôleur de masque LED avec texte défilant
Version basée sur final_mask_controller.py avec ajout du défilement
"""

import asyncio
import time
from bleak import BleakClient, BleakScanner
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PIL import Image, ImageDraw, ImageFont
import struct

# Configuration BLE
DEVICE_NAME = "MASK"
ENCRYPTION_KEY = bytes.fromhex("32672f7974ad43451d9c6c894a0e8764")

# UUIDs des caractéristiques
COMMAND_UUID = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_UUID = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_UUID = "d44bc439-abfd-45a2-b575-925416129601"

# Modes de défilement selon mask-go
SCROLL_MODES = {
    'steady': 1,      # Texte fixe
    'blink': 2,       # Texte qui clignote
    'scroll_left': 3, # Défilement vers la gauche
    'scroll_right': 4 # Défilement vers la droite
}

class ScrollingMaskController:
    """
    Contrôleur de masque LED avec support du texte défilant
    """
    
    def __init__(self):
        self.client = None
        self.upload_running = False
        self.current_upload = {}
        self.notification_response = None
        
    def encrypt_aes128(self, data):
        """Chiffrement AES-128 ECB"""
        if len(data) != 16:
            raise ValueError("Data must be exactly 16 bytes")
            
        cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def pad_byte_array(self, array, length):
        """Remplit le tableau avec des zéros jusqu'à la longueur spécifiée"""
        padded = bytearray(length)
        padded[:len(array)] = array
        return bytes(padded)

    async def send_command(self, data):
        """Envoie une commande chiffrée via la caractéristique de commande"""
        if not self.client:
            raise RuntimeError("Non connecté au masque")
            
        padded_data = self.pad_byte_array(data, 16)
        encrypted_data = self.encrypt_aes128(padded_data)
        
        await self.client.write_gatt_char(COMMAND_UUID, encrypted_data)
        await asyncio.sleep(0.1)

    async def send_upload_data(self, data):
        """Envoie des données via la caractéristique d'upload"""
        if not self.client:
            raise RuntimeError("Non connecté au masque")
            
        await self.client.write_gatt_char(UPLOAD_UUID, data, response=False)
        await asyncio.sleep(0.2)

    def notification_handler(self, sender, data):
        """Gestionnaire des notifications"""
        try:
            cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.ECB(), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(data) + decryptor.finalize()
            
            str_len = decrypted[0]
            if str_len > 0 and str_len < len(decrypted):
                response = decrypted[1:str_len+1].decode('ascii', errors='ignore')
                self.notification_response = response
        except Exception as e:
            print(f"Erreur de déchiffrement: {e}")

    async def connect(self):
        """Connexion au masque"""
        print("Recherche du masque...")
        
        devices = await BleakScanner.discover()
        
        mask_device = None
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                mask_device = device
                break
                
        if not mask_device:
            raise RuntimeError("Masque non trouvé")
            
        print(f"Connexion à {mask_device.name}")
        
        self.client = BleakClient(mask_device.address)
        await self.client.connect()
        
        await self.client.start_notify(NOTIFY_UUID, self.notification_handler)
        
        print("Connecté avec succès!")
        return True

    async def disconnect(self):
        """Déconnexion du masque"""
        if self.client:
            await self.client.disconnect()
            self.client = None

    def get_text_image(self, text, width_multiplier=1.5):
        """
        Génère une image bitmap à partir du texte
        width_multiplier permet de créer plus d'espace pour le défilement
        """
        try:
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "arial.ttf"  # Windows
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, 14)
                    break
                except:
                    continue
                    
            if font is None:
                font = ImageFont.load_default()
                
        except:
            font = ImageFont.load_default()

        # Calcul de la largeur du texte
        dummy_img = Image.new('L', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Pour le défilement, on crée une image plus large
        total_width = int(text_width * width_multiplier)
        
        # Création de l'image 16 pixels de hauteur
        img = Image.new('L', (total_width, 16), 0)
        draw = ImageDraw.Draw(img)
        
        # Dessin du texte centré verticalement et horizontalement
        y_offset = (16 - (bbox[3] - bbox[1])) // 2
        x_offset = (total_width - text_width) // 2
        draw.text((x_offset, y_offset), text, fill=255, font=font)
        
        # Conversion en bitmap binaire par colonnes
        pixels = []
        for x in range(total_width):
            column = []
            for y in range(16):
                pixel_value = img.getpixel((x, y))
                binary_val = 1 if pixel_value > 128 else 0
                column.append(binary_val)
            pixels.append(column)
            
        return pixels

    def encode_bitmap_for_mask(self, bitmap):
        """
        Encode le bitmap au format masque selon mask-go
        """
        results = bytearray()
        
        for column in bitmap:
            if len(column) != 16:
                print(f"ATTENTION: colonne de longueur {len(column)} au lieu de 16")
                
            val = 0
            for j, pixel in enumerate(column):
                if pixel == 1:
                    bit_mapping = {
                        0: 128,    # 0x80
                        1: 64,     # 0x40
                        2: 32,     # 0x20
                        3: 16,     # 0x10
                        4: 8,      # 0x08
                        5: 4,      # 0x04
                        6: 2,      # 0x02
                        7: 1,      # 0x01
                        8: 32768,  # 0x8000
                        9: 16384,  # 0x4000
                        10: 8192,  # 0x2000
                        11: 4096,  # 0x1000
                        12: 2048,  # 0x0800
                        13: 1024,  # 0x0400
                        14: 512,   # 0x0200
                        15: 256    # 0x0100
                    }
                    
                    if j in bit_mapping:
                        val |= bit_mapping[j]
            
            # Encodage little-endian sur 2 bytes
            int_bytes = struct.pack('<H', val)
            results.extend(int_bytes)
            
        return bytes(results)

    def encode_color_array_for_mask(self, columns):
        """Génère un tableau de couleurs blanches"""
        results = bytearray()
        for i in range(columns):
            results.extend([0xFF, 0xFF, 0xFF])  # RGB blanc
        return bytes(results)

    async def upload_part(self):
        """Envoie une partie de l'upload"""
        if self.current_upload['bytes_sent'] == self.current_upload['total_len']:
            return
            
        max_size = 80
        
        bytes_to_send = min(max_size, 
                           self.current_upload['total_len'] - self.current_upload['bytes_sent'])
        
        start_idx = self.current_upload['bytes_sent']
        end_idx = start_idx + bytes_to_send
        data_chunk = self.current_upload['complete_buffer'][start_idx:end_idx]
        
        packet = bytearray()
        packet.append(bytes_to_send + 1)
        packet.append(self.current_upload['packet_count'])
        packet.extend(data_chunk)
        
        await self.send_upload_data(packet)
        
        self.current_upload['bytes_sent'] += bytes_to_send
        self.current_upload['packet_count'] += 1

    async def finish_upload(self):
        """Finalise l'upload avec DATCP"""
        cmd = bytearray()
        cmd.append(5)
        cmd.extend(b"DATCP")
        
        await self.send_command(cmd)

    async def wait_for_response(self, expected_response, timeout=3.0):
        """Attend une réponse spécifique"""
        start_time = time.time()
        
        if self.notification_response == expected_response:
            self.notification_response = None
            return True
        
        while time.time() - start_time < timeout:
            if self.notification_response == expected_response:
                self.notification_response = None
                return True
            await asyncio.sleep(0.1)
            
        raise TimeoutError(f"Timeout en attente de {expected_response}")

    async def init_upload(self, bitmap, color_array):
        """Initialise l'upload avec DATS"""
        if self.upload_running:
            raise RuntimeError("Upload déjà en cours")
            
        self.current_upload = {
            'bitmap': bitmap,
            'color_array': color_array,
            'total_len': len(bitmap) + len(color_array),
            'bytes_sent': 0,
            'packet_count': 0,
            'complete_buffer': bitmap + color_array
        }
        
        cmd = bytearray()
        cmd.append(9)
        cmd.extend(b"DATS")
        cmd.extend(struct.pack('>H', self.current_upload['total_len']))
        cmd.extend(struct.pack('>H', len(bitmap)))
        cmd.append(0)
        
        self.notification_response = None
        await self.send_command(cmd)
        self.upload_running = True
        
        await self.wait_for_response("DATSOK", timeout=5.0)

    async def set_mode(self, mode):
        """Configure le mode d'affichage"""
        if isinstance(mode, str):
            mode = SCROLL_MODES.get(mode, 1)
        
        cmd = bytearray([5]) + b"MODE" + bytes([mode])
        await self.send_command(cmd)
        
        mode_names = {1: "steady", 2: "blink", 3: "scroll left", 4: "scroll right"}
        print(f"Mode configuré: {mode_names.get(mode, f'mode {mode}')}")

    async def set_scroll_speed(self, speed):
        """Configure la vitesse de défilement (0-255, plus haut = plus rapide)"""
        cmd = bytearray([6]) + b"SPEED" + bytes([speed])
        await self.send_command(cmd)
        print(f"Vitesse de défilement: {speed}")

    async def set_scrolling_text(self, text, scroll_mode='scroll_left', speed=50, width_multiplier=1.5):
        """
        Affiche du texte défilant sur le masque
        
        Args:
            text: Texte à afficher
            scroll_mode: 'scroll_left', 'scroll_right', 'blink', ou 'steady'
            speed: Vitesse de défilement (0-255)
            width_multiplier: Multiplicateur de largeur pour le défilement
        """
        print(f"Affichage défilant: '{text}' (mode: {scroll_mode}, vitesse: {speed})")
        
        # 1. Configuration du mode et de la vitesse
        await self.set_mode(scroll_mode)
        await self.set_scroll_speed(speed)
        
        # 2. Génération de l'image avec espace pour le défilement
        pixel_map = self.get_text_image(text, width_multiplier)
        
        # 3. Encodage du bitmap
        bitmap = self.encode_bitmap_for_mask(pixel_map)
        
        # 4. Génération des couleurs
        color_array = self.encode_color_array_for_mask(len(pixel_map))
        
        print(f"Image: {len(pixel_map)} colonnes, Bitmap: {len(bitmap)} bytes")
        
        # 5. Upload
        await self.init_upload(bitmap, color_array)
        
        # 6. Envoi des paquets
        while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
            await self.upload_part()
            await self.wait_for_response("REOK", timeout=3.0)
            
        # 7. Finalisation
        await self.finish_upload()
        await self.wait_for_response("DATCPOK", timeout=3.0)
        
        self.upload_running = False
        print("✅ Texte défilant configuré avec succès!")

    async def set_brightness(self, brightness):
        """Configure la luminosité (0-255)"""
        cmd = bytearray([6]) + b"LIGHT" + bytes([brightness])
        await self.send_command(cmd)

    async def set_background_color(self, r, g, b):
        """Configure la couleur de fond"""
        cmd = bytearray([6]) + b"BG" + bytes([1, r, g, b])
        await self.send_command(cmd)

    async def set_foreground_color(self, r, g, b):
        """Configure la couleur du texte"""
        cmd = bytearray([6]) + b"FC" + bytes([1, r, g, b])
        await self.send_command(cmd)

    async def demo_scrolling_effects(self):
        """Démonstration des différents effets de défilement"""
        texts_and_modes = [
            ("SCROLL LEFT", "scroll_left", 30),
            ("SCROLL RIGHT", "scroll_right", 40),
            ("BLINK TEXT", "blink", 100),
            ("STEADY TEXT", "steady", 0),
            ("FAST SCROLL!", "scroll_left", 80),
            ("Hello World défile", "scroll_left", 50)
        ]
        
        for text, mode, speed in texts_and_modes:
            print(f"\n=== Test: {text} ({mode}) ===")
            await self.set_scrolling_text(text, mode, speed)
            await asyncio.sleep(8)  # Laisser le temps d'observer l'effet

async def demo():
    """Démonstration du texte défilant"""
    mask = ScrollingMaskController()
    
    try:
        await mask.connect()
        
        # Configuration de base
        await mask.set_brightness(80)
        await mask.set_background_color(0, 0, 0)  # Fond noir
        await mask.set_foreground_color(255, 255, 255)  # Texte blanc
        
        print("\n🎬 Démonstration des effets de défilement...")
        
        # Test simple avec défilement à gauche
        print("\n=== Test 1: Défilement simple ===")
        await mask.set_scrolling_text("SALUT CA MARCHE!", "scroll_left", 40)
        await asyncio.sleep(10)
        
        # Test avec défilement à droite
        print("\n=== Test 2: Défilement à droite ===")
        await mask.set_scrolling_text("Direction droite", "scroll_right", 50)
        await asyncio.sleep(10)
        
        # Test avec clignotement
        print("\n=== Test 3: Texte clignotant ===")
        await mask.set_scrolling_text("CLIGNOTANT", "blink", 80)
        await asyncio.sleep(8)
        
        # Test avec texte long
        print("\n=== Test 4: Texte long défilant ===")
        await mask.set_scrolling_text("Voici un texte très long qui défile de gauche à droite!", "scroll_left", 60)
        await asyncio.sleep(15)
        
        print("\n✅ Démonstration terminée!")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mask.disconnect()

if __name__ == "__main__":
    asyncio.run(demo())
