#!/usr/bin/env python3
"""
Test rapide du texte défilant
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

async def quick_test():
    mask = ScrollingMaskController()
    
    try:
        await mask.connect()
        await mask.set_brightness(80)
        await mask.set_background_color(0, 0, 0)
        
        # Test simple défilement gauche
        print("Test défilement gauche...")
        await mask.set_scrolling_text("SALUT CA DEFILE!", "scroll_left", 50)
        await asyncio.sleep(5)
        
        # Test défilement droite
        print("Test défilement droite...")
        await mask.set_scrolling_text("DIRECTION DROITE", "scroll_right", 60)
        await asyncio.sleep(5)
        
        # Test clignotant
        print("Test clignotant...")
        await mask.set_scrolling_text("CLIGNOTANT", "blink", 100)
        await asyncio.sleep(5)
        
        print("✅ Tests terminés!")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mask.disconnect()

if __name__ == "__main__":
    asyncio.run(quick_test())
