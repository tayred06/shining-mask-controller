"""
Test ULTRA-SIMPLE pour afficher du texte
Utilise uniquement les fonctions qui marchent à 100%
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration testée et validée
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

async def connect_mask():
    """Connexion simple au masque"""
    print("🔍 Recherche du masque...")
    devices = await BleakScanner.discover()
    
    for device in devices:
        if "MASK" in (device.name or ""):
            print(f"🔗 Connexion à {device.name}...")
            client = BleakClient(device.address)
            await client.connect()
            print("✅ Connecté")
            return client
    
    print("❌ Masque non trouvé")
    return None

def create_image_command(image_id, cipher):
    """Commande image - 100% fiable"""
    base_command = b'\x06PLAY\x01' + image_id.to_bytes(1, 'big') + b';\x97\xf2\xf3U\xa9r\x13\x8b'
    if len(base_command) < 16:
        base_command += b'\x00' * (16 - len(base_command))
    return cipher.encrypt(base_command)

def create_brightness_command(brightness, cipher):
    """Commande luminosité - 100% fiable"""
    cmd = b'\x06LIGHT' + brightness.to_bytes(1, 'big') + b'\x00' * 9
    return cipher.encrypt(cmd)

async def simple_text_demo():
    """Demo ultra-simple"""
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    client = await connect_mask()
    
    if not client:
        return
    
    try:
        print("\n🎭 DEMO SIMPLE")
        print("=" * 20)
        
        # Test images (simule des lettres)
        print("📝 'HELLO' avec images:")
        
        # H=8, E=5, L=12, L=12, O=15
        letters = [8, 5, 12, 12, 15]
        letter_names = ['H', 'E', 'L', 'L', 'O']
        
        for img, letter in zip(letters, letter_names):
            print(f"  Affichage '{letter}' (image {img})")
            cmd = create_image_command(img, cipher)
            await client.write_gatt_char(COMMAND_CHAR, cmd)
            await asyncio.sleep(1.5)
        
        print("\n💡 Test luminosité:")
        for brightness in [50, 150, 255]:
            print(f"  Luminosité {brightness}")
            cmd = create_brightness_command(brightness, cipher)
            await client.write_gatt_char(COMMAND_CHAR, cmd)
            await asyncio.sleep(1)
        
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        await client.disconnect()
        print("🔌 Déconnecté")

if __name__ == "__main__":
    print("📝 TEST ULTRA-SIMPLE")
    print("Affichage texte avec images prédéfinies")
    asyncio.run(simple_text_demo())
