# Résumé de Session - Reverse Engineering & Optimisation Masque LED
Date: 05 Décembre 2025
## 1. Découvertes sur le Protocole (Reverse Engineering)
### BLE & Connexion
- **UUID Service**: `d44bc439-abfd-45a2-b575-925416129600`
- **UUID Commande**: `d44bc439-abfd-45a2-b575-925416129600` (Write w/ Response)
- **UUID Upload**: `d44bc439-abfd-45a2-b575-92541612960a` (Write w/o Response)
- **UUID Notify**: `d44bc439-abfd-45a2-b575-925416129601`
- **Chiffrement**: AES-128 ECB. Clé : `32 67 2f 79 74 ad 43 45 1d 9c 6c 89 4a 0e 87 64`
- **Attention**: Le masque ne supporte pas bien les déconnexions brutales. Toujours redémarrer le masque (OFF/ON) si "Device not found" ou "Service Discovery failed".
### Commandes Clés
1.  **Lancer Animation (ANIM)**:
    - Commande: `05 41 4E 49 4D <ID>` (ex: ANIM 3 = `05 41 4E 49 4D 03`)
    - L'animation tourne en boucle automatiquement côté masque.
    - Pas besoin de renvoyer la commande en boucle (cause des conflits).
2.  **Lancer Image (IMAG)**:
    - Commande: `05 49 4D 41 47 <ID>`
3.  **Upload Texte Défilant**:
    - Nécessite d'envoyer un Bitmap codé + un tableau de couleurs.
    - Séquence: `DATS` (Start) -> `DAT` (Chunks) -> `DATCP` (Finish).
    - **Mode Défilement**: Commande `MODE` (`05 4D 4F 44 45 <ID>`).
        - 3 = Scroll Left (Meilleur pour le texte).
    - **Vitesse**: Commande `SPEED`.
## 2. Solutions Techniques Validées
### A. Bot "Legacy" (Stable)
Fichier: `twitch_bot/bot_legacy.py`
Basé sur: `ultimate_text_display_with_bold.py`
- Utilise l'ancien contrôleur `CompleteMaskController`.
- **Méthode ajoutée**: `show_image(bank, id)` qui envoie une commande `PLAY` brute pour revenir à l'animation par défaut.
- **Logique**:
    1.  Démarrage -> `show_image(3)`
    2.  Commande `!say` -> Upload texte -> Attente -> `show_image(3)`
- **Correctif Couleur**: Force l'envoi de tuples `(r,g,b)` pour éviter l'erreur `too many values to unpack`.
- **Robustesse**: Tente une reconnexion automatique si `client.is_connected` est faux avant un envoi.
### B. Bot "Optimized" (Expérimental mais plus propre)
Fichier: `twitch_bot/final_bot_optimized.py` (si sauvegardé)
Basé sur: `controller_optimized.py` et `ble_manager_optimized.py`.
- **Lock Asyncio**: Utilise `async with self.ble_lock:` pour empêcher l'upload de texte de heurter une commande d'animation.
- **Gestion des erreurs**: Attrape `InvalidStateError` de `bleak`.
- **Pas de boucle infinie**: On a remplacé `_animation_loop` par un simple set initial, car le masque gère la boucle lui-même.
## 3. Problèmes Résolus & Astuces
- **Erreur "Service Discovery has not been performed yet"**:
    - Cause : Le masque a perdu la connexion ou le script a crashé sans disconnect.
    - Solution : Ajouter un check `is_connected` avant chaque commande critique et tenter un `await connect()` si besoin.
- **Erreur "InvalidStateError"**:
    - Cause : Deux coroutines essaient d'écrire en Bluetooth en même temps.
    - Solution : Ajouter un `asyncio.Lock()` partagé.
- **Texte qui ne s'affiche pas (juste flèche)**:
    - Cause : Le mode n'était pas forcé ou le masque attendait une validation.
    - Solution : Forcer le mode (Scroll Left) *après* l'upload et attendre 0.5s.
- **Masque introuvable**:
    - Cause : Connexion fantôme conservée par le masque.
    - Solution : Redémarrage physique du masque (OFF/ON).
## 4. Code "Legacy" Fonctionnel (Extrait)
```python
    async def display_sequence(self, text, cfg):
        async with self.display_lock:
            try:
                # Reconnexion si perdu
                if not self.mask.client or not self.mask.client.is_connected:
                    await self.mask.connect()
                # Forcer tuple couleur
                text_color = (255, 0, 255) 
                
                # Upload
                await self.mask.set_scrolling_text(text, ...)
                
                # Attente lecture
                await asyncio.sleep(duration)
                
                # RETOUR ANIMATION
                await self.set_default_image() # Envoie PLAY/ANIM 3
                
            except Exception as e:
                # Disconnect pour clean state
                await self.mask.disconnect()
```

