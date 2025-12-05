#!/usr/bin/env python3
"""
Script de découverte pour les commandes PLAY du masque.
Teste différentes valeurs pour le premier octet de la commande PLAY.
"""

import asyncio
import sys
import os
from bleak import BleakClient, BleakScanner
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Configuration BLE
DEVICE_NAME = "MASK"
ENCRYPTION_KEY = bytes.fromhex("32672f7974ad43451d9c6c894a0e8764")
COMMAND_UUID = "d44bc439-abfd-45a2-b575-925416129600"

class DiscoveryController:
    def __init__(self):
        self.client = None

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
        await asyncio.sleep(0.1)

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

    async def test_play_command(self, bank, image_id):
        """Envoie PLAY [Bank] [ImageID]"""
        cmd_str = "PLAY"
        args = bytes([bank, image_id])
        payload = bytearray()
        payload.append(len(cmd_str) + len(args))
        payload.extend(cmd_str.encode('ascii'))
        payload.extend(args)
        
        print(f"Envoi: PLAY Bank={bank} ID={image_id} (Raw: {payload.hex()})")
        await self.send_command(payload)

async def main():
    controller = DiscoveryController()
    try:
        await controller.connect()
        
        print("\n--- TEST DE DÉCOUVERTE ---")
        print("Nous allons tester différentes valeurs de 'Bank' pour l'image 1.")
        print("Regardez le masque et notez ce qui s'affiche.")
        
        banks_to_test = [0, 1, 2, 255]
        
        for bank in banks_to_test:
            print(f"\n--- Test Bank {bank} ---")
            await controller.test_play_command(bank, 1)
            input("Appuyez sur Entrée pour continuer...")
            
        print("\n--- TEST IMAGE ID ---")
        print("Testons si l'ID 0 ou 100 fait quelque chose sur Bank 0")
        await controller.test_play_command(0, 100) # Bank 0, ID 100
        
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
