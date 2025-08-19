# 🎭 Projet Contrôle Masque LED - Code Source

Ce dossier contient tous les scripts Python pour contrôler le masque LED via Bluetooth Low Energy.

## 📁 Structure organisée :

### 🟢 [`working/`](working/) - Scripts Fonctionnels ⭐
**À utiliser en priorité** - Scripts testés et validés
- `quick_mask_demo.py` - Démonstration rapide 
- `encrypted_mask_control.py` - Contrôleur complet (20 images)
- `basic_image_test.py` - Tests de base après problème
- `main.py` - Script principal

### 🟡 [`experimental/`](experimental/) - Scripts Expérimentaux 🧪
**En développement** - Fonctionnalités avancées mais instables
- `real_text_controller.py` - Contrôle de texte (protocole OK, affichage non confirmé)
- `corrected_text_controller.py` - Version corrigée DATSOK
- `simple_text_test.py` - Test texte simplifié
- `advanced_text_test.py` - Tests texte avancés
- `multi_char_text_test.py` - Tests multi-caractères
- `text_scroll_experiment.py` - Expérience de scroll

### 🔴 [`broken/`](broken/) - Scripts Problématiques ⚠️
**NE PAS UTILISER** - Scripts qui ont causé des dysfonctionnements
- `minimal_bitmap_test.py` - A bloqué le masque (upload bitmap)
- `mask_reset_test.py` - Reset logiciel non fonctionnel

### 🔧 [`debug/`](debug/) - Outils de Debug 🛠️
**Outils de diagnostic** - Pour analyser et réparer les problèmes
- `emergency_reset.py` - Reset d'urgence
- `notification_decoder.py` - Déchiffrement des réponses
- `debug_mask.py` - Debug approfondi
- `check_mask_state.py` - Vérification d'état

### 🔍 [`discovery/`](discovery/) - Scripts de Découverte 📚
**Historique du reverse engineering** - Scripts utilisés pour découvrir le protocole
- `discover_codes.py` - Découverte principale
- `systematic_discovery.py` - Exploration systématique
- Nombreux scripts de test et d'analyse

### 📝 [`stubs/`](stubs/) - Fichiers Vides 📄
**Fonctionnalités futures** - Placeholders pour développements futurs

## 🚀 Guide d'utilisation rapide :

### 1. Premier test (recommandé) :
```bash
python src/working/advanced_mask_control.py  # NOUVEAU ! Avec contrôle luminosité
```

### 2. Démonstration rapide :
```bash
python src/working/quick_mask_demo.py
```

### 3. En cas de problème :
```bash
python src/debug/emergency_reset.py
```

## 🔑 Informations techniques :

### Protocole découvert :
- **Chiffrement** : AES-128 ECB
- **Clé** : `32672f7974ad43451d9c6c894a0e8764`
- **Service BLE** : `d44bc439-abfd-45a2-b575-925416129600`

### Fonctionnalités validées :
- ✅ Contrôle de 20 images prédéfinies
- ✅ **Contrôle de luminosité (0-255) 🆕**
- ✅ Changement de couleurs RGB
- ✅ Modes d'affichage différents
- ⚠️ Texte scrollant (protocole OK, affichage non confirmé)

### État actuel :
- **Images** : Fonctionnalité complète et stable
- **Luminosité** : ✅ **Fonctionnalité complète avec commande LIGHT** 🆕
- **Couleurs** : Fonctionnalité complète et stable
- **Texte** : Protocole implémenté, problème d'affichage à résoudre
- **Upload bitmap** : Dangereux, peut bloquer le masque

## ⚠️ Précautions importantes :
1. **Éviter** les scripts du dossier `broken/`
2. **Reset physique** nécessaire si le masque se bloque
3. **Tests progressifs** pour nouvelles fonctionnalités
4. **Backup de l'état** avant tests risqués

## 📞 Dépannage :
Si le masque ne répond plus :
1. Script `debug/emergency_reset.py`
2. Reset physique (éteindre/rallumer)
3. Test avec `working/basic_image_test.py`
