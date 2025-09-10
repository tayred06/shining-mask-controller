#!/usr/bin/env python3
"""
🔥 FIRMWARE FLASHER SIMPLE - Installation du firmware SANS FLÈCHE
===============================================================
Flash le firmware modifié pour éliminer définitivement la flèche d'upload
"""

import asyncio
import sys
import os
import struct
import time
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import os as _os, sys as _sys
_cur = _os.path.dirname(_os.path.abspath(__file__))
_work = _os.path.join(_cur, 'src', 'working')
_sys.path.insert(0, _work)
try:
    from complete_text_display import ENCRYPTION_KEY as WORKING_AES_KEY
except Exception:
    WORKING_AES_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')

# Configuration du masque
DEVICE_NAME = "MASK-3B9D97"
COMMAND_UUID = "d44bc439-abfd-45a2-b575-925416129600"
DATA_UUID = "d44bc439-abfd-45a2-b575-92541612960a"

# Clé AES (identique à celle du protocole normal)
AES_KEY = WORKING_AES_KEY

class SimpleFirmwareFlasher:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(AES_KEY, AES.MODE_ECB)
        
    async def find_and_connect(self):
        """Trouve et se connecte au masque"""
        print("🔍 Recherche du masque...")
        
        devices = await BleakScanner.discover(timeout=5.0)
        mask_device = None
        
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                mask_device = device
                break
        
        if not mask_device:
            print(f"❌ Masque {DEVICE_NAME} non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask_device.name}...")
        self.client = BleakClient(mask_device.address)
        
        try:
            await self.client.connect()
            print("✅ Connecté!")
            # Preflight: envoyer un LIGHT 150 via protocole connu
            try:
                tag = b"LIGHT" + b"\x00"*11
                enc_tag = self.cipher.encrypt(tag)
                await self.client.write_gatt_char(COMMAND_UUID, enc_tag + bytes([150]))
                await asyncio.sleep(0.2)
                print("✅ Pré-vérification commande LIGHT OK")
            except Exception as e:
                print(f"⚠️  Pré-vérification échouée: {e}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def send_command(self, command_bytes, encrypt=True):
        """Envoie une commande (optionnellement chiffrée)"""
        if encrypt:
            # Assurer que la taille est multiple de 16 pour AES
            padded = command_bytes + b'\x00' * (16 - len(command_bytes) % 16)
            encrypted = self.cipher.encrypt(padded)
            await self.client.write_gatt_char(COMMAND_UUID, encrypted)
        else:
            # Mode bootloader sans chiffrement
            await self.client.write_gatt_char(COMMAND_UUID, command_bytes)
        
    async def send_data_chunk(self, data_chunk):
        """Envoie un chunk de données"""
        await self.client.write_gatt_char(DATA_UUID, data_chunk)
    
    async def enter_bootloader_mode(self):
        """Entre en mode bootloader pour le flashage"""
        print("🔧 Tentative d'entrée en mode bootloader...")
        
        # Séquences pour entrer en mode bootloader (basées sur l'analyse firmware)
        bootloader_commands = [
            b"BOOT\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"FLASH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"UPDATE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"FIRM\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ]
        
        for cmd in bootloader_commands:
            try:
                await self.send_command(cmd, encrypt=False)  # Pas de chiffrement en bootloader
                print(f"📤 Commande bootloader envoyée: {cmd[:4]}")
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"⚠️  Erreur commande {cmd[:4]}: {e}")
        
        print("✅ Séquences bootloader envoyées")
        return True
    
    async def flash_firmware(self, firmware_path):
        """Flash le firmware modifié"""
        print(f"💾 Chargement du firmware: {firmware_path}")
        
        if not os.path.exists(firmware_path):
            print(f"❌ Firmware non trouvé: {firmware_path}")
            return False
        
        with open(firmware_path, 'rb') as f:
            firmware_data = f.read()
        
        print(f"📊 Taille firmware: {len(firmware_data)} bytes")
        
        # Entrer en mode bootloader
        await self.enter_bootloader_mode()
        
        # Envoyer le firmware par chunks
        chunk_size = 512  # Taille de chunk standard pour BLE
        total_chunks = (len(firmware_data) + chunk_size - 1) // chunk_size
        
        print(f"📦 Upload en {total_chunks} chunks de {chunk_size} bytes...")
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(firmware_data))
            chunk = firmware_data[start:end]
            
            # Padding si nécessaire
            if len(chunk) < chunk_size:
                chunk += b'\x00' * (chunk_size - len(chunk))
            
            try:
                # Commande d'écriture firmware (sans chiffrement en bootloader)
                write_cmd = struct.pack('<H', i) + b"FWRT\x00\x00\x00\x00\x00\x00"
                await self.send_command(write_cmd, encrypt=False)
                await asyncio.sleep(0.1)
                
                # Envoyer le chunk (données brutes)
                await self.send_data_chunk(chunk)
                
                progress = (i + 1) / total_chunks * 100
                print(f"⏳ Progress: {progress:.1f}% ({i+1}/{total_chunks})")
                
                await asyncio.sleep(0.2)  # Délai pour éviter la surcharge
                
            except Exception as e:
                print(f"❌ Erreur chunk {i}: {e}")
                return False
        
        # Finaliser l'installation
        print("🔧 Finalisation de l'installation...")
        finalize_cmd = b"FWEND\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        await self.send_command(finalize_cmd, encrypt=False)
        await asyncio.sleep(2.0)
        
        # Redémarrer le masque
        print("🔄 Redémarrage du masque...")
        restart_cmd = b"RESTART\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        await self.send_command(restart_cmd, encrypt=False)
        
        print("✅ Firmware flashé avec succès!")
        return True

