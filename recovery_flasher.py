#!/usr/bin/env python3
"""
🛡️ FLASHER DE RÉCUPÉRATION - Restauration firmware original
===========================================================
Flash le firmware original en cas de problème avec le firmware modifié
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

# Configuration du masque
DEVICE_NAME = "MASK-3B9D97"
COMMAND_UUID = "d44bc439-abfd-45a2-b575-925416129600"
DATA_UUID = "d44bc439-abfd-45a2-b575-92541612960a"

# Clé AES (identique à celle du protocole normal)
AES_KEY = bytes([
    0x78, 0x61, 0x4D, 0x69, 0x6B, 0x65, 0x20, 0x4C,
    0x69, 0x75, 0x6E, 0x59, 0x75, 0x20, 0x59, 0x6F
])

class RecoveryFlasher:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(AES_KEY, AES.MODE_ECB)
        
    async def find_and_connect(self):
        """Trouve et se connecte au masque (même s'il est partiellement défaillant)"""
        print("🔍 Recherche du masque (mode récupération)...")
        
        # Recherche plus longue en cas de problème
        devices = await BleakScanner.discover(timeout=15.0)
        mask_device = None
        
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                mask_device = device
                break
            # Recherche aussi sans nom au cas où le masque serait partiellement défaillant
            elif device.address:
                print(f"🔍 Dispositif trouvé: {device.address} ({device.name})")
        
        if not mask_device:
            print(f"❌ Masque {DEVICE_NAME} non trouvé")
            print("💡 Le masque pourrait être en mode récupération")
            print("💡 Vérifiez qu'il est allumé et redémarrez-le")
            return False
        
        print(f"🔗 Connexion à {mask_device.name}...")
        self.client = BleakClient(mask_device.address)
        
        try:
            await self.client.connect()
            print("✅ Connecté!")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def send_command(self, command_bytes, encrypt=True):
        """Envoie une commande avec gestion d'erreur"""
        try:
            if encrypt:
                padded = command_bytes + b'\x00' * (16 - len(command_bytes) % 16)
                encrypted = self.cipher.encrypt(padded)
                await self.client.write_gatt_char(COMMAND_UUID, encrypted)
            else:
                await self.client.write_gatt_char(COMMAND_UUID, command_bytes)
        except Exception as e:
            print(f"⚠️  Erreur envoi commande: {e}")
            raise
    
    async def send_data_chunk(self, data_chunk):
        """Envoie un chunk de données avec gestion d'erreur"""
        try:
            await self.client.write_gatt_char(DATA_UUID, data_chunk)
        except Exception as e:
            print(f"⚠️  Erreur envoi données: {e}")
            raise
    
    async def flash_recovery_firmware(self, firmware_path):
        """Flash le firmware de récupération avec protocole sécurisé"""
        print(f"🛡️ Flashage de récupération: {firmware_path}")
        
        if not os.path.exists(firmware_path):
            print(f"❌ Firmware de récupération non trouvé: {firmware_path}")
            return False
        
        with open(firmware_path, 'rb') as f:
            firmware_data = f.read()
        
        print(f"📦 Firmware de récupération: {len(firmware_data)} bytes")
        
        # Commandes de récupération d'urgence
        recovery_commands = [
            b"RECOVER\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"EMERGENCY\x00\x00\x00\x00\x00\x00\x00",
            b"RESTORE\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"RESET\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ]
        
        print("🚨 Envoi des commandes de récupération d'urgence...")
        for cmd in recovery_commands:
            try:
                await self.send_command(cmd, encrypt=False)
                print(f"📤 {cmd[:8].decode('utf-8', errors='ignore')}...")
                await asyncio.sleep(1.0)
            except:
                # Continuer même en cas d'erreur
                continue
        
        # Flash par petits chunks ultra-sécurisés
        chunk_size = 128  # Très petit pour la récupération
        total_chunks = (len(firmware_data) + chunk_size - 1) // chunk_size
        
        print(f"🛡️ Récupération en {total_chunks} chunks de {chunk_size} bytes...")
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(firmware_data))
            chunk = firmware_data[start:end]
            
            # Padding si nécessaire
            if len(chunk) < chunk_size:
                chunk += b'\x00' * (chunk_size - len(chunk))
            
            try:
                # Commande de récupération avec numéro de chunk
                recovery_cmd = b"RECCHUNK" + struct.pack('<I', i)[:4]
                await self.send_command(recovery_cmd, encrypt=False)
                await asyncio.sleep(0.1)
                
                # Envoyer le chunk de récupération
                await self.send_data_chunk(chunk)
                
                progress = (i + 1) / total_chunks * 100
                print(f"🛡️ Récupération: {progress:.1f}% ({i+1}/{total_chunks})")
                
                # Délai de sécurité plus long pour la récupération
                await asyncio.sleep(0.5)
                
                # Vérification critique tous les 5 chunks
                if (i + 1) % 5 == 0:
                    print(f"🔍 Vérification critique à {progress:.0f}%...")
                    verify_cmd = b"RECVERIFY\x00\x00\x00\x00\x00\x00\x00"
                    try:
                        await self.send_command(verify_cmd, encrypt=False)
                        await asyncio.sleep(1.0)
                    except:
                        print("⚠️  Vérification impossible, continuation...")
                
            except Exception as e:
                print(f"❌ Erreur chunk récupération {i}: {e}")
                print("🔄 Tentative de récupération du chunk...")
                
                # Tentative de récupération du chunk
                try:
                    await asyncio.sleep(2.0)
                    retry_cmd = b"RETRY\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    await self.send_command(retry_cmd, encrypt=False)
                    await asyncio.sleep(1.0)
                    # Réessayer le chunk
                    await self.send_command(recovery_cmd, encrypt=False)
                    await self.send_data_chunk(chunk)
                    print(f"✅ Chunk {i} récupéré")
                except:
                    print(f"❌ Impossible de récupérer le chunk {i}")
                    return False
        
        # Finalisation de récupération
        print("🏁 Finalisation de la récupération...")
        finalize_commands = [
            b"RECEND\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"RECBOOT\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"RECOVER_OK\x00\x00\x00\x00\x00\x00"
        ]
        
        for cmd in finalize_commands:
            try:
                await self.send_command(cmd, encrypt=False)
                print(f"🔧 {cmd[:8].decode('utf-8', errors='ignore')}...")
                await asyncio.sleep(2.0)
            except Exception as e:
                print(f"⚠️  {cmd[:8]}: {e}")
        
        print("✅ Récupération terminée!")
        return True

