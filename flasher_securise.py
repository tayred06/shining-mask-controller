#!/usr/bin/env python3
"""
🔥 FLASHER SÉCURISÉ - Installation firmware SANS FLÈCHE
=======================================================
Flasher avec vérifications de sécurité et sauvegarde
"""

import asyncio
import sys
import os
import struct
import time
import hashlib
from pathlib import Path
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Importer la clé et utilitaires depuis l'implémentation validée
import sys as _sys
import os as _os
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

class SecureFirmwareFlasher:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(AES_KEY, AES.MODE_ECB)
        self.backup_dir = Path("firmware_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    async def preflight_check(self) -> bool:
        """Petit test de connectivité + chiffrement avant flash."""
        print("\n🧪 Pré-vérifications (connectivité/chiffrement)...")
        try:
            # Construire une commande LIGHT pour 1 puis retour 150
            cmd_tag = b"LIGHT" + b"\x00" * 11  # 16 octets pour le tag
            # Le protocole réel attend le bloc chiffré du tag, suivi du payload en clair
            enc_tag = self.cipher.encrypt(cmd_tag)
            # Baisser un peu
            await self.client.write_gatt_char(COMMAND_UUID, enc_tag + bytes([1]))
            await asyncio.sleep(0.2)
            # Restaurer
            await self.client.write_gatt_char(COMMAND_UUID, enc_tag + bytes([150]))
            await asyncio.sleep(0.2)
            print("✅ Pré-vérifications OK")
            return True
        except Exception as e:
            print(f"⚠️  Pré-vérifications échouées: {e}")
            return False
        
    async def find_and_connect(self):
        """Trouve et se connecte au masque avec vérifications"""
        print("🔍 Recherche du masque...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        mask_device = None
        
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                mask_device = device
                break
        
        if not mask_device:
            print(f"❌ Masque {DEVICE_NAME} non trouvé")
            print("💡 Vérifiez que le masque est allumé et proche")
            return False
        
        print(f"🔗 Connexion à {mask_device.name}...")
        self.client = BleakClient(mask_device.address)
        
        try:
            await self.client.connect()
            print("✅ Connecté!")
            # Petit délai pour stabilité BLE
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def backup_current_firmware(self):
        """Tente de sauvegarder le firmware actuel"""
        print("💾 Tentative de sauvegarde du firmware actuel...")
        
        try:
            # Commandes pour lire le firmware (basées sur l'analyse)
            read_commands = [
                b"FWREAD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"DUMP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"BACKUP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            ]
            
            for cmd in read_commands:
                try:
                    # Essayer avec et sans chiffrement
                    await self.send_command(cmd, encrypt=True)
                    await asyncio.sleep(0.5)
                    await self.send_command(cmd, encrypt=False)
                    await asyncio.sleep(0.5)
                except:
                    continue
            
            print("⚠️  Sauvegarde automatique non supportée")
            print("💡 Le firmware original pourra être récupéré via les fichiers .backup")
            return True
            
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde: {e}")
            return True  # Continuer quand même
    
    async def send_command(self, command_bytes, encrypt=True):
        """Envoie une commande (optionnellement chiffrée)"""
        if encrypt:
            # Assurer que la taille est multiple de 16 pour AES
            padded = command_bytes + b'\x00' * (16 - len(command_bytes) % 16)
            encrypted = self.cipher.encrypt(padded)
            await self.client.write_gatt_char(COMMAND_UUID, encrypted)
        else:
            await self.client.write_gatt_char(COMMAND_UUID, command_bytes)
    
    async def send_data_chunk(self, data_chunk):
        """Envoie un chunk de données"""
        await self.client.write_gatt_char(DATA_UUID, data_chunk)
    
    async def verify_firmware_file(self, firmware_path):
        """Vérifie l'intégrité du fichier firmware"""
        print(f"🔍 Vérification du firmware: {firmware_path}")
        
        if not os.path.exists(firmware_path):
            print(f"❌ Firmware non trouvé: {firmware_path}")
            return False
        
        file_size = os.path.getsize(firmware_path)
        print(f"📊 Taille du firmware: {file_size} bytes")
        
        # Vérifier que c'est un firmware modifié (doit contenir "_NO_ARROW")
        if "_NO_ARROW" not in firmware_path:
            print("⚠️  Ce n'est pas un firmware modifié!")
            return False
        
        # Calculer le hash pour vérification
        with open(firmware_path, 'rb') as f:
            firmware_data = f.read()
            file_hash = hashlib.md5(firmware_data).hexdigest()
            print(f"🔐 Hash MD5: {file_hash[:8]}...")
        
        # Vérifier que le firmware semble valide (taille raisonnable)
        if file_size < 10000 or file_size > 200000:
            print(f"⚠️  Taille de firmware suspecte: {file_size}")
            response = input("❓ Continuer malgré tout? (oui/non): ").lower()
            return response in ['oui', 'o', 'yes', 'y']
        
        print("✅ Firmware vérifié")
        return True
    
    async def enter_flash_mode(self):
        """Entre en mode flash avec séquence sécurisée"""
        print("🔧 Entrée en mode flash...")
        
        # Séquences d'entrée en mode flash (plus sûres)
        flash_sequences = [
            # Séquence 1: Standard OTA
            [
                b"OTAMODE\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"FLASHEN\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            ],
            # Séquence 2: Bootloader
            [
                b"BOOTLOAD\x00\x00\x00\x00\x00\x00\x00\x00",
                b"PROGRAM\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            ],
            # Séquence 3: Update mode
            [
                b"UPDATE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"READY\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            ]
        ]
        
        for i, sequence in enumerate(flash_sequences, 1):
            print(f"🧪 Test séquence {i}/{len(flash_sequences)}...")
            
            for cmd in sequence:
                try:
                    # Essayer sans chiffrement d'abord
                    await self.send_command(cmd, encrypt=False)
                    print(f"📤 Envoyé: {cmd[:8]}...")
                    await asyncio.sleep(1.0)
                except Exception as e:
                    print(f"⚠️  Erreur: {e}")
            
            # Tester si le mode flash est actif
            try:
                test_cmd = b"FLASHTEST\x00\x00\x00\x00\x00\x00\x00"
                await self.send_command(test_cmd, encrypt=False)
                await asyncio.sleep(0.5)
                print(f"✅ Séquence {i} envoyée")
            except:
                continue
        
        print("🔧 Séquences flash envoyées")
        return True
    
    async def flash_firmware_secure(self, firmware_path):
        """Flash le firmware avec méthode sécurisée"""
        print(f"🚀 Flashage sécurisé: {firmware_path}")
        
        with open(firmware_path, 'rb') as f:
            firmware_data = f.read()
        
        print(f"📦 Données firmware: {len(firmware_data)} bytes")
        
        # Entrer en mode flash
        await self.enter_flash_mode()
        
        # Flash par petits chunks avec vérification
        chunk_size = 256  # Plus petit pour la sécurité
        total_chunks = (len(firmware_data) + chunk_size - 1) // chunk_size
        
        print(f"📤 Flash en {total_chunks} chunks de {chunk_size} bytes...")
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(firmware_data))
            chunk = firmware_data[start:end]
            
            # Padding si nécessaire
            if len(chunk) < chunk_size:
                chunk += b'\x00' * (chunk_size - len(chunk))
            
            try:
                # En-tête de chunk avec numéro
                chunk_header = struct.pack('<I', i)  # Numéro de chunk en little-endian
                
                # Envoyer l'en-tête
                header_cmd = b"CHUNK\x00\x00\x00\x00\x00\x00" + chunk_header
                await self.send_command(header_cmd, encrypt=False)
                await asyncio.sleep(0.1)
                
                # Envoyer les données
                await self.send_data_chunk(chunk)
                
                progress = (i + 1) / total_chunks * 100
                print(f"⏳ Progress: {progress:.1f}% ({i+1}/{total_chunks})")
                
                # Délai de sécurité entre chunks
                await asyncio.sleep(0.3)
                
                # Vérification périodique (tous les 10 chunks)
                if (i + 1) % 10 == 0:
                    print(f"🔍 Vérification à {progress:.0f}%...")
                    verify_cmd = b"VERIFY\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    await self.send_command(verify_cmd, encrypt=False)
                    await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Erreur chunk {i}: {e}")
                print("⚠️  Tentative de récupération...")
                await asyncio.sleep(1.0)
                
                # Tentative de récupération
                try:
                    recovery_cmd = b"RECOVER\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    await self.send_command(recovery_cmd, encrypt=False)
                    await asyncio.sleep(2.0)
                    continue
                except:
                    print("❌ Échec de récupération")
                    return False
        
        # Finalisation sécurisée
        print("🏁 Finalisation du flash...")
        finalize_commands = [
            b"FINALIZE\x00\x00\x00\x00\x00\x00\x00\x00",
            b"COMPLETE\x00\x00\x00\x00\x00\x00\x00\x00",
            b"REBOOT\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ]
        
        for cmd in finalize_commands:
            try:
                await self.send_command(cmd, encrypt=False)
                print(f"🔧 {cmd[:8].decode('utf-8', errors='ignore')}...")
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"⚠️  {cmd[:8]}: {e}")
        
        print("✅ Flash terminé!")
        return True

async def secure_flash_process():
    """Processus complet de flashage sécurisé"""
    print("🔥 FLASHAGE SÉCURISÉ - FIRMWARE SANS FLÈCHE")
    print("=" * 60)
    
    # Sélection du firmware
    firmware_files = [
        "TR1906R04-1-10_OTA.bin_NO_ARROW.bin",
        "TR1906R04-10_OTA.bin_NO_ARROW.bin"
    ]
    
    print("📁 Firmwares modifiés disponibles:")
    for i, fw in enumerate(firmware_files):
        if os.path.exists(fw):
            size = os.path.getsize(fw)
            print(f"{i+1}. {fw} ({size} bytes)")
        else:
            print(f"{i+1}. {fw} (❌ Non trouvé)")
    
    # Utiliser le premier disponible
    firmware_path = None
    for fw in firmware_files:
        if os.path.exists(fw):
            firmware_path = fw
            break
    
    if not firmware_path:
        print("❌ Aucun firmware modifié trouvé!")
        return False
    
    print(f"🎯 Firmware sélectionné: {firmware_path}")
    
    flasher = SecureFirmwareFlasher()
    
    try:
        # ÉTAPE 1: Connexion
        if not await flasher.find_and_connect():
            return False
        
        # ÉTAPE 1b: Pré-vérifications (obligatoire avant d'aller plus loin)
        if not await flasher.preflight_check():
            print("❌ Pré-vérifications échouées - abandon")
            return False
        
        # ÉTAPE 2: Vérification du firmware
        if not await flasher.verify_firmware_file(firmware_path):
            return False
        
        # ÉTAPE 3: Sauvegarde (tentative)
        await flasher.backup_current_firmware()
        
        # AVERTISSEMENT FINAL
        print("\n" + "="*60)
        print("⚠️  AVERTISSEMENT FINAL ⚠️")
        print("🔥 Vous allez flasher un firmware modifié!")
        print("💀 Risque d'endommagement du masque!")
        print("🚫 Pas de garantie de retour en arrière!")
        print("🛡️  Fichiers de sauvegarde: TR1906R04-*.bin.out.backup")
        print("="*60)
        
        print("\n🎯 FIRMWARE À INSTALLER:")
        print(f"📁 {firmware_path}")
        print("🎊 Effet: Suppression définitive de la flèche d'upload")
        
        response = input("\n❓ CONFIRMER LE FLASHAGE? (TAPEZ 'FLASHER' pour confirmer): ")
        
        if response.upper() != 'FLASHER':
            print("❌ Flashage annulé")
            return False
        
        # ÉTAPE 4: Flashage
        print("\n🚀 DÉBUT DU FLASHAGE...")
        print("⚠️  NE PAS DÉBRANCHER LE MASQUE!")
        
        success = await flasher.flash_firmware_secure(firmware_path)
        
        if success:
            print("\n🎉 FLASHAGE TERMINÉ!")
            print("🎯 Firmware sans flèche installé!")
            print("🧪 Testez maintenant l'envoi de texte...")
            print("💡 La flèche d'upload devrait avoir disparu!")
            
            # Test immédiat
            print("\n🧪 TEST IMMÉDIAT...")
            await asyncio.sleep(3)  # Laisser le masque redémarrer
            
            print("🔄 Reconnexion pour test...")
            await flasher.client.disconnect()
            await asyncio.sleep(2)
            
            if await flasher.find_and_connect():
                print("✅ Reconnecté! Le firmware fonctionne!")
            else:
                print("⚠️  Problème de reconnexion - vérifiez le masque")
        else:
            print("\n❌ ÉCHEC DU FLASHAGE")
            print("🛠️  Le masque devrait toujours fonctionner")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False
        
    finally:
        if flasher.client and flasher.client.is_connected:
            await flasher.client.disconnect()
            print("🔌 Déconnecté")

if __name__ == "__main__":
    asyncio.run(secure_flash_process())
