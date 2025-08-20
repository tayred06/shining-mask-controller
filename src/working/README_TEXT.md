# 🎬 Texte Défilant sur Masque LED - Guide Complet

## Vue d'ensemble

Vous disposez maintenant d'un **système complet de texte défilant** pour votre masque LED ! Plusieurs modes d'affichage sont disponibles avec un contrôle précis de la vitesse.

## 🚀 Utilisation Rapide

### Script Simple
```bash
# Défilement vers la gauche (par défaut)
python simple_scrolling_text.py "MON MESSAGE"

# Avec options personnalisées
python simple_scrolling_text.py "HELLO WORLD" --mode scroll_right --speed 70

# Mode interactif
python simple_scrolling_text.py
```

### Script de Test Rapide
```bash
python quick_scroll_test.py
```

## 📋 Modes Disponibles

| Mode | Description | Exemple d'usage |
|------|-------------|-----------------|
| **scroll_left** | Texte qui défile de droite vers gauche | Messages longs, annonces |
| **scroll_right** | Texte qui défile de gauche vers droite | Effet inverse, variété |
| **blink** | Texte qui clignote | Alertes, notifications |
| **steady** | Texte fixe (statique) | Affichage permanent |

## ⚙️ Paramètres de Configuration

### Vitesse de Défilement
- **Range** : 0-255
- **0** : Très lent
- **50** : Vitesse normale (recommandée)
- **100** : Rapide
- **255** : Très rapide

### Recommandations de Vitesse
- **Texte court** (< 10 caractères) : 30-50
- **Texte moyen** (10-20 caractères) : 40-60
- **Texte long** (> 20 caractères) : 50-80

## 🎮 Utilisation Programmatique

### Import et Initialisation
```python
from scrolling_text_controller import ScrollingMaskController

async def main():
    mask = ScrollingMaskController()
    await mask.connect()
    
    # Configuration de base
    await mask.set_brightness(80)
    await mask.set_background_color(0, 0, 0)  # Fond noir
    await mask.set_foreground_color(255, 255, 255)  # Texte blanc
```

### Affichage de Texte Défilant
```python
# Défilement simple
await mask.set_scrolling_text("MON MESSAGE", "scroll_left", 50)

# Avec paramètres avancés
await mask.set_scrolling_text(
    text="Message personnalisé",
    scroll_mode="scroll_right", 
    speed=60,
    width_multiplier=2.0  # Plus d'espace pour le défilement
)
```

### Contrôles Avancés
```python
# Changer uniquement le mode
await mask.set_mode("blink")

# Changer uniquement la vitesse
await mask.set_scroll_speed(80)

# Couleurs personnalisées
await mask.set_foreground_color(255, 0, 0)  # Texte rouge
await mask.set_background_color(0, 0, 255)  # Fond bleu
```

## 🎉 Conclusion

Votre masque LED dispose maintenant d'un **système de texte défilant professionnel** avec :

- 🎬 **4 modes d'affichage** différents
- ⚡ **Contrôle précis de la vitesse**
- 🎨 **Personnalisation des couleurs** 
- 📱 **Interface simple** d'utilisation
- 🔧 **API complète** pour intégration

**Le texte défile parfaitement sur votre masque !** 🎉

## 📱 Utilisation du fichier text_display.py

### 1. Lancement du programme
```bash
cd src/working
python3 text_display.py
```

### 2. Mode interactif
Une fois connecté au masque, utilisez ces commandes :

- `text HELLO` - Affiche "HELLO" en statique
- `scroll BONJOUR` - Fait défiler "BONJOUR"
- `demo` - Démonstration complète avec couleurs
- `quit` - Quitter le programme

### 3. Exemples d'utilisation

```
📝 AFFICHEUR DE TEXTE MASQUE LED
🔍 Recherche du masque LED...
🔗 Connexion à MASK-12345...
✅ Connecté au masque

texte> text HELLO
📝 Affichage: 'HELLO'
✅ Texte 'HELLO' affiché avec succès

texte> scroll MASQUE LED FONCTIONNE
📜 Défilement: 'MASQUE LED FONCTIONNE'
📍 Défilement: 0%
📍 Défilement: 10%
...
✅ Défilement terminé

texte> demo
🎭 DÉMONSTRATION TEXTE
📝 Affichage: 'HELLO'
📝 Affichage: 'WORLD'
...

texte> quit
👋 Mode interactif terminé
🔌 Déconnecté du masque
```

## 🎨 Couleurs disponibles

Le texte supporte les couleurs RGB :
- Rouge : (255, 0, 0)
- Vert : (0, 255, 0)
- Bleu : (0, 0, 255)
- Jaune : (255, 255, 0)
- Magenta : (255, 0, 255)
- Cyan : (0, 255, 255)
- Blanc : (255, 255, 255)

## 📝 Caractères supportés

- Lettres : A-Z
- Chiffres : 0-9
- Ponctuation : ! ? (espace)

## ⚠️ Notes importantes

1. **Connexion** : Le masque doit être allumé et en mode appairage
2. **Distance** : Restez proche du masque (< 5 mètres)
3. **Texte long** : Utilisez `scroll` pour les messages longs
4. **Majuscules** : Le texte est automatiquement converti en majuscules

## 🔧 Dépannage

Si le masque ne répond plus :
```bash
python3 ../debug/emergency_reset.py
```

Si problème de connexion :
```bash
python3 ../debug/check_mask_state.py
```
