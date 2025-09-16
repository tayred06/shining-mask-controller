# Raspberry Pi setup – Twitch Mask Bot

Ce guide prépare une Raspberry Pi (Debian/Raspbian) pour lancer automatiquement le bot qui anime le masque et affiche "Merci PSEUDO" lors d’un follow (et sub si activé plus tard).

## 1) Pré-requis système

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
  libportaudio2 portaudio19-dev \
  bluetooth bluez bluez-hcidump \
  libglib2.0-0 libglib2.0-dev
```

## 2) Environnement Python

```bash
cd ~/my-python-project/twitch_bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r ../requirements.txt
```

Option BLE sans sudo:
```bash
sudo setcap cap_net_raw,cap_net_admin+eip $(readlink -f ~/.venv/bin/python)
```

## 3) Variables d’environnement Twitch

Créez `~/.config/twitch-mask-bot.env`:
```bash
TWITCH_TOKEN=oauth:xxxxxxxxxxxxxxxx
TWITCH_CHANNEL=monchaine
TWITCH_NICK=monbot
# Follows via Helix
TWITCH_CLIENT_ID=xxxxxxxxxxxxxxxx
TWITCH_APP_TOKEN=xxxxxxxxxxxxxxxx
# Options
MIC_DEVICE=default
VAD_ON=0.020
VAD_OFF=0.012
TEXT_COLOR=255,255,255
BG_COLOR=0,0,0
FACE_OPEN=:O
FACE_CLOSED=:)
```

## 4) Test

```bash
source .venv/bin/activate
export $(grep -v '^#' ~/.config/twitch-mask-bot.env | xargs)
python3 twitch_mask_bot.py --no-mic
```

## 5) Service systemd

`/etc/systemd/system/twitch-mask-bot.service`:
```ini
[Unit]
Description=Twitch Mask Bot
After=network-online.target bluetooth.target
Wants=bluetooth.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/my-python-project/twitch_bot
EnvironmentFile=/home/pi/.config/twitch-mask-bot.env
ExecStart=/home/pi/my-python-project/twitch_bot/.venv/bin/python /home/pi/my-python-project/twitch_bot/twitch_mask_bot.py --no-mic
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable twitch-mask-bot
sudo systemctl start twitch-mask-bot
sudo journalctl -u twitch-mask-bot -f
```
