# Raspberry Pi setup – Twitch Mask Bot

Ce guide prépare une Raspberry Pi (Debian/Raspbian) pour lancer automatiquement le bot qui anime le masque et affiche "Merci PSEUDO" lors d’un abonnement.

## 1) Pré-requis système

- Raspberry Pi OS (Bullseye ou plus récent)
- Bluetooth intégré/USB (BlueZ), micro USB/Jack si bouche animée par la voix

Mises à jour et paquets système:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
  libportaudio2 portaudio19-dev \
  bluetooth bluez bluez-hcidump \
  libglib2.0-0 libglib2.0-dev
```

> libportaudio2 est requis par sounddevice. bluez est requis par bleak (BLE).

## 2) Créer l’environnement Python

```bash
cd ~/my-python-project
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Si besoin d’accéder au Bluetooth sans sudo:

```bash
sudo setcap cap_net_raw,cap_net_admin+eip $(readlink -f ~/.venv/bin/python)
```

## 3) Variables d’environnement Twitch

Créer un fichier d’environnement `~/.config/twitch-mask-bot.env`:

```bash
TWITCH_TOKEN=oauth:xxxxxxxxxxxxxxxxxxxxxxxx
TWITCH_CHANNEL=monchaine
TWITCH_NICK=monbot
# Options (facultatif)
MIC_DEVICE=default        # ou index ALSA, ex: 2
VAD_ON=0.020
VAD_OFF=0.012
TEXT_COLOR=255,255,255
BG_COLOR=0,0,0
FACE_OPEN=:O
FACE_CLOSED=:)
```

Obtenir le token: https://twitchapps.com/tmi/ (ou via OAuth officiel)

## 4) Test manuel

```bash
source .venv/bin/activate
export $(grep -v '^#' ~/.config/twitch-mask-bot.env | xargs)
python3 twitch_mask_bot.py
```

- Le bot connecte le masque et affiche un visage " :) ".
- Parlez dans le micro: la bouche passe à ":O" (si micro activé).
- Lors d’un sub, "Merci PSEUDO" s’affiche en vert.

## 5) Service systemd

Créer `/etc/systemd/system/twitch-mask-bot.service`:

```ini
[Unit]
Description=Twitch Mask Bot
After=network-online.target bluetooth.target
Wants=bluetooth.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/my-python-project
EnvironmentFile=/home/pi/.config/twitch-mask-bot.env
ExecStart=/home/pi/my-python-project/.venv/bin/python /home/pi/my-python-project/twitch_mask_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activer et lancer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable twitch-mask-bot
sudo systemctl start twitch-mask-bot
sudo journalctl -u twitch-mask-bot -f
```

## 6) Dépannage

- Bluetooth: `bluetoothctl` pour vérifier l’interface; s’assurer que le masque est à portée et non déjà connecté à un autre appareil.
- Droits BLE: utiliser l’astuce setcap ci-dessus ou lancer en root (déconseillé).
- Micro: lister les devices avec `arecord -l` ou en Python via `sounddevice.query_devices()`.
- Taux d’update trop élevé: ajuster `--vad-on/--vad-off` ou passer `--no-mic`.

## 7) Options CLI utiles

```bash
python3 twitch_mask_bot.py --no-mic
python3 twitch_mask_bot.py --mic-device 2 --vad-on 0.025 --vad-off 0.015 \
  --text-color 0,255,0 --bg-color 0,0,0 --face-open :O --face-closed :)
```

Bonne diffusion !
