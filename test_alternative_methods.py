#!/usr/bin/env python3
"""
🔧 SOLUTIONS ALTERNATIVES - Contournement Flèche Firmware
=========================================================

Puisque la flèche semble être hardcodée dans le firmware du masque,
explorons différentes approches pour la contourner ou la masquer.
"""

import asyncio
import sys
import os
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class AlternativeUploadMethods:
    """Teste différentes méthodes pour éviter la flèche firmware"""
    
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
    
    def create_command(self, cmd_str, data=b''):
        """Crée une commande chiffrée"""
        cmd = bytearray()
        cmd.append(len(cmd_str) + len(data))
        cmd.extend(cmd_str.encode('ascii'))
        cmd.extend(data)
        
        while len(cmd) < 16:
            cmd.append(0)
        
        return self.cipher.encrypt(bytes(cmd))
    
    def _notification_handler(self, sender, data):
        """Gestionnaire des notifications"""
        try:
            response = data.decode('ascii', errors='ignore').strip('\x00')
            if response:
                print(f"📨 {response}")
                self.responses.append(response)
                self.notification_event.set()
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    async def connect(self):
        """Connexion au masque"""
        print("🔍 Recherche du masque...")
        devices = await BleakScanner.discover()
        
        mask = None
        for device in devices:
            if "MASK" in (device.name or ""):
                mask = device
                break
        
        if not mask:
            print("❌ Masque non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask.name}...")
        self.client = BleakClient(mask.address)
        await self.client.connect()
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        print("✅ Connecté!")
        return True
    
    async def wait_for_response(self, expected, timeout=5):
        """Attend une réponse spécifique"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            for i, response in enumerate(self.responses):
                if expected in response:
                    self.responses.pop(i)
                    return True
            
            try:
                await asyncio.wait_for(self.notification_event.wait(), timeout=0.5)
                self.notification_event.clear()
            except asyncio.TimeoutError:
                continue
        
        return False
    
    async def method_1_brightness_masking(self):
        """Méthode 1: Masquer avec luminosité nulle pendant upload"""
        print("\n🔧 MÉTHODE 1: Masquage par luminosité")
        print("Concept: Réduire luminosité à 0 pendant upload, puis restaurer")
        
        # Sauvegarder luminosité actuelle
        print("💡 Sauvegarde luminosité...")
        original_brightness = 150  # Valeur par défaut
        
        # Réduire à 0 avant upload
        print("🔇 Luminosité à 0 (masquage flèche)...")
        cmd = self.create_command("LIGHT", bytes([0]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await asyncio.sleep(0.5)
        
        # Upload normal avec flèche invisible
        print("📤 Upload avec flèche masquée...")
        await self._upload_sample_text("HI")
        
        # Restaurer luminosité
        print("💡 Restauration luminosité...")
        cmd = self.create_command("LIGHT", bytes([original_brightness]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        
        print("✅ Méthode 1 terminée")
        return True
    
    async def method_2_rapid_mode_switching(self):
        """Méthode 2: Commutation rapide de mode pour "masquer" la flèche"""
        print("\n🔧 MÉTHODE 2: Commutation rapide de mode")
        print("Concept: Changer rapidement de mode pour perturber l'affichage de la flèche")
        
        # Commutation rapide OFF/ON
        print("⚡ Commutation rapide OFF...")
        cmd = self.create_command("MODE", bytes([0]))  # Mode OFF
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await asyncio.sleep(0.1)
        
        # Upload pendant mode OFF
        print("📤 Upload en mode OFF...")
        await self._upload_sample_text("TEST")
        
        # Retour au mode normal
        print("⚡ Retour mode STEADY...")
        cmd = self.create_command("MODE", bytes([1]))  # Mode STEADY
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        
        print("✅ Méthode 2 terminée")
        return True
    
    async def method_3_ultra_fast_upload(self):
        """Méthode 3: Upload ultra-rapide pour minimiser la durée de la flèche"""
        print("\n🔧 MÉTHODE 3: Upload ultra-rapide")
        print("Concept: Upload si rapide que la flèche est à peine visible")
        
        # Préparer données à l'avance
        text = "FAST"
        bitmap_data, color_data = self._prepare_minimal_data(text)
        
        print("⚡ Upload ultra-rapide (pas de délais)...")
        
        # DATS immédiat
        total_len = len(bitmap_data) + len(color_data)
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', len(bitmap_data)))
        dats_cmd.extend([0])
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        # Envoi immédiat sans attendre DATSOK
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        # Upload immédiat (risqué mais rapide)
        complete_data = bitmap_data + color_data
        packet = bytearray([len(complete_data) + 1, 0])
        packet.extend(complete_data)
        await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
        
        # DATCP immédiat
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        print("✅ Méthode 3 terminée (upload ~100ms)")
        return True
    
    async def method_4_background_color_trick(self):
        """Méthode 4: Utiliser couleur de fond pour masquer la flèche"""
        print("\n🔧 MÉTHODE 4: Masquage par couleur de fond")
        print("Concept: Fond noir total pour rendre la flèche moins visible")
        
        # Configuration background noir intense
        print("🌑 Configuration fond noir total...")
        cmd = self.create_command("BG", bytes([1, 0, 0, 0]))  # Background noir activé
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await asyncio.sleep(0.3)
        
        # Upload avec fond noir
        print("📤 Upload avec fond noir...")
        await self._upload_sample_text("DARK")
        
        print("✅ Méthode 4 terminée")
        return True
    
    async def method_5_alternative_commands(self):
        """Méthode 5: Chercher des commandes alternatives à DATS"""
        print("\n🔧 MÉTHODE 5: Commandes alternatives")
        print("Concept: Tester si d'autres commandes permettent l'upload sans flèche")
        
        # Tester des variantes de DATS
        alternatives = [
            "UPLOAD",  # Upload direct?
            "SEND",    # Envoi?
            "DATA",    # Données?
            "WRITE",   # Écriture?
            "SET",     # Définir?
        ]
        
        for alt_cmd in alternatives:
            print(f"🧪 Test commande: {alt_cmd}")
            try:
                cmd = self.create_command(alt_cmd, bytes([0, 10]))  # Données test
                await self.client.write_gatt_char(COMMAND_CHAR, cmd)
                await asyncio.sleep(0.5)
                
                # Vérifier la réponse
                if self.responses:
                    print(f"📨 Réponse à {alt_cmd}: {self.responses[-1]}")
                else:
                    print(f"🔇 Pas de réponse à {alt_cmd}")
                    
            except Exception as e:
                print(f"❌ Erreur avec {alt_cmd}: {e}")
        
        print("✅ Méthode 5 terminée")
        return True
    
    def _prepare_minimal_data(self, text):
        """Prépare des données minimales pour test rapide"""
        # Bitmap minimal (8 colonnes pour 1 caractère)
        bitmap_data = b'\x00\x7E' * len(text)  # Pattern simple
        color_data = bytes([255, 255, 255] * len(text))  # Blanc
        return bitmap_data, color_data
    
    async def _upload_sample_text(self, text):
        """Upload de test avec données minimales"""
        bitmap_data, color_data = self._prepare_minimal_data(text)
        total_len = len(bitmap_data) + len(color_data)
        
        # DATS
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', len(bitmap_data)))
        dats_cmd.extend([0])
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if await self.wait_for_response("DATSOK", 3):
            # Upload
            complete_data = bitmap_data + color_data
            packet = bytearray([len(complete_data) + 1, 0])
            packet.extend(complete_data)
            await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
            
            if await self.wait_for_response("REOK", 3):
                # DATCP
                datcp_cmd = bytearray([5])
                datcp_cmd.extend(b"DATCP")
                while len(datcp_cmd) < 16:
                    datcp_cmd.append(0)
                encrypted = self.cipher.encrypt(bytes(datcp_cmd))
                await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
                
                await self.wait_for_response("DATCPOK", 3)
                return True
        
        return False
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def test_all_methods():
    """Test toutes les méthodes alternatives"""
    print("🧪 TEST DES MÉTHODES ALTERNATIVES ANTI-FLÈCHE")
    print("=" * 55)
    print("Objectif: Trouver une méthode pour contourner la flèche firmware")
    print()
    
    methods = AlternativeUploadMethods()
    
    if await methods.connect():
        try:
            print("👀 OBSERVEZ LE MASQUE pendant chaque méthode!")
            print("📝 Notez laquelle réduit ou élimine la flèche")
            print()
            
            # Test toutes les méthodes
            await methods.method_1_brightness_masking()
            await asyncio.sleep(2)
            
            await methods.method_2_rapid_mode_switching()
            await asyncio.sleep(2)
            
            await methods.method_3_ultra_fast_upload()
            await asyncio.sleep(2)
            
            await methods.method_4_background_color_trick()
            await asyncio.sleep(2)
            
            await methods.method_5_alternative_commands()
            
            print("\n🎯 ANALYSE FINALE:")
            print("Quelle méthode a le mieux masqué la flèche?")
            print("1. Luminosité nulle")
            print("2. Commutation rapide de mode")
            print("3. Upload ultra-rapide")
            print("4. Fond noir")
            print("5. Commandes alternatives")
            print()
            print("💡 La meilleure méthode peut être combinée")
            print("   avec votre système existant!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests arrêtés")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await methods.disconnect()
    else:
        print("❌ Impossible de se connecter au masque")

if __name__ == "__main__":
    asyncio.run(test_all_methods())
