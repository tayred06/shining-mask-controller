"""
Diagnostic et test de l'affichage de texte
Vérifie pourquoi le texte ne s'affiche pas malgré le protocole fonctionnel
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

class TextDisplayDiagnostic:
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
    
    async def test_basic_commands(self):
        """Test des commandes de base pour vérifier que le masque fonctionne"""
        print("\n🧪 TEST DES COMMANDES DE BASE")
        print("=" * 35)
        
        # Test luminosité
        cmd = self.create_command("LIGHT", bytes([150]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print("💡 Luminosité 150 envoyée")
        await asyncio.sleep(1)
        
        # Test image prédéfinie
        cmd = self.create_command("PLAY", bytes([5]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print("🖼️ Image 5 envoyée")
        await asyncio.sleep(2)
        
        # Test couleur
        cmd = self.create_command("FC", bytes([255, 0, 0]))  # Rouge
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print("🔴 Couleur rouge envoyée")
        await asyncio.sleep(2)
        
        return True
    
    async def test_minimal_bitmap_upload(self):
        """Test d'upload bitmap minimal pour diagnostiquer"""
        print("\n🧪 TEST BITMAP MINIMAL")
        print("=" * 25)
        
        # Créer un bitmap très simple : juste un pixel allumé
        # 1 colonne, 16 pixels, seul le premier pixel allumé
        bitmap_data = struct.pack('<H', 1)  # 1 pixel allumé en position 0
        color_data = bytes([255, 0, 0])     # Rouge
        
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        print(f"📊 Bitmap minimal: {bitmap_len}B, Couleurs: {len(color_data)}B")
        
        # DATS
        self.responses.clear()
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        print("📤 Envoi DATS...")
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATSOK"):
            print("❌ Pas de DATSOK")
            return False
        
        # Upload en un seul chunk
        complete_data = bitmap_data + color_data
        packet = bytearray([len(complete_data) + 1, 0])
        packet.extend(complete_data)
        
        print("📤 Upload chunk unique...")
        await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
        
        if not await self.wait_for_response("REOK"):
            print("❌ Pas de REOK")
            return False
        
        # DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        print("📤 Envoi DATCP...")
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATCPOK"):
            print("❌ Pas de DATCPOK")
            return False
        
        print("✅ Upload bitmap minimal terminé")
        print("👀 Vérifiez si un pixel rouge apparaît sur le masque")
        return True
    
    async def test_alternative_approach(self):
        """Test d'une approche alternative"""
        print("\n🧪 TEST APPROCHE ALTERNATIVE")
        print("=" * 32)
        
        # Essayer avec des couleurs différentes pour voir si c'est un problème de visibilité
        colors = [
            (255, 255, 255, "Blanc"),
            (255, 0, 0, "Rouge"),
            (0, 255, 0, "Vert"),
            (0, 0, 255, "Bleu"),
            (255, 255, 0, "Jaune")
        ]
        
        for r, g, b, name in colors:
            print(f"🎨 Test couleur {name} ({r},{g},{b})")
            
            # Créer un bitmap simple : une barre verticale
            bitmap_data = struct.pack('<H', 0xFFFF)  # Tous les pixels allumés sur une colonne
            color_data = bytes([r, g, b])
            
            total_len = len(bitmap_data) + len(color_data)
            
            # DATS
            self.responses.clear()
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
                        print(f"✅ {name} uploadé - regardez le masque!")
                        await asyncio.sleep(3)  # Temps pour observer
                    else:
                        print(f"❌ {name} - pas de DATCPOK")
                else:
                    print(f"❌ {name} - pas de REOK")
            else:
                print(f"❌ {name} - pas de DATSOK")
    
    async def run_full_diagnostic(self):
        """Diagnostic complet"""
        print("🔍 DIAGNOSTIC AFFICHAGE TEXTE")
        print("=" * 35)
        
        # 1. Tester les commandes de base
        await self.test_basic_commands()
        
        print("\n⏸️ Les commandes de base fonctionnent-elles ? (images, couleurs)")
        await asyncio.sleep(3)
        
        # 2. Tester un bitmap minimal
        await self.test_minimal_bitmap_upload()
        
        print("\n⏸️ Un pixel apparaît-il ?")
        await asyncio.sleep(3)
        
        # 3. Tester différentes couleurs
        await self.test_alternative_approach()
        
        print("\n🏁 Diagnostic terminé")
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Lance le diagnostic"""
    print("🩺 DIAGNOSTIC MASQUE LED")
    print("=" * 25)
    
    diagnostic = TextDisplayDiagnostic()
    
    if await diagnostic.connect():
        try:
            await diagnostic.run_full_diagnostic()
        except KeyboardInterrupt:
            print("\n⏹️ Diagnostic interrompu")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await diagnostic.disconnect()
    else:
        print("💡 Vérifiez que le masque est allumé")

if __name__ == "__main__":
    asyncio.run(main())
