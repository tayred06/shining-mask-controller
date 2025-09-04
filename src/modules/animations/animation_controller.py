#!/usr/bin/env python3
"""
Module Animations - Contrôleur d'animations pour masque LED
==========================================================

Classes et fonctions pour créer des animations personnalisées :
- Animations de base (fade, pulse, wave)
- Animations complexes (feu, eau, plasma)
- Séquences d'animation
- Transitions entre animations
"""

import asyncio
import math
import time
from typing import List, Tuple, Callable
from ..text.scrolling_controller import ScrollingTextController

class AnimationController(ScrollingTextController):
    """
    Contrôleur d'animations pour le masque LED
    Permet de créer et jouer des animations personnalisées.
    """
    
    def __init__(self):
        super().__init__()
        self.animation_running = False
        self.current_animation = None
        self.fps = 10  # 10 FPS au lieu de 30 pour réduire la charge BLE
        self.frame_time = 1.0 / self.fps
        
    def create_empty_frame(self) -> List[List[int]]:
        """Crée une frame vide (16x64 pixels)"""
        return [[0 for _ in range(16)] for _ in range(64)]
    
    def set_pixel(self, frame: List[List[int]], x: int, y: int, value: int = 1):
        """Allume un pixel dans la frame"""
        if 0 <= x < len(frame) and 0 <= y < 16:
            frame[x][y] = value
    
    def draw_line(self, frame: List[List[int]], x1: int, y1: int, x2: int, y2: int):
        """Dessine une ligne dans la frame"""
        # Algorithme de Bresenham simplifié
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        x_inc = 1 if x1 < x2 else -1
        y_inc = 1 if y1 < y2 else -1
        error = dx - dy
        
        while True:
            self.set_pixel(frame, x, y, 1)
            if x == x2 and y == y2:
                break
            
            e2 = 2 * error
            if e2 > -dy:
                error -= dy
                x += x_inc
            if e2 < dx:
                error += dx
                y += y_inc
    
    def draw_circle(self, frame: List[List[int]], center_x: int, center_y: int, radius: int):
        """Dessine un cercle dans la frame"""
        for angle in range(0, 360, 5):  # Pas de 5 degrés
            x = center_x + int(radius * math.cos(math.radians(angle)))
            y = center_y + int(radius * math.sin(math.radians(angle)))
            self.set_pixel(frame, x, y, 1)
    
    def apply_wave_effect(self, frame: List[List[int]], time_offset: float, amplitude: int = 3):
        """Applique un effet de vague sur la frame"""
        new_frame = self.create_empty_frame()
        
        for x in range(len(frame)):
            wave_offset = int(amplitude * math.sin(time_offset + x * 0.3))
            for y in range(16):
                new_y = y + wave_offset
                if 0 <= new_y < 16 and frame[x][y] == 1:
                    self.set_pixel(new_frame, x, new_y, 1)
        
        return new_frame
    
    def create_pulse_animation(self, duration: float = 2.0) -> Callable:
        """Crée une animation de pulsation simple"""
        def pulse_frame(t: float) -> List[List[int]]:
            frame = self.create_empty_frame()
            
            # Calculer l'intensité du pulse (plus lent)
            pulse_intensity = (math.sin(t * math.pi / duration) + 1) / 2
            
            # Créer un simple rectangle central qui pulse
            center_x, center_y = 32, 8
            size = int(10 * pulse_intensity) + 5  # Taille variable
            
            # Dessiner un rectangle simple
            for x in range(max(0, center_x - size), min(64, center_x + size)):
                for y in range(max(0, center_y - size//2), min(16, center_y + size//2)):
                    self.set_pixel(frame, x, y, 1)
            
            return frame
        
        return pulse_frame
    
    def create_wave_animation(self, speed: float = 1.0) -> Callable:
        """Crée une animation de vague"""
        def wave_frame(t: float) -> List[List[int]]:
            frame = self.create_empty_frame()
            
            # Créer des vagues sinusoïdales
            for x in range(64):
                y = int(8 + 4 * math.sin(t * speed + x * 0.2))
                self.set_pixel(frame, x, y, 1)
                
                # Ajouter une deuxième vague
                y2 = int(8 + 2 * math.sin(t * speed * 1.5 + x * 0.3 + math.pi))
                self.set_pixel(frame, x, y2, 1)
            
            return frame
        
        return wave_frame
    
    def create_fire_animation(self) -> Callable:
        """Crée une animation de feu"""
        import random
        
        def fire_frame(t: float) -> List[List[int]]:
            frame = self.create_empty_frame()
            
            # Base du feu (toujours allumée)
            for x in range(64):
                if random.random() > 0.2:  # 80% de chance d'être allumé
                    self.set_pixel(frame, x, 15, 1)
                    self.set_pixel(frame, x, 14, 1)
            
            # Flammes qui montent
            for x in range(64):
                height = int(random.random() * 8 + 4)  # Hauteur aléatoire
                for y in range(16 - height, 16):
                    if random.random() > 0.3:  # 70% de chance d'être allumé
                        self.set_pixel(frame, x, y, 1)
            
            return frame
        
        return fire_frame
    
    def create_rain_animation(self, speed: float = 2.0) -> Callable:
        """Crée une animation de pluie"""
        import random
        
        drops = []
        
        def rain_frame(t: float) -> List[List[int]]:
            nonlocal drops
            frame = self.create_empty_frame()
            
            # Ajouter de nouvelles gouttes
            if random.random() < 0.3:  # 30% de chance d'ajouter une goutte
                drops.append({
                    'x': random.randint(0, 63),
                    'y': 0,
                    'speed': random.uniform(0.5, 1.5) * speed
                })
            
            # Mettre à jour et dessiner les gouttes
            drops_to_remove = []
            for i, drop in enumerate(drops):
                drop['y'] += drop['speed']
                
                if drop['y'] >= 16:
                    drops_to_remove.append(i)
                else:
                    self.set_pixel(frame, int(drop['x']), int(drop['y']), 1)
                    # Traînée
                    if drop['y'] > 0:
                        self.set_pixel(frame, int(drop['x']), int(drop['y']) - 1, 1)
            
            # Supprimer les gouttes qui ont dépassé l'écran
            for i in reversed(drops_to_remove):
                drops.pop(i)
            
            return frame
        
        return rain_frame
    
    def create_matrix_animation(self, speed: float = 1.0) -> Callable:
        """Crée une animation style Matrix"""
        import random
        
        columns = [{'pos': random.randint(-20, 0), 'speed': random.uniform(0.5, 2.0) * speed} 
                  for _ in range(20)]
        
        def matrix_frame(t: float) -> List[List[int]]:
            nonlocal columns
            frame = self.create_empty_frame()
            
            for i, col in enumerate(columns):
                x = i * 3 + 2  # Espacement des colonnes
                if x >= 64:
                    continue
                
                # Mettre à jour la position
                col['pos'] += col['speed']
                
                # Réinitialiser si la colonne est sortie
                if col['pos'] > 20:
                    col['pos'] = random.randint(-20, -5)
                    col['speed'] = random.uniform(0.5, 2.0) * speed
                
                # Dessiner la colonne
                for j in range(8):  # Longueur de la traînée
                    y = int(col['pos']) - j
                    if 0 <= y < 16:
                        # Intensité dégradée
                        if j < 3:  # Tête brillante
                            self.set_pixel(frame, x, y, 1)
            
            return frame
        
        return matrix_frame
    
    async def play_animation(self, animation_func: Callable, duration: float = 10.0):
        """Joue une animation pendant une durée donnée"""
        self.animation_running = True
        start_time = time.time()
        frames_sent = 0
        frames_failed = 0
        
        try:
            while self.animation_running and (time.time() - start_time) < duration:
                current_time = time.time() - start_time
                
                # Générer la frame
                frame = animation_func(current_time)
                
                # Encoder et envoyer au masque
                bitmap = self.encode_bitmap_for_mask(frame)
                color_array = self.encode_white_color_array_for_mask(len(frame))
                
                # Upload des données
                success = await self.upload_frame(bitmap, color_array)
                
                if success:
                    frames_sent += 1
                else:
                    frames_failed += 1
                    # Si trop d'échecs, arrêter l'animation
                    if frames_failed > 5:
                        print("❌ Trop d'erreurs, arrêt de l'animation")
                        break
                
                # Attendre le prochain frame (30 FPS = 33ms)
                await asyncio.sleep(self.frame_time)
                
        except Exception as e:
            print(f"❌ Erreur animation: {e}")
        finally:
            self.animation_running = False
            if frames_sent > 0:
                print(f"📊 Animation: {frames_sent} frames envoyées, {frames_failed} échecs")
    
    def stop_animation(self):
        """Arrête l'animation en cours"""
        self.animation_running = False
    
    async def upload_frame(self, bitmap: bytes, color_array: bytes):
        """Upload rapide d'une frame avec gestion de la déconnexion"""
        try:
            # Vérifier la connexion
            if not self.client or not self.client.is_connected:
                print("⚠️ Connexion perdue, tentative de reconnexion...")
                return False
            
            # Réinitialiser l'état d'upload
            self.upload_running = False
            
            # Upload des données
            await self.init_upload(bitmap, color_array)
            
            # Envoyer tous les paquets avec des petites pauses
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                # Petite pause pour éviter la surcharge
                await asyncio.sleep(0.01)  # 10ms entre les paquets
                
            # Finaliser
            await self.finish_upload()
            
            # Pause supplémentaire après chaque frame
            await asyncio.sleep(0.02)  # 20ms après l'upload
            
            return True
            
        except Exception as e:
            if "disconnected" in str(e).lower():
                print(f"⚠️ Déconnexion détectée lors de l'animation")
                return False
            else:
                print(f"❌ Erreur upload frame: {e}")
                return False
    
    def encode_white_color_array_for_mask(self, columns):
        """Génère un tableau de couleurs blanches"""
        results = bytearray()
        for i in range(columns):
            results.extend([0xFF, 0xFF, 0xFF])  # RGB blanc
        return bytes(results)
