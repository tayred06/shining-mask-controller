#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/Users/mathieu/my-python-project/src/working')
from complete_text_display import MaskTextDisplay

async def test_simple_o():
    """Test très simple avec un seul O"""
    print("🔧 TEST SIMPLE - UN SEUL 'O'")
    print("=" * 40)
    
    display = MaskTextDisplay()
    if not await display.connect():
        print("❌ Connexion impossible")
        return
    
    try:
        # Test avec un seul caractère
        await display.display_text("O", color=(255, 255, 255))
        print("✅ Test 'O' terminé - vérifiez le masque")
        
        await asyncio.sleep(3)
        
        # Test avec "HI" (plus simple que "OO")
        await display.display_text("HI", color=(255, 255, 255))
        print("✅ Test 'HI' terminé - vérifiez le masque")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if display.client:
            await display.client.disconnect()
            print("🔌 Déconnecté")

if __name__ == "__main__":
    asyncio.run(test_simple_o())
