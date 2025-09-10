#!/usr/bin/env python3
"""
⚙️ FIRMWARE PATCHER - Modification du firmware pour éliminer la flèche
Patch le firmware pour désactiver complètement l'affichage de la flèche d'upload
"""

import struct
import shutil
import os
from typing import List, Tuple

class ShiningMaskFirmwarePatcher:
    """Patcheur de firmware pour éliminer la flèche d'upload"""
    
    # Adresses découvertes dans l'analyse
    FIRMWARE_TARGETS = {
        "TR1906R04-10_OTA.bin.out": {
            "DATSOK_ADDR": 0x00001dcc,
            "DATCPOK_ADDR": 0x00001dd4,
            "SIZE": 66100
        },
        "TR1906R04-1-10_OTA.bin.out": {
            "DATSOK_ADDR": 0x00001cd4, 
            "DATCPOK_ADDR": 0x00001cdc,
            "SIZE": 65840
        }
    }
    
    def __init__(self, firmware_path: str):
        self.firmware_path = firmware_path
        self.firmware_name = os.path.basename(firmware_path)
        self.config = self.FIRMWARE_TARGETS.get(self.firmware_name, {})
        self.firmware_data = self.load_firmware()
        
    def load_firmware(self) -> bytearray:
        """Charge le firmware en mémoire"""
        try:
            with open(self.firmware_path, 'rb') as f:
                return bytearray(f.read())
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return bytearray()
    
    def save_firmware(self, output_path: str) -> bool:
        """Sauvegarde le firmware modifié"""
        try:
            with open(output_path, 'wb') as f:
                f.write(self.firmware_data)
            print(f"✅ Firmware patché sauvé: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def backup_original(self) -> str:
        """Crée une sauvegarde du firmware original"""
        backup_path = f"{self.firmware_path}.backup"
        try:
            shutil.copy2(self.firmware_path, backup_path)
            print(f"💾 Sauvegarde créée: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return ""
    
    def analyze_dats_function(self) -> dict:
        """Analyse la fonction DATS pour comprendre son fonctionnement"""
        if not self.config:
            print("❌ Configuration firmware inconnue")
            return {}
        
        dats_addr = self.config["DATSOK_ADDR"]
        datcp_addr = self.config["DATCPOK_ADDR"]
        
        print(f"🔍 Analyse fonction DATS autour de 0x{dats_addr:08x}")
        
        # Analyse du contexte autour de DATSOK
        context_start = max(0, dats_addr - 100)
        context_end = min(len(self.firmware_data), dats_addr + 100)
        context_data = self.firmware_data[context_start:context_end]
        
        analysis = {
            "dats_addr": dats_addr,
            "datcp_addr": datcp_addr,
            "context_start": context_start,
            "context_data": context_data,
            "potential_patches": []
        }
        
        # Recherche des instructions ARM qui pourraient afficher la flèche
        # Recherche des appels de fonction autour de DATS
        for i in range(0, len(context_data) - 3, 4):
            try:
                opcode = struct.unpack('<I', context_data[i:i+4])[0]
                addr = context_start + i
                
                # Instructions ARM BL (Branch and Link) - appels de fonction
                if (opcode & 0xFF000000) == 0xEB000000:  # BL instruction
                    analysis["potential_patches"].append({
                        "addr": addr,
                        "opcode": opcode,
                        "type": "function_call",
                        "description": f"Appel fonction @ 0x{addr:08x}"
                    })
                
                # Instructions STR/LDR vers des adresses d'affichage  
                elif (opcode & 0x0E000000) == 0x04000000:  # STR/LDR
                    analysis["potential_patches"].append({
                        "addr": addr,
                        "opcode": opcode, 
                        "type": "memory_access",
                        "description": f"Accès mémoire @ 0x{addr:08x}"
                    })
                    
            except:
                continue
        
        print(f"🎯 Trouvé {len(analysis['potential_patches'])} instructions candidates")
        return analysis
    
    def create_arrow_disable_patches(self) -> List[dict]:
        """Crée des patches pour désactiver la flèche"""
        patches = []
        
        if not self.config:
            return patches
        
        # STRATÉGIE 1: Remplacer DATSOK par des NOP
        dats_addr = self.config["DATSOK_ADDR"]
        patches.append({
            "name": "disable_dats_message",
            "description": "Remplace DATSOK par des NOP",
            "addr": dats_addr,
            "original": b"DATSOK",
            "patch": b"\x00\x00\x00\x00\x00\x00",  # NUL bytes
            "type": "string_replace"
        })
        
        # STRATÉGIE 2: Remplacer DATCPOK par des NOP
        datcp_addr = self.config["DATCPOK_ADDR"]
        patches.append({
            "name": "disable_datcp_message", 
            "description": "Remplace DATCPOK par des NOP",
            "addr": datcp_addr,
            "original": b"DATCPOK",
            "patch": b"\x00\x00\x00\x00\x00\x00\x00",  # NUL bytes
            "type": "string_replace"
        })
        
        # STRATÉGIE 3: Analyser et NOP les appels de fonction d'affichage
        analysis = self.analyze_dats_function()
        for potential in analysis.get("potential_patches", []):
            if potential["type"] == "function_call":
                patches.append({
                    "name": f"nop_function_call_{potential['addr']:08x}",
                    "description": f"NOP appel fonction @ 0x{potential['addr']:08x}",
                    "addr": potential["addr"],
                    "original": struct.pack('<I', potential["opcode"]),
                    "patch": b"\x00\xF0\x20\xE3",  # ARM NOP instruction
                    "type": "instruction_nop"
                })
        
        return patches
    
    def apply_patch(self, patch: dict) -> bool:
        """Applique un patch spécifique"""
        try:
            addr = patch["addr"]
            original = patch["original"]
            new_data = patch["patch"]
            
            # Vérification que l'original correspond
            current_data = self.firmware_data[addr:addr+len(original)]
            if current_data != original:
                print(f"⚠️ Patch {patch['name']}: données ne correspondent pas")
                print(f"   Attendu: {original.hex()}")
                print(f"   Trouvé:  {current_data.hex()}")
                return False
            
            # Application du patch
            self.firmware_data[addr:addr+len(original)] = new_data
            print(f"✅ Patch appliqué: {patch['name']}")
            print(f"   @ 0x{addr:08x}: {original.hex()} → {new_data.hex()}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur patch {patch['name']}: {e}")
            return False
    
    def patch_firmware_complete(self, output_suffix: str = "_NO_ARROW") -> str:
        """Applique tous les patches pour éliminer la flèche"""
        print(f"🚀 PATCHING FIRMWARE: {self.firmware_name}")
        print("=" * 50)
        
        if not self.config:
            print("❌ Firmware non supporté")
            return ""
        
        # Sauvegarde
        backup_path = self.backup_original()
        if not backup_path:
            print("❌ Impossible de créer une sauvegarde - abandon")
            return ""
        
        # Génération des patches
        patches = self.create_arrow_disable_patches()
        print(f"🔧 {len(patches)} patches générés")
        
        # Application des patches
        applied_count = 0
        for patch in patches:
            if self.apply_patch(patch):
                applied_count += 1
        
        print(f"\n📊 RÉSULTAT: {applied_count}/{len(patches)} patches appliqués")
        
        # Sauvegarde du firmware patché
        base_name = self.firmware_path.replace(".out", "")
        output_path = f"{base_name}{output_suffix}.bin"
        
        if self.save_firmware(output_path):
            print(f"\n🎉 FIRMWARE PATCHÉ CRÉÉ AVEC SUCCÈS !")
            print(f"📁 Fichier: {output_path}")
            print(f"💾 Sauvegarde: {backup_path}")
            return output_path
        else:
            print(f"\n❌ Échec création firmware patché")
            return ""

def patch_all_firmwares():
    """Patch tous les firmwares disponibles"""
    firmwares = [
        "TR1906R04-10_OTA.bin.out",
        "TR1906R04-1-10_OTA.bin.out"
    ]
    
    print("🚀 PATCHING COMPLET - ÉLIMINATION FLÈCHE D'UPLOAD")
    print("=" * 60)
    
    patched_files = []
    
    for firmware in firmwares:
        if os.path.exists(firmware):
            print(f"\n📁 TRAITEMENT: {firmware}")
            patcher = ShiningMaskFirmwarePatcher(firmware)
            output_file = patcher.patch_firmware_complete()
            if output_file:
                patched_files.append(output_file)
        else:
            print(f"❌ Firmware non trouvé: {firmware}")
    
    print(f"\n🎯 RÉSUMÉ FINAL")
    print(f"Firmwares patchés: {len(patched_files)}")
    for file in patched_files:
        print(f"  ✅ {file}")
    
    if patched_files:
        print(f"\n🎉 MISSION ACCOMPLIE !")
        print(f"Les firmwares sans flèche sont prêts à être flashés !")
    
    return patched_files

if __name__ == "__main__":
    patch_all_firmwares()
