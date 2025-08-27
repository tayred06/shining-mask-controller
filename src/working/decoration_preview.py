#!/usr/bin/env python3
"""
Démonstration visuelle des décorations dans la console
"""

def show_decoration_preview():
    """Montre un aperçu des décorations dans la console"""
    
    print("🎨 APERÇU DES STYLES DE DÉCORATION")
    print("=" * 60)
    
    # Simulation d'un affichage 16x40 pixels
    width = 40
    height = 16
    
    styles = {
        "lines": "Lignes pleines en haut et bas",
        "dots": "Points réguliers", 
        "blocks": "Blocs alternés",
        "waves": "Effet de vague",
        "none": "Sans décoration"
    }
    
    for style_name, description in styles.items():
        print(f"\n🎨 Style: {style_name.upper()} - {description}")
        print("-" * 50)
        
        # Générer l'aperçu
        for y in range(height):
            line = ""
            for x in range(width):
                
                # Zone de texte (lignes 6-9)
                if 6 <= y <= 9 and 8 <= x <= 31:
                    if style_name == "none":
                        char = "█" if (x - 8) < len("EXEMPLE TEXTE") and y == 7 else " "
                    else:
                        char = "█" if (x - 8) < len("TEXTE") and y == 7 else " "
                
                # Décorations
                elif style_name == "lines":
                    char = "█" if y in [0, 1, 14, 15] else " "
                    
                elif style_name == "dots":
                    char = "█" if y in [0, 1, 14, 15] and x % 3 == 0 else " "
                    
                elif style_name == "blocks":
                    char = "█" if y in [0, 1, 14, 15] and (x // 4) % 2 == 0 else " "
                    
                elif style_name == "waves":
                    if y in [0, 1]:
                        wave_y = int(1.5 + 0.5 * abs(((x % 20) - 10) / 10))
                        char = "█" if y == wave_y else " "
                    elif y in [14, 15]:
                        wave_y = int(14.5 - 0.5 * abs(((x % 20) - 10) / 10))
                        char = "█" if y == wave_y else " "
                    else:
                        char = " "
                        
                else:  # none
                    char = " "
                    
                line += char
            
            print(f"|{line}|")
        
        print("-" * 50)
    
    print("\n💡 Instructions d'utilisation:")
    print("1. Lancez: python decorative_text_display.py")
    print("2. Utilisez: deco:lines, deco:dots, deco:blocks, deco:waves, deco:none")
    print("3. Tapez votre texte pour voir l'effet!")

if __name__ == "__main__":
    show_decoration_preview()
