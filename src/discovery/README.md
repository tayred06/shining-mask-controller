# 🔍 Scripts de Découverte et Exploration

Ce dossier contient tous les scripts utilisés pour **découvrir** et **analyser** le protocole du masque LED. Ces scripts ont servi au reverse engineering initial.

## 🎯 Scripts de découverte du protocole :

### `discover_codes.py` 📡
- **Description** : Script principal de découverte des codes de contrôle
- **Fonction** : Scan et analyse des commandes de base
- **Résultats** : A permis de découvrir le chiffrement AES

### `systematic_discovery.py` 🔬
- **Description** : Exploration systématique des commandes
- **Fonction** : Test méthodique de différents patterns
- **Utilité** : Mapping complet des fonctionnalités

### `pattern_explorer.py` 🧩
- **Description** : Analyse des patterns de communication
- **Fonction** : Identification des structures de commandes
- **Découverte** : Format des commandes cryptées

### `quick_discovery.py` ⚡
- **Description** : Tests rapides de fonctionnalités
- **Fonction** : Validation rapide d'hypothèses

## 🧪 Scripts de test et validation :

### `final_pattern_test.py` ✅
- **Description** : Tests finaux des patterns découverts
- **Fonction** : Validation du protocole complet

### `test_all_characteristics.py` 📋
- **Description** : Test de toutes les caractéristiques BLE
- **Fonction** : Cartographie complète des services

### `test_data_formats.py` 📊
- **Description** : Test des formats de données
- **Fonction** : Validation des structures de commandes

### `test_other_formats.py` 🔄
- **Description** : Test de formats alternatifs
- **Fonction** : Exploration d'options avancées

### `test_single_code.py` 🎯
- **Description** : Test d'une commande isolée
- **Fonction** : Debug ciblé

### `simple_test.py` 🧪
- **Description** : Test basique de connectivité
- **Fonction** : Validation de la communication de base

## 🖼️ Scripts d'analyse des images :

### `image_selector.py` 🎨
- **Description** : Sélecteur d'images interactif
- **Fonction** : Interface pour tester différentes images

### `image_upload_analyzer.py` 📤
- **Description** : Analyse du processus d'upload d'images
- **Fonction** : Reverse engineering du protocole d'upload

### `image_selection_codes.py` 🔢
- **Description** : Codes de sélection des images
- **Fonction** : Mapping des IDs d'images

### `mask_codes.py` 🎭
- **Description** : Collection des codes du masque
- **Fonction** : Base de données des commandes découvertes

## 🏆 Résultats de la découverte :

### Protocole découvert :
- **Chiffrement** : AES-128 ECB
- **Clé** : `32672f7974ad43451d9c6c894a0e8764`
- **Caractéristique** : `d44bc439-abfd-45a2-b575-925416129600`

### Commandes identifiées :
- **DATA** : Affichage d'images (1-20)
- **FC** : Couleur de premier plan
- **BC** : Couleur de fond
- **MODE** : Modes d'affichage
- **SPEED** : Vitesse d'animation
- **DATS** : Début d'upload de données
- **DATCP** : Fin d'upload de données

### Images disponibles :
- 20 images prédéfinies dans le masque
- Contrôle de couleur RGB
- Support de différents modes d'affichage

## 📚 Valeur historique :
Ces scripts représentent le travail de reverse engineering qui a permis de créer les scripts fonctionnels du dossier `working/`. Ils sont conservés pour référence et pour d'éventuelles découvertes futures.
