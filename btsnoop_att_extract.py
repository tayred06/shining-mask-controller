#!/usr/bin/env python3
"""Quick & minimal BTSnoop (HCI H4) parser focused on ATT traffic.

Purpose:
  Extract ATT Write Request/Command and Handle Value Notification PDUs
  from a .btsnoop capture (e.g. produced by btmon -w file.btsnoop) without
  needing tshark/wireshark.

Features:
  - Prints time (relative seconds), ATT opcode, handle (0xHHHH), value hex
  - Detects 17-byte notifications starting with 0x01 (candidate token frames)
  - Counts occurrences per handle
  - Heuristically tags likely token notify handle and token request write handle

Limitations:
  - Only parses unfragmented L2CAP ATT PDUs (sufficient for short control frames)
  - Ignores extended advertising / ISO / other HCI packet types
  - No mapping from handles to UUIDs (needs a separate service discovery dump)

Usage:
  python btsnoop_att_extract.py ota_handshake.btsnoop

Exit codes:
  0 success, >0 on obvious format/read errors.
"""

from __future__ import annotations
import sys, struct, collections
from pathlib import Path

ATT_WRITE_REQ = 0x12
ATT_WRITE_CMD = 0x52
ATT_HANDLE_VALUE_NOTIFICATION = 0x1B
ATT_HANDLE_VALUE_INDICATION = 0x1D

# BTSnoop header constants
SNOOP_HDR_MAGIC = b"btsnoop\x00"

class Record:
    __slots__ = ("orig_len","inc_len","flags","drops","ts","data")
    def __init__(self, o,i,f,d,t,data):
        self.orig_len=o; self.inc_len=i; self.flags=f; self.drops=d; self.ts=t; self.data=data

def parse_btsnoop(path: Path):
    with path.open("rb") as f:
        hdr = f.read(16)
        if len(hdr) != 16 or hdr[:8] != SNOOP_HDR_MAGIC:
            raise ValueError("Not a btsnoop v1 file")
        version, dlt = struct.unpack(">II", hdr[8:16])
        if version != 1:
            raise ValueError(f"Unsupported btsnoop version {version}")
        # DLT 1002 == HCI UART (H4)
        recs = []
        idx = 0
        while True:
            head = f.read(24)
            if not head:
                break
            if len(head) != 24:
                break
            o,i,flags,drops,ts = struct.unpack(">IIIIQ", head)
            data = f.read(i)
            if len(data) != i:
                break
            recs.append(Record(o,i,flags,drops,ts,data))
            idx += 1
        return recs

def iter_att_pdus(recs):
    # HCI H4 packet types
    for r in recs:
        if not r.data:
            continue
        ptype = r.data[0]
        if ptype != 0x02:  # ACL data only
            continue
        if len(r.data) < 5:
            continue
        acl_hdr = r.data[1:5]
        handle_pb_bc, data_len = struct.unpack("<HH", acl_hdr)
        payload = r.data[5:5+data_len]
        if len(payload) < 4:  # Need at least L2CAP header
            continue
        l2_len, l2_cid = struct.unpack("<HH", payload[:4])
        if l2_cid != 0x0004:  # ATT fixed channel
            continue
        att = payload[4:4+l2_len]
        if not att:
            continue
        op = att[0]
        if op in (ATT_WRITE_REQ, ATT_WRITE_CMD, ATT_HANDLE_VALUE_NOTIFICATION, ATT_HANDLE_VALUE_INDICATION):
            # All these have handle in next 2 bytes LE
            if len(att) < 3:
                continue
            handle = struct.unpack("<H", att[1:3])[0]
            value = att[3:]
            yield r.ts, op, handle, value

def fmt_opcode(op:int)->str:
    return {
        ATT_WRITE_REQ: "WRITE_REQ",
        ATT_WRITE_CMD: "WRITE_CMD",
        ATT_HANDLE_VALUE_NOTIFICATION: "NOTIFY",
        ATT_HANDLE_VALUE_INDICATION: "INDIC"
    }.get(op, f"0x{op:02X}")

def main(argv):
    if len(argv) < 2:
        print("Usage: btsnoop_att_extract.py <capture.btsnoop> [--limit N]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2
    limit = None
    if "--limit" in argv:
        try:
            limit = int(argv[argv.index("--limit")+1])
        except Exception:
            pass
    recs = parse_btsnoop(path)
    if not recs:
        print("No records parsed", file=sys.stderr)
        return 3
    att_list = list(iter_att_pdus(recs))
    if not att_list:
        print("No ATT PDUs found (maybe encryption or different link type)")
        return 4
    first_ts = att_list[0][0]
    handle_stats = collections.Counter()
    token_notifs = []
    lines_out = []
    for ts, op, handle, value in att_list:
        rel = (ts - first_ts) / 1_000_000.0  # approximate seconds
        handle_stats[handle] += 1
        tag = ""
        if op == ATT_HANDLE_VALUE_NOTIFICATION and len(value) == 17 and value[0] == 0x01:
            tag = " <TOKEN?>"
            token_notifs.append(handle)
        lines_out.append(f"{rel:8.3f}  {fmt_opcode(op):10}  0x{handle:04X}  {value.hex()}{tag}")
    if limit:
        for l in lines_out[:limit]:
            print(l)
        if len(lines_out) > limit:
            print(f"... ({len(lines_out)-limit} more lines)")
    else:
        for l in lines_out:
            print(l)
    print("\nSummary:")
    for h,c in handle_stats.most_common():
        star = "" if h not in token_notifs else " *token-notify" if token_notifs.count(h)>1 else ""
        print(f"  Handle 0x{h:04X}: {c} frames{star}")
    if token_notifs:
        tn = collections.Counter(token_notifs)
        likely = tn.most_common(1)[0][0]
        print(f"\nLikely AE02 notify handle: 0x{likely:04X}")
        # Guess request handle: preceding WRITE to AE01 often 0x00 value
        # Simple heuristic: find writes of single 00 whose next ATT is a token notify
        preceding = collections.Counter()
        for i,(ts,op,h,v) in enumerate(att_list[:-1]):
            if op in (ATT_WRITE_CMD, ATT_WRITE_REQ) and v == b"\x00":
                nxt = att_list[i+1]
                if nxt[1] == ATT_HANDLE_VALUE_NOTIFICATION and nxt[3][:1] == b"\x01":
                    preceding[h] += 1
        if preceding:
            guess = preceding.most_common(1)[0][0]
            print(f"Likely AE01 write handle (token request): 0x{guess:04X}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
