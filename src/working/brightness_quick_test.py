"""
Test rapide de la nouvelle fonctionnalité de luminosité
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

async def brightness_quick_test():
    print("🔆 TEST RAPIDE DE LUMINOSITÉ")
    print("=" * 40)
    
    # Connexion
    devices = await BleakScanner.discover()
    mask = None
    for device in devices:
        if device.name and "MASK" in device.name:
            mask = device
            break
    
    if not mask:
        print("❌ Masque non trouvé")
        return
    
    print(f"✅ Connexion à {mask.name}...")
    
    async with BleakClient(mask.address) as client:
        print("🔗 Connecté !")
        
        # Créateur de commandes
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        
        def create_command(cmd_ascii, args=b''):
            cmd_bytes = cmd_ascii.encode('ascii')
            length = len(cmd_bytes) + len(args)
            command = length.to_bytes(1, 'big') + cmd_bytes + args
            if len(command) < 16:
                command += b'\x00' * (16 - len(command))
            return cipher.encrypt(command)
        
        # Test des niveaux de luminosité
        levels = [10, 50, 100]
        
        for level in levels:
            print(f"\n🔆 Luminosité {level}")
            
            # Commande LIGHT
            light_cmd = create_command("LIGHT", bytes([level]))
            await client.write_gatt_char(COMMAND_CHAR, light_cmd)
            await asyncio.sleep(0.3)
            
            # Afficher image 1
            data_cmd = create_command("DATA", b'\x01')
            await client.write_gatt_char(COMMAND_CHAR, data_cmd)
            await asyncio.sleep(2)
        
        print("\n✅ Test terminé ! La luminosité change-t-elle ?")

if __name__ == "__main__":
    asyncio.run(brightness_quick_test())
