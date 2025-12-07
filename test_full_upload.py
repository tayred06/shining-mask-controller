#!/usr/bin/env python3
"""
Test d'upload d'image FULL RESOLUTION (46x58) pour le Shining Mask.
Ce script teste spécifiquement le format d'upload pour une image complète et non une icône style "texte".
"""

import asyncio
import sys
import os
from PIL import Image, ImageDraw

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.mask_go_compatible import MaskGoCompatible

# Configuration de la résolution du masque (Shining Mask Standard)
TARGET_WIDTH = 46
TARGET_HEIGHT = 58

class FullImageUploader(MaskGoCompatible):
    async def upload_full_color_test(self):
        """
        Tente d'uploader une image de test "Drapeau Français" (Bleu, Blanc, Rouge)
        pour vérifier le mapping des pixels (Row vs Column) et le support couleur.
        """
        print(f"🎨 Génération image de test {TARGET_WIDTH}x{TARGET_HEIGHT}...")
        
        # 1. Créer le buffer RGB
        # On va tester le format ROW-MAJOR (Ligne par ligne) car c'est le standard
        # Si on obtient un résultat bizarre, on saura ajuster.
        rgb_buffer = bytearray(TARGET_WIDTH * TARGET_HEIGHT * 3)
        
        # Remplissage : Tiers Bleu, Tiers Blanc, Tiers Rouge (Verticalement pour voir les colonnes)
        # Tiers 1 (X < 15): Bleu
        # Tiers 2 (15 <= X < 30): Blanc
        # Tiers 3 (X >= 30): Rouge
        
        for y in range(TARGET_HEIGHT):
            for x in range(TARGET_WIDTH):
                idx = (y * TARGET_WIDTH + x) * 3
                
                if x < 15:
                    # Bleu
                    rgb_buffer[idx] = 0x00
                    rgb_buffer[idx+1] = 0x00
                    rgb_buffer[idx+2] = 0xFF
                elif x < 30:
                    # Blanc
                    rgb_buffer[idx] = 0xFF
                    rgb_buffer[idx+1] = 0xFF
                    rgb_buffer[idx+2] = 0xFF
                else:
                    # Rouge
                    rgb_buffer[idx] = 0xFF
                    rgb_buffer[idx+1] = 0x00
                    rgb_buffer[idx+2] = 0x00
                    
        # 2. Créer le Bitmap Buffer (Tout à 1)
        # Masque-Go semble utiliser 1 bit par pixel pour le "masque" de l'image (transparence ?)
        # Pour une image pleine, on veut tout allumer.
        # Format: 8 bytes par colonne (pour 64 bits max, on en utilise 58).
        # ATTENTION: mask-go utilise encode_bitmap_for_mask qui est LIMITÉ à 16 bits (2 bytes).
        # Ici on doit faire du CUSTOM BITMAP pour 58 pixels.
        
        bitmap_buffer = bytearray()
        # Pour chaque colonne
        for x in range(TARGET_WIDTH):
            # On veut 8 bytes (64 bits) avec les 58 premiers bits à 1.
            # 58 bits à 1 = 0x3FFFFFFFFFFFFFF (à peu près).
            # On peut juste mettre 8 octets à 0xFF pour être sûr.
            chunk = bytearray([0xFF] * 8) 
            bitmap_buffer.extend(chunk)
            
        print(f"Taille RGB: {len(rgb_buffer)} bytes")
        print(f"Taille Bitmap: {len(bitmap_buffer)} bytes")
        
        # 3. Connection et Upload
        try:
            await self.connect()
            
            # Utilisation directe de `init_upload` mais attention !
            # `MaskGoCompatible.init_upload` attend `bitmap` et `color_array`.
            # Il calcule `total_len` et `bitmap_len` automatiquement.
            # IL CONCATÈNE `bitmap` + `color_array`.
            
            # ATTENTION CRITIQUE: `MaskGoCompatible.init_upload` envoie:
            # DATS + TotalLen + BitmapLen
            # C'est ce qu'on veut tester.
            
            await self.init_upload(bitmap_buffer, rgb_buffer)
            
            # Envoi des paquets
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                await self.wait_for_response("REOK", timeout=1.0)
                
            await self.finish_upload()
            await self.wait_for_response("DATCPOK", timeout=5.0)
            
            print("✅ Upload terminé (DATCPOK reçu).")
            
            # 4. Sauvegarder/Activer
            print("Activation (SAVE01)...")
            await self.send_command(b"SAVE01")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.disconnect()

async def main():
    uploader = FullImageUploader()
    await uploader.upload_full_color_test()

if __name__ == "__main__":
    asyncio.run(main())
