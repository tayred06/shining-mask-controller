#!/usr/bin/env python3
"""
🎯 TEST FINAL - Validation élimination flèche DÉFINITIVE
========================================================
Test ultime pour confirmer quelle méthode élimine vraiment la flèche
"""

import asyncio
import sys
import os
import struct

# Ajouter le chemin vers le module
current_dir = os.path.dirname(os.path.abspath(__file__))
working_dir = os.path.join(current_dir, 'src', 'working')
sys.path.insert(0, working_dir)

from complete_text_display import MaskTextDisplay, COMMAND_CHAR

class FinalArrowTest(MaskTextDisplay):
    def __init__(self):
        super().__init__()
    
    async def test_method_1_zero_brightness(self):
        """Test méthode 1: Luminosité 0 pure"""
        print("\n🔬 TEST 1: LUMINOSITÉ 0 PURE")
        print("=" * 40)
        
        try:
            # Luminosité 0 AVANT tout
            cmd = self.cipher.encrypt(b"LIGHT\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") + bytes([0])
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            await asyncio.sleep(0.5)
            
            print("🔅 Luminosité → 0")
            print("👁️  REGARDEZ LE MASQUE - upload en cours...")
            
            # Upload immédiat
            await self.display_text("TEST1", (255, 255, 255))
            
            # Restaurer luminosité
            cmd = self.cipher.encrypt(b"LIGHT\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") + bytes([200])
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    async def test_method_2_interrupt_upload(self):
        """Test méthode 2: Interruption d'upload"""
        print("\n🔬 TEST 2: INTERRUPTION D'UPLOAD")
        print("=" * 40)
        
        try:
            print("👁️  REGARDEZ LE MASQUE - test interruption...")
            
            # Démarrer upload normal
            bitmap, colors, color_data = self.create_text_bitmap("TEST2", (255, 255, 255), (0, 0, 0))
            
            # Envoyer DATS
            header = struct.pack('<HH', len(bitmap), len(color_data))
            cmd = self.cipher.encrypt(b"DATS\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") + header
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            
            print("📤 DATS envoyé - flèche devrait apparaître...")
            await asyncio.sleep(0.1)  # Laisser la flèche apparaître
            
            # INTERRUPTION IMMÉDIATE - luminosité 0
            cmd = self.cipher.encrypt(b"LIGHT\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") + bytes([0])
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            print("⚡ INTERRUPTION! Luminosité 0")
            
            # Continuer l'upload en mode invisible
            data_chunks = [bitmap[i:i+19] for i in range(0, len(bitmap), 19)]
            for chunk in data_chunks:
                if len(chunk) < 19:
                    chunk += b'\x00' * (19 - len(chunk))
                await self.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
                await asyncio.sleep(0.05)
            
            # Finaliser
            cmd = self.cipher.encrypt(b"DATCP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") + color_data
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            
            # Restaurer
            cmd = self.cipher.encrypt(b"LIGHT\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") + bytes([200])
            await self.client.write_gatt_char(COMMAND_CHAR, cmd)
            await self.set_display_mode(1)
            
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    async def test_method_3_flood_black(self):
        """Test méthode 3: Inondation écran noir"""
        print("\n🔬 TEST 3: INONDATION ÉCRAN NOIR")
        print("=" * 40)
        
        try:
            print("👁️  REGARDEZ LE MASQUE - test inondation...")
            
            # Écran complètement noir avant upload
            await self.set_background_color(0, 0, 0, 1)
            await asyncio.sleep(0.2)
            
            # Upload avec fond noir maintenu
            await self.display_text("TEST3", (255, 255, 255), (0, 0, 0))
            
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

async def run_final_validation():
    """Exécute la validation finale"""
    print("🎯 VALIDATION FINALE - ÉLIMINATION FLÈCHE")
    print("=" * 60)
    print("👀 OBSERVEZ ATTENTIVEMENT votre masque pendant chaque test!")
    print("📝 Notez si vous voyez la flèche d'upload apparaître")
    
    tester = FinalArrowTest()
    
    try:
        # Connexion
        await tester.connect()
        print("✅ Connecté au masque")
        
        # Tests séquentiels
        methods = [
            ("Luminosité 0 pure", tester.test_method_1_zero_brightness),
            ("Interruption d'upload", tester.test_method_2_interrupt_upload),
            ("Inondation écran noir", tester.test_method_3_flood_black)
        ]
        
        results = []
        
        for i, (name, method) in enumerate(methods, 1):
            print(f"\n{'='*60}")
            print(f"🧪 TEST {i}/3: {name.upper()}")
            print("👁️  REGARDEZ LE MASQUE MAINTENANT!")
            input("Appuyez sur ENTRÉE pour démarrer ce test...")
            
            success = await method()
            if success:
                print(f"✅ Test {i} terminé")
                response = input(f"❓ Avez-vous vu la flèche pendant ce test? (oui/non): ").lower()
                results.append((name, response not in ['non', 'n', 'no']))
            else:
                results.append((name, None))
            
            await asyncio.sleep(2)  # Pause entre les tests
        
        # Résultats finaux
        print(f"\n{'='*60}")
        print("📊 RÉSULTATS FINAUX")
        print("=" * 60)
        
        best_method = None
        for name, saw_arrow in results:
            if saw_arrow is None:
                print(f"❌ {name}: ÉCHEC du test")
            elif saw_arrow:
                print(f"👁️  {name}: Flèche VISIBLE")
            else:
                print(f"🎯 {name}: Flèche INVISIBLE - SUCCÈS!")
                if best_method is None:
                    best_method = name
        
        if best_method:
            print(f"\n🏆 MEILLEURE MÉTHODE: {best_method}")
            print("🎉 Cette méthode sera intégrée dans votre système!")
        else:
            print("\n⚠️  Aucune méthode n'a complètement éliminé la flèche")
            print("💡 Il faudra explorer d'autres solutions avancées")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    finally:
        if tester.client and tester.client.is_connected:
            await tester.client.disconnect()
            print("🔌 Déconnecté")

if __name__ == "__main__":
    asyncio.run(run_final_validation())
