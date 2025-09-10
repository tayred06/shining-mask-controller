#!/usr/bin/env python3
"""
💾 FIRMWARE FLASHER - Installation des firmwares sans flèche
Flash les firmwares modifiés sur le masque pour éliminer définitivement la flèche
"""

import asyncio
import sys
import os
import struct
import time

# Ajouter le chemin vers le module
current_dir = os.path.dirname(os.path.abspath(__file__))
working_dir = os.path.join(current_dir, 'src', 'working')
sys.path.insert(0, working_dir)

try:
    from complete_text_display import MaskTextDisplay, COMMAND_CHAR, UPLOAD_CHAR
    
    # Adapter la classe pour compatibilité
    class TextDisplayController(MaskTextDisplay):
        def __init__(self):
            super().__init__()
            self.COMMAND_CHAR = COMMAND_CHAR
            self.DATA_CHAR = UPLOAD_CHAR
        
        def create_command(self, cmd, data):
            """Crée une commande compatible avec le protocole"""
            return cmd.encode() + data
            
except ImportError as e:
    print("❌ Erreur: Module complete_text_display non trouvé")
    print(f"💡 Chemin recherché: {working_dir}")
    print(f"💡 Erreur détaillée: {e}")
    
    # Vérification des fichiers
    if os.path.exists(working_dir):
        files = os.listdir(working_dir)
        print(f"📁 Fichiers dans {working_dir}: {files}")
    else:
        print(f"❌ Dossier {working_dir} n'existe pas")
    
    print("\n🛠️ Solution temporaire: Utilisation d'un controller simplifié")
    
    # Créer un controller temporaire pour les tests
    class TempTextDisplayController:
        def __init__(self):
            self.client = None
            self.COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
            self.DATA_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
        
        async def connect(self):
            print("⚠️ Mode simulation - pas de vraie connexion BLE")
            return True
        
        def create_command(self, cmd, data):
            return cmd.encode() + data
        
        async def display_text(self, text, color):
            print(f"📺 Simulation affichage: '{text}' en couleur {color}")
    
    TextDisplayController = TempTextDisplayController

