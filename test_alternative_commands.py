#!/usr/bin/env python3
"""
🔄 COMMANDES ALTERNATIVES - Bypass de DATS
===========================================

Exploration de commandes firmware alternatives qui pourraient
permettre d'afficher du texte SANS utiliser DATS (et donc sans flèche).
"""

import asyncio
import sys
import os

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.complete_text_display import MaskTextDisplay

class AlternativeCommands(MaskTextDisplay):
    """Explorateur de commandes alternatives"""
    
    def __init__(self):
        super().__init__()
    
    async def explore_alternative_commands(self):
        """Explore les commandes alternatives au firmware"""
        print("🔄 EXPLORATION COMMANDES ALTERNATIVES")
        print("=" * 50)
        
        # Liste des commandes firmware connues (d'après les logs précédents)
        commands_to_test = [
            ("ANIM", "Animation command"),
            ("DRAW", "Draw command"),  
            ("PICT", "Picture command"),
            ("DISP", "Display command"),
            ("SHOW", "Show command"),
            ("LOAD", "Load command"),
            ("SEND", "Send command"),
            ("PUSH", "Push command"),
            ("WRITE", "Write command"),
            ("SET", "Set command"),
            ("PUT", "Put command"),
        ]
        
        print("🧪 Test des commandes alternatives...")
        
        for cmd, desc in commands_to_test:
            print(f"\n🔍 Test: {cmd} ({desc})")
            
            try:
                # Créer une commande test
                test_cmd = bytearray([len(cmd) + 1])
                test_cmd.extend(cmd.encode())
                test_cmd.extend([1, 2, 3, 4])  # Données test
                while len(test_cmd) < 16:
                    test_cmd.append(0)
                
                # Chiffrer et envoyer
                encrypted = self.cipher.encrypt(bytes(test_cmd))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
                
                # Attendre réponse
                await asyncio.sleep(0.5)
                if self.responses:
                    response = self.responses[-1]
                    print(f"  📨 Réponse: {response}")
                    
                    # Si on a une réponse positive, approfondir
                    if "OK" in response or len(response) > 2:
                        print(f"  ✨ {cmd} semble reconnu!")
                        await self.test_command_deeper(cmd)
                else:
                    print(f"  ❌ Pas de réponse pour {cmd}")
                
            except Exception as e:
                print(f"  ⚠️  Erreur avec {cmd}: {e}")
            
            await asyncio.sleep(0.3)
    
    async def test_command_deeper(self, cmd):
        """Test approfondi d'une commande qui répond"""
        print(f"    🔬 Test approfondi de {cmd}...")
        
        # Essayer avec des paramètres différents
        test_params = [
            [0, 0, 0, 0],
            [1, 0, 0, 0], 
            [0, 1, 0, 0],
            [255, 255, 255, 255],
            [100, 100, 0, 0],
        ]
        
        for params in test_params:
            try:
                test_cmd = bytearray([len(cmd) + 1])
                test_cmd.extend(cmd.encode())
                test_cmd.extend(params)
                while len(test_cmd) < 16:
                    test_cmd.append(0)
                
                encrypted = self.cipher.encrypt(bytes(test_cmd))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
                
                await asyncio.sleep(0.3)
                if self.responses:
                    response = self.responses[-1]
                    print(f"      params {params}: {response}")
                
            except Exception as e:
                pass
    
    async def test_direct_pixel_commands(self):
        """Test de commandes directes pour pixels"""
        print("\n🎨 TEST COMMANDES DIRECTES PIXELS")
        print("=" * 40)
        
        pixel_commands = [
            ("PIXEL", [10, 10, 255, 0, 0]),  # x, y, r, g, b
            ("DOT", [5, 5, 0, 255, 0]),
            ("POINT", [8, 8, 0, 0, 255]),
            ("COLOR", [255, 255, 255, 0]),
            ("RGB", [255, 0, 255, 0]),
        ]
        
        for cmd, params in pixel_commands:
            print(f"\n🎨 Test: {cmd} avec {params}")
            
            try:
                test_cmd = bytearray([len(cmd) + 1])
                test_cmd.extend(cmd.encode())
                test_cmd.extend(params)
                while len(test_cmd) < 16:
                    test_cmd.append(0)
                
                encrypted = self.cipher.encrypt(bytes(test_cmd))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
                
                await asyncio.sleep(0.5)
                if self.responses:
                    response = self.responses[-1]
                    print(f"  📨 {response}")
                    
                    if "OK" in response:
                        print(f"  ✨ {cmd} fonctionne! Pas de flèche visible?")
                        input("    👁️  Y a-t-il quelque chose d'affiché? (ENTRÉE)")
                
            except Exception as e:
                print(f"  ⚠️  Erreur: {e}")
    
    async def test_immediate_display_commands(self):
        """Test de commandes d'affichage immédiat"""
        print("\n⚡ TEST COMMANDES AFFICHAGE IMMÉDIAT")
        print("=" * 45)
        
        immediate_commands = [
            ("LIVE", [1]),
            ("FAST", [255]),
            ("QUICK", [1, 1]),
            ("REAL", [1, 0, 0, 0]),
            ("NOW", [255, 255, 255]),
            ("INST", [1]),
        ]
        
        for cmd, params in immediate_commands:
            print(f"\n⚡ Test: {cmd}")
            
            try:
                test_cmd = bytearray([len(cmd) + 1])
                test_cmd.extend(cmd.encode())
                test_cmd.extend(params)
                while len(test_cmd) < 16:
                    test_cmd.append(0)
                
                encrypted = self.cipher.encrypt(bytes(test_cmd))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
                
                await asyncio.sleep(0.3)
                if self.responses:
                    response = self.responses[-1]
                    print(f"  📨 {response}")
                
            except Exception as e:
                print(f"  ⚠️  Erreur: {e}")
    
    async def test_bitmap_alternatives(self):
        """Test d'alternatives pour l'upload bitmap"""
        print("\n🖼️  TEST ALTERNATIVES BITMAP")
        print("=" * 35)
        
        # Essayer des alternatives à DATS
        bitmap_commands = [
            "BITS", "MAPS", "DATA", "BUFF", "FRAM", "VRAM", 
            "SCRE", "DISP", "SHOW", "DRAW", "REND"
        ]
        
        for cmd in bitmap_commands:
            print(f"\n🖼️  Test: {cmd}")
            
            try:
                # Données bitmap minimales
                test_cmd = bytearray([len(cmd) + 1])
                test_cmd.extend(cmd.encode())
                test_cmd.extend([0, 32])  # Taille 32 bytes
                test_cmd.extend([0, 16])  # 16 bytes bitmap
                test_cmd.extend([0])
                while len(test_cmd) < 16:
                    test_cmd.append(0)
                
                encrypted = self.cipher.encrypt(bytes(test_cmd))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", encrypted)
                
                await asyncio.sleep(0.5)
                if self.responses:
                    response = self.responses[-1]
                    print(f"  📨 {response}")
                    
                    if "OK" in response:
                        print(f"  🎉 {cmd} accepté! Alternative possible à DATS!")
                        input("    👁️  Flèche visible? (ENTRÉE)")
                
            except Exception as e:
                print(f"  ⚠️  Erreur: {e}")

