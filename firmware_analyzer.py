#!/usr/bin/env python3
"""
🔍 FIRMWARE ANALYZER - Shining Mask Reverse Engineering
Analyse et déchiffrement du firmware pour éliminer la flèche d'upload
"""

import requests
import binascii
import struct
import os
from typing import Optional, List, Tuple

class ShiningMaskFirmwareAnalyzer:
    """Analyseur de firmware pour masques LED Shining Mask / Lumen Couture"""
    
    # Clé XOR découverte par seagal_impersonator sur Reddit
    XOR_KEY_HEX = "2776639913bbb1cc89dd58e6c46e2cf362379679b11bcb3cd88d659eecc6324f76639927bbb1cc13dd58e6896e2cf3c4379679621bcb3cb18d659ed8c6324fec63992776b1cc13bb58e689dd2cf3c46e96796237cb3cb11b659ed88d324fecc699277663cc13bbb1e689dd58f3c46e2c796237963cb11bcb9ed88d654fecc632"
    
    def __init__(self):
        self.xor_key = binascii.unhexlify(self.XOR_KEY_HEX)
        self.decrypted_firmwares = {}
        
    def download_encrypted_firmware(self, url: str, filename: str) -> bool:
        """Télécharge un firmware chiffré"""
        try:
            print(f"📥 Téléchargement de {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ {filename} téléchargé avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur téléchargement {filename}: {e}")
            return False
    
    def xor_decrypt(self, data: bytes) -> bytes:
        """Déchiffre les données avec la clé XOR"""
        decrypted = bytearray()
        key_len = len(self.xor_key)
        
        for i, byte in enumerate(data):
            decrypted.append(byte ^ self.xor_key[i % key_len])
        
        return bytes(decrypted)
    
    def decrypt_firmware(self, encrypted_file: str, output_file: str) -> bool:
        """Déchiffre un firmware complet"""
        try:
            print(f"🔓 Déchiffrement de {encrypted_file}...")
            
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Le code machine commence à l'offset 1024
            header = encrypted_data[:1024]  # Header non chiffré
            encrypted_code = encrypted_data[1024:]  # Code chiffré
            
            decrypted_code = self.xor_decrypt(encrypted_code)
            
            # Reconstruit le firmware déchiffré
            full_decrypted = header + decrypted_code
            
            with open(output_file, 'wb') as f:
                f.write(full_decrypted)
            
            print(f"✅ Firmware déchiffré sauvé: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur déchiffrement: {e}")
            return False
    
    def analyze_firmware_strings(self, firmware_file: str) -> List[str]:
        """Recherche les chaînes de caractères dans le firmware"""
        try:
            with open(firmware_file, 'rb') as f:
                data = f.read()
            
            # Cherche les chaînes ASCII lisibles (min 4 caractères)
            strings = []
            current_string = ""
            
            for byte in data:
                if 32 <= byte <= 126:  # Caractères ASCII imprimables
                    current_string += chr(byte)
                else:
                    if len(current_string) >= 4:
                        strings.append(current_string)
                    current_string = ""
            
            return strings
            
        except Exception as e:
            print(f"❌ Erreur analyse strings: {e}")
            return []
    
    def search_upload_arrow_code(self, firmware_file: str) -> List[Tuple[int, str]]:
        """Recherche le code lié à la flèche d'upload"""
        print(f"🔍 Recherche du code de la flèche dans {firmware_file}...")
        
        strings = self.analyze_firmware_strings(firmware_file)
        
        # Motifs à rechercher
        arrow_patterns = [
            "DATS", "upload", "arrow", "->", "↑", "▲",
            "progress", "loading", "transfer", "send",
            "DATCP", "BITS", "BUFF", "FRAM"
        ]
        
        matches = []
        for i, string in enumerate(strings):
            for pattern in arrow_patterns:
                if pattern.lower() in string.lower():
                    matches.append((i, string))
                    print(f"🎯 Trouvé: '{string}' (motif: {pattern})")
        
        return matches
    
    def generate_firmware_report(self, firmware_file: str) -> str:
        """Génère un rapport d'analyse du firmware"""
        print(f"📊 Génération du rapport pour {firmware_file}...")
        
        report = f"""
# 🔍 RAPPORT D'ANALYSE FIRMWARE - {firmware_file}

## 📋 Informations générales
- **Fichier**: {firmware_file}
- **Taille**: {os.path.getsize(firmware_file) if os.path.exists(firmware_file) else 'N/A'} bytes
- **Architecture**: ARM32LE
- **Offset code**: 1024 bytes

## 🎯 Recherche code flèche d'upload
"""
        
        matches = self.search_upload_arrow_code(firmware_file)
        if matches:
            report += "\n### ✅ Motifs trouvés:\n"
            for i, string in matches:
                report += f"- **{i}**: `{string}`\n"
        else:
            report += "\n### ❌ Aucun motif évident trouvé\n"
        
        strings = self.analyze_firmware_strings(firmware_file)
        report += f"\n## 📝 Statistiques\n"
        report += f"- **Chaînes trouvées**: {len(strings)}\n"
        report += f"- **Motifs flèche**: {len(matches)}\n"
        
        if strings:
            report += f"\n## 🔤 Premières chaînes intéressantes:\n"
            for string in strings[:20]:
                if len(string) > 3:
                    report += f"- `{string}`\n"
        
        return report

