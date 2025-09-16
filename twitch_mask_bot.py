#!/usr/bin/env python3
"""
Twitch Mask Bot
----------------
Anime le masque avec une bouche qui s'ouvre/ferme quand vous parlez (micro)
et affiche automatiquement un message "Merci PSEUDO" lors d'un abonnement.

Prérequis env:
  - TWITCH_TOKEN   : token OAuth au format 'oauth:xxxxxxxx' (chat:read + chat:edit)
  - TWITCH_CHANNEL : nom de la chaîne sans # (ex: "monchaine")
  - TWITCH_NICK    : nom du bot (votre compte)

Dépendances:
  - twitchio, sounddevice, numpy, bleak, pycryptodome

Lancement:
  python3 twitch_mask_bot.py
"""

import os
import sys
import asyncio
import signal
import time
import argparse
from typing import Optional, Dict, Any

# Accès au contrôleur du masque
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from working.complete_text_display import MaskTextDisplay  # type: ignore

# Twitch
from twitchio.ext import commands  # type: ignore

# Audio (VAD simple via RMS)
import numpy as np  # type: ignore


class MaskAnimator:
    """Gère la connexion BLE et les animations/overlays texte du masque."""

    def __init__(self, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
        self.mask = MaskTextDisplay()
        self.text_color = text_color
        self.bg_color = bg_color
        self._connected = False
        self._lock = asyncio.Lock()
        self._last_update = 0.0
        self._min_interval = 0.35  # secondes entre updates pour éviter flicker
        self._default_face_closed = ":)"
        self._default_face_open = ":O"
        self._current_face_open = None  # type: Optional[bool]
        self._overlay_until = 0.0

    async def connect(self):
        if self._connected:
            return
        await self.mask.connect()
        self._connected = True
        # Fond noir, luminosité gérée par display_text
        await self.mask.set_background_color(*self.bg_color, 1)

    async def disconnect(self):
        try:
            if self._connected:
                await self.mask.disconnect()
        finally:
            self._connected = False

    async def _maybe_update(self):
        now = time.time()
        if now - self._last_update < self._min_interval:
            await asyncio.sleep(self._min_interval - (now - self._last_update))
        self._last_update = time.time()

    async def show_face(self, mouth_open: bool):
        """Affiche une tête simple; rate-limite pour stabilité."""
        # Si un overlay est actif, ne pas écraser
        if time.time() < self._overlay_until:
            return
        if self._current_face_open == mouth_open:
            return
        async with self._lock:
            if self._current_face_open == mouth_open:
                return
            await self._maybe_update()
            face = self._default_face_open if mouth_open else self._default_face_closed
            try:
                await self.mask.display_text(face, color=self.text_color, background=self.bg_color)
                self._current_face_open = mouth_open
            except Exception as e:
                print(f"[MaskAnimator] Erreur show_face: {e}")

    async def show_thank_you(self, user: str, duration: float = 5.0):
        """Overlay prioritaire 'Merci PSEUDO' pendant quelques secondes."""
        async with self._lock:
            self._overlay_until = time.time() + duration
            msg = f"Merci {user}"
            try:
                await self._maybe_update()
                await self.mask.display_text(msg, color=(0, 255, 0), background=self.bg_color)
            except Exception as e:
                print(f"[MaskAnimator] Erreur show_thank_you: {e}")
        # Laisser afficher puis restaurer la face neutre
        await asyncio.sleep(duration)
        self._overlay_until = 0.0
        await self.show_face(mouth_open=False)

    async def show_follow_message(self, user: str, cfg: Dict[str, Any]):
        """Affiche un message de follow basé sur la config, défilement puis retour image 1."""
        # Extraire couleur texte
        try:
            tc = cfg.get('text', {}).get('text_color', {})
            color = (int(tc.get('r', 255)), int(tc.get('g', 255)), int(tc.get('b', 255)))
        except Exception:
            color = (255, 165, 0)

        mode_name = cfg.get('scrolling', {}).get('default_mode', 'scroll_left')
        mode = 3 if mode_name == 'scroll_left' else (4 if mode_name == 'scroll_right' else 1)

        # Construire le message
        msg = f"Merci {user}"

        async with self._lock:
            self._overlay_until = time.time() + 15.0  # garde une fenêtre
            try:
                # Upload texte (flèche masquée), puis activer le mode scroll souhaité
                await self._maybe_update()
                await self.mask.display_text(msg, color=color, background=self.bg_color)
                # Forcer le mode après upload (display_text remet mode à 1)
                await self.mask.set_display_mode(mode)

                # Estimer durée de défilement (approx)
                try:
                    # Utilise la conversion pour compter les colonnes
                    cols = len(self.mask.text_to_bitmap(msg))  # type: ignore[attr-defined]
                except Exception:
                    cols = max(10, len(msg) * 6)
                # facteur empirique (ajustable) ~30ms/colonne + marge écran
                duration = min(12.0, max(3.0, 0.03 * (cols + 16)))
            except Exception as e:
                print(f"[MaskAnimator] Erreur show_follow_message: {e}")
                duration = 4.0

        # Attendre la fin estimée du défilement
        await asyncio.sleep(duration)
        self._overlay_until = 0.0
        # Revenir à l'image 1
        try:
            await self.mask.show_image(1)
        except Exception as e:
            print(f"[MaskAnimator] Erreur retour image: {e}")


class MicrophoneVAD:
    """Détection de voix simple basée sur RMS avec hystérésis."""

    def __init__(self, samplerate=16000, blocksize=1024, threshold_on=0.020, threshold_off=0.012, device=None):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.threshold_on = threshold_on
        self.threshold_off = threshold_off
        self.device = device
        self.queue: asyncio.Queue[float] = asyncio.Queue(maxsize=10)
        self._stream = None  # type: ignore

    def _audio_callback(self, indata, frames, time_info, status):  # type: ignore
        if status:
            # Print once, but don't flood
            print(f"[VAD] status={status}")
        # indata: float32 [-1, 1]
        try:
            rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
            if not self.queue.full():
                self.queue.put_nowait(rms)
        except Exception:
            pass

    async def start(self):
        try:
            import sounddevice as sd  # type: ignore
        except Exception as e:
            raise RuntimeError("sounddevice est requis pour le micro (installez libportaudio2 + python3-sounddevice ou pip sounddevice)") from e
        self._stream = sd.InputStream(
            channels=1,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype='float32',
            device=self.device,
            callback=self._audio_callback,
        )
        self._stream.start()
        print(f"[VAD] Micro démarré (sr={self.samplerate}, block={self.blocksize}, device={self.device})")

    async def stop(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            finally:
                self._stream = None
                print("[VAD] Micro arrêté")

    async def speaking_states(self):
        """Génère un flux booléen: True = parle, False = silence."""
        speaking = False
        avg = 0.0
        alpha = 0.2  # lissage
        while True:
            rms = await self.queue.get()
            avg = alpha * rms + (1 - alpha) * avg
            if speaking:
                if avg < self.threshold_off:
                    speaking = False
                    yield False
            else:
                if avg > self.threshold_on:
                    speaking = True
                    yield True


class TwitchMaskBot(commands.Bot):
    """Bot Twitch qui relaie les abonnements au masque."""

    def __init__(self, animator: MaskAnimator, token: str, nick: str, channel: str):
        super().__init__(token=token, prefix='!', initial_channels=[channel], nick=nick)
        self.animator = animator
        self.channel = channel

    async def event_ready(self):
        print(f"[Twitch] Connecté en tant que {self.nick}")

    async def event_message(self, message):
        # Laisser les commandes fonctionner
        await self.handle_commands(message)

    async def event_raw_usernotice(self, channel, tags):  # type: ignore
        """Capture USERNOTICE: subs, resubs, gifts..."""
        try:
            msg_id = tags.get('msg-id')
            display_name = tags.get('display-name') or tags.get('login') or 'mystery'
            if msg_id in {'sub', 'resub', 'subgift', 'anonsubgift', 'giftpaidupgrade'}:
                print(f"[Twitch] Sub event: {msg_id} by {display_name}")
                # Déclenche l'overlay Merci
                asyncio.create_task(self.animator.show_thank_you(display_name))
        except Exception as e:
            print(f"[Twitch] usernotice parse error: {e}")

    # Commande manuelle pour test
    @commands.command(name='merci')
    async def merci_cmd(self, ctx):
        user = ctx.author.display_name if ctx and ctx.author else 'ami'
        asyncio.create_task(self.animator.show_thank_you(user))


async def main():
    # CLI + ENV
    parser = argparse.ArgumentParser(description="Twitch Mask Bot (Raspberry Pi ready)")
    parser.add_argument('--no-mic', action='store_true', help='Désactive la détection micro')
    parser.add_argument('--mic-device', default=os.environ.get('MIC_DEVICE'), help='Index/nom device micro (optionnel)')
    parser.add_argument('--vad-on', type=float, default=float(os.environ.get('VAD_ON', '0.020')), help='Seuil VAD on (RMS)')
    parser.add_argument('--vad-off', type=float, default=float(os.environ.get('VAD_OFF', '0.012')), help='Seuil VAD off (RMS)')
    parser.add_argument('--text-color', default=os.environ.get('TEXT_COLOR', '255,255,255'), help='Couleur texte R,G,B')
    parser.add_argument('--bg-color', default=os.environ.get('BG_COLOR', '0,0,0'), help='Couleur fond R,G,B')
    parser.add_argument('--face-open', default=os.environ.get('FACE_OPEN', ':O'), help='Texte bouche ouverte')
    parser.add_argument('--face-closed', default=os.environ.get('FACE_CLOSED', ':)'), help='Texte bouche fermée')
    args = parser.parse_args()

    token = os.environ.get('TWITCH_TOKEN')
    channel = os.environ.get('TWITCH_CHANNEL')
    nick = os.environ.get('TWITCH_NICK')
    if not token or not channel or not nick:
        print("❌ Variables d'environnement manquantes: TWITCH_TOKEN, TWITCH_CHANNEL, TWITCH_NICK")
        print("Exemple: export TWITCH_TOKEN='oauth:xxxxxxxx' ; export TWITCH_CHANNEL='monchaine' ; export TWITCH_NICK='monbot'")
        return

    def parse_rgb(s: str):
        try:
            r, g, b = (int(x) for x in s.split(','))
            return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        except Exception:
            return (255, 255, 255)

    text_color = parse_rgb(args.text_color)
    bg_color = parse_rgb(args.bg_color)

    animator = MaskAnimator(text_color=text_color, bg_color=bg_color)
    animator._default_face_open = args.face_open
    animator._default_face_closed = args.face_closed
    vad = None if args.no_mic else MicrophoneVAD(threshold_on=args.vad_on, threshold_off=args.vad_off, device=args.mic_device)
    bot = TwitchMaskBot(animator, token=token, nick=nick, channel=channel)

    # Charger la config follow
    follow_cfg_path = os.path.join(SRC_DIR, 'working', 'follow.json')
    try:
        import json
        with open(follow_cfg_path, 'r', encoding='utf-8') as f:
            follow_cfg = json.load(f)
    except Exception as e:
        print(f"[FollowCfg] Impossible de lire {follow_cfg_path}: {e}")
        follow_cfg = {}

    # Watcher Helix pour les follows (si identifiants fournis)
    client_id = os.environ.get('TWITCH_CLIENT_ID')
    app_token = os.environ.get('TWITCH_APP_TOKEN')  # App Access Token (Bearer)

    async def get_user_id(session, login: str) -> Optional[str]:
        import requests
        try:
            def _req():
                return requests.get(
                    'https://api.twitch.tv/helix/users',
                    params={'login': login},
                    headers={'Client-ID': client_id, 'Authorization': f'Bearer {app_token}'},
                    timeout=10,
                )
            resp = await asyncio.to_thread(_req)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data'):
                    return data['data'][0]['id']
        except Exception as e:
            print(f"[Helix] get_user_id error: {e}")
        return None

    async def follow_watcher():
        if not client_id or not app_token:
            print("[Helix] Client-ID/App token manquants → watcher follow désactivé")
            while True:
                await asyncio.sleep(3600)

        user_id = await get_user_id(None, channel.lower())
        if not user_id:
            print("[Helix] Impossible de résoudre user_id → watcher follow off")
            while True:
                await asyncio.sleep(3600)

        print(f"[Helix] Watcher follows actif pour user_id={user_id}")
        last_follow_id = None
        while True:
            try:
                import requests
                def _req():
                    return requests.get(
                        'https://api.twitch.tv/helix/users/follows',
                        params={'to_id': user_id, 'first': 1},
                        headers={'Client-ID': client_id, 'Authorization': f'Bearer {app_token}'},
                        timeout=10,
                    )
                resp = await asyncio.to_thread(_req)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('data', [])
                    if items:
                        top = items[0]
                        fid = top.get('from_id')
                        fname = top.get('from_name') or 'ami'
                        if fid and fid != last_follow_id:
                            # Nouveau follower détecté
                            last_follow_id = fid
                            print(f"[Helix] Nouveau follow: {fname}")
                            asyncio.create_task(animator.show_follow_message(fname, follow_cfg))
                await asyncio.sleep(30)
            except Exception as e:
                print(f"[Helix] Watcher error: {e}")
                await asyncio.sleep(30)

    async def run_vad_loop():
        if vad is None:
            print("[VAD] Mode sans micro activé (--no-mic)")
            while True:
                await asyncio.sleep(3600)
        await vad.start()
        try:
            async for speaking in vad.speaking_states():
                await animator.show_face(mouth_open=speaking)
        finally:
            await vad.stop()

    # Gestion sortie propre
    stop_event = asyncio.Event()

    def _graceful_shutdown(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_running_loop().add_signal_handler(sig, _graceful_shutdown)
        except NotImplementedError:
            # Windows fallback
            signal.signal(sig, lambda *_: _graceful_shutdown())

    # Auto-reconnect BLE simple
    async def connect_loop():
        backoff = 1.0
        while True:
            try:
                await animator.connect()
                await animator.show_face(False)
                return
            except Exception as e:
                print(f"[BLE] Connexion échouée, retry dans {backoff:.0f}s: {e}")
                await asyncio.sleep(backoff)
                backoff = min(30.0, backoff * 2)

    await connect_loop()

    # Lancer tâches concurrentes
    tasks = [asyncio.create_task(bot.start()), asyncio.create_task(follow_watcher())]
    if vad is not None:
        tasks.append(asyncio.create_task(run_vad_loop()))

    await stop_event.wait()
    for t in tasks:
        t.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await t
    await animator.disconnect()
    print("👋 Arrêt propre")


if __name__ == "__main__":
    import contextlib
    asyncio.run(main())
