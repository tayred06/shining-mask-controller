# 🎭 Guide d'utilisation du Contrôleur Unifié

## 🚀 Démarrage rapide

### Exécution du contrôleur unifié
```bash
cd /Users/mathieu/my-python-project
.venv/bin/python src/unified_controller.py
```

## 📋 Menu principal

Quand vous lancez le contrôleur, vous avez 3 options :

```
=== 🎭 Contrôleur de Masque LED Unifié ===
1. Mode Texte 📝
2. Mode Animations 🌈  
3. Quitter ❌
```

## 📝 Mode Texte

### Commandes disponibles :
- **`texte "Votre message"`** - Affiche un texte avec défilement
- **`couleur rouge`** - Change la couleur (rouge, vert, bleu, blanc, jaune, magenta, cyan)
- **`vitesse 100`** - Change la vitesse de défilement (10-500ms)
- **`decoration blocks`** - Active les décorations (none, blocks, lines, dots)
- **`reset`** - Remet à zéro l'état du masque
- **`aide`** - Affiche l'aide
- **`retour`** - Retourne au menu principal

### Exemples d'utilisation :
```
texte "Bonjour le monde!"
couleur rouge
vitesse 150
decoration blocks
texte "Message avec déco"
```

## 🌈 Mode Animations

### Animations disponibles :
1. **Pulse** - Pulsation douce de couleur
2. **Wave** - Vague qui traverse l'écran  
3. **Fire** - Effet de feu animé
4. **Rain** - Gouttes de pluie qui tombent
5. **Matrix** - Effet Matrix avec caractères

### Utilisation :
1. Choisissez une animation (1-5)
2. L'animation se lance automatiquement
3. Appuyez sur **Entrée** pour arrêter
4. Retour au menu des animations

## ⚙️ Configuration

Le système utilise des fichiers de configuration JSON dans `src/working/` :

### Profils disponibles :
- **`elegant_config.json`** - Configuration élégante
- **`gaming_config.json`** - Configuration gaming
- **`follow.json`** - Configuration follow

### Structure d'un profil :
```json
{
    "text": {
        "color": "white",
        "speed": 100,
        "decoration": "blocks"
    },
    "animations": {
        "default": "pulse",
        "speed": 30
    }
}
```

## 🔧 Architecture modulaire

Le projet est organisé en modules :

### `src/modules/core/`
- **`base_controller.py`** - Communication BLE de base
- **`__init__.py`** - Exports du module

### `src/modules/text/`  
- **`scrolling_controller.py`** - Gestion du texte et défilement
- **`__init__.py`** - Exports du module

### `src/modules/animations/`
- **`animation_controller.py`** - Système d'animations
- **`__init__.py`** - Exports du module

### `src/modules/config/`
- **`config_manager.py`** - Gestion des configurations
- **`__init__.py`** - Exports du module

### `src/modules/utils/`
- **`image_utils.py`** - Utilitaires d'image
- **`__init__.py`** - Exports du module

## 🎯 Utilisation avancée

### Créer une nouvelle animation
```python
from src.modules.animations import AnimationController

# Hériter du contrôleur d'animation
class MonAnimation(AnimationController):
    def ma_nouvelle_animation(self, duration=5.0):
        # Votre code d'animation ici
        pass
```

### Utiliser les modules individuellement
```python
# Utiliser seulement le texte
from src.modules.text import ScrollingTextController
controller = ScrollingTextController()

# Utiliser seulement les animations  
from src.modules.animations import AnimationController
animator = AnimationController()
```

## 🐛 Dépannage

### Problème de connexion
- Vérifiez que le masque est allumé
- Assurez-vous que Bluetooth est activé
- Le masque doit contenir "MASK" dans son nom

### Problème d'imports
```bash
# Utiliser l'environnement virtuel
.venv/bin/python src/unified_controller.py
```

### Réinitialiser le masque
```
Mode texte → reset
```

## 📁 Fichiers importants

- **`src/unified_controller.py`** - Point d'entrée principal
- **`src/README_MODULES.md`** - Documentation technique détaillée
- **`requirements.txt`** - Dépendances Python
- **`src/working/`** - Configurations et tests

## 🎉 Prêt à utiliser !

Votre système modulaire est maintenant opérationnel avec :
- ✅ Gestion complète du texte
- ✅ 5 animations prêtes à l'emploi  
- ✅ Système de configuration flexible
- ✅ Architecture modulaire extensible
- ✅ Interface utilisateur intuitive

Lancez `python src/unified_controller.py` et amusez-vous ! 🚀
