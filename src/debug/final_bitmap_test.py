"""
TEST FINAL - Diagnostic problème coupure en deux
Comparaison images prédéfinies vs texte personnalisé
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct
import sys
sys.path.append('/Users/mathieu/my-python-project/src/working')
from complete_text_display import MaskTextDisplay

async def test_images_vs_text():
    """Compare l'affichage d'images prédéfinies vs notre texte"""
    print("🆚 COMPARAISON IMAGES vs TEXTE")
    print("=" * 50)
    
    display = MaskTextDisplay()
    if not await display.connect():
        return
    
    try:
        print("\n--- Test 1: Image prédéfinie (fonctionne) ---")
        
        # Test avec une image prédéfinie qui fonctionne
        cmd = display.create_command("PLAY", bytes([1]))  # Image 1
        await display.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        print("✅ Image 1 affichée")
        await asyncio.sleep(3)
        
        print("\n--- Test 2: Notre texte (problématique) ---")
        
        # Notre texte qui pose problème
        await display.display_text("O")
        print("✅ Texte 'O' envoyé")
        await asyncio.sleep(3)
        
        print("\n--- Test 3: Autre image prédéfinie ---")
        
        # Une autre image
        cmd = display.create_command("PLAY", bytes([5]))  # Image 5
        await display.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
        print("✅ Image 5 affichée")
        await asyncio.sleep(3)
        
        print("\n--- Test 4: Texte simple ---")
        
        # Texte très simple
        await display.display_text("I")
        print("✅ Texte 'I' envoyé")
        
        print("\n🔍 Observation:")
        print("- Les images prédéfinies s'affichent-elles correctement ?")
        print("- Le texte s'affiche-t-il coupé en deux ?")
        print("- Y a-t-il une différence d'orientation ?")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if display.client:
            await display.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    print("🔬 DIAGNOSTIC COMPLET - COUPURE EN DEUX")
    await test_images_vs_text()

if __name__ == "__main__":
    asyncio.run(main())

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class FinalTextDisplay:
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
    
    async def set_display_mode(self, mode):
        """Définit le mode d'affichage (CRUCIAL!)"""
        # mode: 1=steady, 2=blink, 3=scroll left, 4=scroll right, 5=steady
        cmd = self.create_command("MODE", bytes([mode]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🎭 Mode d'affichage: {mode}")
    
    async def upload_and_display_bitmap(self, pattern_name, bitmap_data, color_data):
        """Upload bitmap + affichage avec mode"""
        print(f"\n🧪 TEST: {pattern_name}")
        print("=" * 40)
        
        total_len = len(bitmap_data) + len(color_data)
        
        print(f"📊 Bitmap: {len(bitmap_data)}B, Couleurs: {len(color_data)}B")
        
        # 1. UPLOAD BITMAP
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
        complete_data = bitmap_data + color_data
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
        
        # 2. DÉFINIR LE MODE D'AFFICHAGE (CRUCIAL!)
        print("🎭 Application du mode d'affichage...")
        await asyncio.sleep(0.5)  # Petit délai
        
        await self.set_display_mode(1)  # 1 = steady (affichage fixe)
        
        print(f"🎉 {pattern_name} devrait maintenant être VISIBLE !")
        return True
    
    async def test_different_patterns_with_mode(self):
        """Test différents patterns avec mode d'affichage"""
        
        # Test 1: Croix simple
        print("🧪 TEST 1: Croix simple")
        bitmap_data = struct.pack('<H', 0b0000010000000000)  # Pixel central
        color_data = bytes([255, 255, 255])  # Blanc
        
        success = await self.upload_and_display_bitmap("Pixel central", bitmap_data, color_data)
        if success:
            await asyncio.sleep(5)  # Observer
        
        # Test 2: Barre horizontale avec différents modes
        print("\n🧪 TEST 2: Barre horizontale + modes")
        bitmap_data = struct.pack('<H', 0b0000011100000000)  # 3 pixels horizontaux
        color_data = bytes([255, 0, 0])  # Rouge
        
        success = await self.upload_and_display_bitmap("Barre rouge", bitmap_data, color_data)
        if success:
            await asyncio.sleep(3)
            
            # Tester différents modes
            for mode, name in [(2, "Blink"), (3, "Scroll Left"), (4, "Scroll Right"), (1, "Steady")]:
                print(f"🎭 Mode {mode}: {name}")
                await self.set_display_mode(mode)
                await asyncio.sleep(3)
        
        # Test 3: Pattern plus complexe
        print("\n🧪 TEST 3: Pattern lettres")
        
        # Lettre "H" simple (5 colonnes)
        h_patterns = [
            0b0001111100000000,  # |
            0b0000100000000000,  # 
            0b0000100000000000,  # -
            0b0000100000000000,  # 
            0b0001111100000000   # |
        ]
        
        bitmap_data = bytearray()
        for pattern in h_patterns:
            bitmap_data.extend(struct.pack('<H', pattern))
        
        color_data = bytearray()
        for _ in range(5):
            color_data.extend([0, 255, 0])  # Vert
        
        success = await self.upload_and_display_bitmap("Lettre H verte", bytes(bitmap_data), bytes(color_data))
        if success:
            await asyncio.sleep(5)
        
        return True
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test final avec modes d'affichage"""
    print("🎯 TEST FINAL - BITMAP + MODE D'AFFICHAGE")
    print("Basé sur la découverte du repository mask-go")
    print("=" * 50)
    
    display = FinalTextDisplay()
    
    if await display.connect():
        try:
            await display.test_different_patterns_with_mode()
            print("\n🎉 Tests terminés - le bitmap devrait être visible !")
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
