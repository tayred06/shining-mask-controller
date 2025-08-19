# 🟡 Scripts Expérimentaux

Ce dossier contient les scripts qui implémentent des fonctionnalités avancées mais qui sont **en cours de développement**.

## Scripts disponibles :

### `real_text_controller.py` 🧪
- **Status** : ⚠️ Expérimental - Protocole OK, affichage non confirmé
- **Description** : Implémentation complète du protocole texte basé sur la doc officielle
- **Fonctionnalités** :
  - Upload de bitmap texte via DATS/Upload/DATCP
  - Configuration MODE/SPEED/FC/BC
  - Génération bitmap avec PIL
- **Problème** : Texte ne s'affiche pas visuellement sur le masque

### `corrected_text_controller.py` 🧪
- **Status** : ⚠️ Expérimental - Protocole corrigé avec DATSOK
- **Description** : Version corrigée après découverte que le masque répond DATSOK (pas DATOK)
- **Fonctionnalités** :
  - Protocole upload corrigé
  - Gestion des confirmations DATSOK/REOKOK/DATCPOK
  - Bitmap simplifié
- **Problème** : Upload réussit mais pas d'affichage visuel

### `simple_text_test.py` 🧪
- **Status** : ⚠️ Expérimental - Version simplifiée
- **Description** : Version allégée sans dépendance PIL
- **Fonctionnalités** :
  - Bitmap manuel simple
  - Protocole de base
- **Problème** : Même problème d'affichage

## 🔬 Notes de développement :
- Le protocole technique fonctionne (DATS → DATSOK → Upload → REOKOK → DATCP → DATCPOK)
- Les données sont uploadées avec succès
- Le problème semble être dans le format du bitmap ou l'activation de l'affichage
- Besoin d'analyser le format bitmap attendu par le masque

## 🎯 Prochaines étapes :
1. Analyser le format bitmap exact attendu
2. Tester avec des bitmaps plus simples (noir/blanc)
3. Vérifier s'il faut une commande d'activation supplémentaire
4. Comparer avec l'app mobile officielle
