#!/usr/bin/env python3
"""
🔎 OTA INCREMENTAL PROBE
=========================
Envoie de très petites commandes chiffrées et écoute des notifications
pour découvrir la séquence OTA/bootloader utilisée par le masque.

Principe de sécurité:
- Aucune écriture de gros blocs de données (pas d'UPLOAD_CHAR)
- Uniquement des "pings" courts sur la caractéristique commande
- Délai et journalisation après chaque essai
"""

import asyncio
import os
import sys
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from typing import Tuple
import itertools


# Ajouter src/working au path
_cur = os.path.dirname(os.path.abspath(__file__))
_work = os.path.join(_cur, 'src', 'working')
sys.path.insert(0, _work)

# Chargement robuste via importlib (évite les erreurs d'analyse statique)
import importlib.util as _importlib_util

_ctd_path = os.path.join(_work, 'complete_text_display.py')
_spec = _importlib_util.spec_from_file_location('complete_text_display', _ctd_path)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Impossible de charger complete_text_display depuis {_ctd_path}")
_ctd = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_ctd)

# Exposer les symboles nécessaires
MaskTextDisplay = _ctd.MaskTextDisplay
COMMAND_CHAR = _ctd.COMMAND_CHAR
NOTIFY_CHAR = _ctd.NOTIFY_CHAR


