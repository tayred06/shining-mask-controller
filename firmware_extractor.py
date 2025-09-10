#!/usr/bin/env python3
"""
🔓 FIRMWARE EXTRACTOR - Extraction du firmware via BLE
Extraction du firmware de votre masque pour analyse et modification
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'working'))

from complete_text_display import TextDisplayController
import struct
import time

class FirmwareExtractor:
    """Extracteur de firmware pour masques Shining Mask"""
    
    def __init__(self):
        self.controller = None
        self.firmware_data = bytearray()
        
    async def connect_to_mask(self) -> bool:
        """Se connecte au masque LED"""
        try:
            print("🔗 Connexion au masque...")
            self.controller = TextDisplayController()
            await self.controller.connect()
            print("✅ Connexion établie !")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    async def probe_firmware_commands(self):
        """Teste différentes commandes pour extraire des informations firmware"""
        print("🔍 Sondage des commandes firmware...")
        
        # Commandes potentielles pour extraction firmware
        test_commands = [
            ("FWVER", "Version firmware"),
            ("FWGET", "Récupération firmware"), 
            ("DUMP", "Dump mémoire"),
            ("READ", "Lecture mémoire"),
            ("INFO", "Informations système"),
            ("BOOT", "Mode bootloader"),
            ("OTA", "Mode mise à jour"),
            ("CHIP", "Info chipset"),
            ("MEM", "État mémoire"),
            ("DBG", "Mode debug"),
            ("VERS", "Version"),
            ("STAT", "Statut"),
            ("SYS", "Système")
        ]
        
        results = []
        
        for cmd, desc in test_commands:
            try:
                print(f"🧪 Test: {cmd} ({desc})")
                
                # Essaie la commande
                command = self.controller.create_command(cmd, b"")
                await self.controller.client.write_gatt_char(
                    self.controller.COMMAND_CHAR, command
                )
                
                # Attendre une réponse
                await asyncio.sleep(0.5)
                
                # Essayer de lire une réponse
                try:
                    response = await self.controller.client.read_gatt_char(
                        self.controller.DATA_CHAR
                    )
                    if response:
                        results.append((cmd, desc, response))
                        print(f"✅ {cmd}: Réponse reçue ({len(response)} bytes)")
                        print(f"   Data: {response.hex()}")
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ {cmd}: {e}")
                
        return results
    
    async def attempt_memory_dump(self) -> bytes:
        """Tente d'extraire le contenu de la mémoire"""
        print("🧠 Tentative de dump mémoire...")
        
        firmware_chunks = []
        
        # Adresses mémoire potentielles pour ARM32
        memory_ranges = [
            (0x08000000, 0x10000),  # Flash principale ARM
            (0x20000000, 0x8000),   # RAM
            (0x00000000, 0x10000),  # Boot ROM
        ]
        
        for start_addr, size in memory_ranges:
            print(f"📍 Lecture mémoire: 0x{start_addr:08x} - 0x{(start_addr + size):08x}")
            
            try:
                # Commande de lecture mémoire
                read_cmd = struct.pack('<II', start_addr, size)
                command = self.controller.create_command("READ", read_cmd)
                
                await self.controller.client.write_gatt_char(
                    self.controller.COMMAND_CHAR, command
                )
                
                # Attendre et lire la réponse
                await asyncio.sleep(1.0)
                
                # Lire par chunks
                chunk_data = bytearray()
                for i in range(10):  # Essaie plusieurs lectures
                    try:
                        data = await self.controller.client.read_gatt_char(
                            self.controller.DATA_CHAR
                        )
                        if data:
                            chunk_data.extend(data)
                            print(f"📦 Chunk {i}: {len(data)} bytes")
                        await asyncio.sleep(0.1)
                    except:
                        break
                
                if chunk_data:
                    firmware_chunks.append((start_addr, bytes(chunk_data)))
                    print(f"✅ Mémoire extraite: {len(chunk_data)} bytes depuis 0x{start_addr:08x}")
                
            except Exception as e:
                print(f"❌ Erreur lecture 0x{start_addr:08x}: {e}")
        
        return firmware_chunks
    
    async def attempt_ota_mode(self) -> bool:
        """Tente d'activer le mode OTA pour extraction"""
        print("🔄 Tentative d'activation mode OTA...")
        
        ota_commands = [
            ("OTA", b"\x01"),
            ("BOOT", b""),
            ("UPDATE", b""),
            ("FLASH", b""),
        ]
        
        for cmd, data in ota_commands:
            try:
                print(f"🧪 Test mode OTA: {cmd}")
                command = self.controller.create_command(cmd, data)
                await self.controller.client.write_gatt_char(
                    self.controller.COMMAND_CHAR, command
                )
                await asyncio.sleep(1.0)
                
                # Vérifier si le mode a changé
                try:
                    response = await self.controller.client.read_gatt_char(
                        self.controller.DATA_CHAR
                    )
                    if response:
                        print(f"✅ Réponse OTA {cmd}: {response.hex()}")
                        return True
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ Erreur OTA {cmd}: {e}")
        
        return False
    
    async def save_extracted_data(self, data_chunks: list, filename: str):
        """Sauvegarde les données extraites"""
        if not data_chunks:
            print("❌ Aucune donnée à sauvegarder")
            return
        
        print(f"💾 Sauvegarde dans {filename}...")
        
        with open(filename, 'wb') as f:
            # En-tête avec métadonnées
            f.write(b"SHINING_MASK_DUMP\x00")
            f.write(struct.pack('<I', len(data_chunks)))
            
            # Écrit chaque chunk avec son adresse
            for addr, data in data_chunks:
                f.write(struct.pack('<II', addr, len(data)))
                f.write(data)
        
        print(f"✅ Dump sauvé: {filename} ({os.path.getsize(filename)} bytes)")
    
    async def extract_firmware(self):
        """Processus complet d'extraction firmware"""
        print("🚀 DÉMARRAGE EXTRACTION FIRMWARE")
        print("=" * 50)
        
        # 1. Connexion
        if not await self.connect_to_mask():
            print("❌ Impossible de se connecter au masque")
            return
        
        try:
            # 2. Sondage des commandes
            print("\n🔍 PHASE 1: Sondage des commandes")
            cmd_results = await self.probe_firmware_commands()
            
            if cmd_results:
                with open("command_probe_results.txt", 'w') as f:
                    f.write("# Résultats sondage commandes firmware\n\n")
                    for cmd, desc, response in cmd_results:
                        f.write(f"## {cmd} - {desc}\n")
                        f.write(f"Réponse: {response.hex()}\n")
                        f.write(f"ASCII: {response.decode('ascii', errors='ignore')}\n\n")
            
            # 3. Tentative mode OTA
            print("\n🔄 PHASE 2: Mode OTA")
            ota_success = await self.attempt_ota_mode()
            
            # 4. Dump mémoire
            print("\n🧠 PHASE 3: Extraction mémoire")
            memory_data = await self.attempt_memory_dump()
            
            # 5. Sauvegarde
            if memory_data:
                await self.save_extracted_data(memory_data, "mask_firmware_dump.bin")
            
            print("\n🎯 RÉSUMÉ D'EXTRACTION")
            print(f"- Commandes sondées: {len(cmd_results)}")
            print(f"- Mode OTA: {'✅' if ota_success else '❌'}")
            print(f"- Chunks mémoire: {len(memory_data)}")
            
            if memory_data:
                print("\n✅ EXTRACTION RÉUSSIE !")
                print("📁 Fichiers créés:")
                print("  - mask_firmware_dump.bin (données brutes)")
                print("  - command_probe_results.txt (résultats commandes)")
            else:
                print("\n⚠️ EXTRACTION PARTIELLE")
                print("💡 Le masque peut avoir des protections anti-dump")
                
        finally:
            # Déconnexion propre
            if self.controller and self.controller.client:
                await self.controller.client.disconnect()
                print("🔌 Déconnexion du masque")

async def main():
    """Fonction principale"""
    extractor = FirmwareExtractor()
    await extractor.extract_firmware()

if __name__ == "__main__":
    asyncio.run(main())
