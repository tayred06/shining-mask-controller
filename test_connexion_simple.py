#!/usr/bin/env python3
"""Test de connexion simple au masque.
- Scan BLE
- Connexion
- Réception des premières notifications
- Envoi d'une commande LIGHT (basse puis normale)
Usage: python test_connexion_simple.py [NOM_PARTIEL]
"""
import asyncio
import sys
from src.working.complete_text_display import MaskTextDisplay, COMMAND_CHAR

async def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'MASK'
    m = MaskTextDisplay()
    print(f"🔍 Scan pour périphérique contenant: {target}")
    if not await m.connect():
        return
    # Vérifier nom
    dev_name = 'inconnu'
    try:
        dev_name = m.client._device.name  # type: ignore
    except Exception:
        pass
    print(f"✅ Connecté à: {dev_name}")
    # Envoyer deux commandes LIGHT pour valider chiffrement
    try:
        low = m.create_command('LIGHT', bytes([5]))
        high = m.create_command('LIGHT', bytes([120]))
        await m.client.write_gatt_char(COMMAND_CHAR, low)
        print("📤 LIGHT 5")
        await asyncio.sleep(0.4)
        await m.client.write_gatt_char(COMMAND_CHAR, high)
        print("📤 LIGHT 120")
        await asyncio.sleep(0.6)
    except Exception as e:
        print(f"⚠️ Erreur envoi LIGHT: {e}")
    # Déconnexion
    try:
        await m.client.disconnect()
        print("🔌 Déconnecté")
    except Exception:
        pass

if __name__ == '__main__':
    asyncio.run(main())
