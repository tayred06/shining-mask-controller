#!/usr/bin/env python3
"""
🔍 FIRMWARE STRING ANALYZER - Recherche des fonctions flèche d'upload
Analyse les firmwares déchiffrés pour trouver le code de la flèche
"""

import re
import struct
import binascii

class FirmwareStringAnalyzer:
    """Analyseur de chaînes et code ARM pour firmwares Shining Mask"""
    
    def __init__(self, firmware_path: str):
        self.firmware_path = firmware_path
        self.firmware_data = self.load_firmware()
        
    def load_firmware(self) -> bytes:
        """Charge le firmware en mémoire"""
        try:
            with open(self.firmware_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Erreur chargement {self.firmware_path}: {e}")
            return b""
    
    def extract_strings(self, min_length: int = 4) -> list:
        """Extrait toutes les chaînes ASCII du firmware"""
        strings = []
        current_string = ""
        offset = 0
        
        for i, byte in enumerate(self.firmware_data):
            if 32 <= byte <= 126:  # ASCII imprimable
                current_string += chr(byte)
            else:
                if len(current_string) >= min_length:
                    strings.append((offset, current_string))
                current_string = ""
                offset = i + 1
        
        return strings
    
    def search_upload_patterns(self) -> list:
        """Recherche spécifiquement les motifs liés à l'upload/flèche"""
        print(f"🔍 Recherche motifs upload dans {self.firmware_path}")
        
        # Motifs critiques pour la flèche d'upload
        critical_patterns = [
            # Commandes BLE
            r"DATS|DATCP|BITS|BUFF|FRAM",
            # Interface/UI
            r"upload|arrow|progress|loading|transfer",
            # Symboles flèche
            r"->|→|↑|▲|▶|►",
            # Firmware/Debug
            r"LED|mask|display|show|draw",
            # Protocole
            r"BLE|GATT|char|notify|write"
        ]
        
        strings = self.extract_strings()
        matches = []
        
        for pattern in critical_patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            for offset, string in strings:
                if regex.search(string):
                    matches.append((offset, string, pattern))
                    print(f"🎯 TROUVÉ: '{string}' @ 0x{offset:08x} (motif: {pattern})")
        
        return matches
    
    def search_hex_patterns(self) -> list:
        """Recherche des motifs binaires spécifiques"""
        print(f"🔍 Recherche motifs hexadécimaux...")
        
        # Motifs binaires pour "DATS", "DATCP", etc.
        hex_patterns = [
            (b"DATS", "Commande DATS"),
            (b"DATCP", "Commande DATCP"),  
            (b"BITS", "Commande BITS"),
            (b"BUFF", "Commande BUFF"),
            (b"FRAM", "Commande FRAM"),
            (b"LIGHT", "Commande LIGHT"),
            # Motifs UTF-8 pour flèches
            (b"\xe2\x86\x92", "Flèche droite →"),
            (b"\xe2\x86\x91", "Flèche haut ↑"),
            (b"\xe2\x96\xb2", "Triangle ▲"),
            (b"\xe2\x96\xb6", "Triangle droit ▶"),
        ]
        
        matches = []
        for pattern, description in hex_patterns:
            offset = 0
            while True:
                pos = self.firmware_data.find(pattern, offset)
                if pos == -1:
                    break
                matches.append((pos, pattern.hex(), description))
                print(f"🎯 HEX: {description} @ 0x{pos:08x} = {pattern.hex()}")
                offset = pos + 1
        
        return matches
    
    def analyze_arm_opcodes_around(self, offset: int, context: int = 32) -> str:
        """Analyse le code ARM autour d'un offset donné"""
        start = max(0, offset - context)
        end = min(len(self.firmware_data), offset + context)
        
        data = self.firmware_data[start:end]
        
        analysis = f"\n📍 ANALYSE ARM @ 0x{offset:08x}:\n"
        analysis += f"Contexte: 0x{start:08x} - 0x{end:08x}\n\n"
        
        # Hexdump
        analysis += "HEX:\n"
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            analysis += f"{start+i:08x}: {hex_str:<48} |{ascii_str}|\n"
        
        # Tentative de décodage ARM (simplifié)
        analysis += "\nARM (approximatif):\n"
        for i in range(0, len(data) - 3, 4):
            try:
                opcode = struct.unpack('<I', data[i:i+4])[0]
                analysis += f"{start+i:08x}: {opcode:08x}\n"
            except:
                break
        
        return analysis
    
    def generate_full_report(self) -> str:
        """Génère un rapport complet d'analyse"""
        print(f"📊 Génération rapport complet pour {self.firmware_path}")
        
        report = f"""
# 🔍 RAPPORT ANALYSE FIRMWARE - {self.firmware_path}

## 📋 Informations générales
- **Fichier**: {self.firmware_path}
- **Taille**: {len(self.firmware_data):,} bytes (0x{len(self.firmware_data):x})
- **Type**: Firmware ARM32LE déchiffré

## 🎯 RECHERCHE MOTIFS UPLOAD/FLÈCHE

### 🔤 Chaînes de caractères
"""
        
        # Analyse des chaînes
        upload_matches = self.search_upload_patterns()
        if upload_matches:
            for offset, string, pattern in upload_matches:
                report += f"- **0x{offset:08x}**: `{string}` (motif: {pattern})\n"
        else:
            report += "- ❌ Aucun motif de chaîne trouvé\n"
        
        report += "\n### 🔢 Motifs hexadécimaux\n"
        
        # Analyse hexadécimale
        hex_matches = self.search_hex_patterns()
        if hex_matches:
            for offset, hex_data, description in hex_matches:
                report += f"- **0x{offset:08x}**: `{hex_data}` ({description})\n"
                
                # Analyse du contexte ARM pour les matches importants
                if any(cmd in description for cmd in ["DATS", "DATCP", "flèche"]):
                    report += self.analyze_arm_opcodes_around(offset)
                    report += "\n---\n"
        else:
            report += "- ❌ Aucun motif hexadécimal trouvé\n"
        
        # Statistiques
        all_strings = self.extract_strings()
        report += f"""
## 📊 Statistiques
- **Chaînes totales**: {len(all_strings)}
- **Motifs upload**: {len(upload_matches)}
- **Motifs hex**: {len(hex_matches)}

## 🎯 CONCLUSIONS PRÉLIMINAIRES
"""
        
        if upload_matches or hex_matches:
            report += "✅ **Motifs trouvés** - Analyse approfondie possible\n"
            report += "🔍 **Prochaines étapes**: Analyse ARM détaillée des zones identifiées\n"
        else:
            report += "⚠️ **Peu de motifs** - Firmware peut être optimisé ou obfusqué\n"
            report += "💡 **Alternative**: Analyse des flux de données BLE en temps réel\n"
        
        return report

def analyze_both_firmwares():
    """Analyse les deux firmwares disponibles"""
    firmwares = [
        "TR1906R04-10_OTA.bin.out",
        "TR1906R04-1-10_OTA.bin.out"
    ]
    
    print("🚀 ANALYSE COMPLÈTE DES FIRMWARES DÉCHIFFRÉS")
    print("=" * 60)
    
    all_reports = []
    
    for firmware in firmwares:
        try:
            print(f"\n📁 ANALYSE: {firmware}")
            analyzer = FirmwareStringAnalyzer(firmware)
            report = analyzer.generate_full_report()
            all_reports.append(report)
            
            # Sauvegarde le rapport individuel
            report_file = f"firmware_analysis_{firmware.replace('.', '_')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"📄 Rapport sauvé: {report_file}")
            
        except Exception as e:
            print(f"❌ Erreur analyse {firmware}: {e}")
    
    # Rapport combiné
    combined_report = """
# 🔍 ANALYSE COMBINÉE DES FIRMWARES SHINING MASK

## 📊 Résumé exécutif
Cette analyse compare les deux firmwares déchiffrés pour identifier
les fonctions responsables de l'affichage de la flèche d'upload.

""" + "\n".join(all_reports)
    
    with open("FIRMWARE_COMPLETE_ANALYSIS.md", 'w') as f:
        f.write(combined_report)
    
    print(f"\n🎯 ANALYSE TERMINÉE")
    print("📁 Fichiers générés:")
    print("  - FIRMWARE_COMPLETE_ANALYSIS.md (rapport combiné)")
    for firmware in firmwares:
        report_file = f"firmware_analysis_{firmware.replace('.', '_')}.md"
        print(f"  - {report_file}")

if __name__ == "__main__":
    analyze_both_firmwares()
