#!/usr/bin/env python3
"""
Animation Controller Stable - Version basée sur les couleurs
"""
import asyncio
import math
import time

class StableAnimationController:
    """
    Contrôleur d'animations stable utilisant principalement les commandes de couleur
    pour éviter les déconnexions dues aux uploads d'images trop fréquents.
    """
    
    def __init__(self):
        self.animation_running = False
        self.client = None
    
    async def send_command(self, command_data: bytes):
        """Envoie une commande au masque (copié du base_controller)"""
        if not self.client or not self.client.is_connected:
            return False
            
        try:
            # Créer le paquet de commande (16 bytes)
            padded_data = command_data + b'\x00' * (16 - len(command_data))
            
            # Chiffrer et envoyer
            encrypted_data = self.encrypt_aes128(padded_data)
            await self.client.write_gatt_char(
                "d44bc439-abfd-45a2-b575-925416129600",  # UUID correct
                encrypted_data, 
                response=False
            )
            return True
            
        except Exception as e:
            print(f"❌ Erreur envoi commande: {e}")
            return False
    
    def encrypt_aes128(self, data: bytes) -> bytes:
        """Chiffrement AES-128 ECB (copié du base_controller)"""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        
        # Clé de chiffrement (16 bytes)
        key = b'1234567890123456'
        
        # Créer le chiffreur AES-128 ECB
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Chiffrer les données
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return encrypted_data
    
    async def play_simple_animation(self, animation_type: str, duration: float = 10.0):
        """Joue une animation simple basée sur les couleurs"""
        self.animation_running = True
        start_time = time.time()
        
        try:
            print(f"🎬 Démarrage animation stable: {animation_type}")
            
            while self.animation_running and (time.time() - start_time) < duration:
                current_time = time.time() - start_time
                
                if animation_type == "pulse":
                    await self._pulse_color_animation(current_time)
                elif animation_type == "wave":
                    await self._wave_color_animation(current_time)
                elif animation_type == "fire":
                    await self._fire_color_animation(current_time)
                elif animation_type == "rain":
                    await self._rain_color_animation(current_time)
                elif animation_type == "matrix":
                    await self._matrix_color_animation(current_time)
                else:
                    print(f"❌ Animation inconnue: {animation_type}")
                    break
                
                # Pause entre les frames (10 FPS)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Erreur animation: {e}")
        finally:
            self.animation_running = False
            # Remettre en blanc
            await self.send_command("FCFFFFFF".encode())
            print(f"✅ Animation terminée: {animation_type}")
    
    async def _pulse_color_animation(self, t: float):
        """Animation pulse basée sur la luminosité"""
        # Pulse toutes les 2 secondes
        pulse_intensity = (math.sin(t * math.pi) + 1) / 2
        brightness = int(255 * pulse_intensity)
        
        # Couleur blanche pulsante
        color_command = f"FC{brightness:02X}{brightness:02X}{brightness:02X}"
        await self.send_command(color_command.encode())
    
    async def _wave_color_animation(self, t: float):
        """Animation vague basée sur les couleurs"""
        # Cycle entre différentes couleurs
        hue = (t * 50) % 360  # Cycle de couleur
        
        # Convertir HSV vers RGB simplifié
        if hue < 120:
            r, g, b = 255, int(255 * hue / 120), 0
        elif hue < 240:
            r, g, b = int(255 * (240 - hue) / 120), 255, 0
        else:
            r, g, b = 0, int(255 * (hue - 240) / 120), 255
        
        color_command = f"FC{r:02X}{g:02X}{b:02X}"
        await self.send_command(color_command.encode())
    
    async def _fire_color_animation(self, t: float):
        """Animation feu basée sur les couleurs rouge/orange"""
        import random
        
        # Couleurs de feu aléatoires
        red = 255
        green = random.randint(100, 200)
        blue = random.randint(0, 50)
        
        color_command = f"FC{red:02X}{green:02X}{blue:02X}"
        await self.send_command(color_command.encode())
    
    async def _rain_color_animation(self, t: float):
        """Animation pluie basée sur les couleurs bleues"""
        # Intensité variable pour simuler les gouttes
        intensity = (math.sin(t * 5) + 1) / 2
        blue = int(255 * intensity)
        
        color_command = f"FC00{blue//4:02X}{blue:02X}"
        await self.send_command(color_command.encode())
    
    async def _matrix_color_animation(self, t: float):
        """Animation Matrix basée sur les couleurs vertes"""
        # Scintillement vert
        import random
        green = random.randint(150, 255)
        
        color_command = f"FC00{green:02X}00"
        await self.send_command(color_command.encode())
    
    def stop_animation(self):
        """Arrête l'animation en cours"""
        self.animation_running = False
