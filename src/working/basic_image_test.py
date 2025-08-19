"""
Test basique des images du masque LED
Script simple pour tester l'affichage d'images
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

async def basic_image_test():
    """Test basique des images"""
    print("📸 TEST BASIQUE DES IMAGES")
    print("=" * 30)
    
    # Initialisation AES
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    # Connexion
    print("🔍 Recherche du masque...")
    devices = await BleakScanner.discover()
    mask = None
    for device in devices:
        if "MASK" in (device.name or ""):
            mask = device
            break
    
    if not mask:
        print("❌ Masque non trouvé")
        return
    
    print(f"🔗 Connexion à {mask.name}...")
    client = BleakClient(mask.address)
    await client.connect()
    print("✅ Connecté")
    
    # Test images 1 à 10
    for image_id in range(1, 11):
        print(f"📸 Test image {image_id}")
        
        # Création de la commande
        base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b'
        if len(base_command) < 16:
            base_command += b'\x00' * (16 - len(base_command))
        
        encrypted_command = cipher.encrypt(base_command)
        
        # Envoi
        await client.write_gatt_char(COMMAND_CHAR, encrypted_command)
        await asyncio.sleep(1.5)
    
    print("🔌 Déconnexion...")
    await client.disconnect()
    print("✅ Test terminé")

if __name__ == "__main__":
    asyncio.run(basic_image_test())
