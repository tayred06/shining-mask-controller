"""
Vérificateur d'état du masque LED
Diagnostic des connexions et de l'état du masque
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

async def check_mask_state():
    """Vérifie l'état du masque"""
    print("🔍 VÉRIFICATION DE L'ÉTAT DU MASQUE")
    print("=" * 40)
    
    # Recherche de périphériques
    print("📡 Scan des périphériques BLE...")
    devices = await BleakScanner.discover()
    
    mask_devices = []
    for device in devices:
        if "MASK" in (device.name or ""):
            mask_devices.append(device)
    
    if not mask_devices:
        print("❌ Aucun masque trouvé")
        print("💡 Vérifiez que le masque est allumé et en mode appairage")
        return
    
    print(f"✅ {len(mask_devices)} masque(s) trouvé(s):")
    for i, mask in enumerate(mask_devices):
        print(f"  {i+1}. {mask.name} - {mask.address} (RSSI: {mask.rssi})")
    
    # Test de connexion
    mask = mask_devices[0]
    print(f"\n🔗 Test de connexion avec {mask.name}...")
    
    try:
        client = BleakClient(mask.address)
        await client.connect()
        print("✅ Connexion réussie")
        
        # Vérification des services
        print("\n📋 Services disponibles:")
        services = await client.get_services()
        for service in services:
            print(f"  Service: {service.uuid}")
            for char in service.characteristics:
                print(f"    Caractéristique: {char.uuid}")
                if "read" in char.properties:
                    print("      - Lecture supportée")
                if "write" in char.properties:
                    print("      - Écriture supportée")
                if "notify" in char.properties:
                    print("      - Notifications supportées")
        
        # Test de commande simple
        print("\n🧪 Test de commande simple...")
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        
        # Commande LIGHT avec luminosité 100
        cmd = b'\x06LIGHT\x64' + b'\x00' * 9
        encrypted = cipher.encrypt(cmd)
        
        await client.write_gatt_char(COMMAND_CHAR, encrypted)
        print("✅ Commande envoyée avec succès")
        
        await client.disconnect()
        print("🔌 Déconnexion réussie")
        
        print("\n✅ DIAGNOSTIC COMPLET")
        print("Le masque fonctionne correctement")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        print("\n🔧 Suggestions:")
        print("- Redémarrez le masque")
        print("- Vérifiez la distance (restez proche)")
        print("- Redémarrez le Bluetooth")

if __name__ == "__main__":
    asyncio.run(check_mask_state())
