#!/usr/bin/env python3
"""
Test du système d'export/import de configuration
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultimate_text_display_with_bold import CompleteMaskController

def test_config_system():
    """Test complet du système de configuration"""
    print("=" * 60)
    print("🧪 TEST DU SYSTÈME D'EXPORT/IMPORT")
    print("=" * 60)
    print()
    
    # Créer un contrôleur
    mask = CompleteMaskController()
    
    # Configuration 1: Mode Gaming
    print("🎮 Configuration 1: Mode Gaming")
    mask.set_font_size(14)
    mask.set_auto_fit(False)
    mask.set_bold(True)
    mask.set_decoration_style("blocks")
    mask.set_text_color("red")
    mask.set_decoration_color("cyan")
    
    print(f"   Police: {mask.font_size}px, Gras: {mask.bold_text}")
    print(f"   Déco: {mask.decoration_style}, Couleurs: {mask.get_color_name(mask.text_color)}/{mask.get_color_name(mask.decoration_color)}")
    
    # Export
    success, path = mask.export_config("gaming_config.json")
    if success:
        print(f"   ✅ Exporté: {os.path.basename(path)}")
    else:
        print(f"   ❌ Erreur: {path}")
    print()
    
    # Configuration 2: Mode Élégant
    print("✨ Configuration 2: Mode Élégant")
    mask.set_font_size(10)
    mask.set_auto_fit(True)
    mask.set_bold(False)
    mask.set_decoration_style("waves")
    mask.set_text_color("violet")
    mask.set_decoration_color("rose")
    
    print(f"   Police: {mask.font_size}px (auto), Gras: {mask.bold_text}")
    print(f"   Déco: {mask.decoration_style}, Couleurs: {mask.get_color_name(mask.text_color)}/{mask.get_color_name(mask.decoration_color)}")
    
    # Export
    success, path = mask.export_config("elegant_config.json")
    if success:
        print(f"   ✅ Exporté: {os.path.basename(path)}")
    else:
        print(f"   ❌ Erreur: {path}")
    print()
    
    # Configuration 3: Mode Tata
    print("🎭 Configuration 3: Mode Tata")
    mask.set_font_size(12)
    mask.set_auto_fit(True)
    mask.set_bold(True)
    mask.set_decoration_style("tata_line_pattern")
    mask.set_text_color("yellow")
    mask.set_decoration_color("orange")
    
    print(f"   Police: {mask.font_size}px (auto), Gras: {mask.bold_text}")
    print(f"   Déco: {mask.decoration_style}, Couleurs: {mask.get_color_name(mask.text_color)}/{mask.get_color_name(mask.decoration_color)}")
    
    # Export
    success, path = mask.export_config("tata_config.json")
    if success:
        print(f"   ✅ Exporté: {os.path.basename(path)}")
    else:
        print(f"   ❌ Erreur: {path}")
    print()
    
    # Test d'import
    print("📥 TEST D'IMPORT")
    print("Configuration actuelle (avant import):")
    print(f"   Police: {mask.font_size}px, Auto: {mask.auto_fit}, Gras: {mask.bold_text}")
    print(f"   Déco: {mask.decoration_style}, Couleurs: {mask.get_color_name(mask.text_color)}/{mask.get_color_name(mask.decoration_color)}")
    print()
    
    # Import gaming config
    print("🔄 Import de gaming_config.json...")
    success, result = mask.import_config("gaming_config.json")
    if success:
        print(f"   ✅ Succès: {result}")
        print("Configuration après import:")
        print(f"   Police: {mask.font_size}px, Auto: {mask.auto_fit}, Gras: {mask.bold_text}")
        print(f"   Déco: {mask.decoration_style}, Couleurs: {mask.get_color_name(mask.text_color)}/{mask.get_color_name(mask.decoration_color)}")
    else:
        print(f"   ❌ Erreur: {result}")
    print()
    
    # Liste des configs
    print("📁 CONFIGURATIONS DISPONIBLES:")
    configs = mask.list_config_files()
    for i, config in enumerate(configs, 1):
        print(f"   {i}. {config}")
    print()
    
    print("✅ Test terminé!")
    print()
    print("🎯 UTILISATION DANS L'INTERFACE:")
    print("   export                    - Sauvegarde auto avec timestamp")
    print("   export:ma_config.json     - Sauvegarde avec nom personnalisé")
    print("   import:gaming_config.json - Charge une configuration")
    print("   configs                   - Liste les configs disponibles")
    print("=" * 60)

if __name__ == "__main__":
    test_config_system()
