#!/usr/bin/env python3
"""
Module Utils - Fonctions utilitaires
====================================

Fonctions helpers pour :
- Manipulation d'images et bitmaps
- Calculs mathématiques
- Helpers pour couleurs
- Fonctions de debug
"""

import math
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limite une valeur entre min et max"""
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """Interpolation linéaire entre a et b"""
    return a + (b - a) * t

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calcule la distance euclidienne entre deux points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convertit HSV vers RGB"""
    h = h % 360.0
    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convertit RGB vers HSV"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    # Hue
    if diff == 0:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    # Saturation
    s = 0 if max_val == 0 else diff / max_val
    
    # Value
    v = max_val
    
    return (h, s, v)

def create_gradient(width: int, height: int, color1: Tuple[int, int, int], 
                   color2: Tuple[int, int, int], direction: str = "horizontal") -> List[List[Tuple[int, int, int]]]:
    """Crée un dégradé entre deux couleurs"""
    gradient = []
    
    for x in range(width):
        column = []
        for y in range(height):
            if direction == "horizontal":
                t = x / (width - 1) if width > 1 else 0
            elif direction == "vertical":
                t = y / (height - 1) if height > 1 else 0
            elif direction == "diagonal":
                t = (x + y) / (width + height - 2) if width + height > 2 else 0
            else:
                t = 0
            
            r = int(lerp(color1[0], color2[0], t))
            g = int(lerp(color1[1], color2[1], t))
            b = int(lerp(color1[2], color2[2], t))
            
            column.append((r, g, b))
        gradient.append(column)
    
    return gradient

def apply_brightness(color: Tuple[int, int, int], brightness: float) -> Tuple[int, int, int]:
    """Applique une luminosité à une couleur (0.0 à 1.0)"""
    brightness = clamp(brightness, 0.0, 1.0)
    return (
        int(color[0] * brightness),
        int(color[1] * brightness),
        int(color[2] * brightness)
    )

def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                factor: float) -> Tuple[int, int, int]:
    """Mélange deux couleurs avec un facteur (0.0 = color1, 1.0 = color2)"""
    factor = clamp(factor, 0.0, 1.0)
    return (
        int(lerp(color1[0], color2[0], factor)),
        int(lerp(color1[1], color2[1], factor)),
        int(lerp(color1[2], color2[2], factor))
    )

def create_noise_pattern(width: int, height: int, scale: float = 0.1) -> List[List[float]]:
    """Crée un pattern de bruit (valeurs entre 0.0 et 1.0)"""
    import random
    pattern = []
    
    for x in range(width):
        column = []
        for y in range(height):
            # Bruit simple basé sur les coordonnées
            value = (math.sin(x * scale) * math.cos(y * scale) + 1) / 2
            value += random.random() * 0.2 - 0.1  # Ajouter du bruit aléatoire
            value = clamp(value, 0.0, 1.0)
            column.append(value)
        pattern.append(column)
    
    return pattern

def bitmap_to_frame(bitmap: List[List[int]]) -> List[List[int]]:
    """Convertit un bitmap en frame pour le masque"""
    # Le bitmap est déjà au bon format
    return bitmap

def frame_to_bitmap(frame: List[List[int]]) -> bytes:
    """Convertit une frame en bitmap pour transmission"""
    results = bytearray()
    
    for x in range(len(frame)):
        column = frame[x]
        
        # Encoder chaque colonne en 2 bytes (16 bits pour 16 pixels)
        byte1 = 0
        byte2 = 0
        
        for y in range(8):
            if y < len(column) and column[y] == 1:
                byte1 |= (1 << y)
        
        for y in range(8, 16):
            if y < len(column) and column[y] == 1:
                byte2 |= (1 << (y - 8))
        
        results.extend([byte1, byte2])
    
    return bytes(results)

