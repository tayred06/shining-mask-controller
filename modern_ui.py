#!/usr/bin/env python3
"""
Interface Utilisateur Moderne - Shining Mask Controller
=======================================================

Interface en ligne de commande avancée avec support interactif et monitoring en temps réel.
"""

import asyncio
import sys
import os
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
from datetime import datetime, timedelta

# Interface utilisateur riche
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Imports locaux
from controller_optimized import OptimizedMaskController
from config_optimized import get_config

@dataclass
class UIState:
    """État de l'interface utilisateur"""
    controller: Optional[OptimizedMaskController] = None
    running: bool = False
    last_update: float = 0
    show_debug: bool = False
    auto_refresh: bool = True

class ModernUI:
    """Interface utilisateur moderne avec Rich"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.state = UIState()
        self.config = get_config()
        
        # Historique des commandes
        self.command_history = []
        self.status_history = []
    
    def print(self, text: str, style: str = None):
        """Affichage avec ou sans Rich"""
        if self.console and RICH_AVAILABLE:
            self.console.print(text, style=style)
        else:
            print(text)
    
    def clear_screen(self):
        """Efface l'écran"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_banner(self):
        """Affiche la bannière d'accueil"""
        banner = """
╭─────────────────────────────────────────────────────────────╮
│                 🎭 SHINING MASK CONTROLLER 🎭                │
│                      Version Optimisée                       │
│                                                             │
│  Contrôle clavier pour masque LED BLE avec patterns texte   │
│  ● 20 patterns pré-configurés                              │
│  ● Auto-blink et animations                                │
│  ● Architecture modulaire                                  │
╰─────────────────────────────────────────────────────────────╯
        """
        
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(banner.strip(), style="cyan"))
        else:
            print(banner)
    
    def show_help(self):
        """Affiche l'aide complète"""
        help_content = """
🎮 COMMANDES PRINCIPALES:
  start          - Démarre le contrôleur
  stop           - Arrête le contrôleur
  status         - Affiche le statut détaillé
  patterns       - Liste tous les patterns disponibles
  test <id>      - Teste un pattern spécifique (1-20)
  blink          - Déclenche un clignotement
  config         - Affiche la configuration
  monitor        - Mode monitoring en temps réel
  debug          - Active/désactive le mode debug
  history        - Affiche l'historique des commandes
  clear          - Efface l'écran
  help           - Affiche cette aide
  quit/exit      - Quitte l'application

🔤 RACCOURCIS CLAVIER (quand le contrôleur est actif):
  Q W E R T     - Patterns émotions (😊 😢 😮 😎 😍)
  A S D F G     - Patterns actions (👌 🤝 👋 💪 🙏)
  Z X C V B     - Patterns symboles (♥ ★ ? ! ⚡)
  1 2 3 4 5     - Patterns texte libre

⚙️  CONFIGURATION:
  Fichier: elegant_config.json
  BLE: Chiffrement AES-128, Auto-reconnexion
  Patterns: Personnalisables par catégorie
  Animations: Auto-blink 4%, durées ajustables

📊 MONITORING:
  Connexion BLE, patterns affichés, animations,
  statistiques temps réel, santé du système
        """
        
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(help_content.strip(), title="📚 Guide d'Utilisation", style="green"))
        else:
            print(help_content)
    
    def show_patterns_table(self):
        """Affiche la table des patterns"""
        patterns = self.config.patterns
        
        if RICH_AVAILABLE and self.console:
            table = Table(title="🎭 Patterns Disponibles", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", width=4)
            table.add_column("Touche", style="yellow", width=8)
            table.add_column("Texte", style="green", width=10)
            table.add_column("Catégorie", style="blue", width=12)
            table.add_column("Description", style="white")
            
            for i, pattern in enumerate(patterns, 1):
                table.add_row(
                    str(i),
                    pattern.key_binding or "N/A",
                    pattern.text,
                    pattern.category,
                    pattern.description
                )
            
            self.console.print(table)
        else:
            print("\n🎭 PATTERNS DISPONIBLES:")
            print("-" * 70)
            for i, pattern in enumerate(patterns, 1):
                print(f"{i:2d} | {pattern.key_binding or 'N/A':6s} | {pattern.text:8s} | {pattern.category:10s} | {pattern.description}")
            print("-" * 70)
    
    def show_status(self, detailed: bool = False):
        """Affiche le statut du contrôleur"""
        if not self.state.controller:
            self.print("❌ Contrôleur non initialisé", "red")
            return
        
        status = self.state.controller.get_status()
        
        if RICH_AVAILABLE and self.console:
            # Table principale
            table = Table(title="📊 Statut du Contrôleur", show_header=True)
            table.add_column("Propriété", style="cyan", width=20)
            table.add_column("Valeur", style="green")
            
            # État général
            state_color = "green" if status['state'] == 'running' else "yellow"
            table.add_row("État", f"[{state_color}]{status['state'].upper()}[/{state_color}]")
            
            # Statistiques
            stats = status['stats']
            uptime = str(timedelta(seconds=int(stats['uptime_seconds'])))
            table.add_row("Temps de fonctionnement", uptime)
            table.add_row("Patterns affichés", str(stats['patterns_displayed']))
            table.add_row("Animations jouées", str(stats['animations_played']))
            table.add_row("Clignotements", str(stats['blinks_triggered']))
            table.add_row("Erreurs", str(stats['errors_count']))
            table.add_row("Dernier pattern", str(stats['last_pattern_id']) if stats['last_pattern_id'] else "Aucun")
            
            # BLE si disponible
            if 'ble' in status:
                ble_stats = status['ble']
                table.add_row("Connexions BLE", str(ble_stats.get('connection_count', 0)))
                table.add_row("Reconnexions", str(ble_stats.get('reconnection_count', 0)))
                table.add_row("Dernière activité", ble_stats.get('last_activity', 'N/A'))
            
            self.console.print(table)
            
            # Tâches de fond si détaillé
            if detailed and 'background_tasks' in status:
                task_table = Table(title="🔄 Tâches de Fond", show_header=True)
                task_table.add_column("Nom", style="cyan")
                task_table.add_column("État", style="green")
                
                for task_name, is_running in status['background_tasks'].items():
                    state_text = "[green]●[/green] Actif" if is_running else "[red]●[/red] Arrêté"
                    task_table.add_row(task_name, state_text)
                
                self.console.print(task_table)
        else:
            # Version texte simple
            print(f"\n📊 STATUT DU CONTRÔLEUR:")
            print(f"État: {status['state'].upper()}")
            print(f"Patterns affichés: {stats['patterns_displayed']}")
            print(f"Animations: {stats['animations_played']}")
            print(f"Clignotements: {stats['blinks_triggered']}")
            print(f"Erreurs: {stats['errors_count']}")
            print(f"Temps de fonctionnement: {timedelta(seconds=int(stats['uptime_seconds']))}")
    
    def show_config(self):
        """Affiche la configuration actuelle"""
        config_data = {
            "BLE Settings": {
                "Device Name": self.config.ble_settings.get('device_name', 'N/A'),
                "Auto Reconnect": self.config.ble_settings.get('auto_reconnect', 'N/A'),
                "Max Retries": self.config.ble_settings.get('max_connection_retries', 'N/A'),
            },
            "Animation Settings": {
                "Auto Blink": self.config.animation_settings.get('auto_blink_enabled', 'N/A'),
                "Blink Chance": f"{self.config.animation_settings.get('auto_blink_chance', 'N/A')}%",
                "Animation Duration": f"{self.config.animation_settings.get('default_animation_duration', 'N/A')}s",
            },
            "System": {
                "Total Patterns": len(self.config.patterns),
                "Debug Mode": self.state.show_debug,
            }
        }
        
        if RICH_AVAILABLE and self.console:
            for section, items in config_data.items():
                table = Table(title=f"⚙️ {section}", show_header=True)
                table.add_column("Paramètre", style="cyan")
                table.add_column("Valeur", style="green")
                
                for key, value in items.items():
                    table.add_row(key, str(value))
                
                self.console.print(table)
                print()
        else:
            print("\n⚙️ CONFIGURATION:")
            for section, items in config_data.items():
                print(f"\n{section}:")
                for key, value in items.items():
                    print(f"  {key}: {value}")
    
    async def start_controller(self):
        """Démarre le contrôleur"""
        if self.state.controller and self.state.running:
            self.print("⚠️ Contrôleur déjà en marche", "yellow")
            return
        
        self.print("🚀 Démarrage du contrôleur...", "blue")
        
        try:
            self.state.controller = OptimizedMaskController()
            
            # Démarrage asynchrone
            init_success = await self.state.controller.initialize()
            
            if init_success:
                self.state.running = True
                self.print("✅ Contrôleur démarré avec succès!", "green")
                
                # Lancer la tâche de contrôle en arrière-plan
                asyncio.create_task(self.state.controller.run())
            else:
                self.print("❌ Échec du démarrage", "red")
                self.state.controller = None
        
        except Exception as e:
            self.print(f"❌ Erreur: {e}", "red")
            self.state.controller = None
    
    async def stop_controller(self):
        """Arrête le contrôleur"""
        if not self.state.controller or not self.state.running:
            self.print("⚠️ Contrôleur non actif", "yellow")
            return
        
        self.print("🛑 Arrêt du contrôleur...", "blue")
        
        try:
            await self.state.controller.shutdown()
            self.state.running = False
            self.print("✅ Contrôleur arrêté", "green")
        except Exception as e:
            self.print(f"❌ Erreur arrêt: {e}", "red")
    
    async def test_pattern(self, pattern_id: int):
        """Teste un pattern spécifique"""
        if not self.state.controller or not self.state.running:
            self.print("❌ Contrôleur non actif", "red")
            return
        
        if pattern_id < 1 or pattern_id > len(self.config.patterns):
            self.print(f"❌ Pattern ID invalide (1-{len(self.config.patterns)})", "red")
            return
        
        self.print(f"🧪 Test du pattern {pattern_id}...", "blue")
        
        try:
            success = await self.state.controller.display_pattern(pattern_id)
            if success:
                pattern = self.config.get_pattern_by_id(pattern_id)
                self.print(f"✅ Pattern {pattern_id} ('{pattern.text}') affiché", "green")
            else:
                self.print(f"❌ Échec affichage pattern {pattern_id}", "red")
        except Exception as e:
            self.print(f"❌ Erreur: {e}", "red")
    
    async def trigger_blink(self):
        """Déclenche un clignotement"""
        if not self.state.controller or not self.state.running:
            self.print("❌ Contrôleur non actif", "red")
            return
        
        self.print("👁️ Clignotement...", "blue")
        
        try:
            success = await self.state.controller.trigger_blink()
            if success:
                self.print("✅ Clignotement terminé", "green")
            else:
                self.print("❌ Échec clignotement", "red")
        except Exception as e:
            self.print(f"❌ Erreur: {e}", "red")
    
    def show_history(self):
        """Affiche l'historique des commandes"""
        if not self.command_history:
            self.print("📝 Aucune commande dans l'historique", "yellow")
            return
        
        self.print("📝 Historique des commandes:", "blue")
        for i, cmd in enumerate(self.command_history[-10:], 1):  # 10 dernières
            self.print(f"  {i:2d}. {cmd}")
    
    async def monitor_mode(self):
        """Mode monitoring en temps réel"""
        if not self.state.controller:
            self.print("❌ Contrôleur non initialisé", "red")
            return
        
        self.print("📊 Mode monitoring activé (Ctrl+C pour quitter)", "blue")
        
        try:
            if RICH_AVAILABLE and self.console:
                # Monitoring avec Rich Live
                with Live(self._create_monitor_layout(), refresh_per_second=2) as live:
                    while True:
                        live.update(self._create_monitor_layout())
                        await asyncio.sleep(0.5)
            else:
                # Monitoring simple
                while True:
                    self.clear_screen()
                    self.show_status(detailed=True)
                    print("\n(Ctrl+C pour quitter)")
                    await asyncio.sleep(2)
        
        except KeyboardInterrupt:
            self.print("\n📊 Monitoring arrêté", "blue")
    
    def _create_monitor_layout(self):
        """Crée le layout pour le monitoring"""
        if not RICH_AVAILABLE:
            return None
        
        layout = Layout()
        layout.split_column(
            Layout(Panel("📊 Monitoring Temps Réel", style="blue"), size=3),
            Layout(name="main")
        )
        
        # Contenu principal
        if self.state.controller:
            status = self.state.controller.get_status()
            
            # Table de statut
            table = Table(show_header=False, box=None)
            table.add_column("", style="cyan", width=20)
            table.add_column("", style="green")
            
            state_color = "green" if status['state'] == 'running' else "yellow"
            table.add_row("État:", f"[{state_color}]{status['state'].upper()}[/{state_color}]")
            
            stats = status['stats']
            table.add_row("Patterns:", str(stats['patterns_displayed']))
            table.add_row("Animations:", str(stats['animations_played']))
            table.add_row("Clignotements:", str(stats['blinks_triggered']))
            table.add_row("Erreurs:", str(stats['errors_count']))
            
            uptime = str(timedelta(seconds=int(stats['uptime_seconds'])))
            table.add_row("Temps:", uptime)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            table.add_row("Heure:", current_time)
            
            layout["main"].update(Panel(table, title="État en Temps Réel"))
        else:
            layout["main"].update(Panel("Contrôleur non initialisé", style="red"))
        
        return layout
    
    async def interactive_mode(self):
        """Mode interactif principal"""
        self.clear_screen()
        self.show_banner()
        
        self.print("\n🎯 Mode interactif activé. Tapez 'help' pour l'aide, 'quit' pour quitter.", "blue")
        
        while True:
            try:
                # Prompt
                if RICH_AVAILABLE and self.console:
                    cmd = self.console.input("\n[bold cyan]mask>[/bold cyan] ").strip()
                else:
                    cmd = input("\nmask> ").strip()
                
                if not cmd:
                    continue
                
                # Ajouter à l'historique
                self.command_history.append(cmd)
                
                # Traiter la commande
                await self._process_command(cmd)
                
            except KeyboardInterrupt:
                self.print("\n👋 Au revoir!", "blue")
                break
            except EOFError:
                break
    
    async def _process_command(self, cmd: str):
        """Traite une commande utilisateur"""
        parts = cmd.lower().split()
        if not parts:
            return
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Commandes de base
        if command in ['quit', 'exit']:
            if self.state.controller and self.state.running:
                await self.stop_controller()
            self.print("👋 Au revoir!", "blue")
            sys.exit(0)
        
        elif command == 'help':
            self.show_help()
        
        elif command == 'clear':
            self.clear_screen()
        
        elif command == 'start':
            await self.start_controller()
        
        elif command == 'stop':
            await self.stop_controller()
        
        elif command == 'status':
            detailed = 'detail' in args or '-d' in args
            self.show_status(detailed)
        
        elif command == 'patterns':
            self.show_patterns_table()
        
        elif command == 'config':
            self.show_config()
        
        elif command == 'test':
            if args:
                try:
                    pattern_id = int(args[0])
                    await self.test_pattern(pattern_id)
                except ValueError:
                    self.print("❌ ID de pattern invalide", "red")
            else:
                self.print("❌ Usage: test <id>", "red")
        
        elif command == 'blink':
            await self.trigger_blink()
        
        elif command == 'debug':
            self.state.show_debug = not self.state.show_debug
            status = "activé" if self.state.show_debug else "désactivé"
            self.print(f"🐛 Mode debug {status}", "yellow")
        
        elif command == 'monitor':
            await self.monitor_mode()
        
        elif command == 'history':
            self.show_history()
        
        else:
            self.print(f"❌ Commande inconnue: {command}", "red")
            self.print("💡 Tapez 'help' pour voir les commandes disponibles", "yellow")

# Point d'entrée
async def main():
    """Point d'entrée principal"""
    ui = ModernUI()
    
    # Vérifier Rich
    if not RICH_AVAILABLE:
        print("⚠️ Rich non installé - interface basique utilisée")
        print("💡 Installer avec: pip install rich")
    
    # Mode interactif
    await ui.interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)
