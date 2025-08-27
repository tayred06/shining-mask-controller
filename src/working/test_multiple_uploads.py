#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des envois multiples pour vérifier la correction du bug
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultimate_text_display_with_bold import CompleteMaskController

async def test_multiple_uploads():
    """Test des envois multiples"""
    print("🔄 TEST DES ENVOIS MULTIPLES")
    print("=" * 40)
    
    mask = CompleteMaskController()
    
    try:
        # Connexion
        print("📡 Connexion au masque...")
        await mask.connect()
        await mask.set_brightness(80)
        print("✅ Connecté!")
        
        # Test 1: Premier envoi
        print("\n📤 Test 1: Premier envoi")
        mask.set_text_color("red")
        mask.set_decoration_color("yellow")
        await mask.set_scrolling_text("TEST 1", "scroll_left", 30)
        print("✅ Premier envoi réussi!")
        
        # Attendre un peu
        await asyncio.sleep(2)
        
        # Test 2: Deuxième envoi
        print("\n📤 Test 2: Deuxième envoi")
        mask.set_text_color("green")
        mask.set_decoration_color("blue")
        await mask.set_scrolling_text("TEST 2", "scroll_right", 50)
        print("✅ Deuxième envoi réussi!")
        
        # Attendre un peu
        await asyncio.sleep(2)
        
        # Test 3: Troisième envoi
        print("\n📤 Test 3: Troisième envoi")
        mask.set_text_color("white")
        mask.set_decoration_color("red")
        await mask.set_scrolling_text("TEST 3", "blink", 40)
        print("✅ Troisième envoi réussi!")
        
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Le bug des envois multiples est corrigé!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print(f"Upload running: {mask.upload_running}")
        
    finally:
        try:
            await mask.disconnect()
            print("👋 Déconnexion réussie")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_multiple_uploads())
