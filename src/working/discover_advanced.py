#!/usr/bin/env python3
"""
Script de découverte AVANCÉ pour les commandes du masque.
Teste :
1. La commande DATA (nouveau protocole supposé)
2. La commande PLAY avec le suffixe magique (ancien protocole supposé)
3. Des IDs élevés (45, 100)
"""

import asyncio
import sys
import os
from bleak import BleakClient, BleakScanner
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES

# Configuration BLE
DEVICE_NAME = "MASK"
ENCRYPTION_KEY = bytes.fromhex("32672f7974ad43451d9c6c894a0e8764")
COMMAND_UUID = "d44bc439-abfd-45a2-b575-925416129600"

class AdvancedDiscoveryController:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)

    def encrypt_aes128(self, data):
        if len(data) != 16:
            raise ValueError("Data must be exactly 16 bytes")
        cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def pad_byte_array(self, array, length):
        padded = bytearray(length)
        padded[:len(array)] = array
        return bytes(padded)

    async def send_command(self, data):
        if not self.client:
            return
        padded_data = self.pad_byte_array(data, 16)
        encrypted_data = self.encrypt_aes128(padded_data)
        await self.client.write_gatt_char(COMMAND_UUID, encrypted_data)
        await asyncio.sleep(0.2)

    async def connect(self):
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
        print("Connecté !")
        return True

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def test_data_command(self, image_id):
        """Envoie DATA [ImageID]"""
        cmd_str = "DATA"
        args = bytes([image_id])
        payload = bytearray()
        payload.append(len(cmd_str) + len(args))
        payload.extend(cmd_str.encode('ascii'))
        payload.extend(args)
        
        print(f"Envoi: DATA ID={image_id} (Raw: {payload.hex()})")
        await self.send_command(payload)

    async def test_play_magic_suffix(self, image_id):
        """Envoie PLAY [0x01] [ImageID] [MagicSuffix]"""
        # Format découvert: b'\x06PLAY\x01' + image_id + suffixe_fixe
        # Le suffixe est ; + bytes bizarres
        suffix = b';\x97\xf2\xf3U\xa9r\x13\x8b'
        
        base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + suffix
        
        # Note: send_command fait déjà le padding et l'encryption
        # Mais ici on veut envoyer exactement ce blob, peut-être sans le header de longueur standard ?
        # Non, send_command attend des données brutes avant encryption.
        
        # Le format standard est [Len] [CMD] [Args]
        # Ici \x06PLAY\x01 semble être [Len=6] [PLAY] [Arg=1]
        # Donc on envoie PLAY + \x01 + ID + Suffixe
        
        cmd_str = "PLAY"
        args = b'\x01' + image_id.to_bytes(1, 'big') + suffix
        
        payload = bytearray()
        payload.append(len(cmd_str) + len(args))
        payload.extend(cmd_str.encode('ascii'))
        payload.extend(args)
        
        print(f"Envoi: PLAY MAGIC ID={image_id} (Raw: {payload.hex()})")
        await self.send_command(payload)

async def main():
    controller = AdvancedDiscoveryController()
    try:
        await controller.connect()
        
        print("\n--- TEST DE DÉCOUVERTE AVANCÉ ---")
        
        print("\n1. Test de la commande DATA (ID 1)")
        await controller.test_data_command(1)
        input("Appuyez sur Entrée si vous voyez l'image SYSTÈME (sinon Entrée)...")

        print("\n2. Test de la commande PLAY avec Suffixe Magique (ID 1)")
        await controller.test_play_magic_suffix(1)
        input("Appuyez sur Entrée si vous voyez l'image SYSTÈME (sinon Entrée)...")
        
        print("\n3. Test ID élevé (ID 45) avec DATA")
        await controller.test_data_command(45)
        input("Appuyez sur Entrée si vous voyez quelque chose...")

    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