async def run_alternative_exploration():
    """Lance l'exploration complète"""
    explorer = AlternativeCommands()
    
    if await explorer.connect():
        try:
            print("🔄 EXPLORATION DES ALTERNATIVES AU SYSTÈME DATS")
            print("=" * 55)
            print("Objectif: trouver des commandes qui affichent du contenu")
            print("          SANS déclencher la flèche firmware")
            print()
            
            # 1. Commandes générales
            await explorer.explore_alternative_commands()
            
            # 2. Commandes pixels directs
            await explorer.test_direct_pixel_commands()
            
            # 3. Commandes affichage immédiat
            await explorer.test_immediate_display_commands()
            
            # 4. Alternatives bitmap
            await explorer.test_bitmap_alternatives()
            
            print("\n🎯 RÉSUMÉ DE L'EXPLORATION")
            print("=" * 30)
            print("Si nous avons trouvé des commandes qui répondent 'OK'")
            print("et qui n'affichent PAS de flèche, nous avons notre solution!")
            print()
            print("Sinon, nous devrons accepter que la flèche est")
            print("inhérente au protocole firmware du masque.")
            
        except KeyboardInterrupt:
            print("\n⏹️ Exploration arrêtée")
        finally:
            await explorer.disconnect()
    else:
        print("❌ Connexion impossible")

if __name__ == "__main__":
    asyncio.run(run_alternative_exploration())
