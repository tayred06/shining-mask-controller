#!/usr/bin/env python3
"""
Test local – Follow message
--------------------------
Affiche localement "Merci PSEUDO" en utilisant la config src/working/follow.json,
puis revient à l'image 1. Ne nécessite pas de token Twitch.

Usage:
  python3 test_local_follow.py --name PSEUDO
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Tuple


def resolve_src_path() -> Path:
    here = Path(__file__).resolve()
    candidates = [here.parent / 'src', here.parent.parent / 'src']
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Impossible de trouver le dossier src/ à côté de twitch_bot/")


def load_follow_cfg(root_dir: Path) -> dict:
    cfg_path = root_dir / 'src' / 'working' / 'follow.json'
    with cfg_path.open('r', encoding='utf-8') as f:
        return json.load(f)


def color_from_cfg(cfg: dict) -> Tuple[int, int, int]:
    try:
        tc = cfg.get('text', {}).get('text_color', {})
        return int(tc.get('r', 255)), int(tc.get('g', 255)), int(tc.get('b', 255))
    except Exception:
        return 255, 165, 0


def mode_from_cfg(cfg: dict) -> int:
    mode_name = cfg.get('scrolling', {}).get('default_mode', 'scroll_left')
    return 3 if mode_name == 'scroll_left' else (4 if mode_name == 'scroll_right' else 1)


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test local du message follow")
    parser.add_argument('--name', default='TestUser', help='Nom du follower à afficher')
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent

    # Résoudre et charger le contrôleur masque
    src_path = resolve_src_path()
    if str(src_path) not in sys.path:
        sys.path.append(str(src_path))
    from working.complete_text_display import MaskTextDisplay  # type: ignore

    # Config
    cfg = load_follow_cfg(root_dir)
    color = color_from_cfg(cfg)
    mode = mode_from_cfg(cfg)
    msg = f"Merci {args.name}"

    display = MaskTextDisplay()
    try:
        await display.connect()
        await display.set_background_color(0, 0, 0, 1)

        # Afficher le message et basculer en mode scroll
        await display.display_text(msg, color=color, background=(0, 0, 0))
        await display.set_display_mode(mode)

        # Estimation durée du défilement
        try:
            cols = len(display.text_to_bitmap(msg))  # type: ignore[attr-defined]
        except Exception:
            cols = max(10, len(msg) * 6)
        duration = min(12.0, max(3.0, 0.03 * (cols + 16)))
        await asyncio.sleep(duration)

        # Revenir à l'image 1
        await display.show_image(1)

    finally:
        await display.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
