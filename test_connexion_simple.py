#!/usr/bin/env python3
"""Test de connexion simple / diagnostic BLE.

Fonctions:
- Multi-scan (plusieurs passes) avec affichage de tous les périphériques
- Filtrage par fragment de nom ou adresse (insensible à la casse)
- Tentatives de connexion répétées (retry)
- Envoi de deux commandes LIGHT si connexion OK

Usage:
  python test_connexion_simple.py              # cherche 'MASK'
  python test_connexion_simple.py --match MASK-3B9D
  python test_connexion_simple.py --address XX:XX:XX:XX:XX:XX
Options utiles:
  --scans 5   (nombre de passes scan)
  --timeout 4 (durée de chaque scan en secondes)
  --retry 2   (retries connexion)
"""
import asyncio
import argparse
from bleak import BleakScanner, BleakClient
from src.working.complete_text_display import MaskTextDisplay, COMMAND_CHAR


def _norm(s: str) -> str:
    return (s or "").strip().lower()


async def pick_device(args):
    target_fragment = _norm(args.match) if args.match else None
    target_addr = _norm(args.address) if args.address else None
    print(f"🔍 Démarrage multi-scan: scans={args.scans} timeout={args.timeout}s")
    chosen = None
    seen = {}
    for i in range(1, args.scans + 1):
        print(f"--- Scan {i}/{args.scans} ---")
        devices = await BleakScanner.discover(timeout=args.timeout)
        if not devices:
            print("(Aucun périphérique trouvé cette passe)")
        for d in devices:
            key = (d.address, d.name)
            if key in seen:
                continue
            seen[key] = True
            print(f" • {d.address}  RSSI={getattr(d,'rssi','?'):>4}  Name={d.name}")
            name_n = _norm(d.name or "")
            addr_n = _norm(d.address or "")
            cond_match = True
            if target_fragment:
                cond_match &= target_fragment in name_n
            if target_addr:
                cond_match &= addr_n == target_addr
            if cond_match and not chosen:
                chosen = d
        if chosen:
            print("➡️  Candidat sélectionné")
            break
        await asyncio.sleep(0.7)
    if not chosen:
        print("❌ Aucun périphérique ne correspond au filtre.")
    return chosen


async def connect_and_test(dev, args):
    print(f"🔗 Connexion à {dev.name} ({dev.address}) …")
    client = BleakClient(dev.address)
    await client.connect()
    print("✅ Connecté (niveau bas)")
    # Utiliser MaskTextDisplay juste pour create_command (clé + cipher)
    m = MaskTextDisplay()
    m.client = client
    try:
        await client.start_notify(m.NOTIFY_CHAR if hasattr(m,'NOTIFY_CHAR') else 'd44bc439-abfd-45a2-b575-925416129601', m._notification_handler)
    except Exception:
        # fallback silencieux
        pass
    try:
        low = m.create_command('LIGHT', bytes([5]))
        high = m.create_command('LIGHT', bytes([120]))
        await client.write_gatt_char(COMMAND_CHAR, low)
        print("📤 LIGHT 5")
        await asyncio.sleep(0.5)
        await client.write_gatt_char(COMMAND_CHAR, high)
        print("📤 LIGHT 120")
        await asyncio.sleep(0.6)
        print("🎯 Test commandes terminé (pas d'erreur = OK)")
    finally:
        await client.disconnect()
        print("🔌 Déconnecté")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', help='Fragment de nom (ex: MASK, MASK-3B9D)')
    parser.add_argument('--address', help='Adresse exacte XX:XX:XX:XX:XX:XX')
    parser.add_argument('--scans', type=int, default=4, help='Nombre de passes scan')
    parser.add_argument('--timeout', type=float, default=3.5, help='Durée de chaque scan')
    parser.add_argument('--retry', type=int, default=1, help='Tentatives de reconnexion')
    args = parser.parse_args()
    if not args.match and not args.address:
        args.match = 'MASK'
    dev = await pick_device(args)
    if not dev:
        print("ℹ️ Astuces: \n - Vérifie que le masque n'est pas déjà connecté au téléphone\n - Coupe le Bluetooth du téléphone\n - Rapproche la Pi (<1m)\n - Essaie: bluetoothctl -> scan on\n - Allume/éteins le masque")
        return
    for attempt in range(1, args.retry + 2):
        try:
            await connect_and_test(dev, args)
            break
        except Exception as e:
            print(f"⚠️ Échec connexion tentative {attempt}: {e}")
            await asyncio.sleep(1.5)

if __name__ == '__main__':
    asyncio.run(main())
