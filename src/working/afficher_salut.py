#!/usr/bin/env python3

import asyncio
import sys
import os

# Ajouter le chemin vers nos modules
sys.path.append('/Users/mathieu/my-python-project/src/working')

from complete_text_display import MaskTextDisplay

def create_8x8_font():
    """Police 8x8 optimisée pour le masque (au lieu de 8x16)"""
    return {
        'O': [
            " ██████ ",
            "█      █",
            "█      █", 
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            " ██████ "
        ],
        'H': [
            "██    ██",
            "██    ██",
            "██    ██",
            "████████", 
            "████████",
            "██    ██",
            "██    ██",
            "██    ██"
        ],
        'I': [
            "████████",
            "   ██   ",
            "   ██   ",
            "   ██   ",
            "   ██   ",
            "   ██   ",
            "   ██   ",
            "████████"
        ],
        'L': [
            "██      ",
            "██      ",
            "██      ",
            "██      ",
            "██      ",
            "██      ",
            "██      ",
            "████████"
        ],
        'E': [
            "████████",
            "██      ",
            "██      ",
            "██████  ",
            "██████  ",
            "██      ",
            "██      ",
            "████████"
        ],
        ' ': [
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        "
        ]
    }

def text_to_bitmap_8x8(text, font_8x8):
    """Convertit le texte en bitmap 8x8 (au lieu de 8x16)"""
    columns = []
    
    for char in text.upper():
        if char in font_8x8:
            pattern = font_8x8[char]
            
            # 8 colonnes par caractère, 8 lignes seulement
            for col_idx in range(8):
                column = []
                for row_idx in range(8):  # Seulement 8 lignes !
                    if row_idx < len(pattern) and col_idx < len(pattern[row_idx]):
                        if pattern[row_idx][col_idx] == '█':
                            column.append(1)
                        else:
                            column.append(0)
                    else:
                        column.append(0)
                
                # IMPORTANT: Ajouter 8 zéros pour compatibilité avec l'encodage 16-bit
                column.extend([0] * 8)
                columns.append(column)
    
    return columns

def afficher_bitmap_console(text, display_obj):
    """Affiche le bitmap 8x8 dans la console"""
    print(f"\n🖥️  APERÇU CONSOLE 8x8 DE '{text}':")
    print("=" * 50)
    
    # Utiliser notre police 8x8
    font_8x8 = create_8x8_font()
    bitmap = text_to_bitmap_8x8(text, font_8x8)
    
    if not bitmap:
        print("❌ Impossible de générer le bitmap")
        return bitmap
    
    # Afficher les 8 lignes
    print("📺 Affichage bitmap 8x8:")
    for row in range(8):
        line = ""
        for col_idx, column in enumerate(bitmap):
            if row < len(column):
                if column[row] == 1:
                    line += "██"  # Pixel allumé
                else:
                    line += "  "  # Pixel éteint
            else:
                line += "  "
        print(f"│{line}│")
    
    print("=" * 50)
    print(f"📊 Dimensions: {len(bitmap)} colonnes x 8 lignes")
    
    return bitmap

async def afficher_salut():
    """Affiche 'SALUT!' sur le masque LED"""
    print("🎭 AFFICHAGE 'SALUT!' SUR LE MASQUE LED")
    print("=" * 40)
    
    # Créer l'instance d'affichage
    display = MaskTextDisplay()
    
    try:
        # Connexion au masque
        if not await display.connect():
            print("❌ Impossible de se connecter au masque")
            return
        
        # Générer bitmap 8x8 personnalisé
        text_a_afficher = "OO"
        bitmap_8x8 = afficher_bitmap_console(text_a_afficher, display)
        
        if bitmap_8x8:
            # Encoder le bitmap 8x8
            bitmap_data = display.encode_bitmap(bitmap_8x8)
            
            # Background noir
            await display.set_background_color(0, 0, 0, 1)
            
            # Couleurs
            colors = bytes([255, 255, 255] * len(bitmap_8x8))  # Blanc
            
            print(f"\n🎯 Upload bitmap 8x8 de '{text_a_afficher}'...")
            print(f"📊 {len(bitmap_8x8)} colonnes, {len(bitmap_data)}B bitmap, {len(colors)}B couleurs")
            
            # Upload manuel avec le bitmap 8x8
            import struct
            cmd = display.create_command("DATS", struct.pack('<HH', len(bitmap_data), len(colors)))
            await display.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await display.wait_for_response("OK")
            
            # Upload bitmap par chunks
            chunk_size = 16
            for i in range(0, len(bitmap_data), chunk_size):
                chunk = bitmap_data[i:i+chunk_size]
                await display.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
                await display.wait_for_response("OK")
            
            # Upload couleurs par chunks
            for i in range(0, len(colors), chunk_size):
                chunk = colors[i:i+chunk_size]
                await display.client.write_gatt_char("d44bc439-abfd-45a2-b575-92541612960a", chunk)
                await display.wait_for_response("OK")
            
            # DATCP
            cmd = display.create_command("DATCP")
            await display.client.write_gatt_char("d44bc439-abfd-45a2-b575-925416129600", cmd)
            await display.wait_for_response("OK")
            
            # Mode d'affichage
            await display.set_display_mode(1)
            
            print(f"✅ '{text_a_afficher}' affiché avec bitmap 8x8!")
            print("🖥️  Le même motif 8x8 est visible ci-dessus dans la console")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage: {e}")
    
    finally:
        # Déconnexion propre
        if display.client and display.client.is_connected:
            await display.client.disconnect()
            print("🔌 Déconnecté du masque")

def main():
    """Point d'entrée principal"""
    print("🚀 Démarrage du script avec aperçu console!")
    
    try:
        # Lance l'affichage
        asyncio.run(afficher_salut())
    except KeyboardInterrupt:
        print("\n⚠️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    main()