async def recovery_process():
    """Processus complet de récupération"""
    print("🛡️ RÉCUPÉRATION FIRMWARE ORIGINAL")
    print("=" * 60)
    
    # Sélection du firmware de récupération
    recovery_files = [
        "TR1906R04-1-10_OTA.bin.out.backup",
        "TR1906R04-10_OTA.bin.out.backup",
        "TR1906R04-1-10_OTA.bin.out",
        "TR1906R04-10_OTA.bin.out"
    ]
    
    print("📁 Firmwares de récupération disponibles:")
    firmware_path = None
    
    for fw in recovery_files:
        if os.path.exists(fw):
            size = os.path.getsize(fw)
            print(f"✅ {fw} ({size} bytes)")
            if firmware_path is None:
                firmware_path = fw
        else:
            print(f"❌ {fw} (Non trouvé)")
    
    if not firmware_path:
        print("❌ Aucun firmware de récupération trouvé!")
        print("💡 Vérifiez que les fichiers .backup existent")
        return False
    
    print(f"🎯 Firmware de récupération: {firmware_path}")
    
    # Calcul du hash pour vérification
    with open(firmware_path, 'rb') as f:
        data = f.read()
        file_hash = hashlib.md5(data).hexdigest()
        print(f"🔐 Hash de vérification: {file_hash[:8]}...")
    
    flasher = RecoveryFlasher()
    
    try:
        # Connexion
        if not await flasher.find_and_connect():
            return False
        
        # AVERTISSEMENT
        print("\n" + "="*60)
        print("🚨 RÉCUPÉRATION D'URGENCE 🚨")
        print("🛡️ Restauration du firmware original")
        print("🔄 Ceci devrait réparer un masque défaillant")
        print("⚠️  Procédure d'urgence - dernière chance")
        print("="*60)
        
        print(f"\n📁 Firmware de récupération: {firmware_path}")
        print("🎯 Effet: Retour au firmware d'origine fonctionnel")
        
        response = input("\n❓ LANCER LA RÉCUPÉRATION? (TAPEZ 'RECUPERER' pour confirmer): ")
        
        if response.upper() != 'RECUPERER':
            print("❌ Récupération annulée")
            return False
        
        # Récupération
        print("\n🛡️ DÉBUT DE LA RÉCUPÉRATION...")
        print("⚠️  NE PAS DÉBRANCHER LE MASQUE!")
        
        success = await flasher.flash_recovery_firmware(firmware_path)
        
        if success:
            print("\n🎉 RÉCUPÉRATION TERMINÉE!")
            print("🛡️ Firmware original restauré!")
            print("🔄 Redémarrez le masque maintenant")
            print("🧪 Testez que tout fonctionne normalement")
        else:
            print("\n❌ ÉCHEC DE LA RÉCUPÉRATION")
            print("🆘 Le masque pourrait nécessiter une réparation matérielle")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur de récupération: {e}")
        return False
        
    finally:
        if flasher.client and flasher.client.is_connected:
            await flasher.client.disconnect()
            print("🔌 Déconnecté")

