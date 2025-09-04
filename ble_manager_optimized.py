#!/usr/bin/env python3
"""
Gestionnaire BLE Optimisé pour Shining Mask Controller
=====================================================
"""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class MaskBLEManager:
    """Gestionnaire BLE optimisé et robuste"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client: Optional[BleakClient] = None
        self.device_address: Optional[str] = None
        self.is_connected = False
        
        # UUIDs
        self.COMMAND_UUID = "d44bc439-abfd-45a2-b575-925416129600"
        self.UPLOAD_UUID = "d44bc439-abfd-45a2-b575-92541612960a"
        self.NOTIFY_UUID = "d44bc439-abfd-45a2-b575-925416129601"
        
        # Chiffrement
        self.encryption_key = bytes.fromhex(config.get('encryption_key', ''))
        
        # Callbacks
        self.notification_callbacks: Dict[str, Callable] = {}
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Métriques de connexion
        self.connection_stats = {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'last_error': None
        }
    
    async def scan_for_device(self, timeout: float = 10.0) -> Optional[str]:
        """Scan et trouve le dispositif masque"""
        device_prefix = self.config.get('device_name_prefix', 'MASK')
        
        self.logger.info(f"🔍 Scan des dispositifs {device_prefix}... (timeout: {timeout}s)")
        
        try:
            devices = await BleakScanner.discover(timeout=timeout)
            
            for device in devices:
                if device.name and device_prefix in device.name:
                    self.logger.info(f"✅ Dispositif trouvé: {device.name} ({device.address})")
                    return device.address
            
            self.logger.warning(f"❌ Aucun dispositif {device_prefix} trouvé")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur scan: {e}")
            return None
    
    async def connect(self, device_address: str = None) -> bool:
        """Connexion robuste avec retry automatique"""
        self.connection_stats['attempts'] += 1
        
        try:
            # Scan si pas d'adresse fournie
            if not device_address:
                device_address = await self.scan_for_device()
                if not device_address:
                    return False
            
            self.device_address = device_address
            
            # Tentatives de connexion avec retry
            max_attempts = self.config.get('retry_attempts', 3)
            timeout = self.config.get('connection_timeout', 10)
            
            for attempt in range(max_attempts):
                try:
                    self.logger.info(f"🔗 Tentative connexion {attempt + 1}/{max_attempts}...")
                    
                    self.client = BleakClient(device_address)
                    await asyncio.wait_for(self.client.connect(), timeout=timeout)
                    
                    if self.client.is_connected:
                        self.is_connected = True
                        self.connection_stats['successes'] += 1
                        
                        # Setup des notifications
                        await self._setup_notifications()
                        
                        self.logger.info("✅ Connexion BLE réussie!")
                        return True
                
                except asyncio.TimeoutError:
                    self.logger.warning(f"⏱️ Timeout connexion (tentative {attempt + 1})")
                except Exception as e:
                    self.logger.warning(f"❌ Erreur connexion: {e}")
                
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)  # Délai entre tentatives
            
            self.connection_stats['failures'] += 1
            self.connection_stats['last_error'] = "Max attempts reached"
            return False
            
        except Exception as e:
            self.connection_stats['failures'] += 1
            self.connection_stats['last_error'] = str(e)
            self.logger.error(f"❌ Erreur connexion fatale: {e}")
            return False
    
    async def _setup_notifications(self):
        """Configure les notifications BLE"""
        try:
            def notification_handler(sender: BleakGATTCharacteristic, data: bytearray):
                """Gestionnaire de notifications générique"""
                try:
                    # Déchiffrement si nécessaire
                    if self.encryption_key:
                        decrypted_data = self._decrypt_data(data)
                    else:
                        decrypted_data = data
                    
                    # Appeler les callbacks enregistrés
                    for callback_name, callback in self.notification_callbacks.items():
                        try:
                            callback(sender, decrypted_data)
                        except Exception as e:
                            self.logger.error(f"❌ Erreur callback {callback_name}: {e}")
                
                except Exception as e:
                    self.logger.error(f"❌ Erreur notification: {e}")
            
            await self.client.start_notify(self.NOTIFY_UUID, notification_handler)
            self.logger.info("🔔 Notifications activées")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Impossible d'activer les notifications: {e}")
    
    def register_notification_callback(self, name: str, callback: Callable):
        """Enregistre un callback pour les notifications"""
        self.notification_callbacks[name] = callback
    
    def unregister_notification_callback(self, name: str):
        """Désenregistre un callback"""
        self.notification_callbacks.pop(name, None)
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Chiffre les données avec AES-128 ECB"""
        if not self.encryption_key or len(data) != 16:
            return data
        
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Déchiffre les données avec AES-128 ECB"""
        if not self.encryption_key or len(data) != 16:
            return data
        
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(data) + decryptor.finalize()
    
    def _pad_data(self, data: bytes, length: int = 16) -> bytes:
        """Remplit les données à la longueur spécifiée"""
        if len(data) >= length:
            return data[:length]
        return data + b'\x00' * (length - len(data))
    
    async def send_command(self, data: bytes, encrypt: bool = True) -> bool:
        """Envoie une commande via la caractéristique de commande"""
        if not self.is_connected or not self.client:
            self.logger.error("❌ Pas de connexion BLE")
            return False
        
        try:
            # Préparation des données
            padded_data = self._pad_data(data, 16)
            
            if encrypt and self.encryption_key:
                final_data = self._encrypt_data(padded_data)
            else:
                final_data = padded_data
            
            # Envoi
            await self.client.write_gatt_char(self.COMMAND_UUID, final_data)
            self.logger.debug(f"📤 Commande envoyée: {final_data.hex()}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur envoi commande: {e}")
            return False
    
    async def send_upload_data(self, data: bytes) -> bool:
        """Envoie des données via la caractéristique d'upload"""
        if not self.is_connected or not self.client:
            self.logger.error("❌ Pas de connexion BLE")
            return False
        
        try:
            await self.client.write_gatt_char(self.UPLOAD_UUID, data, response=False)
            self.logger.debug(f"📤 Upload envoyé: {len(data)} bytes")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur upload: {e}")
            return False
    
    async def disconnect(self):
        """Déconnexion propre"""
        if self.client and self.is_connected:
            try:
                await self.client.disconnect()
                self.is_connected = False
                self.logger.info("🔌 Déconnexion BLE")
            except Exception as e:
                self.logger.error(f"❌ Erreur déconnexion: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de connexion"""
        return {
            **self.connection_stats,
            'success_rate': (
                self.connection_stats['successes'] / 
                max(self.connection_stats['attempts'], 1) * 100
            ),
            'is_connected': self.is_connected,
            'device_address': self.device_address
        }
    
    async def health_check(self) -> bool:
        """Vérifie la santé de la connexion"""
        if not self.is_connected or not self.client:
            return False
        
        try:
            # Test simple: envoyer une commande de ping
            ping_data = b"PING"
            return await self.send_command(ping_data)
        except:
            return False
    
    async def __aenter__(self):
        """Support du context manager"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager"""
        await self.disconnect()