def resize_frame(frame: List[List[int]], new_width: int) -> List[List[int]]:
    """Redimensionne une frame horizontalement"""
    if not frame:
        return [[0 for _ in range(16)] for _ in range(new_width)]
    
    old_width = len(frame)
    new_frame = []
    
    for x in range(new_width):
        # Interpolation simple
        old_x = int(x * old_width / new_width)
        old_x = min(old_x, old_width - 1)
        new_frame.append(frame[old_x][:])  # Copie de la colonne
    
    return new_frame

def crop_frame(frame: List[List[int]], start_x: int, width: int) -> List[List[int]]:
    """Découpe une frame"""
    if not frame:
        return []
    
    end_x = min(start_x + width, len(frame))
    start_x = max(0, start_x)
    
    return frame[start_x:end_x]

def merge_frames(frame1: List[List[int]], frame2: List[List[int]], 
                mode: str = "add") -> List[List[int]]:
    """Fusionne deux frames"""
    if not frame1:
        return frame2
    if not frame2:
        return frame1
    
    width = min(len(frame1), len(frame2))
    result = []
    
    for x in range(width):
        column = []
        for y in range(16):
            val1 = frame1[x][y] if y < len(frame1[x]) else 0
            val2 = frame2[x][y] if y < len(frame2[x]) else 0
            
            if mode == "add":
                result_val = min(1, val1 + val2)
            elif mode == "subtract":
                result_val = max(0, val1 - val2)
            elif mode == "multiply":
                result_val = val1 * val2
            elif mode == "or":
                result_val = 1 if val1 or val2 else 0
            elif mode == "and":
                result_val = 1 if val1 and val2 else 0
            elif mode == "xor":
                result_val = 1 if val1 != val2 else 0
            else:  # "overlay"
                result_val = val2 if val2 else val1
            
            column.append(result_val)
        result.append(column)
    
    return result

def debug_print_frame(frame: List[List[int]], title: str = "Frame"):
    """Affiche une frame en ASCII pour debug"""
    print(f"\n{title}:")
    print("+" + "-" * len(frame) + "+")
    
    for y in range(16):
        line = "|"
        for x in range(len(frame)):
            if y < len(frame[x]):
                line += "█" if frame[x][y] else " "
            else:
                line += " "
        line += "|"
        print(line)
    
    print("+" + "-" * len(frame) + "+")
    print(f"Taille: {len(frame)}x16")

def save_frame_as_image(frame: List[List[int]], filename: str, scale: int = 10):
    """Sauvegarde une frame comme image PNG (pour debug)"""
    if not frame:
        return
    
    width = len(frame)
    height = 16
    
    # Créer une image plus grande pour la visibilité
    img = Image.new('RGB', (width * scale, height * scale), (0, 0, 0))
    
    for x in range(width):
        for y in range(height):
            if y < len(frame[x]) and frame[x][y]:
                # Dessiner un carré blanc
                for sx in range(scale):
                    for sy in range(scale):
                        img.putpixel((x * scale + sx, y * scale + sy), (255, 255, 255))
    
    img.save(filename)
    print(f"Frame sauvegardée: {filename}")

class FrameBuffer:
    """Buffer circulaire pour stocker des frames d'animation"""
    
    def __init__(self, size: int = 100):
        self.size = size
        self.buffer = []
        self.index = 0
    
    def add_frame(self, frame: List[List[int]]):
        """Ajoute une frame au buffer"""
        if len(self.buffer) < self.size:
            self.buffer.append(frame)
        else:
            self.buffer[self.index] = frame
            self.index = (self.index + 1) % self.size
    
    def get_frame(self, offset: int = 0) -> Optional[List[List[int]]]:
        """Récupère une frame avec un offset"""
        if not self.buffer:
            return None
        
        index = (self.index - 1 - offset) % len(self.buffer)
        return self.buffer[index]
    
    def get_frames(self, count: int) -> List[List[List[int]]]:
        """Récupère les dernières frames"""
        frames = []
        for i in range(min(count, len(self.buffer))):
            frame = self.get_frame(i)
            if frame:
                frames.append(frame)
        return frames
    
    def clear(self):
        """Vide le buffer"""
        self.buffer.clear()
        self.index = 0
