#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test isolé pour vérifier la correction du bug upload_running
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

async def test_upload_fix():
    """Test du fix de upload_running"""
    print("🔧 TEST CORRECTION BUG UPLOAD")
    print("=" * 35)
    
    mask = ScrollingMaskController()
    
    try:
        # Connexion
        print("📡 Connexion au masque...")
        await mask.connect()
        print("✅ Connecté!")
        
        # Vérifier état initial
        print(f"📊 État initial upload_running: {mask.upload_running}")
        
        # Premier envoi
        print("\n📤 Premier envoi...")
        await mask.set_scrolling_text("PREMIER", "scroll_left", 30)
        print(f"📊 Après premier envoi upload_running: {mask.upload_running}")
        
        # Attendre un peu
        await asyncio.sleep(1)
        
        # Deuxième envoi - ici était le bug
        print("\n📤 Deuxième envoi...")
        await mask.set_scrolling_text("SECOND", "scroll_right", 50)
        print(f"📊 Après deuxième envoi upload_running: {mask.upload_running}")
        
        # Troisième envoi pour être sûr
        await asyncio.sleep(1)
        print("\n📤 Troisième envoi...")
        await mask.set_scrolling_text("TROISIEME", "blink", 40)
        print(f"📊 Après troisième envoi upload_running: {mask.upload_running}")
        
        print("\n🎉 SUCCÈS! Envois multiples fonctionnent!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print(f"📊 upload_running à l'erreur: {mask.upload_running}")
        
    finally:
        try:
            await mask.disconnect()
            print("👋 Déconnexion")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_upload_fix())
