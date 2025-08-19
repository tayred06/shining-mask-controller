# 🎭 Projet Contrôle Masque LED BLE

## 📖 Description

Projet Python pour la communication avec un masque LED via Bluetooth Low Energy (BLE). Ce projet explore les capacités de contrôle d'un masque LED intelligent et documente les découvertes sur son architecture.

## 🎯 Objectifs

- ✅ Établir une connexion BLE stable avec le masque
- ✅ Découvrir les services et caractéristiques BLE
- ✅ Tester les protocoles de communication
- ✅ Documenter l'architecture du dispositif

## 🔍 Découvertes Principales

### ✅ Contrôle Total du Masque Réalisé !

**BREAKTHROUGH :** Découverte du protocole crypté AES permettant le contrôle complet !

1. **Protocole crypté AES** → Chiffrement avec clé fixe découverte
2. **20 images contrôlables** → Sélection directe via BLE (ID 1-20)
3. **Format découvert** → `\x06PLAY\x01` + image_id + suffixe crypté

### Protocole BLE Découvert

- **Chiffrement** : AES ECB mode avec clé fixe
- **Format** : Commandes `\x06PLAY\x01XX` cryptées
- **Résultat** : Contrôle complet des patterns/images du masque ✅

### Informations Techniques

- **Dispositif** : MASK-3B9D97 (86179C2D-07A2-AD8E-6D64-08E8BEB9B6CD)
- **Caractéristique principale** : d44bc439-abfd-45a2-b575-925416129600
- **Codes testés** : 63+ codes (0x00-0x3F, A0XX format)

## 🚀 Installation

```bash
# Cloner le projet
git clone <repository-url>
cd my-python-project

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## 💻 Utilisation

### Script Principal - Contrôle Crypté ⭐

```bash
python src/encrypted_mask_control.py
```

**Fonctionnalités :**
- Contrôle complet des 20 images du masque
- Mode interactif pour sélection d'images
- Test automatique de toutes les images
- Protocole crypté AES découvert

### Script de Démonstration Rapide

```bash
python src/quick_mask_demo.py
```

**Démonstration rapide** du contrôle avec 5 images test.

### Scripts Historiques (Recherche)

```bash
# Script original (infrastructure BLE)
python src/main.py

# Debug BLE avancé
python src/debug_mask.py

# Tests de découverte
python src/final_pattern_test.py
```

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd my-python-project
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application
To run the application, execute the following command:
```
python src/main.py
```

### Running Tests
To run the unit tests, use the following command:
```
python -m unittest discover -s tests
```
or if you are using pytest:
```
pytest tests
```

## Contributing
Feel free to submit issues or pull requests to improve the project.

## License
This project is licensed under the MIT License - see the LICENSE file for details.