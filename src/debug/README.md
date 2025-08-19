# 🔧 Scripts de Debug et Diagnostics

Ce dossier contient les outils de **diagnostic** et de **dépannage** pour analyser et réparer les problèmes du masque.

## Outils de debug :

### `emergency_reset.py` 🚨
- **Status** : 🔧 Outil de dépannage
- **Description** : Reset d'urgence pour débloquer le masque
- **Usage** : `python debug/emergency_reset.py`
- **Fonctionnalités** :
  - Déconnexion/reconnexion BLE
  - Séquence de commandes de reset
  - Test de récupération d'état
- **Efficacité** : Limitée - reset physique souvent nécessaire

### `notification_decoder.py` 🔍
- **Status** : ✅ Outil fonctionnel
- **Description** : Déchiffre et analyse les notifications du masque
- **Usage** : `python debug/notification_decoder.py`
- **Fonctionnalités** :
  - Déchiffrement AES des réponses
  - Affichage ASCII des commandes
  - Test de différents formats DATS
- **Utilité** : **Très utile** pour comprendre les réponses du masque

### `debug_mask.py` 🔍
- **Status** : 🔧 Outil d'analyse
- **Description** : Debug approfondi de la communication BLE
- **Fonctionnalités** :
  - Analyse complète des services BLE
  - Test interactif de commandes
  - Session de debug en ligne de commande

### `check_mask_state.py` 📊
- **Status** : 🔧 Outil de diagnostic
- **Description** : Vérification de l'état du masque
- **Fonctionnalités** :
  - Test de connectivité
  - Vérification des réponses
  - Diagnostic de l'état général

## 🛠️ Utilisation des outils :

### Pour diagnostiquer un problème :
1. `check_mask_state.py` - État général
2. `notification_decoder.py` - Analyser les réponses
3. `debug_mask.py` - Tests approfondis

### Pour récupérer un masque bloqué :
1. `emergency_reset.py` - Tentative de reset logiciel
2. Si échec → Reset physique (éteindre/rallumer)
3. Test avec `working/basic_image_test.py`

## 📝 Découvertes importantes :
- Le masque répond **DATSOK** (pas DATOK comme dans la doc)
- Les confirmations sont : DATSOK → REOKOK → DATCPOK
- Le déchiffrement AES est nécessaire pour lire les réponses
- Reset logiciel insuffisant en cas de blocage sévère
