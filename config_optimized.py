#!/usr/bin/env python3
"""
Configuration centralisée pour le Shining Mask Controller
========================================================
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class PatternConfig:
    """Configuration d'un pattern"""
    name: str
    text: str
    color: Tuple[int, int, int]
    category: str

@dataclass
class KeyMapping:
    """Configuration du mapping clavier"""
    key: str
    action_type: str  # 'pattern', 'animation', 'action', 'color'
    value: str

class MaskControllerConfig:
    """Configuration principale du contrôleur"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.patterns: Dict[int, PatternConfig] = {}
        self.key_mappings: List[KeyMapping] = []
        self.ble_settings = {}
        self.animation_settings = {}
        
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """Chemin de configuration par défaut"""
        return str(Path(__file__).parent / "config" / "mask_config.json")
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Charger les patterns
            for pattern_id, pattern_data in config.get('patterns', {}).items():
                self.patterns[int(pattern_id)] = PatternConfig(**pattern_data)
            
            # Charger les mappings clavier
            for mapping_data in config.get('key_mappings', []):
                self.key_mappings.append(KeyMapping(**mapping_data))
            
            # Autres paramètres
            self.ble_settings = config.get('ble', {})
            self.animation_settings = config.get('animations', {})
            
        except FileNotFoundError:
            print("⚠️ Configuration non trouvée, création des valeurs par défaut")
            self._create_default_config()
    
    def _create_default_config(self):
        """Crée une configuration par défaut"""
        # Patterns par défaut (améliorés)
        default_patterns = {
            # Émotions de base
            1: PatternConfig("Happy", ":)", (255, 255, 0), "emotion"),
            2: PatternConfig("Neutral", ":|", (255, 255, 255), "emotion"),
            3: PatternConfig("Sad", ":(", (100, 150, 255), "emotion"),
            4: PatternConfig("Surprised", ":O", (255, 150, 0), "emotion"),
            5: PatternConfig("Angry", ">:(", (255, 50, 50), "emotion"),
            
            # Actions/États
            6: PatternConfig("Wink", ";)", (255, 255, 0), "action"),
            7: PatternConfig("Sleep", "-_-", (150, 150, 150), "action"),
            8: PatternConfig("Love", "<3", (255, 100, 150), "emotion"),
            9: PatternConfig("Cool", "B)", (100, 255, 255), "style"),
            10: PatternConfig("Dizzy", "X_X", (255, 100, 255), "state"),
            
            # Symboles
            11: PatternConfig("Star", "*", (255, 255, 100), "symbol"),
            12: PatternConfig("Circle", "o", (255, 255, 255), "symbol"),
            13: PatternConfig("Big Circle", "O", (100, 255, 100), "symbol"),
            14: PatternConfig("Plus", "+", (255, 100, 100), "symbol"),
            15: PatternConfig("Question", "?", (255, 255, 100), "symbol"),
            
            # Texte utile
            16: PatternConfig("OK", "OK", (100, 255, 100), "text"),
            17: PatternConfig("NO", "NO", (255, 100, 100), "text"),
            18: PatternConfig("YES", "YES", (100, 255, 100), "text"),
            19: PatternConfig("Alert", "!", (255, 150, 50), "alert"),
            20: PatternConfig("Hi", "HI", (100, 200, 255), "greeting"),
        }
        
        self.patterns = default_patterns
        
        # Mappings clavier par défaut
        default_mappings = [
            # Patterns émotions (ligne QWERT)
            KeyMapping("q", "pattern", "1"),  # :)
            KeyMapping("w", "pattern", "2"),  # :|
            KeyMapping("e", "pattern", "3"),  # :(
            KeyMapping("r", "pattern", "4"),  # :O
            KeyMapping("t", "pattern", "5"),  # >:(
            
            # Patterns actions (ligne ASDFG)
            KeyMapping("a", "pattern", "6"),  # ;)
            KeyMapping("s", "pattern", "7"),  # -_-
            KeyMapping("d", "pattern", "8"),  # <3
            KeyMapping("f", "pattern", "9"),  # B)
            KeyMapping("g", "pattern", "10"), # X_X
            
            # Patterns symboles (ligne ZXCVB)
            KeyMapping("z", "pattern", "11"), # *
            KeyMapping("x", "pattern", "12"), # o
            KeyMapping("c", "pattern", "13"), # O
            KeyMapping("v", "pattern", "14"), # +
            KeyMapping("b", "pattern", "15"), # ?
            
            # Animations
            KeyMapping("up", "animation", "pulse"),
            KeyMapping("down", "animation", "wave"),
            KeyMapping("left", "animation", "fire"),
            KeyMapping("right", "animation", "rain"),
            KeyMapping("space", "animation", "matrix"),
            
            # Actions spéciales
            KeyMapping("enter", "action", "blink"),
            KeyMapping("backspace", "action", "random"),
            KeyMapping("tab", "action", "clear"),
            
            # Couleurs
            KeyMapping("shift+r", "color", "red"),
            KeyMapping("shift+g", "color", "green"),
            KeyMapping("shift+b", "color", "blue"),
            KeyMapping("shift+w", "color", "white"),
            
            # Contrôle
            KeyMapping("h", "action", "help"),
            KeyMapping("esc", "action", "quit"),
        ]
        
        self.key_mappings = default_mappings
        
        # Paramètres BLE
        self.ble_settings = {
            "device_name_prefix": "MASK",
            "connection_timeout": 10,
            "retry_attempts": 3,
            "encryption_key": "32672f7974ad43451d9c6c894a0e8764"
        }
        
        # Paramètres animations
        self.animation_settings = {
            "auto_blink_enabled": True,
            "auto_blink_chance": 4,  # %
            "auto_blink_interval": 0.1,  # secondes
            "animation_fps": 12,
            "default_animation_duration": 3.0
        }
    
    def save_config(self):
        """Sauvegarde la configuration"""
        config_data = {
            "patterns": {
                str(pid): {
                    "name": pattern.name,
                    "text": pattern.text,
                    "color": pattern.color,
                    "category": pattern.category
                }
                for pid, pattern in self.patterns.items()
            },
            "key_mappings": [
                {
                    "key": mapping.key,
                    "action_type": mapping.action_type,
                    "value": mapping.value
                }
                for mapping in self.key_mappings
            ],
            "ble": self.ble_settings,
            "animations": self.animation_settings
        }
        
        # Créer le dossier de config si nécessaire
        config_path = Path(self.config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def get_pattern_by_id(self, pattern_id: int) -> PatternConfig:
        """Récupère un pattern par son ID"""
        return self.patterns.get(pattern_id)
    
    def get_patterns_by_category(self, category: str) -> Dict[int, PatternConfig]:
        """Récupère tous les patterns d'une catégorie"""
        return {
            pid: pattern 
            for pid, pattern in self.patterns.items() 
            if pattern.category == category
        }
    
    def get_key_mapping(self, key: str) -> KeyMapping:
        """Récupère le mapping pour une touche"""
        for mapping in self.key_mappings:
            if mapping.key == key:
                return mapping
        return None

# Configuration globale
config = MaskControllerConfig()

def get_config() -> MaskControllerConfig:
    """Récupère la configuration globale"""
    return config