def main():
    """Fonction principale d'analyse firmware"""
    print("🚀 DÉMARRAGE ANALYSE FIRMWARE SHINING MASK")
    print("=" * 50)
    
    analyzer = ShiningMaskFirmwareAnalyzer()
    
    # URLs des firmwares déjà déchiffrés (si disponibles)
    decrypted_url = "https://pastebin.com/raw/Usfp1s7w"  # Lien du post Reddit
    
    print("📥 Tentative de récupération des firmwares déchiffrés...")
    
    try:
        response = requests.get(decrypted_url)
        if response.status_code == 200:
            print("✅ Firmwares déchiffrés récupérés !")
            
            # Sauvegarde les firmwares déchiffrés
            with open("decrypted_firmwares.txt", 'w') as f:
                f.write(response.text)
            
            print("📄 Firmwares sauvés dans decrypted_firmwares.txt")
            
        else:
            print("⚠️ Impossible de récupérer les firmwares déchiffrés")
            print("💡 On va procéder à l'analyse alternative...")
            
    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
    
    # Génère un script d'analyse pour la suite
    analysis_script = """
# 🎯 PROCHAINES ÉTAPES

## 1. 📁 Récupération du firmware de votre masque
```python
# Se connecter au masque et extraire le firmware
await connect_to_mask()
firmware_data = await extract_firmware_via_ble()
```

## 2. 🔓 Déchiffrement avec la clé XOR
```python
analyzer = ShiningMaskFirmwareAnalyzer()
analyzer.decrypt_firmware("mask_firmware.bin", "decrypted_mask.bin")
```

## 3. 🔍 Analyse du code ARM
```bash
# Utiliser un décompilateur ARM comme Ghidra ou IDA
# Rechercher les fonctions contenant "DATS", "upload", etc.
```

## 4. ✂️ Modification du firmware
- Identifier la fonction d'affichage de flèche
- Modifier le code pour NOP (No Operation)
- Recalculer les checksums

## 5. 💾 Flash du firmware modifié
- Utiliser l'interface BLE OTA
- Flasher le nouveau firmware sans flèche
"""
    
    with open("firmware_analysis_plan.md", 'w') as f:
        f.write(analysis_script)
    
    print("\n🎯 Plan d'analyse créé dans firmware_analysis_plan.md")
    print("\n🚀 PRÊT POUR LE REVERSE ENGINEERING COMPLET !")

if __name__ == "__main__":
    main()
