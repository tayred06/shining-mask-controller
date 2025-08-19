# 🔴 Scripts Cassés/Problématiques

Ce dossier contient les scripts qui ont causé des **problèmes** ou qui ne fonctionnent **plus** après certains tests.

## Scripts problématiques :

### `minimal_bitmap_test.py` ❌
- **Status** : 🚨 DANGEREUX - A causé le blocage du masque
- **Description** : Test de bitmap minimal qui a rendu le masque non-responsif
- **Problème** : 
  - Upload de bitmap a bloqué l'interface du masque
  - Plus aucune réponse visuelle après exécution
  - Flèche d'upload figée/buggée
- **⚠️ NE PAS UTILISER** sans reset physique du masque

### `mask_reset_test.py` ❌
- **Status** : ❌ Non fonctionnel
- **Description** : Tentative de reset du masque via commandes logicielles
- **Problème** :
  - Commandes envoyées sans erreur
  - Aucun effet visuel sur le masque
  - Reset logiciel insuffisant
- **Leçon** : Le reset logiciel ne fonctionne pas, reset physique nécessaire

## 🚨 Leçons apprises :

### Problème principal :
Les tests d'upload de bitmap ont saturé ou corrompu l'état interne du masque, le rendant non-responsif aux commandes d'affichage.

### Solutions identifiées :
1. **Reset physique obligatoire** : Éteindre/rallumer le masque
2. **App mobile officielle** : Peut faire un factory reset
3. **Éviter les uploads bitmap** : Tant que le format n'est pas maîtrisé

### État du masque après ces tests :
- ✅ Connexion BLE fonctionne
- ✅ Commandes envoyées sans erreur
- ❌ Aucune réponse visuelle
- ❌ Interface figée en mode upload

## 🔧 Récupération :
Si le masque est dans cet état :
1. Éteindre complètement (bouton power long)
2. Attendre 30 secondes minimum
3. Rallumer
4. Utiliser uniquement les scripts du dossier `working/`
