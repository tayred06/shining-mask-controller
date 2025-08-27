#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration du système de couleurs - test rapide
"""

import sys
import os

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ultimate_text_display_with_bold import CompleteMaskController

def test_color_system():
    """Test rapide du système de couleurs"""
    print("🌈 TEST DU SYSTÈME DE COULEURS")
    print("=" * 40)
    
    # Créer le contrôleur
    controller = CompleteMaskController()
    
    # Test 1: Couleurs de base
    print("\n✅ Test 1: Couleurs de base")
    print(f"Texte par défaut: {controller.get_color_name(controller.text_color)}")
    print(f"Déco par défaut: {controller.get_color_name(controller.decoration_color)}")
    
    # Test 2: Changement de couleur du texte
    print("\n✅ Test 2: Changement couleur texte")
    result = controller.set_text_color("red")
    print(f"set_text_color('red'): {result}")
    print(f"Nouvelle couleur texte: {controller.get_color_name(controller.text_color)}")
    
    # Test 3: Changement de couleur des décorations
    print("\n✅ Test 3: Changement couleur décorations")
    result = controller.set_decoration_color("blue")
    print(f"set_decoration_color('blue'): {result}")
    print(f"Nouvelle couleur déco: {controller.get_color_name(controller.decoration_color)}")
    
    # Test 4: Test avec couleur invalide
    print("\n✅ Test 4: Couleur invalide")
    result = controller.set_text_color("purple")
    print(f"set_text_color('purple'): {result}")
    print(f"Couleur texte inchangée: {controller.get_color_name(controller.text_color)}")
    
    # Test 5: Génération d'image
    print("\n✅ Test 5: Génération d'image colorée")
    controller.set_text_color("green")
    controller.set_decoration_color("yellow")
    controller.decoration_style = "lines"
    controller.show_decorations = True
    
    pixel_map = controller.get_text_image("TEST")
    print(f"Image générée: {len(pixel_map)} colonnes")
    
    # Test 6: Génération de couleurs
    print("\n✅ Test 6: Génération tableau couleurs")
    color_array = controller.encode_color_array_for_mask(pixel_map)
    print(f"Tableau couleurs: {len(color_array)} bytes")
    print(f"Couleurs/pixel: {len(color_array) // (len(pixel_map) * 16)} bytes")
    
    # Vérifier les premières couleurs (décorations)
    if len(color_array) >= 9:
        r1, g1, b1 = color_array[0], color_array[1], color_array[2]
        print(f"Premier pixel RGB: ({r1}, {g1}, {b1})")
        if controller.decoration_color == (255, 255, 0):  # Jaune
            print("✅ Couleur jaune détectée pour décoration!")
        else:
            print("❌ Couleur décoration incorrecte")
    
    print("\n🎉 Tests terminés!")

if __name__ == "__main__":
    test_color_system()
