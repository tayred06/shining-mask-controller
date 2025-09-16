#!/usr/bin/env python3
"""
parse_btmon_text.py (v2)
------------------------
Extraction des opérations ATT (Write Request, Write Command, Notification)
depuis un log texte btmon classique (sans timestamps entre crochets).

Format attendu (exemples):
  < ACL Data TX: Handle 64 flags 0x00 dlen 8    #123 [hci0] 12.345678
        ATT: Write Request (0x12) len 3
          Handle: 0x0011 Type: Unknown (0xfd01)
            Data: 00

On reconstruit un timestamp flottant depuis la fin de la première ligne.
Si indisponible, on incrémente un compteur.

Usage:
  python3 parse_btmon_text.py btmon_new.txt > parsed_handles.txt
"""
import re, sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: parse_btmon_text.py <btmon_log.txt>")
    sys.exit(1)

path = sys.argv[1]
try:
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
except Exception as e:
    print(f"Erreur lecture {path}: {e}")
    sys.exit(2)

evt_re = re.compile(r"^(<|>) ACL Data (TX|RX): Handle .*?#\d+ \[hci\d+\] (\d+\.\d+)")
att_re = re.compile(r"ATT: (Write Request|Write Command|Handle Value Notification) \((0x[0-9a-fA-F]{2})\)")
handle_re = re.compile(r"Handle: 0x([0-9a-fA-F]{4}).*?\(0x([0-9a-fA-F]{4})\)")
data_re = re.compile(r"Data: ([0-9a-fA-F]+)")

events = []
current_ts = None
pending = None  # store partial ATT block
auto_counter = 0

def flush_pending():
    if pending and pending.get('handle') is not None:
        # ensure data key exists
        pending.setdefault('data', '')
        events.append(pending.copy())

for ln in lines:
    m_evt = evt_re.match(ln)
    if m_evt:
        # new transport line; flush any pending ATT
        flush_pending()
        try:
            current_ts = float(m_evt.group(3))
        except Exception:
            auto_counter += 1
            current_ts = float(auto_counter)
        continue
    if 'ATT:' in ln:
        # starting a new ATT block inside the last ACL event
        flush_pending()
        m_att = att_re.search(ln)
        if not m_att:
            continue
        kind = m_att.group(1)
        op = 'UNK'
        if 'Write Command' in kind:
            op = 'WCMD'
        elif 'Write Request' in kind:
            op = 'WREQ'
        elif 'Handle Value Notification' in kind:
            op = 'NOTI'
        pending = {
            'ts': current_ts if current_ts is not None else 0.0,
            'op': op,
            'handle': None,
            'data': ''
        }
        continue
    if pending:
        # Try to capture handle / data lines
        if pending['handle'] is None:
            m_h = handle_re.search(ln)
            if m_h:
                try:
                    pending['handle'] = int(m_h.group(1), 16)
                except Exception:
                    pass
        m_d = data_re.search(ln)
        if m_d:
            # Some writes have short len (e.g. 00) => keep first data only
            if not pending.get('data'):
                pending['data'] = m_d.group(1)

# flush remainder
flush_pending()

if not events:
    print("(Aucun évènement ATT détecté: vérifier format ou filtres)")
    sys.exit(0)

# Sort by timestamp (some ordering may shift if reused timestamp)
events.sort(key=lambda e: e['ts'])

# Stats
handle_stats = defaultdict(lambda: defaultdict(int))
for e in events:
    handle_stats[e['handle']][e['op']] += 1

print("Handles (op counts):")
for h in sorted(handle_stats):
    stats = handle_stats[h]
    stat_s = ', '.join(f"{k}:{v}" for k, v in stats.items())
    print(f"  0x{h:04X}: {stat_s}")

print("\nSéquences (delta_ms handle op len data_prefix):")
prev_ts = None
for e in events:
    ts = e['ts']
    delta = 0 if prev_ts is None else (ts - prev_ts) * 1000
    prev_ts = ts
    data = e.get('data', '')
    print(f"  +{delta:7.1f}ms 0x{e['handle']:04X} {e['op']:<4} len={len(data)//2:02d} {data[:24]}")

print("\nHeuristiques tokens:")
for e in events:
    d = e.get('data', '')
    if e['op'] == 'NOTI' and len(d) >= 34 and d.startswith('01'):
        # Remove leading 01 (tag) keep next 32 hex (16B)
        tok = d[2:34]
        print(f"  Token handle 0x{e['handle']:04X}: {tok}")

print("\nRésumé rapide hypothèses:")
for h, stats in sorted(handle_stats.items()):
    if 'WCMD' in stats and h > 0x0080:
        print(f"  0x{h:04X} probable AE01 (write cmd)")
    if 'NOTI' in stats and h > 0x0080:
        print(f"  0x{h:04X} probable AE02 (notify tokens)")
    if 'WREQ' in stats and h < 0x0080 and stats.get('WREQ',0) > 5:
        print(f"  0x{h:04X} probable FD01/FD02 (write req fréquence) -> vérifier taille")

print("\nDone.")
