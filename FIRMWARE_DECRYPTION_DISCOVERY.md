# 🎯 DÉCOUVERTE MAJEURE - Clé de déchiffrement firmware trouvée !

## 💥 RÉVÉLATION REDDIT - Reverse Engineering Shining Mask

**Source** : https://www.reddit.com/r/ReverseEngineering/comments/lr9xxr/comment/hqwox47/
**Auteur** : `seagal_impersonator`
**Date** : Il y a 4 ans

## 🔑 CLÉ DE CHIFFREMENT FIRMWARE

### Informations critiques découvertes :

**Masque** : **Lumen Couture LED Face Changing Mask** - EXACTEMENT le même type !
**Chiffrement** : **XOR avec clé de 128 octets**
**Architecture** : **ARM32LE** (ARM 32-bit Little Endian)

### Clé XOR (hex) :
```
2776639913bbb1cc89dd58e6c46e2cf362379679b11bcb3cd88d659eecc6324f76639927bbb1cc13dd58e6896e2cf3c4379679621bcb3cb18d659ed8c6324fec63992776b1cc13bb58e689dd2cf3c46e96796237cb3cb11b659ed88d324fecc699277663cc13bbb1e689dd58f3c46e2c796237963cb11bcb9ed88d654fecc632
```

### Firmwares déchiffrés :
- **TR1906R04-10_OTA.bin** : SHA-1 `36a3b4a1144ada273e03e08c91d6cb1b7fdb9f35`
- **TR1906R04-1-10_OTA.bin** : SHA-1 `f0f38c1faacf3fc2730b0809d381aecdd56566e2`

## 🛠️ SPÉCIFICATIONS TECHNIQUES

### Structure du firmware :
- **Offset code machine** : 1024 bytes
- **Taille TR1906R04-10** : 55,296 bytes
- **Taille TR1906R04-1-10** : 54,272 bytes
- **Constantes AES** détectées dans le code déchiffré

### Méthodologie de reverse engineering utilisée :
1. **Comparaison des firmwares** → Détection XOR vs AES-ECB
2. **Analyse d'entropie** (binwalk -E) → Identification sections chiffrées
3. **Distance de Hamming** → Détermination longueur de clé
4. **Séquences ARM32LE communes** → Scoring des clés candidates
5. **Validation avec constantes AES** → Confirmation déchiffrement

## 🎯 IMPLICATIONS RÉVOLUTIONNAIRES

### Ce que cette découverte nous permet :

#### 🔓 **NIVEAU 1 - Analyse du firmware**
- Déchiffrer complètement le firmware de notre masque
- Lire le code source ARM des commandes DATS, BITS, FRAM, etc.
- Comprendre EXACTEMENT pourquoi la flèche d'upload apparaît

#### ⚙️ **NIVEAU 2 - Modification firmware**
- Identifier le code responsable de l'affichage de la flèche
- Modifier/supprimer cette fonctionnalité
- Recompiler un firmware custom sans flèche

#### 🚀 **NIVEAU 3 - Firmware custom complet**
- Créer notre propre firmware optimisé
- Ajouter de nouvelles commandes
- Optimiser les performances d'affichage

## 🔍 PROCHAINES ÉTAPES POSSIBLES

### Option A - Analyse du firmware actuel :
1. Extraire le firmware de notre masque via BLE
2. Appliquer la clé XOR pour déchiffrer
3. Analyser le code ARM pour trouver la fonction de flèche
4. Comprendre les paramètres modifiables

### Option B - Récupération des firmwares déchiffrés :
1. Télécharger les firmwares déjà déchiffrés (lien pastebin dans le post)
2. Analyser directement le code source ARM
3. Rechercher les chaînes "DATS", "upload", "arrow", etc.

### Option C - Développement firmware custom :
1. Utiliser le firmware déchiffré comme base
2. Modifier le code pour supprimer la flèche
3. Recompiler et flasher sur le masque

## 🎊 CONCLUSION

Cette découverte **change complètement la donne** ! 

Au lieu de simplement **contourner** la flèche avec des astuces de luminosité, nous pouvons maintenant potentiellement **l'éliminer complètement au niveau firmware**.

**Cela transforme notre projet de "hack logiciel" en "modification firmware complète" !**

---

**Cette information Reddit est littéralement une mine d'or pour notre projet ! 🏆**

---
*Discovered: Firmware decryption key for Shining Mask / Lumen Couture LED masks*
