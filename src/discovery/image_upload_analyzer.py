# Analyser le protocole d'upload d'images du masque LED

import asyncio
import time
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

MASK_ADDRESS = "86179C2D-07A2-AD8E-6D64-08E8BEB9B6CD"

# Toutes les caractéristiques writables découvertes
ALL_CHARACTERISTICS = [
    "d44bc439-abfd-45a2-b575-925416129600",  # Principale
    "d44bc439-abfd-45a2-b575-92541612960a",  # Variante A
    "d44bc439-abfd-45a2-b575-92541612960b",  # Variante B
    "0000fd01-0000-1000-8000-00805f9b34fb",  # Service FD
    "0000fd02-0000-1000-8000-00805f9b34fb",  # Service FD notify+write
    "0000ae01-0000-1000-8000-00805f9b34fb",  # Service AE
]

class MaskProtocolAnalyzer:
    def __init__(self):
        self.client = None
        self.notification_data = []
        
    async def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        """Capture toutes les notifications du masque"""
        timestamp = time.time()
        print(f"📨 NOTIFICATION [{timestamp:.3f}]")
        print(f"   Char: {characteristic.uuid}")
        print(f"   Data: {data.hex()} ({len(data)} bytes)")
        print(f"   ASCII: {self._safe_ascii(data)}")
        
        self.notification_data.append({
            'timestamp': timestamp,
            'characteristic': characteristic.uuid,
            'data': data.hex(),
            'length': len(data)
        })
    
    def _safe_ascii(self, data):
        """Convertir en ASCII si possible"""
        try:
            return ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
        except:
            return "non-printable"
    
    async def setup_notifications(self):
        """Activer les notifications sur toutes les caractéristiques possibles"""
        services = self.client.services
        
        for service in services:
            for char in service.characteristics:
                if "notify" in char.properties:
                    try:
                        await self.client.start_notify(char, self.notification_handler)
                        print(f"✅ Notifications activées sur: {char.uuid}")
                    except Exception as e:
                        print(f"❌ Impossible d'activer notifications sur {char.uuid}: {e}")
    
    async def test_image_upload_simulation(self):
        """Simuler différents protocoles d'upload d'images"""
        print("\n🧪 TEST DE SIMULATION D'UPLOAD D'IMAGES")
        print("="*50)
        
        # Protocoles potentiels d'upload
        test_protocols = [
            # Header + données simulées
            {
                "name": "Upload initiation",
                "char": "d44bc439-abfd-45a2-b575-925416129600",
                "data": bytes([0xAA, 0x55, 0x01, 0x00])  # Header possible
            },
            {
                "name": "Image header (64x64)",
                "char": "d44bc439-abfd-45a2-b575-925416129600", 
                "data": bytes([0x40, 0x40, 0x01, 0x00])  # 64x64, image 1
            },
            {
                "name": "Image data chunk",
                "char": "d44bc439-abfd-45a2-b575-925416129600",
                "data": bytes(range(20))  # Données simulées
            },
            {
                "name": "Upload complete",
                "char": "d44bc439-abfd-45a2-b575-925416129600",
                "data": bytes([0xFF, 0xFF, 0x01, 0x00])  # Fin d'upload
            },
            
            # Test sur autres caractéristiques
            {
                "name": "Test char A - Init",
                "char": "d44bc439-abfd-45a2-b575-92541612960a",
                "data": bytes([0xAA, 0x55, 0x01, 0x00])
            },
            {
                "name": "Test char B - Init", 
                "char": "d44bc439-abfd-45a2-b575-92541612960b",
                "data": bytes([0xAA, 0x55, 0x01, 0x00])
            },
            
            # Commandes de sélection d'image
            {
                "name": "Select image 1",
                "char": "d44bc439-abfd-45a2-b575-925416129600",
                "data": bytes([0x01])
            },
            {
                "name": "Select image 2", 
                "char": "d44bc439-abfd-45a2-b575-925416129600",
                "data": bytes([0x02])
            },
        ]
        
        for protocol in test_protocols:
            print(f"\n🔄 Test: {protocol['name']}")
            print(f"📡 Char: {protocol['char']}")
            print(f"📤 Data: {protocol['data'].hex()}")
            
            try:
                await self.client.write_gatt_char(protocol['char'], protocol['data'])
                print("✅ Envoyé avec succès")
                
                # Attendre les notifications
                await asyncio.sleep(2)
                
                # Demander observation
                response = input("👀 Effet visible sur le masque? (y/n/details): ").strip().lower()
                if response == 'y':
                    description = input("Décrivez l'effet: ")
                    print(f"🎉 EFFET DÉTECTÉ: {description}")
                elif response == 'details':
                    details = input("Détails observés: ")
                    print(f"📝 Noté: {details}")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
                if "disconnected" in str(e).lower():
                    print("💥 Déconnexion - ce protocole cause des problèmes")
                    break
    
    async def monitor_real_upload(self):
        """Monitorer une vraie session d'upload depuis l'app mobile"""
        print("\n📱 MONITORING D'UPLOAD RÉEL")
        print("="*50)
        print("Instructions:")
        print("1. Gardez ce script en cours d'exécution")
        print("2. Ouvrez votre app mobile")
        print("3. Uploadez une nouvelle image")
        print("4. Toutes les communications BLE seront capturées")
        print("\n⏱️ Monitoring en cours... (Ctrl+C pour arrêter)")
        
        try:
            # Monitoring continu
            start_time = time.time()
            while True:
                await asyncio.sleep(1)
                elapsed = time.time() - start_time
                
                if len(self.notification_data) > 0:
                    print(f"📊 [{elapsed:.0f}s] {len(self.notification_data)} notifications capturées")
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring arrêté par l'utilisateur")
            
            # Analyser les données capturées
            if self.notification_data:
                print(f"\n📋 ANALYSE DES DONNÉES CAPTURÉES")
                print("="*50)
                
                for i, notif in enumerate(self.notification_data):
                    print(f"[{i+1}] {notif['timestamp']:.3f}s")
                    print(f"    Char: {notif['characteristic']}")
                    print(f"    Data: {notif['data']} ({notif['length']} bytes)")
                
                # Sauvegarder les données
                with open('/Users/mathieu/my-python-project/captured_protocol.txt', 'w') as f:
                    f.write("# Protocole BLE capturé du masque LED\n")
                    f.write(f"# Capturé le: {time.ctime()}\n\n")
                    
                    for notif in self.notification_data:
                        f.write(f"Timestamp: {notif['timestamp']:.3f}\n")
                        f.write(f"Characteristic: {notif['characteristic']}\n")
                        f.write(f"Data: {notif['data']}\n")
                        f.write(f"Length: {notif['length']}\n")
                        f.write("-" * 40 + "\n")
                
                print("✅ Données sauvegardées dans captured_protocol.txt")
            else:
                print("❌ Aucune donnée capturée")

async def main():
    print("🔍 ANALYSEUR DE PROTOCOLE D'UPLOAD D'IMAGES")
    print("=" * 60)
    
    analyzer = MaskProtocolAnalyzer()
    
    try:
        async with BleakClient(MASK_ADDRESS) as client:
            analyzer.client = client
            print("🔗 Connecté au masque!")
            
            # Activer les notifications
            await analyzer.setup_notifications()
            
            print("\nChoisissez un mode:")
            print("1. Test de simulation d'upload")
            print("2. Monitoring d'upload réel depuis l'app mobile")
            
            choice = input("Votre choix (1/2): ").strip()
            
            if choice == "1":
                await analyzer.test_image_upload_simulation()
            elif choice == "2":
                await analyzer.monitor_real_upload()
            else:
                print("❌ Choix invalide")
                
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    asyncio.run(main())