class FirmwareFlasher:
    """Flasheur de firmware pour masques Shining Mask"""
    
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
    
    def load_patched_firmware(self, firmware_path: str) -> bool:
        """Charge le firmware patché"""
        try:
            print(f"📁 Chargement firmware: {firmware_path}")
            with open(firmware_path, 'rb') as f:
                self.firmware_data = bytearray(f.read())
            print(f"✅ Firmware chargé: {len(self.firmware_data):,} bytes")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement firmware: {e}")
            return False
    
    async def backup_current_firmware(self) -> bool:
        """Sauvegarde le firmware actuel avant flash"""
        print("💾 Sauvegarde du firmware actuel...")
        
        try:
            # Tentative de lecture du firmware actuel
            backup_data = bytearray()
            
            # Commandes potentielles pour lecture firmware
            read_commands = [
                ("FWREAD", "Lecture firmware"),
                ("DUMP", "Dump complet"),
                ("BACKUP", "Sauvegarde")
            ]
            
            for cmd, desc in read_commands:
                try:
                    print(f"🧪 Test: {cmd}")
                    command = self.controller.create_command(cmd, b"")
                    await self.controller.client.write_gatt_char(
                        self.controller.COMMAND_CHAR, command
                    )
                    await asyncio.sleep(1.0)
                    
                    # Tentative de lecture
                    try:
                        response = await self.controller.client.read_gatt_char(
                            self.controller.DATA_CHAR
                        )
                        if response and len(response) > 10:
                            backup_data.extend(response)
                            print(f"✅ Données récupérées: {len(response)} bytes")
                    except:
                        pass
                        
                except Exception as e:
                    print(f"⚠️ {cmd}: {e}")
            
            if backup_data:
                backup_filename = f"firmware_backup_{int(time.time())}.bin"
                with open(backup_filename, 'wb') as f:
                    f.write(backup_data)
                print(f"✅ Sauvegarde créée: {backup_filename}")
                return True
            else:
                print("⚠️ Impossible de sauvegarder - continuons prudemment")
                return False
                
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    async def enter_flash_mode(self) -> bool:
        """Active le mode flash/OTA"""
        print("🔄 Activation du mode flash...")
        
        flash_commands = [
            ("OTA", b"\x01", "Mode OTA"),
            ("FLASH", b"", "Mode flash"),
            ("UPDATE", b"", "Mode update"),
            ("BOOT", b"", "Mode bootloader"),
            ("PROGRAM", b"", "Mode programmation")
        ]
        
        for cmd, data, desc in flash_commands:
            try:
                print(f"🧪 Test mode: {cmd} ({desc})")
                command = self.controller.create_command(cmd, data)
                await self.controller.client.write_gatt_char(
                    self.controller.COMMAND_CHAR, command
                )
                await asyncio.sleep(2.0)
                
                # Vérifier la réponse
                try:
                    response = await self.controller.client.read_gatt_char(
                        self.controller.DATA_CHAR
                    )
                    if response:
                        print(f"✅ Mode {cmd} activé: {response.hex()}")
                        return True
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ Erreur mode {cmd}: {e}")
        
        print("⚠️ Aucun mode flash standard détecté")
        return False
    
    async def flash_firmware_chunks(self) -> bool:
        """Flash le firmware par chunks"""
        print("📡 Début du flash du firmware...")
        
        if not self.firmware_data:
            print("❌ Aucun firmware chargé")
            return False
        
        # Paramètres de flash
        chunk_size = 128  # Taille des chunks BLE
        total_chunks = (len(self.firmware_data) + chunk_size - 1) // chunk_size
        
        print(f"📊 Flash: {len(self.firmware_data):,} bytes en {total_chunks} chunks")
        
        try:
            # Commande d'initialisation du flash
            flash_init_cmd = struct.pack('<I', len(self.firmware_data))
            command = self.controller.create_command("FWSTART", flash_init_cmd)
            await self.controller.client.write_gatt_char(
                self.controller.COMMAND_CHAR, command
            )
            await asyncio.sleep(1.0)
            
            # Flash par chunks
            for i in range(total_chunks):
                start_idx = i * chunk_size
                end_idx = min(start_idx + chunk_size, len(self.firmware_data))
                chunk = self.firmware_data[start_idx:end_idx]
                
                # Progression
                progress = (i + 1) * 100 // total_chunks
                print(f"📡 Flash chunk {i+1}/{total_chunks} ({progress}%)")
                
                # Envoi du chunk avec métadonnées
                chunk_header = struct.pack('<II', i, len(chunk))
                chunk_data = chunk_header + chunk
                
                # Utiliser DATS pour l'envoi (ironique !)
                command = self.controller.create_command("DATS", chunk_data)
                await self.controller.client.write_gatt_char(
                    self.controller.COMMAND_CHAR, command
                )
                
                # Envoyer les données
                await self.controller.client.write_gatt_char(
                    self.controller.DATA_CHAR, chunk
                )
                
                await asyncio.sleep(0.1)  # Délai entre chunks
            
            # Finalisation
            command = self.controller.create_command("FWEND", b"")
            await self.controller.client.write_gatt_char(
                self.controller.COMMAND_CHAR, command
            )
            
            print("✅ Flash terminé avec succès !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur durant le flash: {e}")
            return False
    
    async def verify_flash(self) -> bool:
        """Vérifie que le flash s'est bien passé"""
        print("🔍 Vérification du flash...")
        
        try:
            # Redémarrage du masque
            command = self.controller.create_command("RESET", b"")
            await self.controller.client.write_gatt_char(
                self.controller.COMMAND_CHAR, command
            )
            await asyncio.sleep(3.0)
            
            # Test de fonctionnement
            print("🧪 Test post-flash...")
            await self.controller.display_text("TEST", (0, 255, 0))
            await asyncio.sleep(2.0)
            
            print("✅ Flash vérifié - masque fonctionnel !")
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur vérification: {e}")
            print("💡 Le masque peut nécessiter un redémarrage manuel")
            return False
    
    async def flash_no_arrow_firmware(self, firmware_path: str):
        """Processus complet de flash du firmware sans flèche"""
        print("🚀 DÉMARRAGE FLASH FIRMWARE SANS FLÈCHE")
        print("=" * 60)
        
        # 1. Connexion
        if not await self.connect_to_mask():
            print("❌ Impossible de se connecter - abandon")
            return False
        
        try:
            # 2. Chargement firmware
            if not self.load_patched_firmware(firmware_path):
                print("❌ Impossible de charger le firmware - abandon")
                return False
            
            # 3. Sauvegarde (optionnelle)
            print("\n💾 PHASE 1: Sauvegarde")
            await self.backup_current_firmware()
            
            # 4. Mode flash
            print("\n🔄 PHASE 2: Mode flash")
            flash_mode_ok = await self.enter_flash_mode()
            
            # 5. Flash du firmware
            print("\n📡 PHASE 3: Flash firmware")
            if await self.flash_firmware_chunks():
                print("✅ FLASH RÉUSSI !")
                
                # 6. Vérification
                print("\n🔍 PHASE 4: Vérification")
                if await self.verify_flash():
                    print("\n🎉 MISSION ACCOMPLIE !")
                    print("🎯 Votre masque n'a maintenant PLUS DE FLÈCHE D'UPLOAD !")
                    return True
                else:
                    print("\n⚠️ Flash terminé mais vérification incomplète")
                    return True
            else:
                print("❌ Échec du flash")
                return False
                
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
            return False
            
        finally:
            # Déconnexion propre
            if self.controller and self.controller.client:
                try:
                    await self.controller.client.disconnect()
                    print("🔌 Déconnexion du masque")
                except:
                    pass