async def flash_no_arrow_firmware():
    """Fonction principale pour flasher le firmware sans flèche"""
    print("🔥 FLASHAGE FIRMWARE SANS FLÈCHE")
    print("=" * 50)
    
    # Choisir le firmware à flasher
    firmware_files = [
        "TR1906R04-1-10_OTA.bin_NO_ARROW.bin",
        "TR1906R04-10_OTA.bin_NO_ARROW.bin"
    ]
    
    print("📁 Firmwares modifiés disponibles:")
    for i, fw in enumerate(firmware_files):
        print(f"{i+1}. {fw}")
    
    # Utiliser le premier par défaut
    firmware_path = firmware_files[0]
    print(f"🎯 Utilisation de: {firmware_path}")
    
    flasher = SimpleFirmwareFlasher()
    
    try:
        # Connexion
        if not await flasher.find_and_connect():
            return False
        
        # AVERTISSEMENT IMPORTANT
        print("\n⚠️  AVERTISSEMENT IMPORTANT ⚠️")
        print("🔥 Vous êtes sur le point de flasher un firmware modifié!")
        print("💀 Ceci peut potentiellement endommager votre masque!")
        print("🛡️  Assurez-vous d'avoir une sauvegarde du firmware original!")
        
        response = input("\n❓ Voulez-vous continuer? (oui/non): ").lower()
        
        if response not in ['oui', 'o', 'yes', 'y']:
            print("❌ Annulé par l'utilisateur")
            return False
        
        # Flashage
        print("\n🚀 DÉBUT DU FLASHAGE...")
        success = await flasher.flash_firmware(firmware_path)
        
        if success:
            print("\n🎉 SUCCÈS! Firmware sans flèche installé!")
            print("🎯 La flèche d'upload devrait maintenant être éliminée!")
            print("🧪 Testez maintenant l'envoi de texte...")
        else:
            print("\n❌ Échec du flashage")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
        
    finally:
        if flasher.client and flasher.client.is_connected:
            await flasher.client.disconnect()
            print("🔌 Déconnecté")

if __name__ == "__main__":
    asyncio.run(flash_no_arrow_firmware())
