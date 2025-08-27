#!/usr/bin/env python3
"""
Test rapide des différents styles de décoration
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from decorative_text_display import DecorativeMaskController

async def test_decorations():
    """Teste tous les styles de décoration"""
    mask = DecorativeMaskController()
    
    try:
        print("🔄 Connexion au masque...")
        await mask.connect()
        await mask.set_brightness(80)
        await mask.set_background_color(0, 0, 0)
        await mask.set_foreground_color(255, 255, 255)
        
        # Test des différents styles
        styles = [
            ("lines", "LIGNES PLEINES"),
            ("dots", "POINTS REGULIERS"),
            ("blocks", "BLOCS ALTERNES"),
            ("waves", "EFFET VAGUE"),
            ("none", "SANS DECORATION")
        ]
        
        for style, text in styles:
            print(f"\n🎨 Test style '{style}': {text}")
            mask.set_decoration_style(style)
            await mask.set_scrolling_text(text, "scroll_right", 40)
            print(f"✅ Style '{style}' affiché!")
            
            # Attendre un peu pour voir l'effet
            await asyncio.sleep(3)
        
        print("\n🎉 Tous les styles testés!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mask.disconnect()
        print("Déconnecté du masque")

if __name__ == "__main__":
    asyncio.run(test_decorations())
