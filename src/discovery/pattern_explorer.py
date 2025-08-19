"""
Explorateur de motifs pour découvrir de nouveaux codes
Teste différentes combinaisons de commandes
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import itertools

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class PatternExplorer:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.discovered_patterns = []
    
    def _notification_handler(self, sender, data):
        """Gestionnaire de notifications"""
        try:
            decrypted = self.cipher.decrypt(data)
            hex_data = decrypted.hex()
            ascii_part = decrypted.rstrip(b'\x00').decode('ascii', errors='ignore')
            
            print(f"📨 Notification: {hex_data}")
            if ascii_part:
                print(f"📝 ASCII: {ascii_part}")
                
            self.discovered_patterns.append({
                'hex': hex_data,
                'ascii': ascii_part,
                'raw': decrypted
            })
        except Exception as e:
            print(f"❌ Erreur déchiffrement: {e}")
            print(f"📨 Brut: {data.hex()}")
    
    async def connect(self):
        """Connexion avec notifications"""
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
        
        # Activer les notifications
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        print("✅ Connecté avec notifications")
        return True
    
    async def test_command_pattern(self, cmd_ascii, args_list):
        """Teste un motif de commande avec différents arguments"""
        print(f"\n🧪 Test commande: {cmd_ascii}")
        
        for args in args_list:
            try:
                # Création de la commande
                cmd_bytes = cmd_ascii.encode('ascii')
                if isinstance(args, int):
                    args_bytes = args.to_bytes(1, 'big')
                elif isinstance(args, bytes):
                    args_bytes = args
                else:
                    args_bytes = b''
                
                length = len(cmd_bytes) + len(args_bytes)
                command = length.to_bytes(1, 'big') + cmd_bytes + args_bytes
                
                # Padding
                if len(command) < 16:
                    command += b'\x00' * (16 - len(command))
                
                encrypted = self.cipher.encrypt(command)
                
                print(f"📤 Test {cmd_ascii} avec args {args}")
                print(f"   Commande: {command.hex()}")
                
                await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    async def discover_new_commands(self):
        """Découverte de nouvelles commandes"""
        print("\n🔍 DÉCOUVERTE DE NOUVEAUX MOTIFS")
        print("=" * 40)
        
        # Commandes connues à tester
        known_commands = [
            "PLAY", "STOP", "PAUSE", "LIGHT", "COLOR", 
            "SPEED", "MODE", "BRIGHT", "RESET", "TEST"
        ]
        
        # Commandes hypothétiques
        hypothetical_commands = [
            "ANIM", "FLASH", "FADE", "PULSE", "WAVE",
            "SHIFT", "TURN", "SPIN", "ZOOM", "MOVE"
        ]
        
        all_commands = known_commands + hypothetical_commands
        
        for cmd in all_commands:
            print(f"\n🧪 Test de '{cmd}'...")
            
            # Test avec différents arguments
            test_args = [
                0, 1, 2, 5, 10, 50, 100, 255,
                b'\x00', b'\x01', b'\xff',
                b'\x00\x00', b'\x01\x02'
            ]
            
            await self.test_command_pattern(cmd, test_args[:3])  # Limite pour éviter de bloquer
            
            if len(self.discovered_patterns) > 0:
                print(f"✅ Réponse détectée pour {cmd}!")
    
    async def explore_byte_patterns(self):
        """Exploration de motifs de bytes bruts"""
        print("\n🔬 EXPLORATION DE MOTIFS BYTES")
        print("=" * 40)
        
        # Motifs intéressants à tester
        patterns = [
            # Motifs de longueur
            b'\x01A\x00',
            b'\x02AB\x00',
            b'\x03ABC\x00',
            
            # Motifs numériques
            b'\x04TEST',
            b'\x05HELLO',
            b'\x06WORLD!',
            
            # Motifs hex intéressants
            b'\x00\x00\x00\x00',
            b'\xff\xff\xff\xff',
            b'\x55\xaa\x55\xaa',
            b'\x01\x23\x45\x67'
        ]
        
        for pattern in patterns:
            try:
                # Padding
                command = pattern
                if len(command) < 16:
                    command += b'\x00' * (16 - len(command))
                
                encrypted = self.cipher.encrypt(command)
                
                print(f"📤 Test motif: {pattern.hex()}")
                await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
                await asyncio.sleep(0.8)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    async def test_known_working_patterns(self):
        """Teste les motifs qui fonctionnent déjà"""
        print("\n✅ TEST DES MOTIFS CONNUS")
        print("=" * 30)
        
        # Pattern PLAY pour image 1
        play_pattern = b'\x06PLAY\x01\x01;\x97\xf2\xf3U\xa9r\x13'
        if len(play_pattern) < 16:
            play_pattern += b'\x00' * (16 - len(play_pattern))
        
        encrypted = self.cipher.encrypt(play_pattern)
        print("📤 Test PLAY pattern (image 1)")
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        await asyncio.sleep(2)
        
        # Pattern LIGHT
        light_pattern = b'\x06LIGHT\x80' + b'\x00' * 9
        encrypted = self.cipher.encrypt(light_pattern)
        print("📤 Test LIGHT pattern (luminosité 128)")
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        await asyncio.sleep(2)
    
    def print_discoveries(self):
        """Affiche les découvertes"""
        print(f"\n📋 DÉCOUVERTES ({len(self.discovered_patterns)} notifications)")
        print("=" * 50)
        
        for i, pattern in enumerate(self.discovered_patterns):
            print(f"\n{i+1}. Hex: {pattern['hex']}")
            if pattern['ascii']:
                print(f"   ASCII: {pattern['ascii']}")
            print(f"   Raw: {pattern['raw']}")
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Main exploration"""
    explorer = PatternExplorer()
    
    if await explorer.connect():
        try:
            # Test des patterns connus d'abord
            await explorer.test_known_working_patterns()
            
            # Découverte de nouveaux motifs
            await explorer.discover_new_commands()
            
            # Exploration de bytes
            await explorer.explore_byte_patterns()
            
            # Résultats
            explorer.print_discoveries()
            
        except KeyboardInterrupt:
            print("\n⏹️ Exploration interrompue")
        finally:
            await explorer.disconnect()

if __name__ == "__main__":
    print("🔍 EXPLORATEUR DE MOTIFS")
    print("Découverte de nouveaux protocoles")
    asyncio.run(main())
