#!/usr/bin/env python3
"""
Module Text - Contrôleur de texte défilant
==========================================

Classe pour la gestion du texte défilant et des décorations.
Hérite du contrôleur de base et ajoute les fonctionnalités de texte.
"""

import asyncio
import struct
from PIL import Image, ImageDraw, ImageFont
from ..core.base_controller import BaseMaskController

class ScrollingTextController(BaseMaskController):
    """
    Contrôleur de texte défilant pour le masque LED
    Hérite de BaseMaskController et ajoute les fonctionnalités de texte.
    """
    
    def __init__(self):
        super().__init__()
        # Propriétés spécifiques au texte
        self.font_size = 12
        self.auto_fit = True
        self.bold_text = False
        
    def reset_upload_state(self):
        """Réinitialise complètement l'état d'upload"""
        self.upload_running = False
        if hasattr(self, 'upload_in_progress'):
            self.upload_in_progress = False
        if hasattr(self, '_upload_task') and self._upload_task:
            self._upload_task.cancel()
            self._upload_task = None
        if hasattr(self, 'current_upload'):
            self.current_upload = None
        print("🔄 État d'upload réinitialisé")
    
    async def init_upload(self, bitmap, color_array):
        """Initialise l'upload avec DATS"""
        if self.upload_running:
            raise RuntimeError("Upload déjà en cours")
            
        self.current_upload = {
            'bitmap': bitmap,
            'color_array': color_array,
            'total_len': len(bitmap) + len(color_array),
            'bytes_sent': 0,
            'packet_count': 0,
            'complete_buffer': bitmap + color_array
        }
        
        cmd = bytearray()
        cmd.append(9)
        cmd.extend(b"DATS")
        cmd.extend(struct.pack('<I', self.current_upload['total_len']))
        
        await self.send_command(cmd)
        self.upload_running = True
    
    async def upload_part(self):
        """Envoie une partie des données d'upload"""
        if not self.upload_running or not self.current_upload:
            raise RuntimeError("Aucun upload en cours")
        
        PACKET_SIZE = 128
        remaining = self.current_upload['total_len'] - self.current_upload['bytes_sent']
        chunk_size = min(PACKET_SIZE, remaining)
        
        if chunk_size <= 0:
            return False
        
        start_pos = self.current_upload['bytes_sent']
        end_pos = start_pos + chunk_size
        chunk = self.current_upload['complete_buffer'][start_pos:end_pos]
        
        await self.send_upload_data(chunk)
        
        self.current_upload['bytes_sent'] += chunk_size
        self.current_upload['packet_count'] += 1
        
        return self.current_upload['bytes_sent'] < self.current_upload['total_len']
    
    async def finish_upload(self):
        """Finalise l'upload avec DATCP"""
        if not self.upload_running:
            raise RuntimeError("Aucun upload en cours")
        
        cmd = bytearray()
        cmd.append(2)
        cmd.extend(b"DATCP")
        
        await self.send_command(cmd)
        self.upload_running = False
        self.current_upload = {}
    
    def find_optimal_font_size(self, text):
        """Trouve la taille de police optimale"""
        max_height = 12  # Hauteur disponible avec décorations
        max_size = 14
        
        for test_size in range(max_size, 6, -1):
            try:
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "arial.ttf"
                ]
                
                font = None
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, test_size)
                        break
                    except:
                        continue
                        
                if font is None:
                    font = ImageFont.load_default()
                
                dummy_img = Image.new('L', (1, 1))
                dummy_draw = ImageDraw.Draw(dummy_img)
                bbox = dummy_draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                
                if text_height <= max_height:
                    return test_size
                    
            except Exception:
                continue
        
        return 8
    
    def create_text_bitmap(self, text, width_multiplier=1.5):
        """Génère uniquement le bitmap (sans image RGB) pour le masque"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Déterminer la taille de police
            if self.auto_fit:
                optimal_size = self.find_optimal_font_size(text)
                actual_font_size = optimal_size
                if optimal_size != self.font_size:
                    print(f"🔧 Auto-ajustement: {self.font_size}px → {optimal_size}px")
            else:
                actual_font_size = self.font_size
            
            # Charger la police
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "arial.ttf"
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, actual_font_size)
                    break
                except:
                    continue
                    
            if font is None:
                font = ImageFont.load_default()
                
        except:
            from PIL import ImageFont
            font = ImageFont.load_default()

        # Calcul de la largeur du texte
        dummy_img = Image.new('L', (1, 1))  # Noir et blanc uniquement
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        total_width = int(text_width * width_multiplier)
        
        # Création de l'image en noir et blanc pour bitmap
        img = Image.new('L', (total_width, 16), 0)  # Fond noir
        draw = ImageDraw.Draw(img)
        
        # Zone de texte (sans décorations pour l'instant)
        text_area_height = 16
        text_y_start = 0
        
        # Positionnement du texte
        text_bbox = draw.textbbox((0, 0), text, font=font)
        actual_height = text_bbox[3] - text_bbox[1]
        text_top = text_bbox[1]
        
        y_offset = text_y_start + (text_area_height - actual_height) // 2 - text_top
        x_offset = (total_width - text_width) // 2
        
        # Dessiner le texte en blanc
        draw.text((x_offset, y_offset), text, fill=255, font=font)
        
        # Effet gras par superposition si activé
        if self.bold_text:
            draw.text((x_offset + 1, y_offset), text, fill=255, font=font)
            draw.text((x_offset, y_offset + 1), text, fill=255, font=font)
            draw.text((x_offset + 1, y_offset + 1), text, fill=255, font=font)
        
        # Conversion directe en bitmap pour le masque
        pixels = []
        for x in range(total_width):
            column = []
            for y in range(16):
                pixel_value = img.getpixel((x, y))
                column.append(1 if pixel_value > 0 else 0)
            pixels.append(column)
        
        return pixels
    
    def encode_white_color_array_for_mask(self, columns):
        """Génère un tableau de couleurs blanches selon mask-go"""
        results = bytearray()
        for i in range(columns):
            results.extend([0xFF, 0xFF, 0xFF])  # RGB blanc pour chaque colonne
        return bytes(results)
