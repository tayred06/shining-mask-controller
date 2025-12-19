# 📦 Deployment Guide for Raspberry Pi

This guide explains how to install and run the **Shining Mask Controller** on a Raspberry Pi 3B+ (or 4/5).

---

## 1. Prerequisites

Ensure your Raspberry Pi is:
1.  Running **Raspberry Pi OS** (Bookworm or Bullseye).
2.  Connected to the internet.
3.  Bluetooth is enabled.

Run these commands on the Pi to install system dependencies:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git bluetooth bluez libbluetooth-dev libglib2.0-dev
```

---

## 2. Installation

1.  **Clone the project** (or copy files via SFTP):
    ```bash
    git clone <YOUR_REPO_URL> shining-mask
    # OR if copying files:
    # scp -r shining-mask-controller pi@<IP>:/home/pi/
    cd shining-mask
    ```

2.  **Create Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python Libraries**:
    ```bash
    pip install -r requirements_rpi.txt
    ```

---

## 3. Configuration

1.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```bash
    nano .env
    ```
    Paste your Twitch credentials:
    ```ini
    TWITCH_TOKEN=oauth:xxxxxxxxxxxxxx
    TWITCH_CHANNEL=your_channel_name
    TWITCH_CLIENT_ID=xxxxxxxxxxxxxx
    TWITCH_CLIENT_SECRET=xxxxxxxxxxxxxx (if needed)
    ```

2.  **Find your Pi's IP Address**:
    Run:
    ```bash
    hostname -I
    ```
    Save this IP (e.g., `192.168.1.50`).

---

## 4. Running the Bot

Start the bot normally:

```bash
source venv/bin/activate
python final_bot_v1/main.py
```

If you see `✅ Twitch Bot Ready` and `✅ Mask Connected`, it works!

---

## 5. Accessing the Dashboard

From your **PC** (or phone) on the same Wi-Fi:

1.  Open your browser.
2.  Go to: `http://<RASPBERRY_PI_IP>:8080`
    *   Example: `http://192.168.1.50:8080`

---

## 6. Auto-Start Service (Optional)

To keep the bot running even after a reboot, create a service:

1.  Create file:
    ```bash
    sudo nano /etc/systemd/system/maskbot.service
    ```
2.  Paste this content:
    ```ini
    [Unit]
    Description=Shining Mask Bot
    After=network.target bluetooth.target

    [Service]
    Type=simple
    User=pi
    WorkingDirectory=/home/pi/shining-mask
    ExecStart=/home/pi/shining-mask/venv/bin/python final_bot_v1/main.py
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
3.  Enable and start:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable maskbot
    sudo systemctl start maskbot
    ```

---

## 🛠 Troubleshooting on Pi

*   **Bluetooth Errors**: If you get "Permission denied" for BLE, run:
    ```bash
    sudo usermod -aG bluetooth pi
    sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
    sudo reboot
    ```
