# 🟢 Scripts Fonctionnels

Ce dossier contient les scripts qui **fonctionnent parfaitement** et sont prêts à l'emploi.

## Scripts disponibles :

### `quick_mask_demo.py` ⭐
- **Status** : ✅ Fonctionne parfaitement
- **Description** : Démonstration rapide du contrôle d'images
- **Usage** : `python working/quick_mask_demo.py`
- **Fonctionnalités** : Affiche une séquence d'images (1,2,1,2,1,1)

### `encrypted_mask_control.py` ⭐
- **Status** : ✅ Fonctionne parfaitement  
- **Description** : Contrôleur complet pour 20 images + option texte
- **Usage** : `python working/encrypted_mask_control.py`
- **Fonctionnalités** : 
  - Contrôle des 20 images prédéfinies
  - Changement de couleurs
  - Interface interactive

### `advanced_mask_control.py` ⭐⭐ **NOUVEAU !**
- **Status** : ✅ Fonctionne parfaitement + Contrôle luminosité !
- **Description** : Contrôleur complet avec luminosité et couleurs
- **Usage** : `python working/advanced_mask_control.py`
- **Fonctionnalités** : 
  - **🔆 Contrôle de luminosité (0-255)**
  - Contrôle des 20 images prédéfinies
  - Changement de couleurs RGB
  - Démonstrations interactives
  - Mode interactif complet

### `brightness_controller.py` 🔆
- **Status** : ✅ Fonctionne parfaitement
- **Description** : Contrôleur spécialisé pour la luminosité
- **Usage** : `python working/brightness_controller.py`
- **Fonctionnalités** : 
  - Réglage luminosité précis
  - Mode interactif luminosité
  - Démonstration des niveaux

### `basic_image_test.py` ⭐
- **Status** : ✅ Fonctionne (à tester après reset)
- **Description** : Version simplifiée pour tests après problèmes
- **Usage** : `python working/basic_image_test.py`
- **Fonctionnalités** : Test de base + démo couleurs

## 🔑 Notes importantes :
- Ces scripts utilisent le protocole AES découvert
- Clé de chiffrement : `32672f7974ad43451d9c6c894a0e8764`
- Caractéristique BLE : `d44bc439-abfd-45a2-b575-925416129600`

## 🆕 **NOUVELLE FONCTIONNALITÉ : Contrôle de Luminosité**

### Commande LIGHT découverte :
- **Commande** : `LIGHT` (hex: `4c49474854`)
- **Arguments** : 1 byte pour luminosité (0-255)
- **Recommandation** : Maximum 100 pour éviter le scintillement
- **Usage** : Intégré dans `advanced_mask_control.py`

### Niveaux recommandés :
- **10-30** : Faible luminosité (économie batterie)
- **50-75** : Luminosité normale 
- **100** : Luminosité maximale recommandée
- **>100** : Risque de scintillement

## 📋 Pour utiliser :
1. Assurer que le masque est allumé et à proximité
2. **RECOMMANDÉ** : Commencer par `advanced_mask_control.py`
3. Le masque sera détecté automatiquement
4. Profiter du contrôle complet luminosité + couleurs !