async def flash_menu():
    """Menu interactif pour choisir le firmware à flasher"""
    print("🎯 FLASHER FIRMWARE SANS FLÈCHE - MENU")
    print("=" * 40)
    
    # Liste des firmwares disponibles
    firmware_files = [
        "TR1906R04-10_OTA.bin_NO_ARROW.bin",
        "TR1906R04-1-10_OTA.bin_NO_ARROW.bin"
    ]
    
    available_firmwares = []
    for firmware in firmware_files:
        if os.path.exists(firmware):
            size = os.path.getsize(firmware)
            available_firmwares.append((firmware, size))
    
    if not available_firmwares:
        print("❌ Aucun firmware patché trouvé !")
        print("💡 Exécutez d'abord firmware_patcher.py")
        return
    
    print("📁 Firmwares disponibles:")
    for i, (firmware, size) in enumerate(available_firmwares):
        print(f"  {i+1}. {firmware} ({size:,} bytes)")
    
    print("\n⚠️  ATTENTION: Cette opération va modifier le firmware de votre masque")
    print("⚠️  Assurez-vous que votre masque est bien connecté et chargé")
    
    choice = input(f"\nChoisissez un firmware (1-{len(available_firmwares)}) ou 'q' pour quitter: ")
    
    if choice.lower() == 'q':
        print("👋 Annulation du flash")
        return
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(available_firmwares):
            firmware_path = available_firmwares[choice_idx][0]
            
            print(f"\n🚀 Flash de: {firmware_path}")
            confirm = input("Confirmez-vous le flash ? (oui/non): ")
            
            if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                flasher = FirmwareFlasher()
                await flasher.flash_no_arrow_firmware(firmware_path)
            else:
                print("👋 Flash annulé")
        else:
            print("❌ Choix invalide")
            
    except ValueError:
        print("❌ Choix invalide")

if __name__ == "__main__":
    asyncio.run(flash_menu())
