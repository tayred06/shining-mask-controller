#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/Users/mathieu/my-python-project/src/working')
from complete_text_display import MaskTextDisplay

def debug_bitmap_generation(text):
    """Debug la génération de bitmap pour identifier les problèmes"""
    print(f"\n🔍 DEBUG BITMAP POUR '{text}'")
    print("=" * 50)
    
    display = MaskTextDisplay()
    bitmap = display.text_to_bitmap(text)
    
    print(f"📊 Nombre de colonnes générées: {len(bitmap)}")
    
    # Vérifier chaque colonne
    for i, column in enumerate(bitmap):
        print(f"Colonne {i:2d}: {len(column)} pixels - {sum(column)} allumés")
        if i < 5:  # Détail des premières colonnes
            pixel_str = ''.join(['█' if p else ' ' for p in column])
            print(f"         Pattern: '{pixel_str}'")
    
    # Affichage bitmap ligne par ligne avec numéros
    print("\n🖼️  BITMAP DÉTAILLÉ (avec numéros de ligne):")
    for row in range(16):
        line = f"{row:2d}│"
        for col_idx, column in enumerate(bitmap):
            if row < len(column):
                if column[row] == 1:
                    line += "██"
                else:
                    line += "  "
            else:
                line += "  "
        line += "│"
        print(line)
    
    # Vérifier l'encodage
    bitmap_data = display.encode_bitmap(bitmap)
    print(f"\n📦 Données encodées: {len(bitmap_data)} bytes")
    print(f"    Expected: {len(bitmap) * 2} bytes ({len(bitmap)} colonnes x 2 bytes)")
    
    # Afficher les premières valeurs encodées
    print("🔢 Premières valeurs encodées:")
    for i in range(min(8, len(bitmap_data)//2)):
        val = int.from_bytes(bitmap_data[i*2:(i*2)+2], 'little')
        print(f"    Colonne {i}: 0x{val:04x} = {val}")

async def test_simple_patterns():
    """Test avec des patterns très simples"""
    print("\n🧪 TEST PATTERNS SIMPLES")
    print("=" * 50)
    
    display = MaskTextDisplay()
    if not await display.connect():
        print("❌ Connexion impossible")
        return
    
    try:
        # Test 1: Un seul "O"
        print("\n--- Test 1: Un seul 'O' ---")
        debug_bitmap_generation("O")
        await display.display_text("O", color=(255, 255, 255))
        await asyncio.sleep(3)
        
        # Test 2: "I" simple (plus facile à visualiser)
        print("\n--- Test 2: Un seul 'I' ---")
        debug_bitmap_generation("I")
        await display.display_text("I", color=(255, 255, 255))
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if display.client:
            await display.client.disconnect()
            print("🔌 Déconnecté")

def main():
    print("🔧 DIAGNOSTIC BITMAP - PROBLÈME RÉPÉTITION")
    
    # D'abord debug sans connexion
    debug_bitmap_generation("OO")
    debug_bitmap_generation("O")
    
    # Puis test avec connexion
    asyncio.run(test_simple_patterns())

if __name__ == "__main__":
    main()
