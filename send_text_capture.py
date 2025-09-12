#!/usr/bin/env python3
"""
Petit runner d'envoi de texte pour capture PacketLogger côté Mac.

But: générer une séquence GATT similaire à l'app officielle (commande + upload de blocs)
afin que PacketLogger sur le Mac voie tous les Write / Notifications.

Usage de base:
  python3 send_text_capture.py                 # envoie le texte par défaut "CAPTURE"
  python3 send_text_capture.py "HELLO DFU"     # texte personnalisé

Options env facultatives:
  MASK_NAME_FILTER=MASK-ABCD   # filtrer précisément un périphérique
  PRE_DELAY=2                  # secondes avant envoi (laisser PacketLogger démarrer)
  POST_DELAY=3                 # secondes après l'envoi avant déconnexion

Séquence:
  1. Scan BLE (5s)
  2. Sélection du masque (nom commence par MASK- ou filtre)
  3. Connexion + abonnement notification
  4. Envoi du texte via MaskTextDisplay.display_text
  5. Attente POST_DELAY secondes
  6. Déconnexion propre

Note: Aucune tentative d'OTA ici; purement l'upload texte.
"""
import asyncio
import os
import sys
import time
from typing import Optional

# Import de la classe existante
from src.working.complete_text_display import MaskTextDisplay, BleakScanner

DEFAULT_TEXT = "CAPTURE"

async def pick_device(filter_name: Optional[str], timeout: float = 5.0):
    print(f"[SCAN] Démarrage scan {timeout}s…")
    devices = await BleakScanner.discover(timeout=timeout)
    candidates = []
    for d in devices:
        n = (d.name or "").strip()
        if not n:
            continue
        if filter_name:
            if filter_name.lower() in n.lower():
                candidates.append(d)
        else:
            if n.upper().startswith("MASK"):
                candidates.append(d)
    if not candidates:
        print("[SCAN] Aucun périphérique correspondant.")
        return None
    # Choisir le plus fort RSSI si dispo
    best = sorted(candidates, key=lambda x: (x.rssi if getattr(x, 'rssi', None) is not None else -999), reverse=True)[0]
    print(f"[SCAN] Sélection: {best.name} ({getattr(best,'address', 'unknown')}) RSSI={getattr(best,'rssi', '?')}")
    return best

class CaptureTextDisplay(MaskTextDisplay):
    def __init__(self):
        super().__init__()

async def run(text: str):
    filter_name = os.environ.get("MASK_NAME_FILTER")
    pre_delay = float(os.environ.get("PRE_DELAY", "2"))
    post_delay = float(os.environ.get("POST_DELAY", "3"))

    dev = await pick_device(filter_name)
    if not dev:
        return 1

    disp = CaptureTextDisplay()
    print(f"[INFO] Pause pré-envoi {pre_delay}s (PacketLogger: START maintenant)…")
    await asyncio.sleep(pre_delay)

    print("[BLE] Connexion…")
    try:
        if not await disp.connect(address_override=getattr(dev, 'address', None)):
            print("[ERR] Connexion échouée")
            return 2
    except TypeError:
        # Version antérieure ne supportant pas address_override
        if not await disp.connect():
            print("[ERR] Connexion échouée")
            return 2

    print(f"[SEND] Texte: {text!r}")
    t0 = time.time()
    try:
        await disp.display_text(text)
    except Exception as e:
        print(f"[ERR] display_text: {e}")
    dt = time.time() - t0
    print(f"[SEND] Durée upload approximative: {dt:.2f}s")

    print(f"[INFO] Attente post-envoi {post_delay}s…")
    await asyncio.sleep(post_delay)

    print("[BLE] Déconnexion…")
    try:
        if disp.client:
            await disp.client.disconnect()
    except Exception:
        pass
    return 0

async def amain():
    text = DEFAULT_TEXT if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    rc = await run(text)
    sys.exit(rc)

if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        print("[INT] Interrompu")
