#!/usr/bin/env python3
"""
🎮 Upload d'Images pour Contrôleur Clavier Masque LED
===================================================

Outil pour uploader les 20 images nécessaires au contrôleur clavier
inspiré du projet shining-mask.

Ce script génère et uploade des images prédéfinies qui correspondent
aux 20 images du projet shining-mask original.
"""

import asyncio
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import random

# Ajouter le répertoire des modules au path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from working.mask_go_compatible import MaskGoCompatible

class ShiningMaskImageUploader(MaskGoCompatible):
    """
    Uploadeur d'images pour répliquer les 20 images du projet shining-mask
    """
    
    def __init__(self):
        super().__init__()
        self.images_uploaded = 0
        
    def generate_predefined_images(self):
        """
        Génère 20 images prédéfinies inspirées du projet shining-mask
        
        Images 1-5: Expressions de base (sourires, yeux, etc.)
        Images 6-10: Émotions (clin d'œil, surprise, etc.)
        Images 11-15: Formes géométriques et patterns
        Images 16-20: Animations et effets spéciaux
        """
        images = []
        
        # Images 1-5: Expressions de base
        images.extend([
            self.create_happy_face(),      # Image 1
            self.create_neutral_face(),    # Image 2  
            self.create_sad_face(),        # Image 3
            self.create_surprised_face(),  # Image 4
            self.create_angry_face(),      # Image 5
        ])
        
        # Images 6-10: Émotions avancées
        images.extend([
            self.create_wink_face(),       # Image 6 - Utilisée pour clignotement
            self.create_sleepy_face(),     # Image 7 - Utilisée pour clignotement
            self.create_heart_eyes(),      # Image 8
            self.create_cool_face(),       # Image 9
            self.create_dizzy_face(),      # Image 10
        ])
        
        # Images 11-15: Formes et patterns
        images.extend([
            self.create_circle_pattern(),  # Image 11
            self.create_square_pattern(),  # Image 12
            self.create_diamond_pattern(), # Image 13
            self.create_cross_pattern(),   # Image 14
            self.create_star_pattern(),    # Image 15
        ])
        
        # Images 16-20: Effets spéciaux
        images.extend([
            self.create_spiral_pattern(),  # Image 16
            self.create_wave_pattern(),    # Image 17
            self.create_random_dots(),     # Image 18
            self.create_border_pattern(),  # Image 19
            self.create_full_display(),    # Image 20
        ])
        
        return images
    
    def create_16_height_image(self, draw_function, width=32):
        """Crée une image avec 16 pixels de hauteur (format masque)"""
        img = Image.new('L', (width, 16), 0)  # Fond noir, hauteur 16
        draw = ImageDraw.Draw(img)
        draw_function(draw, width)
        
        # Conversion en bitmap binaire par colonnes
        bitmap = []
        for x in range(width):
            column = []
            for y in range(16):
                pixel_value = img.getpixel((x, y))
                binary_val = 1 if pixel_value > 128 else 0
                column.append(binary_val)
            bitmap.append(column)
        
        return bitmap
    
    # === EXPRESSIONS DE BASE ===
    
    def create_happy_face(self):
        """Visage souriant 😊"""
        def draw(d, w):
            # Yeux (ajustés pour 16 pixels de hauteur)
            d.ellipse([w//4, 4, w//4+4, 8], fill=255)  # Œil gauche
            d.ellipse([3*w//4-4, 4, 3*w//4, 8], fill=255)  # Œil droit
            # Sourire
            d.arc([w//4, 10, 3*w//4, 14], 0, 180, fill=255, width=1)
        return self.create_16_height_image(draw, 32)
    
    def create_neutral_face(self):
        """Visage neutre 😐"""
        def draw(d, w):
            # Yeux
            d.ellipse([w//4, 4, w//4+4, 8], fill=255)
            d.ellipse([3*w//4-4, 4, 3*w//4, 8], fill=255)
            # Bouche neutre
            d.line([w//3, 12, 2*w//3, 12], fill=255, width=1)
        return self.create_16_height_image(draw, 32)
    
    def create_sad_face(self):
        """Visage triste 😢"""
        def draw(d, w):
            # Yeux
            d.ellipse([w//4, 4, w//4+4, 8], fill=255)
            d.ellipse([3*w//4-4, 4, 3*w//4, 8], fill=255)
            # Bouche triste
            d.arc([w//4, 11, 3*w//4, 15], 180, 360, fill=255, width=1)
        return self.create_16_height_image(draw, 32)
    
    def create_surprised_face(self):
        """Visage surpris 😮"""
        def draw(d, w):
            # Yeux grands ouverts
            d.ellipse([w//4-1, 3, w//4+5, 9], fill=255)
            d.ellipse([3*w//4-5, 3, 3*w//4+1, 9], fill=255)
            # Bouche ouverte
            d.ellipse([w//2-2, 11, w//2+2, 15], fill=255)
        return self.create_16_height_image(draw, 32)
    
    def create_angry_face(self):
        """Visage en colère 😠"""
        def draw(d, w):
            # Yeux froncés
            d.ellipse([w//4, 5, w//4+4, 9], fill=255)
            d.ellipse([3*w//4-4, 5, 3*w//4, 9], fill=255)
            # Sourcils froncés
            d.line([w//4-2, 3, w//4+6, 4], fill=255, width=1)
            d.line([3*w//4-6, 4, 3*w//4+2, 3], fill=255, width=1)
            # Bouche grognon
            d.arc([w//3, 11, 2*w//3, 15], 180, 360, fill=255, width=1)
        return self.create_16_height_image(draw, 32)
    
    # === ÉMOTIONS AVANCÉES ===
    
    def create_wink_face(self):
        """Clin d'œil 😉 - Utilisé pour clignotement"""
        def draw(d):
            # Œil fermé (gauche)
            d.line([20, 24, 28, 24], fill=255, width=2)
            # Œil ouvert (droit)
            d.ellipse([36, 20, 44, 28], fill=255)
            # Sourire
            d.arc([20, 35, 44, 50], 0, 180, fill=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_sleepy_face(self):
        """Visage endormi 😴 - Utilisé pour clignotement"""
        def draw(d):
            # Yeux fermés
            d.line([20, 24, 28, 24], fill=255, width=2)
            d.line([36, 24, 44, 24], fill=255, width=2)
            # Bouche légèrement ouverte
            d.ellipse([30, 40, 34, 44], fill=255)
        return self.create_64x64_image(draw)
    
    def create_heart_eyes(self):
        """Yeux en cœur 😍"""
        def draw(d):
            # Cœurs à la place des yeux
            d.polygon([(24, 18), (20, 22), (18, 26), (24, 32), (30, 26), (28, 22)], fill=255)
            d.polygon([(40, 18), (36, 22), (34, 26), (40, 32), (46, 26), (44, 22)], fill=255)
            # Sourire
            d.arc([20, 35, 44, 50], 0, 180, fill=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_cool_face(self):
        """Visage cool avec lunettes 😎"""
        def draw(d):
            # Lunettes de soleil
            d.rectangle([16, 18, 48, 32], outline=255, width=2)
            d.line([32, 20, 32, 30], fill=255, width=2)  # Pont
            # Bouche cool
            d.arc([24, 38, 40, 48], 0, 180, fill=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_dizzy_face(self):
        """Visage étourdi 😵"""
        def draw(d):
            # Yeux croisés (X)
            d.line([20, 20, 28, 28], fill=255, width=2)
            d.line([28, 20, 20, 28], fill=255, width=2)
            d.line([36, 20, 44, 28], fill=255, width=2)
            d.line([44, 20, 36, 28], fill=255, width=2)
            # Bouche ondulée
            d.arc([20, 38, 44, 48], 0, 180, fill=255, width=2)
        return self.create_64x64_image(draw)
    
    # === FORMES ET PATTERNS ===
    
    def create_circle_pattern(self):
        """Motif circulaire"""
        def draw(d):
            for r in range(10, 30, 6):
                d.ellipse([32-r, 32-r, 32+r, 32+r], outline=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_square_pattern(self):
        """Motif carré"""
        def draw(d):
            for s in range(8, 32, 6):
                d.rectangle([32-s, 32-s, 32+s, 32+s], outline=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_diamond_pattern(self):
        """Motif diamant"""
        def draw(d):
            for s in range(8, 28, 6):
                d.polygon([(32, 32-s), (32+s, 32), (32, 32+s), (32-s, 32)], 
                         outline=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_cross_pattern(self):
        """Motif croix"""
        def draw(d):
            d.line([32, 8, 32, 56], fill=255, width=4)   # Vertical
            d.line([8, 32, 56, 32], fill=255, width=4)   # Horizontal
        return self.create_64x64_image(draw)
    
    def create_star_pattern(self):
        """Motif étoile"""
        def draw(d):
            # Étoile à 5 branches
            points = []
            import math
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    r = 20
                else:
                    r = 10
                x = 32 + r * math.cos(angle - math.pi/2)
                y = 32 + r * math.sin(angle - math.pi/2)
                points.append((x, y))
            d.polygon(points, fill=255)
        return self.create_64x64_image(draw)
    
    # === EFFETS SPÉCIAUX ===
    
    def create_spiral_pattern(self):
        """Motif spirale"""
        def draw(d):
            import math
            for i in range(0, 360, 10):
                angle = math.radians(i)
                r = i / 20
                x = 32 + r * math.cos(angle)
                y = 32 + r * math.sin(angle)
                d.ellipse([x-1, y-1, x+1, y+1], fill=255)
        return self.create_64x64_image(draw)
    
    def create_wave_pattern(self):
        """Motif vague"""
        def draw(d):
            import math
            for x in range(0, 64, 2):
                y = 32 + 15 * math.sin(x * math.pi / 16)
                d.ellipse([x-1, y-1, x+1, y+1], fill=255)
        return self.create_64x64_image(draw)
    
    def create_random_dots(self):
        """Points aléatoires"""
        def draw(d):
            random.seed(42)  # Seed fixe pour reproductibilité
            for _ in range(30):
                x = random.randint(4, 60)
                y = random.randint(4, 60)
                d.ellipse([x-2, y-2, x+2, y+2], fill=255)
        return self.create_64x64_image(draw)
    
    def create_border_pattern(self):
        """Motif bordure"""
        def draw(d):
            d.rectangle([2, 2, 62, 62], outline=255, width=4)
            d.rectangle([10, 10, 54, 54], outline=255, width=2)
        return self.create_64x64_image(draw)
    
    def create_full_display(self):
        """Affichage complet"""
        def draw(d):
            # Damier
            for x in range(0, 64, 8):
                for y in range(0, 64, 8):
                    if (x + y) % 16 == 0:
                        d.rectangle([x, y, x+4, y+4], fill=255)
        return self.create_64x64_image(draw)
    
    async def upload_image_bitmap(self, image_id, bitmap):
        """Upload une image bitmap sur le masque avec l'ID spécifié"""
        try:
            print(f"📸 Upload image {image_id}...")
            
            # Encoder le bitmap pour le masque
            encoded_bitmap = self.encode_bitmap_for_mask(bitmap)
            
            # Génération du tableau de couleurs (blanc par défaut)
            color_array = [0xFF, 0xFF, 0xFF] * len(bitmap)  # RGB blanc pour chaque colonne
            
            # Initialisation de l'upload
            await self.init_upload(encoded_bitmap, color_array)
            
            # Upload par chunks
            while self.current_upload['bytes_sent'] < self.current_upload['total_len']:
                await self.upload_part()
                await asyncio.sleep(0.1)  # Délai entre chunks
            
            # Finalisation
            await self.finish_upload()
            
            # Enregistrer l'image avec l'ID spécifique
            save_command = f"SAVE{image_id:02d}".encode()
            await self.send_command(save_command)
            
            print(f"✅ Image {image_id} uploadée et sauvegardée!")
            self.images_uploaded += 1
            
        except Exception as e:
            print(f"❌ Erreur upload image {image_id}: {e}")
            return False
        
        return True
    
    async def upload_all_shining_mask_images(self):
        """Upload toutes les 20 images du projet shining-mask"""
        print("🎮 === UPLOAD DES IMAGES SHINING-MASK ===")
        print("Génération des 20 images prédéfinies...")
        
        # Génération des images
        images = self.generate_predefined_images()
        
        if len(images) != 20:
            print(f"❌ Erreur: {len(images)} images générées au lieu de 20")
            return False
        
        print(f"✅ {len(images)} images générées avec succès!")
        
        # Connexion au masque
        try:
            await self.connect()
        except Exception as e:
            print(f"❌ Impossible de se connecter: {e}")
            return False
        
        # Upload de chaque image
        success_count = 0
        for i, bitmap in enumerate(images, 1):
            print(f"\n🔄 Upload {i}/20...")
            if await self.upload_image_bitmap(i, bitmap):
                success_count += 1
            else:
                print(f"❌ Échec upload image {i}")
        
        # Déconnexion
        await self.disconnect()
        
        # Rapport final
        print(f"\n🎯 === RAPPORT FINAL ===")
        print(f"Images uploadées: {success_count}/20")
        
        if success_count == 20:
            print("🎉 SUCCESS! Toutes les images ont été uploadées!")
            print("🎮 Votre masque est maintenant prêt pour le contrôleur clavier!")
            return True
        else:
            print(f"⚠️ Seulement {success_count} images uploadées sur 20")
            return False

async def main():
    """Point d'entrée principal"""
    print("🎮 === UPLOADER D'IMAGES SHINING-MASK ===")
    print("Préparation du masque pour le contrôleur clavier")
    print("-" * 50)
    
    uploader = ShiningMaskImageUploader()
    
    try:
        success = await uploader.upload_all_shining_mask_images()
        
        if success:
            print("\n✅ Upload terminé avec succès!")
            print("🎮 Vous pouvez maintenant utiliser:")
            print("   python launcher.py")
            print("   (Option 1: Contrôleur interactif)")
        else:
            print("\n❌ Upload partiellement échoué")
            print("🔄 Vous pouvez relancer ce script pour réessayer")
            
    except KeyboardInterrupt:
        print("\n⚠️ Upload interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")

if __name__ == "__main__":
    asyncio.run(main())
