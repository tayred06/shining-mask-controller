# 🎮 Contrôleur Clavier pour Masque LED

## 🎯 Projet inspiré de shining-mask

Ce projet s'inspire du [shining-mask](https://github.com/shawnrancatore/shining-mask) de shawnrancatore, mais remplace la manette Wii Nunchuck par un contrôle clavier.

### 🔄 Comparaison avec l'original

| **shining-mask (Original)** | **Notre Version** |
|------------------------------|-------------------|
| Manette Wii Nunchuck | ⌨️ Clavier |
| CircuitPython | 🐍 Python standard |
| 20 images préchargées | 📸 15 images mappées (extensible à 20) |
| Joystick analogique | 🔤 Touches lettres (QWERT/ASDFG/ZXCVB) |
| Boutons C/Z | 🎬 Flèches directionnelles |
| Clignotement automatique | 👁️ Clignotement automatique conservé |
| Gestes | 🎨 Couleurs + Actions spéciales |

## 🚀 Installation et Utilisation

### Prérequis
```bash
# Installer les dépendances
pip install keyboard bleak cryptography pillow
```

### Démarrage rapide
```bash
# Lancer le contrôleur interactif
python src/simplified_keyboard_controller.py

# Ou test sans interaction
python test_simplified_controller.py
```

## 🎮 Commandes Clavier

### 📸 Images Préchargées
```
Q W E R T  →  Images 1-5
A S D F G  →  Images 6-10  
Z X C V B  →  Images 11-15
```

### 🎬 Animations
```
↑ (Flèche Haut)    →  Pulse (pulsation)
↓ (Flèche Bas)     →  Wave (vague)
← (Flèche Gauche)  →  Fire (feu)
→ (Flèche Droite)  →  Rain (pluie)
SPACE              →  Matrix
```

### 🎭 Actions Spéciales
```
ENTER      →  Clignotement manuel
BACKSPACE  →  Image aléatoire
TAB        →  Effacer l'écran
```

### 🎨 Couleurs Rapides
```
Shift+R  →  Rouge
Shift+G  →  Vert
Shift+B  →  Bleu
Shift+W  →  Blanc
```

### ⚙️ Contrôles Système
```
H    →  Afficher l'aide
ESC  →  Quitter
```

## 🎭 Fonctionnalités Héritées de shining-mask

### ✅ Conservées
- **Images préchargées** : 20 emplacements pour des images custom
- **Clignotement automatique** : 4% de chance toutes les 100ms
- **Séquences d'animation** : Frames à 12 FPS pour le clignotement
- **Commandes PLAY** : Format compatible avec les images du masque
- **Gestion des erreurs** : Reconnexion automatique

### 🆕 Améliorations
- **Contrôle clavier** : Plus accessible que Wii Nunchuck
- **Animations couleur** : Système stable sans déconnexion
- **Interface claire** : Aide intégrée et retours visuels
- **Architecture modulaire** : Code organisé et extensible

## 🔧 Architecture Technique

### Structure des fichiers
```
src/
├── simplified_keyboard_controller.py  # Contrôleur principal
├── modules/
│   ├── text/scrolling_controller.py   # Base de communication
│   ├── animations/stable_animation_controller.py  # Animations couleur
│   └── config/config_manager.py       # Configuration
└── test_simplified_controller.py      # Tests automatisés
```

### Protocole de communication
- **Chiffrement** : AES-128 ECB (compatible shining-mask)
- **Commandes PLAY** : `PLAY01` à `PLAY20` pour les images
- **Commandes couleur** : `FCRRGGBB` pour les couleurs
- **BLE GATT** : Même UUID que l'original

## 🎯 Utilisation Gaming/Interactive

### Mode Performance
```python
# Réactivité maximale (20 FPS)
controller.process_commands()  # 50ms par cycle

# Clignotement réaliste (comme l'original)
controller.auto_blink_loop()  # 4% de chance toutes les 100ms
```

### Séquences d'expressions
```python
# Clignotement (inspiré de l'original)
blink_sequence = [6, 7, 7, 6]  # Ouverts → Mi-fermés → Fermés → Ouverts

# Extensible pour d'autres expressions
smile_sequence = [2, 3, 4]     # Sourire progressif
wink_sequence = [5, 6, 5]      # Clin d'œil
```

## 📊 Performance et Stabilité

### ✅ Tests validés
- **Connexion BLE** : Stable avec MASK-3B9D97
- **Envoi d'images** : 15 images testées avec succès
- **Clignotement** : Séquence fluide à 12 FPS
- **Couleurs** : 4 couleurs de base fonctionnelles
- **Gestion d'erreurs** : Reconnexion automatique

### 🎮 Réactivité
- **Délai de réponse** : < 50ms par commande
- **FPS clignotement** : 12 FPS (comme l'original)
- **Auto-blink** : 4% de chance/100ms (comme l'original)

## 🔄 Migration depuis shining-mask

### Équivalences de commandes
| **Wii Nunchuck** | **Clavier** | **Action** |
|-------------------|-------------|------------|
| Joystick X > 200 | Q,W,E,R,T | Images 1-5 |
| Joystick X < 50  | A,S,D,F,G | Images 6-10 |
| Bouton C | BACKSPACE | Image aléatoire |
| Bouton Z | ENTER | Clignotement |
| Auto-blink | Auto-blink | 4% chance/100ms |

### Format des images
- **Compatible** : Même format PLAY01-PLAY20
- **Résolution** : 64x16 pixels (comme l'original)
- **Upload** : Utilise le même protocole d'upload d'images

## 🎉 Résultat

**Contrôleur clavier fonctionnel inspiré de shining-mask !**

- ✅ **15 images** mappées et testées
- ✅ **5 animations** couleur stables  
- ✅ **Clignotement automatique** comme l'original
- ✅ **Interface clavier** intuitive
- ✅ **Architecture extensible** pour plus de fonctionnalités

**Prêt pour du gaming interactif et des démonstrations ! 🎭🎮**
