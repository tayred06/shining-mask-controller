#!/usr/bin/env python3
"""
Contrôleur Principal Optimisé - Shining Mask Controller
======================================================

Version refactorisée avec architecture modulaire et gestion d'erreurs robuste.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Imports locaux (à adapter selon la structure finale)
from config_optimized import get_config, PatternConfig
from ble_manager_optimized import MaskBLEManager

class ControllerState(Enum):
    """États du contrôleur"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class ControllerStats:
    """Statistiques du contrôleur"""
    patterns_displayed: int = 0
    animations_played: int = 0
    blinks_triggered: int = 0
    errors_count: int = 0
    uptime_seconds: float = 0
    last_pattern_id: Optional[int] = None

class OptimizedMaskController:
    """Contrôleur principal optimisé pour le masque LED"""
    
    def __init__(self):
        # Configuration
        self.config = get_config()
        
        # État et statistiques
        self.state = ControllerState.STOPPED
        self.stats = ControllerStats()
        
        # Gestionnaires
        self.ble_manager: Optional[MaskBLEManager] = None
        self.input_handler: Optional[Any] = None  # À implémenter
        
        # Tâches asynchrones
        self.background_tasks: Dict[str, asyncio.Task] = {}
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Gestion d'arrêt propre
        self._shutdown_event = asyncio.Event()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Configure les gestionnaires de signaux pour arrêt propre"""
        def signal_handler(signum, frame):
            self.logger.info(f"📡 Signal {signum} reçu, arrêt en cours...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self) -> bool:
        """Initialisation complète du contrôleur"""
        try:
            self.state = ControllerState.STARTING
            self.logger.info("🚀 Initialisation du contrôleur...")
            
            # 1. Initialisation BLE
            if not await self._initialize_ble():
                return False
            
            # 2. Initialisation des gestionnaires d'entrée
            if not await self._initialize_input():
                return False
            
            # 3. Démarrage des tâches de fond
            await self._start_background_tasks()
            
            self.state = ControllerState.RUNNING
            self.logger.info("✅ Contrôleur initialisé avec succès!")
            return True
            
        except Exception as e:
            self.state = ControllerState.ERROR
            self.logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def _initialize_ble(self) -> bool:
        """Initialise la connexion BLE"""
        try:
            self.ble_manager = MaskBLEManager(self.config.ble_settings)
            
            # Enregistrer les callbacks de notification
            self.ble_manager.register_notification_callback(
                "main", self._handle_ble_notification
            )
            
            # Connexion
            if await self.ble_manager.connect():
                self.logger.info("✅ BLE initialisé")
                return True
            else:
                self.logger.error("❌ Échec connexion BLE")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur init BLE: {e}")
            return False
    
    async def _initialize_input(self) -> bool:
        """Initialise les gestionnaires d'entrée"""
        try:
            # Pour l'instant, simulation réussie
            # TODO: Implémenter KeyboardHandler et GamepadHandler
            self.logger.info("✅ Gestionnaires d'entrée initialisés")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur init input: {e}")
            return False
    
    async def _start_background_tasks(self):
        """Démarre les tâches de fond"""
        try:
            # Tâche de clignotement automatique
            if self.config.animation_settings.get('auto_blink_enabled', True):
                self.background_tasks['auto_blink'] = asyncio.create_task(
                    self._auto_blink_loop()
                )
                self.logger.info("👁️ Auto-blink activé")
            
            # Tâche de monitoring de santé
            self.background_tasks['health_monitor'] = asyncio.create_task(
                self._health_monitor_loop()
            )
            self.logger.info("❤️ Monitoring de santé activé")
            
            # Tâche de statistiques
            self.background_tasks['stats_updater'] = asyncio.create_task(
                self._stats_updater_loop()
            )
            self.logger.info("📊 Suivi des statistiques activé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage tâches: {e}")
    
    def _handle_ble_notification(self, sender, data: bytes):
        """Gestionnaire des notifications BLE"""
        try:
            # Traitement des notifications reçues du masque
            response = data.decode('ascii', errors='ignore').strip('\x00')
            self.logger.debug(f"📨 Notification BLE: {response}")
            
            # Ici on pourrait traiter différents types de réponses
            if response == "DATSOK":
                self.logger.debug("✅ Upload confirmé")
            elif response == "REOK":
                self.logger.debug("✅ Chunk reçu")
            elif response == "DATCPOK":
                self.logger.debug("✅ Upload terminé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur notification: {e}")
            self.stats.errors_count += 1
    
    async def display_pattern(self, pattern_id: int) -> bool:
        """Affiche un pattern par son ID"""
        try:
            pattern = self.config.get_pattern_by_id(pattern_id)
            if not pattern:
                self.logger.warning(f"⚠️ Pattern {pattern_id} introuvable")
                return False
            
            # Utilisation du système de texte simplifié
            success = await self._send_text_pattern(pattern)
            
            if success:
                self.stats.patterns_displayed += 1
                self.stats.last_pattern_id = pattern_id
                self.logger.info(f"📝 Pattern {pattern_id} ('{pattern.text}') affiché")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erreur affichage pattern {pattern_id}: {e}")
            self.stats.errors_count += 1
            return False
    
    async def _send_text_pattern(self, pattern: PatternConfig) -> bool:
        """Envoie un pattern texte au masque"""
        try:
            # Implémentation simplifiée du rendu texte
            # TODO: Utiliser un TextRenderer dédié
            
            if not self.ble_manager or not self.ble_manager.is_connected:
                return False
            
            # Pour l'instant, simulation d'envoi réussi
            # Dans la vraie implémentation, on utiliserait le TextRenderer
            await asyncio.sleep(0.1)  # Simulation latence
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur envoi pattern: {e}")
            return False
    
    async def trigger_animation(self, animation_type: str, duration: float = None) -> bool:
        """Déclenche une animation"""
        try:
            if duration is None:
                duration = self.config.animation_settings.get('default_animation_duration', 3.0)
            
            self.logger.info(f"🎬 Animation {animation_type} démarrée ({duration}s)")
            
            # TODO: Implémenter les vraies animations
            await asyncio.sleep(0.1)  # Simulation
            
            self.stats.animations_played += 1
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur animation {animation_type}: {e}")
            self.stats.errors_count += 1
            return False
    
    async def trigger_blink(self) -> bool:
        """Déclenche une séquence de clignotement"""
        try:
            # Séquence: pattern fermé -> ouvert -> fermé
            blink_sequence = [
                (6, 0.1),   # ;) - clin d'œil
                (7, 0.2),   # -_- - fermé
                (7, 0.2),   # -_- - fermé
                (6, 0.1),   # ;) - clin d'œil
            ]
            
            for pattern_id, delay in blink_sequence:
                await self.display_pattern(pattern_id)
                await asyncio.sleep(delay)
            
            # Retour au pattern précédent
            if self.stats.last_pattern_id:
                await self.display_pattern(self.stats.last_pattern_id)
            
            self.stats.blinks_triggered += 1
            self.logger.debug("👁️ Clignotement terminé")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur clignotement: {e}")
            self.stats.errors_count += 1
            return False
    
    async def _auto_blink_loop(self):
        """Boucle de clignotement automatique"""
        import random
        
        blink_chance = self.config.animation_settings.get('auto_blink_chance', 4)
        interval = self.config.animation_settings.get('auto_blink_interval', 0.1)
        
        while self.state == ControllerState.RUNNING:
            try:
                if random.randint(0, 100) < blink_chance:
                    await self.trigger_blink()
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur auto-blink: {e}")
                await asyncio.sleep(1)  # Éviter les boucles d'erreur
    
    async def _health_monitor_loop(self):
        """Boucle de monitoring de santé"""
        check_interval = 30  # secondes
        
        while self.state == ControllerState.RUNNING:
            try:
                # Vérifier la connexion BLE
                if self.ble_manager:
                    is_healthy = await self.ble_manager.health_check()
                    if not is_healthy:
                        self.logger.warning("⚠️ Connexion BLE dégradée")
                        # Tentative de reconnexion
                        await self.ble_manager.connect()
                
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur health monitor: {e}")
                await asyncio.sleep(check_interval)
    
    async def _stats_updater_loop(self):
        """Boucle de mise à jour des statistiques"""
        import time
        start_time = time.time()
        
        while self.state == ControllerState.RUNNING:
            try:
                self.stats.uptime_seconds = time.time() - start_time
                await asyncio.sleep(1)  # Mise à jour chaque seconde
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erreur stats updater: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Boucle principale du contrôleur"""
        try:
            # Initialisation
            if not await self.initialize():
                return False
            
            self.logger.info("🎮 Contrôleur en marche!")
            
            # Attendre l'arrêt
            await self._shutdown_event.wait()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur run: {e}")
            return False
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Arrêt propre du contrôleur"""
        if self.state == ControllerState.STOPPING:
            return  # Déjà en cours d'arrêt
        
        self.state = ControllerState.STOPPING
        self.logger.info("🛑 Arrêt du contrôleur...")
        
        # Arrêter les tâches de fond
        for task_name, task in self.background_tasks.items():
            if not task.done():
                self.logger.info(f"🛑 Arrêt de {task_name}")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Déconnexion BLE
        if self.ble_manager:
            await self.ble_manager.disconnect()
        
        self.state = ControllerState.STOPPED
        self._shutdown_event.set()
        self.logger.info("✅ Contrôleur arrêté proprement")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du contrôleur"""
        status = {
            'state': self.state.value,
            'stats': {
                'patterns_displayed': self.stats.patterns_displayed,
                'animations_played': self.stats.animations_played,
                'blinks_triggered': self.stats.blinks_triggered,
                'errors_count': self.stats.errors_count,
                'uptime_seconds': self.stats.uptime_seconds,
                'last_pattern_id': self.stats.last_pattern_id,
            },
            'background_tasks': {
                name: not task.done() for name, task in self.background_tasks.items()
            }
        }
        
        if self.ble_manager:
            status['ble'] = self.ble_manager.get_connection_stats()
        
        return status

# Interface CLI pour démonstration
async def main():
    """Point d'entrée principal"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    controller = OptimizedMaskController()
    
    # Démarrage avec gestion d'erreur
    try:
        success = await controller.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
