"""
Script d'urgence pour réinitialiser le masque LED
À utiliser quand le masque ne répond plus
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"

async def emergency_reset():
    """Réinitialisation d'urgence du masque"""
    print("🚨 RÉINITIALISATION D'URGENCE")
    print("=" * 40)
    
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    
    # Connexion
    devices = await BleakScanner.discover()
    mask = None
    for device in devices:
        if "MASK" in (device.name or ""):
            mask = device
            break
    
    if not mask:
        print("❌ Masque non trouvé")
        return
    
    print(f"🔗 Connexion d'urgence à {mask.name}...")
    client = BleakClient(mask.address)
    
    try:
        await client.connect()
        print("✅ Connecté")
        
        # Commandes de réinitialisation
        reset_commands = [
            # Luminosité minimale
            b'\x06LIGHT\x00' + b'\x00' * 9,
            # Image 1 (sûre)
            b'\x06PLAY\x01\x01' + b';\x97\xf2\xf3U\xa9r\x13',
            # Arrêt
            b'\x05STOP\x00' + b'\x00' * 10
        ]
        
        for i, cmd in enumerate(reset_commands):
            print(f"📤 Envoi commande de reset {i+1}/3...")
            
            # Padding et cryptage
            if len(cmd) < 16:
                cmd += b'\x00' * (16 - len(cmd))
            
            encrypted = cipher.encrypt(cmd)
            await client.write_gatt_char(COMMAND_CHAR, encrypted)
            await asyncio.sleep(1)
        
        print("✅ Réinitialisation terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        await client.disconnect()
        print("🔌 Déconnecté")

if __name__ == "__main__":
    print("⚠️  Utilisez ce script seulement si le masque ne répond plus")
    input("Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler...")
    asyncio.run(emergency_reset())
