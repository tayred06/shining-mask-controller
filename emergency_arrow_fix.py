#!/usr/bin/env python3
"""
Script d'upload d'image vers Shining Mask (Protocole Image Full Frame).
Version corrigée avec stratégie anti-flèche (Luminosité).
"""

import asyncio
import struct
import sys
import os
from PIL import Image

# Ajout du path pour trouver le module working
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from working.mask_go_compatible import MaskGoCompatible
except ImportError:
    print("❌ Impossible d'importer MaskGoCompatible. Vérifiez le path.")
    sys.exit(1)

class ShiningMaskImageUploader(MaskGoCompatible):
    
    async def upload_image_file(self, image_path):
        """Lit, redimensionne et upload une image avec stratégie anti-flèche."""
        
        TARGET_W = 46
        TARGET_H = 58
        
        # 1. Traitement Image
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_resized = img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"❌ Erreur lecture image: {e}")
            return False
            
        # 2. Préparation Buffer (BISHOP FOX STYLE + COLUMN MAJOR)
        # "Une ligne de chaque couleur qui s'alterne" suggère un mauvais mapping (Row vs Col).
        # On tente COLUMN-MAJOR (Vertical) tout en RESTANT sur le protocole PURE RGB.
        
        bitmap_buffer = bytearray() 
        rgb_buffer = bytearray()
        
        width, height = img_resized.size # 46, 58
        pixels = img_resized.load()
        
        # Parcours Colonne par Colonne (x puis y)
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                rgb_buffer.extend([r, g, b])
                
        rgb_data = rgb_buffer
        if len(rgb_data) != 8004:
            print(f"⚠️ Attention taille: {len(rgb_data)} != 8004")
        
        total_len = len(rgb_data)
        image_index = 1 # Slot 1
        
        self.current_upload = {
            'total_len': total_len,
            'bytes_sent': 0,
            'packet_count': 0,
            'complete_buffer': rgb_data
        }
        
        try:
            print("Recherche du masque...")
            await self.connect()
            
            # STRATEGIE: On réplique EXACTEMENT BishopFox DATS
            # b"\x09\x44\x41\x54\x53\x1f\x44\x00\x01\x01\x00\x00\x00\x00\x00\x00"
            # 09 DATS 1F44 0001 01
            
            cmd = bytearray()
            cmd.append(9)
            cmd.extend(b"DATS")
            cmd.extend(struct.pack('>H', total_len))
            cmd.extend(struct.pack('>H', image_index))
            cmd.append(1) # <--- LE FLAG MAGIQUE 0x01 QUE J'AVAIS MIS A 0
            
            print(f"Envoi DATS BishopFox Style: {cmd.hex()}")
            await self.send_command(cmd)
            self.upload_running = True
            
            # BishopFox attend 0.1s, ne check pas DATSOK explicitement dans le code simplifié ?
            # Mais mon code attend DATSOK. On garde l'attente pour validation.
            if not await self.wait_for_response("DATSOK", timeout=5.0):
                 print("⚠️ Pas de DATSOK, on continue quand même (Bishop style)...")

            # 5. Transfert
            print("Transfert PURE RGB...")
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                await asyncio.sleep(0.05) # BishopFox met 0.1s, on met 0.05 pour être safe
                
            # 6. Finalisation
            # Bishop sends: 09 DATCP ff f9 c5 07 ...
            # Mon code standard: 05 DATCP
            # On essaye le mien d'abord qui marchait pour la validation
            cmd_fin = bytearray([5]) + b"DATCP"
            await self.send_command(cmd_fin)
            await self.wait_for_response("DATCPOK", timeout=5.0)
            
            # 7. Save & Display
            await self.send_command(b"SAVE01")
            
            # Force Refresh
            # cmd_disp = bytearray([5]) + b"DISP" + b"\x01"
            # await self.send_command(cmd_disp)
            
            print("✅ SUCCÈS Bishop Style!")
            return True

        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.disconnect()

async def main():
    if len(sys.argv) < 2:
        image_path = "test_text.png" # Image générée précédemment
    else:
        image_path = sys.argv[1]
        
    uploader = ShiningMaskImageUploader()
    await uploader.upload_image_file(image_path)

if __name__ == "__main__":
    asyncio.run(main())
