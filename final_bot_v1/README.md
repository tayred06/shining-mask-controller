# Bot Twitch - Masque LED (Final Version)

Ce dossier contient la version consolidée et finale du bot pour le masque LED.

## Fonctionnalités

*   **Commandes Twitch :**
    *   `!anim <id>` : Change l'animation du masque (1-40). Active le mode "Animation".
    *   `!randanim` : Choisit une animation aléatoire.
    *   `!say <texte>` : Affiche un texte défilant sur le masque.
    *   `!face` : Active le mode "Micro" (bouche qui bouge).
    *   `!testfollow` : Teste l'affichage de follow.
*   **Mode "Micro" (VAD) :**
    *   La bouche du masque s'ouvre/ferme quand vous parlez.
    *   Actif uniquement en mode "SPEECH" (activable via `!face` ou par défaut si micro présent).
*   **Événements :**
    *   **Follows** : Affiche "Merci <Pseudo>" en cyan.
    *   **Subs/Gifts** : Affiche "Merci <Pseudo> <3" en or.

## Installation

1.  Assurez-vous d'avoir Python 3.9+.
2.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
3.  Copiez votre fichier `.env` depuis la racine du projet dans ce dossier (ou assurez-vous qu'il est accessible) :
    ```bash
    cp ../.env .
    ```
    Le fichier `.env` doit contenir :
    ```
    TWITCH_TOKEN=oauth:xxxxxx
    TWITCH_CHANNEL=votre_chaine
    TWITCH_NICK=nom_du_bot
    TWITCH_CLIENT_ID=votre_client_id_helix
    TWITCH_APP_TOKEN=votre_app_token_helix
    ```

## Lancement

Lancer le bot avec :

```bash
python3 main.py
```

Arguments optionnels :
*   `--no-mic` : Désactive la détection du micro (utile si pas de micro ou pour tests silencieux).