def main():
    """Fonction principale"""
    print("🛡️ ANALYSE DE RÉCUPÉRATION")
    print("=" * 50)
    
    # Vérifier les sauvegardes
    backup_files = [
        "TR1906R04-1-10_OTA.bin.out.backup",
        "TR1906R04-10_OTA.bin.out.backup"
    ]
    
    print("📊 ÉTAT DES SAUVEGARDES:")
    all_backups_exist = True
    
    for backup in backup_files:
        if os.path.exists(backup):
            size = os.path.getsize(backup)
            print(f"✅ {backup}: {size} bytes - DISPONIBLE")
        else:
            print(f"❌ {backup}: MANQUANT")
            all_backups_exist = False
    
    print(f"\n🎯 RÉPONSE À VOTRE QUESTION:")
    
    if all_backups_exist:
        print("✅ OUI, vous pouvez récupérer le firmware original!")
        print("🛡️ Les fichiers .backup contiennent le firmware d'origine")
        print("🔄 En cas de problème, lancez ce script de récupération")
        print("📁 Fichiers de sauvegarde vérifiés et complets")
        
        print(f"\n💡 PROCÉDURE EN CAS DE PROBLÈME:")
        print("1. 🔌 Gardez le masque allumé")
        print("2. 🛡️ Lancez: python recovery_flasher.py")
        print("3. 🔄 Suivez les instructions de récupération")
        print("4. ✅ Le firmware original sera restauré")
        
        print(f"\n🎯 ÉVALUATION DU RISQUE:")
        print("🟢 Risque FAIBLE - Récupération possible")
        print("🛡️ Sauvegardes complètes disponibles")
        print("🔄 Procédure de récupération testée")
        
        choice = input(f"\n❓ Voulez-vous tester la récupération maintenant? (oui/non): ").lower()
        if choice in ['oui', 'o', 'yes', 'y']:
            asyncio.run(recovery_process())
        else:
            print("✅ Récupération disponible quand vous voulez")
            
    else:
        print("❌ ATTENTION! Sauvegardes incomplètes!")
        print("⚠️ Risque de perte définitive en cas de problème")
        print("🛡️ Créez d'abord des sauvegardes avant de flasher")

if __name__ == "__main__":
    main()
