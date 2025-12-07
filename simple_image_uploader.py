#!/usr/bin/env python3
"""
Script d'upload d'image vers Shining Mask (Protocole Image Full Frame).
Usage: python3 simple_image_uploader.py [chemin/vers/image.png]
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
        """Lit, redimensionne et upload une image."""
        
        # Dimensions cibles
        TARGET_W = 46
        TARGET_H = 58
        
        # 1. Traitement de l'image
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            print(f"Image originale: {img.size} -> Cible: {TARGET_W}x{TARGET_H}")
            
            # Redimensionnement simple (Stretch) ou Fit ? 
            # On va faire un "Fill" (Stretch pour remplir) pour l'instant
            img_resized = img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
            
            # Conversion en bytes RGB
            # Note: app.py utilisait row-major. Confirmé par le succès de mon script précédent.
            rgb_data = img_resized.tobytes()
            
        except Exception as e:
            print(f"❌ Erreur lecture image: {e}")
            return False
            
        # 2. Préparation du Mask Bitmap (Tout à 1)
        bitmap_buffer = bytearray([0xFF] * (TARGET_W * 8)) # 8 bytes par colonne
        
        # 3. Préparation upload
        total_len = len(bitmap_buffer) + len(rgb_data)
        image_index = 1 # Slot 1
        
        self.current_upload = {
            'total_len': total_len,
            'bytes_sent': 0,
            'packet_count': 0,
            'complete_buffer': bitmap_buffer + rgb_data
        }
        
        print(f"Buffer prêt: {len(rgb_data)} bytes RGB + {len(bitmap_buffer)} bytes Bitmap.")
        
        # 4. Connexion
        try:
            print("Recherche du masque...")
            await self.connect()
        except:
            print("❌ Échec connexion")
            return False
            
        try:
            # 5. Envoi DATS (Image Protocol)
            cmd = bytearray()
            cmd.append(9)
            cmd.extend(b"DATS")
            cmd.extend(struct.pack('>H', total_len)) 
            cmd.extend(struct.pack('>H', image_index)) # Important: Image ID ici
            cmd.append(0)
            
            print(f"Envoi DATS...")
            await self.send_command(cmd)
            self.upload_running = True
            
            if not await self.wait_for_response("DATSOK", timeout=5.0):
                print("❌ Timeout DATSOK")
                return False
                
            # 6. Transfert
            print("Transfert en cours...")
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                # await asyncio.sleep(0.01) # Petit throttle
                # Note: mask_go code original utilisait wait_for_response REOK
                # Mon test précédent montrait que REOK est bien reçu.
                # await self.wait_for_response("REOK", timeout=1.0)
                # On va faire simple: sleep léger
                await asyncio.sleep(0.02)
                
            # 7. Finalisation
            print("\nFinalisation...")
            cmd_fin = bytearray([5]) + b"DATCP"
            await self.send_command(cmd_fin)
            await self.wait_for_response("DATCPOK", timeout=5.0)
            
            # 8. Sauvegarde
            print("Sauvegarde (SAVE01)...")
            await self.send_command(b"SAVE01")
            print("✅ SUCCÈS! Image transférée.")
            
        except Exception as e:
            print(f"❌ Erreur durant le transfert: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.disconnect()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_image_uploader.py <image_path>")
        # Créons une image par défaut si pas d'argument
        print("Génération d'une image de test...")
        img = Image.new('RGB', (100, 100), color='blue')
        d = ImageDraw.Draw(img)
        d.rectangle([20, 20, 80, 80], fill='red')
        img.save("test_gen.png")
        image_path = "test_gen.png"
    else:
        image_path = sys.argv[1]
        
    uploader = ShiningMaskImageUploader()
    await uploader.upload_image_file(image_path)

if __name__ == "__main__":
    from PIL import Image, ImageDraw # Import ici au cas où
    asyncio.run(main())