class OTAProbe(MaskTextDisplay):
    """Sonde OTA à pas très fin, non destructive."""

    def __init__(self):
        super().__init__()
        self.log_lines = []
        self.raw_events = []
        # Chars additionnels potentiels pour OTA/DFU
        self.FD_WRITE = "0000fd01-0000-1000-8000-00805f9b34fb"
        self.FD_NOTIFY = "0000fd02-0000-1000-8000-00805f9b34fb"
        self.AE_WRITE = "0000ae01-0000-1000-8000-00805f9b34fb"
        self.AE_NOTIFY = "0000ae02-0000-1000-8000-00805f9b34fb"
        # Capture dernier paquet AE02 et signalisation
        self.last_ae02 = None
        self.raw_event_evt = asyncio.Event()
        # Infos périphérique (pour dérivations de clés)
        self.device_name = None
        self.device_address = None

    def log(self, msg: str):
        line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}"
        print(line)
        self.log_lines.append(line)

    async def send_and_listen(self, cmd_ascii: str, args: bytes = b"", wait_s: float = 0.8):
        """Envoie une commande minuscule et écoute les notifs pendant un court délai."""
        # Snapshot des réponses existantes, puis purge locale
        pre_count = len(self.responses)

        try:
            payload = self.create_command(cmd_ascii, args)
            await self.client.write_gatt_char(COMMAND_CHAR, payload)
            self.log(f"📤 {cmd_ascii} ({len(args)}B args)")
        except Exception as e:
            self.log(f"⚠️ Envoi {cmd_ascii} échoué: {e}")
            return []

        # Attente brève pour capter des notifs éventuelles
        try:
            await asyncio.sleep(wait_s)
        except asyncio.CancelledError:
            pass

        # Collecter les nouvelles réponses apparues depuis l'envoi
        new = []
        if len(self.responses) > pre_count:
            new = self.responses[pre_count:]
            for r in new:
                self.log(f"📨 {r}")
        else:
            self.log("🕳️ Aucune notification nouvelle")

        return new

    async def run_safe_probe(self):
        """Séquence de sondes OTA prudente."""
        self.log("🔗 Connexion et préparation des notifications…")
        # Pré-scan pour capturer nom/adresse (utiles pour dérivations)
        try:
            from bleak import BleakScanner
            devs = await BleakScanner.discover(timeout=3.0)
            for d in devs:
                if (d.name or '').upper().startswith('MASK'):
                    self.device_name = d.name or None
                    self.device_address = getattr(d, 'address', None)
                    break
        except Exception:
            pass
        if not await self.connect():
            self.log("❌ Connexion impossible")
            return False

        try:
            # Dump initial services/characteristics
            await self.dump_services("avant_sonde")

            # Activer des notifications supplémentaires si disponibles
            await self.enable_extra_notifications()

            # Préflight: très petit changement de luminosité pour valider la clé/pipe
            self.log("🧪 Préflight LIGHT…")
            await self.send_and_listen("LIGHT", bytes([1]), 0.3)
            await self.send_and_listen("LIGHT", bytes([150]), 0.3)

            # Groupe 1: introspection/statut (sans changer de mode)
            group1 = [
                ("FWVER", b""), ("VER", b""), ("VERS", b""), ("INFO", b""),
                ("STAT", b""), ("SYS", b""), ("DBG", b"")
            ]
            self.log("🔍 Groupe 1: introspection")
            for cmd, args in group1:
                await self.send_and_listen(cmd, args, 0.6)

            # Groupe 2: requêtes d'état de mode/OTA (idempotentes si non supportées)
            group2 = [
                ("OTA", b"\x00"), ("OTA", b"\x01"), ("OTAMODE", b""),
                ("UPDATE", b""), ("UPDT", b""), ("UPGD", b""),
                ("FLASH", b""), ("BOOT", b""), ("PROGRAM", b""), ("READY", b"")
            ]
            self.log("🧪 Groupe 2: sonde modes OTA/bootloader")
            for cmd, args in group2:
                await self.send_and_listen(cmd, args, 1.0)

            # Groupe 2b: pings bruts sur services suspects (FD/AE)
            self.log("🧪 Groupe 2b: pings bruts sur FD01/AE01")
            for payload in (b"\x00", b"\x01", b"\xaa", b"OTA\x01", b"PING"):
                await self.write_raw(self.FD_WRITE, payload, response=True)
                await asyncio.sleep(0.5)
                await self.write_raw(self.AE_WRITE, payload, response=False)
                await asyncio.sleep(0.5)

            # Groupe 2c: bloc chiffré type commande envoyé sur FD/AE (prudence)
            self.log("🧪 Groupe 2c: motif chiffré OTA sur FD/AE")
            enc_ota = self.create_command("OTA", b"\x01")
            await self.write_raw(self.FD_WRITE, enc_ota[:16], response=True)
            await asyncio.sleep(0.8)
            await self.write_raw(self.AE_WRITE, enc_ota[:16], response=False)
            await asyncio.sleep(0.8)

            # Groupe 2cbis: si challenge AE02 disponible, tenter des réponses prudentes
            await self.challenge_response_probe()

            # Groupe 2d: écriture directe sur FD02 (write+notify) - patterns triviaux
            self.log("🧪 Groupe 2d: patterns triviaux sur FD02 (write+notify)")
            for p in (b"\x00", b"\x01", b"\x55", b"\xaa", b"\x01\x00", b"\x00\x01"):
                await self.write_raw(self.FD_NOTIFY, p, response=True)
                await asyncio.sleep(0.6)

            # Groupe 2e: motifs ASCII courts
            self.log("🧪 Groupe 2e: motifs ASCII courts sur FD02/AE01")
            for p in (b"DFU", b"OTA", b"BOOT", b"PING", b"HELLO"):
                await self.write_raw(self.FD_NOTIFY, p, response=True)
                await asyncio.sleep(0.5)
                await self.write_raw(self.AE_WRITE, p, response=False)
                await asyncio.sleep(0.5)

            # Groupe 3: légers pings de suivi après tentative d'OTA
            group3 = [("STAT", b""), ("INFO", b""), ("VER", b"")]
            self.log("🔁 Groupe 3: re-check status après sonde OTA")
            for cmd, args in group3:
                await self.send_and_listen(cmd, args, 0.6)

            # Dump services/characteristics après sonde OTA
            await self.dump_services("apres_sonde")

            # Scan rapide pour repérer un périphérique DFU/OTA éventuel
            await self.scan_for_dfu()

            # Balayage final très prudent
            await self.safe_sweep()

            # Token-hunt + réponses candidates
            await self.token_hunt_and_responses(max_tries=4, wait_token=2.0)

            # Mode burst expérimental (brute-force plus serré) si variable d'env BURST=1
            if os.environ.get("BURST") == "1":
                self.log("🚀 Mode BURST activé (expérimental)")
                try:
                    await self.burst_handshake(rounds=2)
                except Exception as e:
                    self.log(f"⚠️ burst_handshake: {e}")

            self.log("✅ Sondes terminées")
            return True

        finally:
            # Sauvegarde du log minimal
            try:
                with open("ota_probe.log", "w") as f:
                    f.write("\n".join(self.log_lines) + "\n")
                self.log("💾 Log écrit dans ota_probe.log")
                if self.raw_events:
                    with open("ota_raw.log", "w") as rf:
                        rf.write("\n".join(self.raw_events) + "\n")
                    self.log("💾 Log brut écrit dans ota_raw.log")
            except Exception as e:
                self.log(f"⚠️ Écriture log échouée: {e}")

            if self.client:
                try:
                    await self.client.stop_notify(NOTIFY_CHAR)
                except Exception:
                    pass
                # Désactiver extra notifs si actives
                for extra in (self.FD_NOTIFY, self.AE_NOTIFY):
                    try:
                        await self.client.stop_notify(extra)
                    except Exception:
                        pass
                try:
                    await self.client.disconnect()
                    self.log("🔌 Déconnecté")
                except Exception:
                    pass

    async def dump_services(self, label: str):
        """Log des services/characteristics présents."""
        try:
            # Compat: certaines versions exposent .services (propriété) sans get_services()
            svcs = getattr(self.client, "services", None)
            if svcs is None:
                get_services = getattr(self.client, "get_services", None)
                if callable(get_services):
                    svcs = await get_services()
            if svcs is None:
                self.log("⚠️ Impossible d'obtenir la liste des services (API non supportée)")
                return

            # svcs peut être un ServiceCollection (dict-like) ou similaire
            services = []
            try:
                # bleak >=0.21: svcs.services dict
                services = list(getattr(svcs, "services", {}).values())
            except Exception:
                pass
            if not services:
                # Fallback: iterable direct
                try:
                    services = list(svcs)
                except Exception:
                    services = []

            self.log(f"🧭 Services {label}: {len(services)} services")
            for s in services:
                suuid = getattr(s, "uuid", str(s))
                chars = getattr(s, "characteristics", [])
                self.log(f"  • Service {suuid}")
                for ch in chars:
                    cuuid = getattr(ch, "uuid", str(ch))
                    props = ",".join(getattr(ch, "properties", []) or [])
                    self.log(f"     - Char {cuuid} [{props}]")
        except Exception as e:
            self.log(f"⚠️ dump_services: {e}")

    async def scan_for_dfu(self):
        """Scan en périphérie d’un mode DFU/OTA."""
        from bleak import BleakScanner
        try:
            self.log("🔎 Scan périphériques post-OTA (3s)…")
            devs = await BleakScanner.discover(timeout=3.0)
            hits = []
            for d in devs:
                name = (d.name or "").upper()
                if any(tag in name for tag in ["DFU", "OTA", "BOOT"]):
                    hits.append(f"{d.name} ({d.address})")
            if hits:
                for h in hits:
                    self.log(f"🛠️ Candidat DFU/OTA: {h}")
            else:
                self.log("🧩 Aucun périphérique DFU/OTA détecté")
        except Exception as e:
            self.log(f"⚠️ scan_for_dfu: {e}")

    def _derive_ids(self) -> Tuple[bytes, bytes]:
        """Retourne (mac6, name_hex3x2) si détectés, sinon (b'', b'').
        - mac6: 6 octets de l'adresse MAC si au format standard XX:XX:XX:XX:XX:XX
        - name_hex3x2: si le nom est MASK-XXXXXX (hex 6), renvoie ces 3 octets répétés x2 (6B)
        """
        mac6 = b""
        name6 = b""
        # Adresse BLE si disponible (sur macOS, peut être un UUID CoreBluetooth)
        try:
            addr = (self.client.address if getattr(self, 'client', None) else None) or self.device_address or ''
            if isinstance(addr, str) and ':' in addr and len(addr.split(':')) == 6:
                parts = addr.split(':')
                mac6 = bytes(int(p, 16) for p in parts)
        except Exception:
            pass
        # Suffixe de nom MASK-XXXXXX
        try:
            name = self.device_name or ''
            up = name.upper()
            if up.startswith('MASK-') and len(up) >= 11:
                hex6 = up[5:11]
                if all(c in '0123456789ABCDEF' for c in hex6):
                    b3 = bytes.fromhex(hex6)
                    name6 = b3 + b3  # 3 octets répétés pour former 6B
        except Exception:
            pass
        return mac6, name6

    @staticmethod
    def _crc8(data: bytes, poly: int = 0x07, init: int = 0x00) -> int:
        """CRC-8 (ATM) simple, pour tenter un framing compact (1 octet)."""
        crc = init & 0xFF
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ poly) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def _raw_notify_handler(self, sender: str, data: bytes):
        su = getattr(sender, "uuid", sender)
        s = str(su).lower()
        is_ae = s.startswith("0000ae02-")
        is_fd = s.startswith("0000fd02-")
        tag = "AE02" if is_ae else ("FD02" if is_fd else s)
        hexdata = data.hex()
        line = f"📡 {tag} notif: {hexdata}"
        self.raw_events.append(line)
        self.log(line)

        # Tentative de déchiffrement AES-ECB par blocs de 16
        try:
            if hasattr(self, "cipher") and len(data) >= 16:
                dec_all = b""
                for off in range(0, len(data) // 16 * 16, 16):
                    dec_all += self.cipher.decrypt(data[off:off+16])
                # Log brut + ASCII filtré
                asci = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in dec_all)
                self.log(f"🔓 {tag} dec: {dec_all.hex()} | {asci}")
        except Exception:
            pass

        # Mémoriser AE02 et signaler
        try:
            if is_ae:
                self.last_ae02 = data
                self.raw_event_evt.set()
        except Exception:
            pass

    async def enable_extra_notifications(self):
        """Souscrire aux notifs des services suspects si présents."""
        try:
            svcs = getattr(self.client, "services", None)
            available = set()
            if svcs is not None:
                try:
                    services = list(getattr(svcs, "services", {}).values()) or list(svcs)
                except Exception:
                    services = []
                for s in services:
                    for ch in getattr(s, "characteristics", []):
                        available.add(str(getattr(ch, "uuid", "")).lower())

            for char in (self.FD_NOTIFY, self.AE_NOTIFY):
                if char.lower() in available:
                    try:
                        await self.client.start_notify(char, self._raw_notify_handler)
                        self.log(f"🔔 Notifications activées sur {char}")
                    except Exception as e:
                        self.log(f"⚠️ start_notify {char}: {e}")
        except Exception as e:
            self.log(f"⚠️ enable_extra_notifications: {e}")

    async def write_raw(self, char_uuid: str, data: bytes, response: bool):
        """Écrit un petit payload brut sur une caractéristique donnée (prudence)."""
        try:
            # Limiter prudemment à 20B (ATT sans segmentation, MTU par défaut ~23)
            payload = data[:20] if data else b"\x00"
            await self.client.write_gatt_char(char_uuid, payload, response=response)
            self.log(f"📤 RAW->{char_uuid[-4:]} {payload.hex()}")
        except Exception as e:
            self.log(f"⚠️ write_raw {char_uuid[-4:]}: {e}")

    async def get_ae02_token(self, timeout: float = 1.5):
        """Demande un token sur AE01 (0x00) et renvoie les 16 octets si présents."""
        try:
            self.last_ae02 = None
            self.raw_event_evt.clear()
            await self.write_raw(self.AE_WRITE, b"\x00", response=False)
            try:
                await asyncio.wait_for(self.raw_event_evt.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                return None
            pkt = self.last_ae02 or b""
            if len(pkt) >= 17 and pkt[0] == 0x01:
                token = pkt[1:17]
                self.log(f"🧩 Token AE02: {token.hex()}")
                return token
            return None
        except Exception as e:
            self.log(f"⚠️ get_ae02_token: {e}")
            return None

    async def challenge_response_probe(self):
        """Si un token AE02 est présent, tenter quelques échos prudents."""
        token = await self.get_ae02_token()
        if not token:
            self.log("🧪 Aucun token AE02 obtenu")
            return
        # 1) Écho brut sur FD02 (write+notify)
        await self.write_raw(self.FD_NOTIFY, token, response=True)
        await asyncio.sleep(0.6)
        # 2) Écho brut sur AE01
        await self.write_raw(self.AE_WRITE, token, response=False)
        await asyncio.sleep(0.6)
        # 3) Préfixe 0x02 + token sur FD02
        await self.write_raw(self.FD_NOTIFY, b"\x02" + token[:15], response=True)
        await asyncio.sleep(0.8)
        # 4) Variante chiffrée: chiffrer token et envoyer sur FD02
        try:
            enc = self.cipher.encrypt(token)
            await self.write_raw(self.FD_NOTIFY, enc, response=True)
            await asyncio.sleep(0.8)
        except Exception:
            pass

    async def safe_sweep(self):
        """Balayage prudent: 1 octet sur [0x00..0x0F] sur AE01 et FD02."""
        self.log("🧪 Sweep sûr 0x00..0x0F sur AE01 et FD02")
        for val in range(0x00, 0x10):
            b = bytes([val])
            await self.write_raw(self.AE_WRITE, b, response=False)
            await asyncio.sleep(0.2)
            await self.write_raw(self.FD_NOTIFY, b, response=True)
            await asyncio.sleep(0.5)

    async def token_hunt_and_responses(self, max_tries: int = 3, wait_token: float = 2.0):
        """Boucle: tenter d'obtenir un token AE02 puis tester plusieurs réponses candidates."""
        self.log("🧪 Token-hunt: AE02 + réponses candidates")
        tokens = []
        for i in range(max_tries):
            self.log(f"🔄 Demande token AE02 (try {i+1}/{max_tries})")
            tok = await self.get_ae02_token(timeout=wait_token)
            if not tok:
                continue
            hex_tok = tok.hex()
            if hex_tok not in [t.hex() for t in tokens]:
                tokens.append(tok)
            # Réponses candidates (16B max). On tente d'abord très vite 1-2 variantes.
            variants = []  # (name, payload, fast)
            mac6, name6 = self._derive_ids()
            # Dérivations de clés potentielles à partir de l'identité
            key_app = _ctd.ENCRYPTION_KEY
            # utilitaires
            def _pad16(b: bytes) -> bytes:
                if not b:
                    return b"\x00" * 16
                reps = (16 + len(b) - 1) // len(b)
                return (b * reps)[:16]
            def _cmac(key: bytes, data: bytes) -> bytes:
                c = CMAC.new(key, ciphermod=AES)
                c.update(data)
                return c.digest()
            key_mac_pad = _pad16(mac6)
            key_name_pad = _pad16(name6)
            cand_keys = []
            try:
                cand_keys.append(("cmac(app,mac)", _cmac(key_app, key_mac_pad)))
            except Exception:
                pass
            try:
                cand_keys.append(("cmac(app,name)", _cmac(key_app, key_name_pad)))
            except Exception:
                pass
            try:
                cand_keys.append(("app^mac", bytes([a ^ b for a, b in zip(key_app, key_mac_pad or b"\x00"*16)])))
            except Exception:
                pass
            try:
                cand_keys.append(("app^name", bytes([a ^ b for a, b in zip(key_app, key_name_pad or b"\x00"*16)])))
            except Exception:
                pass
            # identité
            variants.append(("id", tok, True))
            # reverse
            variants.append(("rev", tok[::-1], False))
            # xor AA
            variants.append(("xAA", bytes([b ^ 0xAA for b in tok]), False))
            # AES ECB known key
            try:
                variants.append(("aesK", self.cipher.encrypt(tok), False))
            except Exception:
                pass
            # AES ECB key reversed
            try:
                key_rev = _ctd.ENCRYPTION_KEY[::-1]
                enc_rev = AES.new(key_rev, AES.MODE_ECB).encrypt(tok)
                variants.append(("aesKr", enc_rev, False))
            except Exception:
                pass
            # AES on reversed token
            try:
                variants.append(("aes(trev)", self.cipher.encrypt(tok[::-1]), False))
            except Exception:
                pass
            # AES on tok^AA
            try:
                tok_xaa = bytes([b ^ 0xAA for b in tok])
                variants.append(("aes(xAA)", self.cipher.encrypt(tok_xaa), False))
            except Exception:
                pass

            # Déchiffrer le token (si c'était chiffré avec notre clé), puis renvoyer décodé
            try:
                dec = self.cipher.decrypt(tok)
                variants.append(("decK", dec, False))
            except Exception:
                pass
            # CMAC-AES sur token (RFC4493), tronqué à 16
            try:
                cobj = CMAC.new(_ctd.ENCRYPTION_KEY, ciphermod=AES)
                cobj.update(tok)
                mac = cobj.digest()
                variants.append(("cmacK", mac[:16], False))
            except Exception:
                pass
            # CMAC avec identifiants: 0x02||CMAC_Kapp(token||id)
            try:
                if mac6:
                    macv = _cmac(key_app, tok + mac6)
                    variants.append(("02+cmac(tok|mac)", b"\x02" + macv[:16], True))
                    variants.append(("cmac(tok|mac)", macv[:16], False))
                if name6:
                    macv2 = _cmac(key_app, tok + name6)
                    variants.append(("02+cmac(tok|name)", b"\x02" + macv2[:16], True))
                    variants.append(("cmac(tok|name)", macv2[:16], False))
            except Exception:
                pass
            # AES avec le token comme clé (si le bootloader attend une PRF K=token)
            try:
                key_tok = tok[:16]
                enc_tk = AES.new(key_tok, AES.MODE_ECB).encrypt(tok)
                variants.append(("aesK=tok", enc_tk, False))
            except Exception:
                pass
            # AES avec clé dérivée token^AA
            try:
                key_der = bytes([b ^ 0xAA for b in tok[:16]])
                enc_der = AES.new(key_der, AES.MODE_ECB).encrypt(tok)
                variants.append(("aesK=tok^AA", enc_der, False))
            except Exception:
                pass
            # AES avec clés candidates dérivées de l'identité
            for kname, k in cand_keys:
                try:
                    enc_idk = AES.new(k, AES.MODE_ECB).encrypt(tok)
                    variants.append((f"aesK={kname}", enc_idk, False))
                except Exception:
                    pass

            # Framing compact avec CRC (16B total)
            try:
                # token[0:15] + crc(token[0:15])
                p = tok[:15]
                crc = self._crc8(p)
                variants.append(("tok+crc", p + bytes([crc]), True))
            except Exception:
                pass
            try:
                # 0x01 + tok[0:14] + crc(0x01||tok[0:14])
                p = b"\x01" + tok[:14]
                crc = self._crc8(p)
                variants.append(("01+tok14+crc", p + bytes([crc]), False))
            except Exception:
                pass
            try:
                # 0x10 (len=16?) + tok[0:14] + crc(0x10||tok[0:14])
                p = b"\x10" + tok[:14]
                crc = self._crc8(p)
                variants.append(("10+tok14+crc", p + bytes([crc]), False))
            except Exception:
                pass
            try:
                # tok[0:15] + sum modulo 256
                p = tok[:15]
                s = sum(p) & 0xFF
                variants.append(("tok+sum", p + bytes([s]), False))
            except Exception:
                pass

            # Variantes 17 octets (si acceptées par FD02): 0x01||tok, 0x02||tok, 0x11||tok, tok||0x01, 0x02||CMAC(tok)
            try:
                variants.append(("01+tok", b"\x01" + tok, True))
            except Exception:
                pass
            try:
                variants.append(("02+tok", b"\x02" + tok, False))
            except Exception:
                pass
            try:
                variants.append(("11+tok", b"\x11" + tok, False))
            except Exception:
                pass
            try:
                variants.append(("tok+01", tok + b"\x01", False))
            except Exception:
                pass
            try:
                cobj = CMAC.new(_ctd.ENCRYPTION_KEY, ciphermod=AES)
                cobj.update(tok)
                mac = cobj.digest()
                variants.append(("02+cmac", b"\x02" + mac[:16], False))
            except Exception:
                pass

            # Variantes ASCII avec verbe + token, tronquées à 20B
            verbs = [b"OTA", b"DFU", b"BOOT", b"ERASE", b"START", b"INIT", b"DATA", b"DONE", b"UPDT"]
            for v in verbs:
                try:
                    cap = 20 - len(v)
                    variants.append((f"{v.decode()}+tok", v + tok[:max(0, cap)], False))
                except Exception:
                    pass
            # Préfixe 0x01 + verbe
            for v in verbs[:5]:  # limiter un peu
                try:
                    cap = 20 - (1 + len(v))
                    variants.append((f"01+{v.decode()}+tok", b"\x01" + v + tok[:max(0, cap)], False))
                except Exception:
                    pass

            # Envoi: FD02 (write+notify), puis AE01 echo, puis FD01; petite attente ciblée
            for name, data, fast in variants:
                self.log(f"📦 Réponse {name} -> FD02")
                await self.write_raw(self.FD_NOTIFY, data, response=True)
                await asyncio.sleep(0.15 if fast else 0.8)
                self.log(f"📦 Echo {name} -> AE01")
                await self.write_raw(self.AE_WRITE, data, response=False)
                await asyncio.sleep(0.15 if fast else 0.6)
                self.log(f"📦 Réplique {name} -> FD01")
                await self.write_raw(self.FD_WRITE, data, response=True)
                # Attente ciblée d'un éventuel nouveau token AE02 juste après
                try:
                    self.last_ae02 = None
                    self.raw_event_evt.clear()
                    await asyncio.wait_for(self.raw_event_evt.wait(), timeout=0.45 if fast else 0.8)
                    if self.last_ae02:
                        self.log(f"🧩 AE02 après {name}: {self.last_ae02.hex()}")
                except Exception:
                    pass

        self.log(f"🧾 Tokens vus: {[t.hex() for t in tokens]}")

    async def burst_handshake(self, rounds: int = 2):
        """Tentative agressive mais courte de réponses handshake en rafale.
        Hypothèse: réponse attendue = f(token) sur FD02 en <50ms.
        On envoie séries de frames compactes puis variants multi-étapes.
        Sécurité: limite stricte du nombre total (< 220 frames).
        """
        self.log("🧪 BURST: démarrage")
        total_sent = 0
        for r in range(rounds):
            tok = await self.get_ae02_token(timeout=2.0)
            if not tok:
                self.log("BURST: pas de token, stop")
                break
            self.log(f"BURST round {r+1}/{rounds} token={tok.hex()}")
            # Transformations principales
            def xor_const(b, c):
                return bytes([x ^ c for x in b])
            transforms = {
                "id": lambda t: t,
                "rev": lambda t: t[::-1],
                "xaa": lambda t: xor_const(t, 0xAA),
                "x55": lambda t: xor_const(t, 0x55),
                "xff": lambda t: xor_const(t, 0xFF),
                "rol1": lambda t: t[1:]+t[:1],
            }
            # AES / CMAC variants
            try:
                transforms["aes"] = lambda t: self.cipher.encrypt(t)
            except Exception:
                pass
            try:
                def _cmac(t):
                    c = CMAC.new(_ctd.ENCRYPTION_KEY, ciphermod=AES); c.update(t); return c.digest()
                transforms["cmac"] = _cmac
                transforms["cmac01"] = lambda t: _cmac(b"\x01"+t)
            except Exception:
                pass
            # Préfixes potentiels
            prefixes = [b"", b"\x01", b"\x02", b"\x11", b"\x10", b"\x55", b"\xAA"]
            # Postfix options (CRC8 / SUM)
            def crc8(d):
                return bytes([self._crc8(d)])
            def ssum(d):
                return bytes([sum(d)&0xFF])
            postfixers = [lambda d: d, lambda d: d[:15]+crc8(d[:15]), lambda d: d[:15]+ssum(d[:15])]
            # Build first wave single-frame
            wave = []
            for name,(pfx, (tname, tf), post) in enumerate(itertools.product(prefixes, transforms.items(), postfixers)):
                base = tf(tok)
                if not base:
                    continue
                frame_core = post(base)
                frame = (pfx + frame_core)[:20]
                wave.append((f"{tname}|{pfx.hex()}|{post.__name__ if hasattr(post,'__name__') else 'p'}", frame))
                if len(wave) >= 140:  # cap
                    break
            self.log(f"BURST wave frames: {len(wave)}")
            # Envoi rapide sur FD02 uniquement (write+notify) puis écoute d'un nouveau token
            for label, frame in wave:
                if total_sent > 220:
                    self.log("BURST limite atteinte")
                    return
                total_sent += 1
                await self.write_raw(self.FD_NOTIFY, frame, response=True)
                # écoute courte
                try:
                    self.last_ae02 = None
                    self.raw_event_evt.clear()
                    await asyncio.wait_for(self.raw_event_evt.wait(), timeout=0.05)
                    if self.last_ae02:
                        self.log(f"BURST: nouveau AE02 après {label}: {self.last_ae02.hex()}")
                        break  # passer round suivant
                except asyncio.TimeoutError:
                    pass
            # Deuxième phase (séquences 2 frames): ACK puis frame principale
            seq_prefixes = [b"\x01", b"\x02"]
            for p in seq_prefixes:
                if total_sent > 220:
                    break
                base = tok
                frame2 = p + (self.cipher.encrypt(base) if hasattr(self,'cipher') else base)
                await self.write_raw(self.FD_NOTIFY, p, response=True)
                await asyncio.sleep(0.015)
                await self.write_raw(self.FD_NOTIFY, frame2[:20], response=True)
                total_sent += 2
                try:
                    self.last_ae02 = None
                    self.raw_event_evt.clear()
                    await asyncio.wait_for(self.raw_event_evt.wait(), timeout=0.08)
                    if self.last_ae02:
                        self.log(f"BURST: AE02 après sequence {p.hex()} -> {self.last_ae02.hex()}")
                        break
                except asyncio.TimeoutError:
                    pass
        self.log(f"BURST terminé, frames envoyées: {total_sent}")


async def main():
    probe = OTAProbe()
    await probe.run_safe_probe()


if __name__ == "__main__":
    asyncio.run(main())
