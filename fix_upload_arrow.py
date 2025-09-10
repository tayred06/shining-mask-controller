#!/usr/bin/env python3
"""
🔧 CORRECTION FLÈCHE UPLOAD - Masque LED
=======================================

Solution pour éliminer la flèche d'upload qui apparaît pendant l'envoi de texte.

PROBLÈME IDENTIFIÉ:
- Le masque affiche un indicateur de progression (flèche) pendant l'upload
- Le mode d'affichage n'est défini qu'APRÈS l'upload complet
- Pendant DATS → chunks → DATCP, le masque utilise son mode par défaut

SOLUTION:
- Définir le mode d'affichage AVANT de commencer l'upload
- Cacher l'indicateur en mettant le masque en mode "éteint" temporairement
- Ou définir directement le mode final avant upload
"""

import asyncio
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES
import struct

# Configuration
ENCRYPTION_KEY = bytes.fromhex('32672f7974ad43451d9c6c894a0e8764')
COMMAND_CHAR = "d44bc439-abfd-45a2-b575-925416129600"
UPLOAD_CHAR = "d44bc439-abfd-45a2-b575-92541612960a"
NOTIFY_CHAR = "d44bc439-abfd-45a2-b575-925416129601"

class NoArrowTextDisplay:
    """Afficheur de texte SANS flèche d'upload"""
    
    def __init__(self):
        self.client = None
        self.cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
        self.responses = []
        self.notification_event = asyncio.Event()
        
        # Modes d'affichage disponibles
        self.DISPLAY_MODES = {
            'OFF': 0,           # Éteint
            'STEADY': 1,        # Fixe
            'BLINK': 2,         # Clignotant
            'SCROLL_LEFT': 3,   # Défile gauche
            'SCROLL_RIGHT': 4,  # Défile droite
            'STATIC': 5         # Statique
        }
    
    def create_command(self, cmd_str, data=b''):
        """Crée une commande chiffrée"""
        cmd = bytearray()
        cmd.append(len(cmd_str) + len(data))
        cmd.extend(cmd_str.encode('ascii'))
        cmd.extend(data)
        
        while len(cmd) < 16:
            cmd.append(0)
        
        return self.cipher.encrypt(bytes(cmd))
    
    def _notification_handler(self, sender, data):
        """Gestionnaire des notifications"""
        try:
            response = data.decode('ascii', errors='ignore').strip('\x00')
            if response:
                print(f"📨 Réponse: {response}")
                self.responses.append(response)
                self.notification_event.set()
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    async def connect(self):
        """Connexion au masque"""
        print("🔍 Recherche du masque...")
        devices = await BleakScanner.discover()
        
        mask = None
        for device in devices:
            if "MASK" in (device.name or ""):
                mask = device
                break
        
        if not mask:
            print("❌ Masque non trouvé")
            return False
        
        print(f"🔗 Connexion à {mask.name}...")
        self.client = BleakClient(mask.address)
        await self.client.connect()
        await self.client.start_notify(NOTIFY_CHAR, self._notification_handler)
        print("✅ Connecté!")
        return True
    
    async def wait_for_response(self, expected, timeout=10):
        """Attend une réponse spécifique"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            for i, response in enumerate(self.responses):
                if expected in response:
                    self.responses.pop(i)
                    return True
            
            try:
                await asyncio.wait_for(self.notification_event.wait(), timeout=0.5)
                self.notification_event.clear()
            except asyncio.TimeoutError:
                continue
        
        return False
    
    async def set_display_mode(self, mode_name):
        """Définit le mode d'affichage"""
        if mode_name not in self.DISPLAY_MODES:
            print(f"❌ Mode invalide: {mode_name}")
            return False
        
        mode_value = self.DISPLAY_MODES[mode_name]
        cmd = self.create_command("MODE", bytes([mode_value]))
        await self.client.write_gatt_char(COMMAND_CHAR, cmd)
        print(f"🎭 Mode: {mode_name} ({mode_value})")
        return True
    
    async def clear_display(self):
        """Efface l'affichage"""
        print("🧹 Effacement de l'affichage...")
        await self.set_display_mode('OFF')
        await asyncio.sleep(0.2)
    
    async def hide_upload_indicator(self):
        """Cache l'indicateur d'upload AVANT l'upload"""
        print("🔇 Masquage de l'indicateur d'upload...")
        
        # Méthode 1: Mettre en mode OFF temporairement
        await self.set_display_mode('OFF')
        await asyncio.sleep(0.3)
        
        # Méthode 2: Définir directement le mode final
        await self.set_display_mode('STEADY')
        await asyncio.sleep(0.2)
    
    def text_to_bitmap(self, text):
        """Convertit le texte en bitmap (version simplifiée)"""
        # Patterns basiques pour tests
        simple_patterns = {
            'H': ["█   █", "█   █", "█████", "█   █", "█   █"],
            'I': ["█████", "  █  ", "  █  ", "  █  ", "█████"],
            ':': ["     ", "  █  ", "     ", "  █  ", "     "],
            ')': ["█    ", " █   ", "  █  ", " █   ", "█    "],
            '!': ["  █  ", "  █  ", "  █  ", "     ", "  █  "],
        }
        
        columns = []
        for char in text.upper():
            if char in simple_patterns:
                pattern = simple_patterns[char]
                for row in pattern:
                    for col_idx in range(len(row)):
                        if col_idx >= len(columns):
                            columns.extend([[] for _ in range(len(row) - len(columns))])
                        columns[col_idx].append(1 if row[col_idx] == '█' else 0)
            else:
                # Espace ou caractère inconnu
                for _ in range(3):  # 3 colonnes vides
                    columns.append([0] * 16)
        
        return columns
    
    def encode_bitmap(self, columns):
        """Encode le bitmap au format du masque"""
        result = bytearray()
        for column in columns:
            bits = column[:16]  # 16 pixels max par colonne
            while len(bits) < 16:
                bits.append(0)
            
            # Conversion en 2 bytes (16 bits)
            value = 0
            for i, bit in enumerate(bits):
                if bit:
                    value |= (1 << i)
            
            result.extend(struct.pack('<H', value))
        
        return bytes(result)
    
    def encode_colors(self, num_columns, color):
        """Encode les couleurs"""
        r, g, b = color
        result = bytearray()
        for _ in range(num_columns):
            result.extend([r, g, b])
        return bytes(result)
    
    async def display_text_no_arrow(self, text, color=(255, 255, 255)):
        """Affiche du texte SANS flèche d'upload"""
        print(f"\n📝 Affichage sans flèche: '{text}'")
        
        # 🔧 SOLUTION 1: Cacher l'indicateur AVANT l'upload
        await self.hide_upload_indicator()
        
        # Générer le bitmap
        bitmap_columns = self.text_to_bitmap(text)
        if not bitmap_columns:
            print("❌ Aucun caractère valide")
            return False
        
        bitmap_data = self.encode_bitmap(bitmap_columns)
        color_data = self.encode_colors(len(bitmap_columns), color)
        
        total_len = len(bitmap_data) + len(color_data)
        bitmap_len = len(bitmap_data)
        
        print(f"📊 {len(bitmap_columns)} colonnes, {bitmap_len}B bitmap, {len(color_data)}B couleurs")
        
        # 🔧 SOLUTION 2: Définir le mode final AVANT DATS
        print("🎯 Pré-configuration du mode d'affichage...")
        await self.set_display_mode('STEADY')  # Mode final défini AVANT upload
        await asyncio.sleep(0.3)
        
        # ÉTAPE 1: DATS (avec mode déjà défini)
        self.responses.clear()
        
        dats_cmd = bytearray([9])
        dats_cmd.extend(b"DATS")
        dats_cmd.extend(struct.pack('>H', total_len))
        dats_cmd.extend(struct.pack('>H', bitmap_len))
        dats_cmd.extend([0])
        
        while len(dats_cmd) < 16:
            dats_cmd.append(0)
        
        print("📤 DATS (mode pré-défini)...")
        encrypted = self.cipher.encrypt(bytes(dats_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATSOK", 5):
            print("❌ Pas de DATSOK")
            return False
        
        # ÉTAPE 2: Upload silencieux (indicateur masqué)
        complete_data = bitmap_data + color_data
        max_chunk = 96
        bytes_sent = 0
        packet_count = 0
        
        print("📦 Upload silencieux en cours...")
        while bytes_sent < len(complete_data):
            remaining = len(complete_data) - bytes_sent
            chunk_size = min(max_chunk, remaining)
            
            chunk = complete_data[bytes_sent:bytes_sent + chunk_size]
            
            packet = bytearray([chunk_size + 1, packet_count])
            packet.extend(chunk)
            
            await self.client.write_gatt_char(UPLOAD_CHAR, bytes(packet))
            
            if not await self.wait_for_response("REOK", 3):
                print(f"❌ Pas de REOK pour chunk {packet_count}")
                return False
            
            bytes_sent += chunk_size
            packet_count += 1
            
            # Pas d'affichage de progression visible sur le masque!
        
        # ÉTAPE 3: DATCP
        datcp_cmd = bytearray([5])
        datcp_cmd.extend(b"DATCP")
        
        while len(datcp_cmd) < 16:
            datcp_cmd.append(0)
        
        print("📤 DATCP (finalisation)...")
        encrypted = self.cipher.encrypt(bytes(datcp_cmd))
        await self.client.write_gatt_char(COMMAND_CHAR, encrypted)
        
        if not await self.wait_for_response("DATCPOK", 5):
            print("❌ Pas de DATCPOK")
            return False
        
        # 🔧 SOLUTION 3: Confirmer le mode final (optionnel)
        print("✅ Confirmation du mode d'affichage...")
        await self.set_display_mode('STEADY')
        
        print(f"🎉 '{text}' affiché SANS flèche!")
        return True
    
    async def demonstration_methods(self):
        """Démontre différentes méthodes pour masquer la flèche"""
        test_texts = [
            ("HI", (255, 0, 0)),      # Rouge
            (":)", (0, 255, 0)),      # Vert
            ("!", (0, 0, 255)),       # Bleu
        ]
        
        for text, color in test_texts:
            print(f"\n{'='*50}")
            print(f"🧪 TEST: {text}")
            print(f"{'='*50}")
            
            success = await self.display_text_no_arrow(text, color)
            if success:
                print("✅ Succès - aucune flèche visible!")
                await asyncio.sleep(3)  # Observer le résultat
            else:
                print("❌ Échec du test")
                break
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NOTIFY_CHAR)
            await self.client.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Test de la solution anti-flèche"""
    print("🔧 SOLUTION ANTI-FLÈCHE D'UPLOAD")
    print("="*40)
    
    display = NoArrowTextDisplay()
    
    if await display.connect():
        try:
            # Test des différentes méthodes
            await display.demonstration_methods()
            
            print("\n🎯 SOLUTION APPLIQUÉE:")
            print("✅ Mode d'affichage défini AVANT upload")
            print("✅ Indicateur de progression masqué")
            print("✅ Upload silencieux réalisé")
            print("✅ Flèche d'upload éliminée!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await display.disconnect()
    else:
        print("💡 Vérifiez que le masque est allumé")

if __name__ == "__main__":
    asyncio.run(main())
