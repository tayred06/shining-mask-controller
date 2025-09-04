#!/usr/bin/env python3
"""
Module Core - Contrôleur de base du masque LED
===============================================

Classe de base pour la communication BLE avec le masque LED.
Gère la connexion, le chiffrement et les protocoles de base.
"""

import asyncio
import time
from bleak import BleakClient, BleakScanner
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
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

class BaseMaskController:
    """
    Contrôleur de base pour le masque LED
    Gère la connexion BLE, le chiffrement et les protocoles de base.
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
    
    def notification_handler(self, sender, data):
        """Gestionnaire des notifications BLE"""
        try:
            decrypted = self.decrypt_aes128(data)
            response = decrypted.decode('utf-8', errors='ignore').rstrip('\x00')
            print(f"📨 Réponse reçue: {response}")
            self.notification_response = response
        except Exception as e:
            print(f"❌ Erreur déchiffrement notification: {e}")
    
    def decrypt_aes128(self, data):
        """Déchiffrement AES-128 ECB"""
        if len(data) != 16:
            raise ValueError("Encrypted data must be exactly 16 bytes")
            
        cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(data) + decryptor.finalize()
    
    async def connect(self):
        """Connexion au masque LED"""
        try:
            print(f"Recherche du masque...")
            devices = await BleakScanner.discover()
            
            target_device = None
            for device in devices:
                if device.name and DEVICE_NAME in device.name:
                    target_device = device
                    break
            
            if not target_device:
                raise Exception(f"Aucun appareil avec '{DEVICE_NAME}' trouvé")
            
            print(f"Connexion à {target_device.name}")
            self.client = BleakClient(target_device.address)
            await self.client.connect()
            
            # S'abonner aux notifications
            await self.client.start_notify(NOTIFY_UUID, self.notification_handler)
            
            print("Connecté avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def disconnect(self):
        """Déconnexion du masque"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Déconnecté du masque")
    
    async def send_command(self, command_data):
        """Envoie une commande chiffrée au masque"""
        if not self.client or not self.client.is_connected:
            raise Exception("Pas connecté au masque")
        
        # Padding à 16 bytes
        padded_data = command_data + b'\x00' * (16 - len(command_data))
        encrypted_data = self.encrypt_aes128(padded_data)
        
        await self.client.write_gatt_char(COMMAND_UUID, encrypted_data)
    
    async def send_upload_data(self, data):
        """Envoie des données via le canal d'upload"""
        if not self.client or not self.client.is_connected:
            raise Exception("Pas connecté au masque")
            
        await self.client.write_gatt_char(UPLOAD_UUID, data)
    
    async def wait_for_response(self, expected_response, timeout=5.0):
        """Attend une réponse spécifique"""
        start_time = time.time()
        self.notification_response = None
        
        while time.time() - start_time < timeout:
            if self.notification_response and expected_response in self.notification_response:
                return self.notification_response
            await asyncio.sleep(0.1)
            
        raise TimeoutError(f"Timeout en attente de {expected_response}")
    
    async def set_brightness(self, brightness):
        """Configure la luminosité (0-100)"""
        brightness = max(0, min(100, brightness))
        cmd = bytearray()
        cmd.append(6)
        cmd.extend(b"LIGHT")
        cmd.append(brightness)
        await self.send_command(cmd)
    
    async def set_foreground_color(self, r, g, b):
        """Configure la couleur de premier plan (commande FC)"""
        cmd = bytearray()
        cmd.append(6)
        cmd.extend(b"FC")
        cmd.append(1)  # Enable
        cmd.append(r)
        cmd.append(g)
        cmd.append(b)
        await self.send_command(cmd)
    
    async def set_background_color(self, r, g, b):
        """Configure la couleur d'arrière-plan (commande BG)"""
        cmd = bytearray()
        cmd.append(6)
        cmd.extend(b"BG")
        cmd.append(1)  # Enable
        cmd.append(r)
        cmd.append(g)
        cmd.append(b)
        await self.send_command(cmd)
    
    async def set_mode(self, mode_name):
        """Configure le mode d'affichage"""
        if mode_name not in SCROLL_MODES:
            raise ValueError(f"Mode inconnu: {mode_name}")
        
        mode_value = SCROLL_MODES[mode_name]
        cmd = bytearray()
        cmd.append(5)
        cmd.extend(b"MODE")
        cmd.append(mode_value)
        await self.send_command(cmd)
    
    async def set_scroll_speed(self, speed):
        """Configure la vitesse de défilement (0-255)"""
        speed = max(0, min(255, speed))
        cmd = bytearray()
        cmd.append(5)
        cmd.extend(b"SPEED")
        cmd.append(speed)
        await self.send_command(cmd)
    
    def encode_bitmap_for_mask(self, pixel_map):
        """Encode une carte de pixels en bitmap pour le masque"""
        results = bytearray()
        
        for x in range(len(pixel_map)):
            column = pixel_map[x]
            
            # Encoder chaque colonne en 2 bytes (16 bits pour 16 pixels)
            byte1 = 0
            byte2 = 0
            
            for y in range(8):
                if column[y] == 1:
                    byte1 |= (1 << y)
            
            for y in range(8, 16):
                if y < len(column) and column[y] == 1:
                    byte2 |= (1 << (y - 8))
            
            results.extend([byte1, byte2])
        
        return bytes(results)
