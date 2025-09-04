#!/usr/bin/env python3
"""
Module Config - Gestionnaire de configuration
=============================================

Classes pour gérer les configurations :
- Import/export de configurations
- Profils utilisateur
- Validation des paramètres
- Configurations par défaut
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

class ConfigManager:
    """
    Gestionnaire de configuration pour le masque LED
    """
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Utiliser le dossier working par défaut
            self.config_dir = os.path.join(os.path.dirname(__file__), '../../working')
        else:
            self.config_dir = config_dir
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(self.config_dir, exist_ok=True)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut"""
        return {
            "metadata": {
                "version": "2.0",
                "created_at": datetime.now().isoformat(),
                "description": "Configuration par défaut du masque LED"
            },
            "display": {
                "font_size": 12,
                "auto_fit": True,
                "bold_text": False
            },
            "scrolling": {
                "default_mode": "scroll_right",
                "default_speed": 50
            },
            "decorations": {
                "show_decorations": True,
                "decoration_style": "lines",
                "decoration_color": {
                    "r": 255,
                    "g": 255,
                    "b": 255,
                    "name": "BLANC"
                }
            },
            "text": {
                "text_color": {
                    "r": 255,
                    "g": 255,
                    "b": 255,
                    "name": "BLANC"
                }
            },
            "animations": {
                "fps": 30,
                "default_duration": 10.0,
                "auto_loop": True
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valide une configuration et retourne les erreurs"""
        errors = []
        
        # Vérifier la structure de base
        required_sections = ["metadata", "display", "scrolling", "decorations", "text"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Section manquante: {section}")
        
        # Valider les paramètres d'affichage
        if "display" in config:
            display = config["display"]
            if "font_size" in display:
                if not isinstance(display["font_size"], int) or not 6 <= display["font_size"] <= 32:
                    errors.append("font_size doit être un entier entre 6 et 32")
            
            if "auto_fit" in display:
                if not isinstance(display["auto_fit"], bool):
                    errors.append("auto_fit doit être un booléen")
        
        # Valider les couleurs
        for section_name in ["decorations", "text"]:
            if section_name in config:
                section = config[section_name]
                color_key = "decoration_color" if section_name == "decorations" else "text_color"
                
                if color_key in section:
                    color = section[color_key]
                    if not isinstance(color, dict):
                        errors.append(f"{color_key} doit être un objet")
                    else:
                        for rgb in ["r", "g", "b"]:
                            if rgb not in color:
                                errors.append(f"{color_key} manque la composante {rgb}")
                            elif not isinstance(color[rgb], int) or not 0 <= color[rgb] <= 255:
                                errors.append(f"{color_key}.{rgb} doit être un entier entre 0 et 255")
        
        return len(errors) == 0, errors
    
    def save_config(self, config: Dict[str, Any], filename: str = None) -> Tuple[bool, str]:
        """Sauvegarde une configuration"""
        try:
            # Valider la configuration
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                return False, f"Configuration invalide: {', '.join(errors)}"
            
            # Générer un nom de fichier si nécessaire
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"mask_config_{timestamp}.json"
            
            # Assurer l'extension .json
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Chemin complet
            filepath = os.path.join(self.config_dir, filename)
            
            # Sauvegarder
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True, filepath
            
        except Exception as e:
            return False, str(e)
    
    def load_config(self, filename: str) -> Tuple[bool, Dict[str, Any], str]:
        """Charge une configuration"""
        try:
            # Construire le chemin
            if not os.path.isabs(filename):
                filepath = os.path.join(self.config_dir, filename)
            else:
                filepath = filename
            
            # Vérifier l'existence
            if not os.path.exists(filepath):
                return False, {}, f"Fichier non trouvé: {filepath}"
            
            # Charger le fichier
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Valider
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                return False, config, f"Configuration invalide: {', '.join(errors)}"
            
            return True, config, "Configuration chargée avec succès"
            
        except Exception as e:
            return False, {}, str(e)
    
    def list_configs(self) -> List[str]:
        """Liste tous les fichiers de configuration disponibles"""
        try:
            files = []
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json') and filename.startswith('mask_config_'):
                    files.append(filename)
            
            return sorted(files, reverse=True)  # Plus récents en premier
            
        except Exception:
            return []
    
    def delete_config(self, filename: str) -> Tuple[bool, str]:
        """Supprime un fichier de configuration"""
        try:
            filepath = os.path.join(self.config_dir, filename)
            
            if not os.path.exists(filepath):
                return False, f"Fichier non trouvé: {filename}"
            
            os.remove(filepath)
            return True, f"Configuration supprimée: {filename}"
            
        except Exception as e:
            return False, str(e)
    
    def create_profile(self, name: str, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Crée un profil nommé"""
        try:
            # Ajouter des métadonnées de profil
            profile_config = config.copy()
            profile_config["metadata"]["profile_name"] = name
            profile_config["metadata"]["is_profile"] = True
            
            filename = f"profile_{name.lower().replace(' ', '_')}.json"
            return self.save_config(profile_config, filename)
            
        except Exception as e:
            return False, str(e)
    
    def list_profiles(self) -> List[str]:
        """Liste tous les profils disponibles"""
        try:
            profiles = []
            for filename in os.listdir(self.config_dir):
                if filename.startswith('profile_') and filename.endswith('.json'):
                    # Extraire le nom du profil
                    profile_name = filename[8:-5].replace('_', ' ').title()
                    profiles.append(profile_name)
            
            return sorted(profiles)
            
        except Exception:
            return []
    
    def get_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Retourne le nom d'une couleur à partir du RGB"""
        color_names = {
            (255, 255, 255): "BLANC",
            (255, 0, 0): "ROUGE",
            (0, 255, 0): "VERT", 
            (0, 0, 255): "BLEU",
            (255, 255, 0): "JAUNE",
            (255, 0, 255): "MAGENTA",
            (0, 255, 255): "CYAN",
            (255, 165, 0): "ORANGE",
            (128, 0, 128): "VIOLET",
            (255, 192, 203): "ROSE"
        }
        return color_names.get(rgb, f"RGB({rgb[0]},{rgb[1]},{rgb[2]})")
    
    def rgb_from_name(self, color_name: str) -> Tuple[int, int, int]:
        """Retourne le RGB d'une couleur à partir de son nom"""
        colors = {
            "blanc": (255, 255, 255),
            "white": (255, 255, 255),
            "rouge": (255, 0, 0),
            "red": (255, 0, 0),
            "vert": (0, 255, 0),
            "green": (0, 255, 0),
            "bleu": (0, 0, 255),
            "blue": (0, 0, 255),
            "jaune": (255, 255, 0),
            "yellow": (255, 255, 0),
            "magenta": (255, 0, 255),
            "cyan": (0, 255, 255),
            "orange": (255, 165, 0),
            "violet": (128, 0, 128),
            "purple": (128, 0, 128),
            "rose": (255, 192, 203),
            "pink": (255, 192, 203)
        }
        return colors.get(color_name.lower(), (255, 255, 255))
