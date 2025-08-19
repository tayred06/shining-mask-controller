"""
Découverte systématique des codes du masque LED
Teste méthodiquement toutes les combinaisons possibles
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import itertools
import time

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class SystematicDiscovery:
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.results = []
        self.test_count = 0
    
    def _notification_handler(self, sender, data):
        """Capture les notifications"""
        try:
            decrypted = self.cipher.decrypt(data)
            self.results.append({
                'test_id': self.test_count,
                'timestamp': time.time(),
                'raw_response': data.hex(),
                'decrypted': decrypted.hex(),
                'ascii': decrypted.rstrip(b'\x00').decode('ascii', errors='ignore')
            })
            print(f"📨 Réponse capturée pour test #{self.test_count}")
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    async def connect(self):
        """Connexion avec surveillance"""
        devices = await BleakScanner.discover()
        mask = None
        for device in devices:
            if "MASK" in (device.name or ""):
                mask = device
                break
        
        if not mask:
            print("❌ Masque non trouvé")
            return False
        
        self.client = BleakClient(mask.address)
        await self.client.connect()
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        print("✅ Connexion établie avec surveillance")
        return True
    
    async def test_single_command(self, command_bytes, description=""):
        """Teste une commande unique"""
        self.test_count += 1
        
        try:
            # Padding et cryptage
            if len(command_bytes) < 16:
                command_bytes += b'\x00' * (16 - len(command_bytes))
            
            encrypted = self.cipher.encrypt(command_bytes)
            
            print(f"🧪 Test #{self.test_count}: {description}")
            print(f"   Commande: {command_bytes.hex()}")
            
            # Envoi et attente
            await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
            await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur test #{self.test_count}: {e}")
            return False
    
    async def discover_ascii_commands(self):
        """Découverte des commandes ASCII"""
        print("\n🔤 DÉCOUVERTE COMMANDES ASCII")
        print("=" * 40)
        
        # Commandes ASCII potentielles
        ascii_commands = [
            "PLAY", "STOP", "PAUSE", "RESET", "CLEAR",
            "LIGHT", "BRIGHT", "DIM", "ON", "OFF",
            "COLOR", "RED", "GREEN", "BLUE", "WHITE",
            "SPEED", "FAST", "SLOW", "MODE", "DEMO",
            "TEST", "INFO", "STATUS", "GET", "SET",
            "ANIM", "FLASH", "FADE", "PULSE", "WAVE",
            "UP", "DOWN", "LEFT", "RIGHT", "CENTER",
            "START", "END", "NEXT", "PREV", "LOOP"
        ]
        
        for cmd in ascii_commands:
            # Test basique
            cmd_bytes = cmd.encode('ascii')
            length = len(cmd_bytes)
            command = length.to_bytes(1, 'big') + cmd_bytes
            
            await self.test_single_command(command, f"ASCII: {cmd}")
            
            # Test avec argument simple
            command_with_arg = length.to_bytes(1, 'big') + cmd_bytes + b'\x01'
            await self.test_single_command(command_with_arg, f"ASCII: {cmd} + arg")
    
    async def discover_numeric_patterns(self):
        """Découverte des motifs numériques"""
        print("\n🔢 DÉCOUVERTE MOTIFS NUMÉRIQUES")
        print("=" * 40)
        
        # Motifs de longueur + données
        for length in [1, 2, 3, 4, 5, 6]:
            for value in [0, 1, 2, 5, 10, 50, 100, 255]:
                if length == 1:
                    command = b'\x01' + value.to_bytes(1, 'big')
                elif length == 2:
                    command = b'\x02' + value.to_bytes(1, 'big') + b'\x00'
                else:
                    command = length.to_bytes(1, 'big') + (b'\x00' * (length - 1)) + value.to_bytes(1, 'big')
                
                await self.test_single_command(command, f"Len={length}, Val={value}")
    
    async def discover_special_patterns(self):
        """Découverte de motifs spéciaux"""
        print("\n✨ DÉCOUVERTE MOTIFS SPÉCIAUX")
        print("=" * 40)
        
        special_patterns = [
            # Motifs de reset
            b'\x00\x00\x00\x00',
            b'\xff\xff\xff\xff',
            
            # Motifs alternés
            b'\x55\xaa\x55\xaa',
            b'\xaa\x55\xaa\x55',
            
            # Motifs incrémentaux
            b'\x01\x02\x03\x04',
            b'\x10\x20\x30\x40',
            
            # Motifs de masque connus
            b'\x06PLAY\x01',
            b'\x06LIGHT\x80',
            b'\x05STOP\x00',
            
            # Variations du motif PLAY
            b'\x06PLAY\x02',
            b'\x06PLAY\x05',
            b'\x06PLAY\x0a',
            
            # Variations LIGHT
            b'\x06LIGHT\x00',
            b'\x06LIGHT\xff',
            b'\x06LIGHT\x7f'
        ]
        
        for pattern in special_patterns:
            await self.test_single_command(pattern, f"Spécial: {pattern.hex()}")
    
    async def discover_color_commands(self):
        """Découverte des commandes de couleur"""
        print("\n🎨 DÉCOUVERTE COMMANDES COULEUR")
        print("=" * 40)
        
        # Test commande FC (couleur) avec différentes valeurs RGB
        colors = [
            (255, 0, 0),    # Rouge
            (0, 255, 0),    # Vert
            (0, 0, 255),    # Bleu
            (255, 255, 0),  # Jaune
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 255, 255) # Blanc
        ]
        
        for r, g, b in colors:
            # Commande FC standard
            command = b'\x05FC\x00' + r.to_bytes(1, 'big') + g.to_bytes(1, 'big') + b.to_bytes(1, 'big')
            await self.test_single_command(command, f"Couleur RGB({r},{g},{b})")
            
            # Test autres formats de couleur
            command2 = b'\x04RGB' + r.to_bytes(1, 'big') + g.to_bytes(1, 'big') + b.to_bytes(1, 'big')
            await self.test_single_command(command2, f"RGB alt({r},{g},{b})")
    
    async def full_systematic_scan(self):
        """Scan systématique complet"""
        print("\n🔬 SCAN SYSTÉMATIQUE COMPLET")
        print("⚠️  Ceci peut prendre du temps...")
        
        # Test tous les premiers bytes possibles (longueur)
        for length in range(1, 16):
            print(f"\n📏 Test longueur {length}...")
            
            # Test avec différents patterns
            patterns = [
                b'\x00' * length,           # Tous zéros
                b'\xff' * length,           # Tous 1
                bytes(range(length)),       # Incrémental
                bytes(range(length, 0, -1)) # Décrémental
            ]
            
            for pattern in patterns:
                command = length.to_bytes(1, 'big') + pattern
                await self.test_single_command(command, f"Len={length}, Pattern={pattern.hex()}")
                
                # Limite pour éviter de bloquer le masque
                if self.test_count % 50 == 0:
                    print(f"⏸️  Pause après {self.test_count} tests...")
                    await asyncio.sleep(2)
    
    def generate_report(self):
        """Génère un rapport des découvertes"""
        print(f"\n📊 RAPPORT DE DÉCOUVERTE")
        print("=" * 50)
        print(f"Tests effectués: {self.test_count}")
        print(f"Réponses capturées: {len(self.results)}")
        
        if self.results:
            print("\n📨 RÉPONSES DÉTECTÉES:")
            for result in self.results:
                print(f"\nTest #{result['test_id']}:")
                print(f"  Raw: {result['raw_response']}")
                print(f"  Décrypté: {result['decrypted']}")
                if result['ascii']:
                    print(f"  ASCII: {result['ascii']}")
        else:
            print("\n❌ Aucune réponse détectée")
        
        # Sauvegarde des résultats
        return self.results
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Découverte systématique complète"""
    discovery = SystematicDiscovery()
    
    if await discovery.connect():
        try:
            # Découverte progressive
            await discovery.discover_ascii_commands()
            await discovery.discover_color_commands()
            await discovery.discover_special_patterns()
            await discovery.discover_numeric_patterns()
            
            # Scan complet (optionnel)
            response = input("\n🤔 Effectuer le scan complet ? (peut être long) [y/N]: ")
            if response.lower() == 'y':
                await discovery.full_systematic_scan()
            
            # Rapport
            results = discovery.generate_report()
            
        except KeyboardInterrupt:
            print("\n⏹️ Découverte interrompue")
            discovery.generate_report()
        finally:
            await discovery.disconnect()

if __name__ == "__main__":
    print("🔬 DÉCOUVERTE SYSTÉMATIQUE")
    print("Exploration complète du protocole")
    asyncio.run(main())
