"""
Test d'affichage avec commande PLAY après upload
Hypothèse : le masque a besoin d'une commande pour afficher le bitmap uploadé
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class TextDisplayWithPlay:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
    
    def create_command(self, cmd_ascii, args=b''):
        """Crée une commande AES cryptée"""
        cmd_bytes = cmd_ascii.encode('ascii')
        length = len(cmd_bytes) + len(args)
        command = length.to_bytes(1, 'big') + cmd_bytes + args
        
        if len(command) < 16:
            command += b'\x00' * (16 - len(command))
        
        return self.cipher.encrypt(command)
    
    def _notification_handler(self, sender, data):
        """Gestionnaire des notifications"""
        try:
            decrypted = self.cipher.decrypt(data)
            str_len = decrypted[0]
            if str_len > 0 and str_len < len(decrypted):
                response = decrypted[1:str_len+1].decode('ascii', errors='ignore')
                self.responses.append(response)
                self.notification_event.set()
                print(f"📨 {response}")
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
        
        print("✅ Connecté")
        return True
    
    async def wait_for_response(self, expected, timeout=5):
        """Attend une réponse spécifique"""
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
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
    
    async def upload_bitmap_and_trigger_display(self):
        """Upload bitmap puis test de différentes commandes d'affichage"""
        print("\n🧪 UPLOAD + COMMANDES D'AFFICHAGE")
        print("=" * 40)
        
        # Créer un bitmap visible : croix 3x3 au centre
        # On va créer plusieurs colonnes pour avoir quelque chose de visible
        bitmap_columns = []
        
        # Pattern croix simple 5 colonnes
        patterns = [
            0b0000100000000000,  # Colonne 1: pixel central
            0b0000100000000000,  # Colonne 2: pixel central  
            0b0001110000000000,  # Colonne 3: 3 pixels horizontaux
            0b0000100000000000,  # Colonne 4: pixel central
            0b0000100000000000   # Colonne 5: pixel central
        ]
        
        bitmap_data = bytearray()
        for pattern in patterns:
            bitmap_data.extend(struct.pack('<H', pattern))
        
        # Couleurs pour 5 colonnes
        color_data = bytearray()
        for _ in range(5):
            color_data.extend([255, 255, 255])  # Blanc brillant
        
        total_len = len(bitmap_data) + len(color_data)
        
        print(f"📊 Bitmap croix: {len(bitmap_data)}B, Couleurs: {len(color_data)}B")
        
        # 1. Upload standard
        self.responses.clear()
        
        # DATS
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', len(bitmap_data)))
        dats_cmd.extend([0])
        
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        print("📤 DATS...")
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATSOK"):
            print("❌ Pas de DATSOK")
            return False
        
        # Upload
        complete_data = bytes(bitmap_data) + bytes(color_data)
        packet = bytearray([len(complete_data) + 1, 0])
        packet.extend(complete_data)
        
        print("📤 Upload...")
        await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
        
        if not await self.wait_for_response("REOK"):
            print("❌ Pas de REOK")
            return False
        
        # DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        print("📤 DATCP...")
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATCPOK"):
            print("❌ Pas de DATCPOK")
            return False
        
        print("✅ Upload terminé")
        
        # 2. Tester différentes commandes pour déclencher l'affichage
        await asyncio.sleep(1)
        
        # Test PLAY 0 (peut-être que 0 = bitmap uploadé ?)
        print("🧪 Test PLAY 0...")
        cmd = self.create_command("PLAY", bytes([0]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        await asyncio.sleep(2)
        
        # Test autres commandes
        test_commands = [
            ("PLAY 255", "PLAY", [255]),
            ("PLAY 21", "PLAY", [21]),  # Au-delà des images prédéfinies
            ("PLAY 22", "PLAY", [22]),
            ("LIGHT 255", "LIGHT", [255])  # Luminosité max
        ]
        
        for desc, cmd_name, args in test_commands:
            print(f"🧪 Test {desc}...")
            cmd = self.create_command(cmd_name, bytes(args))
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            await asyncio.sleep(2)
        
        print("🏁 Tests terminés - est-ce que quelque chose s'affiche ?")
        return True
    
    async def test_different_bitmap_formats(self):
        """Test différents formats de bitmap"""
        print("\n🧪 TEST FORMATS BITMAP DIFFÉRENTS")
        print("=" * 40)
        
        # Format 1: Un seul pixel en haut à gauche
        print("📍 Test: pixel unique position 0")
        await self.upload_simple_pattern(0b0000000000000001, "Rouge", (255, 0, 0))
        
        # Format 2: Pixel au milieu
        print("📍 Test: pixel unique position 8") 
        await self.upload_simple_pattern(0b0000000100000000, "Vert", (0, 255, 0))
        
        # Format 3: Barre horizontale
        print("📍 Test: barre horizontale")
        await self.upload_simple_pattern(0b0000000011111111, "Bleu", (0, 0, 255))
        
        # Format 4: Barre verticale (plusieurs colonnes)
        print("📍 Test: barre verticale")
        bitmap_data = bytearray()
        for _ in range(8):  # 8 colonnes
            bitmap_data.extend(struct.pack('<H', 0b0000000000001000))  # Pixel au milieu
        
        color_data = bytearray()
        for _ in range(8):
            color_data.extend([255, 255, 0])  # Jaune
        
        await self.upload_custom_bitmap(bytes(bitmap_data), bytes(color_data), "Barre verticale jaune")
    
    async def upload_simple_pattern(self, pattern, name, color):
        """Upload un pattern simple (1 colonne)"""
        bitmap_data = struct.pack('<H', pattern)
        color_data = bytes(color)
        
        await self.upload_custom_bitmap(bitmap_data, color_data, name)
    
    async def upload_custom_bitmap(self, bitmap_data, color_data, description):
        """Upload un bitmap personnalisé"""
        total_len = len(bitmap_data) + len(color_data)
        
        print(f"  📤 {description}: {len(bitmap_data)}B bitmap, {len(color_data)}B couleurs")
        
        self.responses.clear()
        
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
                
                if await self.wait_for_response("DATCPOK", 3):
                    print(f"  ✅ {description} uploadé")
                    
                    # Test PLAY 0 après chaque upload
                    cmd = self.create_command("PLAY", bytes([0]))
                    await self.client.write_gatt_char(COMMAND_CHAR, cmd)
                    
                    await asyncio.sleep(3)  # Temps d'observation
                    return True
        
        print(f"  ❌ Échec {description}")
        return False
    
    async def run_tests(self):
        """Lance tous les tests"""
        await self.upload_bitmap_and_trigger_display()
        await self.test_different_bitmap_formats()
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test complet d'affichage"""
    print("🎯 TEST AFFICHAGE BITMAP AVEC PLAY")
    print("=" * 40)
    
    display = TextDisplayWithPlay()
    
    if await display.connect():
        try:
            await display.run_tests()
        except KeyboardInterrupt:
            print("\n⏹️ Test interrompu")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await display.disconnect()
    else:
        print("💡 Vérifiez que le masque est allumé")

if __name__ == "__main__":
    asyncio.run(main())
