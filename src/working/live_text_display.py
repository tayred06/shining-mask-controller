#!/usr/bin/env python3
"""
Script pour affichage de texte en temps réel sur le masque LED
Tapez du texte et il s'affiche immédiatement sur le masque
"""

import asyncio
import sys
import os
import threading
from queue import Queue

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrolling_text_controller import ScrollingMaskController

class LiveTextDisplay:
    def __init__(self):
        self.mask = ScrollingMaskController()
        self.text_queue = Queue()
        self.running = True
        self.connected = False
        
    async def connect_mask(self):
        """Connexion initiale au masque"""
        try:
            print("🔄 Connexion au masque...")
            await self.mask.connect()
            await self.mask.set_brightness(80)
            await self.mask.set_background_color(0, 0, 0)  # Fond noir
            await self.mask.set_foreground_color(255, 255, 255)  # Texte blanc
            self.connected = True
            print("✅ Masque connecté et configuré!")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def display_text(self, text, mode="scroll_right", speed=50):
        """Affiche le texte sur le masque"""
        if not self.connected:
            return
            
        try:
            print(f"📱 Affichage: '{text}'")
            await self.mask.set_scrolling_text(text, mode, speed)
            print("✅ Texte mis à jour!")
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
    
    def input_thread(self):
        """Thread pour la saisie utilisateur"""
        print("\n🎮 MASQUE LED - Affichage en temps réel")
        print("=" * 50)
        print("📝 Tapez votre texte et appuyez sur Entrée")
        print("🔄 Le texte s'affichera immédiatement sur le masque")
        print("💡 Commandes spéciales:")
        print("   'quit' ou 'exit' - Quitter")
        print("   'speed:X' - Changer vitesse (ex: speed:80)")
        print("   'mode:X' - Changer mode (scroll_left/scroll_right/blink/steady)")
        print("=" * 50)
        
        current_mode = "scroll_right"
        current_speed = 50
        
        while self.running:
            try:
                user_input = input("\n💬 Votre texte: ").strip()
                
                if not user_input:
                    continue
                    
                # Commandes spéciales
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.running = False
                    self.text_queue.put(('quit', None, None))
                    break
                    
                elif user_input.startswith('speed:'):
                    try:
                        new_speed = int(user_input.split(':')[1])
                        current_speed = max(0, min(255, new_speed))
                        print(f"⚡ Vitesse changée: {current_speed}")
                        continue
                    except ValueError:
                        print("❌ Format de vitesse invalide (ex: speed:80)")
                        continue
                        
                elif user_input.startswith('mode:'):
                    new_mode = user_input.split(':')[1].strip()
                    if new_mode in ['scroll_left', 'scroll_right', 'blink', 'steady']:
                        current_mode = new_mode
                        print(f"🎬 Mode changé: {current_mode}")
                        continue
                    else:
                        print("❌ Mode invalide. Utilisez: scroll_left/scroll_right/blink/steady")
                        continue
                
                # Texte normal à afficher
                self.text_queue.put((user_input, current_mode, current_speed))
                
            except KeyboardInterrupt:
                self.running = False
                self.text_queue.put(('quit', None, None))
                break
            except EOFError:
                self.running = False
                self.text_queue.put(('quit', None, None))
                break
    
    async def main_loop(self):
        """Boucle principale pour traiter les textes"""
        # Connexion au masque
        if not await self.connect_mask():
            return
        
        # Démarrer le thread de saisie
        input_thread = threading.Thread(target=self.input_thread, daemon=True)
        input_thread.start()
        
        # Boucle de traitement des textes
        while self.running:
            try:
                # Vérifier s'il y a du nouveau texte (non-bloquant)
                if not self.text_queue.empty():
                    text, mode, speed = self.text_queue.get_nowait()
                    
                    if text == 'quit':
                        break
                    
                    await self.display_text(text, mode, speed)
                
                # Petite pause pour éviter la surcharge CPU
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Erreur dans la boucle principale: {e}")
                await asyncio.sleep(1)
        
        # Nettoyage
        try:
            await self.mask.disconnect()
            print("\n👋 Déconnecté du masque. Au revoir!")
        except:
            pass

async def main():
    """Point d'entrée principal"""
    display = LiveTextDisplay()
    try:
        await display.main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
