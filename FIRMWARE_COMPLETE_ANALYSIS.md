
# 🔍 ANALYSE COMBINÉE DES FIRMWARES SHINING MASK

## 📊 Résumé exécutif
Cette analyse compare les deux firmwares déchiffrés pour identifier
les fonctions responsables de l'affichage de la flèche d'upload.


# 🔍 RAPPORT ANALYSE FIRMWARE - TR1906R04-10_OTA.bin.out

## 📋 Informations générales
- **Fichier**: TR1906R04-10_OTA.bin.out
- **Taille**: 66,100 bytes (0x10234)
- **Type**: Firmware ARM32LE déchiffré

## 🎯 RECHERCHE MOTIFS UPLOAD/FLÈCHE

### 🔤 Chaînes de caractères
- **0x00001dcb**: ` DATSOK` (motif: DATS|DATCP|BITS|BUFF|FRAM)
- **0x00001dd4**: `DATCPOK` (motif: DATS|DATCP|BITS|BUFF|FRAM)
- **0x00007cd0**: `gattc_send_svc_changed_cmd_handler` (motif: BLE|GATT|char|notify|write)

### 🔢 Motifs hexadécimaux
- **0x00001dcc**: `44415453` (Commande DATS)

📍 ANALYSE ARM @ 0x00001dcc:
Contexte: 0x00001dac - 0x00001dec

HEX:
00001dac: 11 49 a0 79 08 70 19 20 09 f0 14 fc f8 bd 00 00  |.I.y.p. ........|
00001dbc: a0 30 00 20 9e 30 00 20 6a 26 00 20 ac 30 00 20  |.0. .0. j&. .0. |
00001dcc: 44 41 54 53 4f 4b 00 00 44 41 54 43 50 4f 4b 00  |DATSOK..DATCPOK.|
00001ddc: 45 52 52 4f 52 30 30 00 6e 26 00 20 9c 30 00 20  |ERROR00.n&. .0. |

ARM (approximatif):
00001dac: 79a04911
00001db0: 20197008
00001db4: fc14f009
00001db8: 0000bdf8
00001dbc: 200030a0
00001dc0: 2000309e
00001dc4: 2000266a
00001dc8: 200030ac
00001dcc: 53544144
00001dd0: 00004b4f
00001dd4: 43544144
00001dd8: 004b4f50
00001ddc: 4f525245
00001de0: 00303052
00001de4: 2000266e
00001de8: 2000309c

---
- **0x00001dd4**: `4441544350` (Commande DATCP)

📍 ANALYSE ARM @ 0x00001dd4:
Contexte: 0x00001db4 - 0x00001df4

HEX:
00001db4: 09 f0 14 fc f8 bd 00 00 a0 30 00 20 9e 30 00 20  |.........0. .0. |
00001dc4: 6a 26 00 20 ac 30 00 20 44 41 54 53 4f 4b 00 00  |j&. .0. DATSOK..|
00001dd4: 44 41 54 43 50 4f 4b 00 45 52 52 4f 52 30 30 00  |DATCPOK.ERROR00.|
00001de4: 6e 26 00 20 9c 30 00 20 ac 36 00 20 6b 26 00 20  |n&. .0. .6. k&. |

ARM (approximatif):
00001db4: fc14f009
00001db8: 0000bdf8
00001dbc: 200030a0
00001dc0: 2000309e
00001dc4: 2000266a
00001dc8: 200030ac
00001dcc: 53544144
00001dd0: 00004b4f
00001dd4: 43544144
00001dd8: 004b4f50
00001ddc: 4f525245
00001de0: 00303052
00001de4: 2000266e
00001de8: 2000309c
00001dec: 200036ac
00001df0: 2000266b

---

## 📊 Statistiques
- **Chaînes totales**: 660
- **Motifs upload**: 3
- **Motifs hex**: 2

## 🎯 CONCLUSIONS PRÉLIMINAIRES
✅ **Motifs trouvés** - Analyse approfondie possible
🔍 **Prochaines étapes**: Analyse ARM détaillée des zones identifiées


# 🔍 RAPPORT ANALYSE FIRMWARE - TR1906R04-1-10_OTA.bin.out

## 📋 Informations générales
- **Fichier**: TR1906R04-1-10_OTA.bin.out
- **Taille**: 65,840 bytes (0x10130)
- **Type**: Firmware ARM32LE déchiffré

## 🎯 RECHERCHE MOTIFS UPLOAD/FLÈCHE

### 🔤 Chaînes de caractères
- **0x00001cd3**: ` DATSOK` (motif: DATS|DATCP|BITS|BUFF|FRAM)
- **0x00001cdc**: `DATCPOK` (motif: DATS|DATCP|BITS|BUFF|FRAM)
- **0x00007bcc**: `gattc_send_svc_changed_cmd_handler` (motif: BLE|GATT|char|notify|write)

### 🔢 Motifs hexadécimaux
- **0x00001cd4**: `44415453` (Commande DATS)

📍 ANALYSE ARM @ 0x00001cd4:
Contexte: 0x00001cb4 - 0x00001cf4

HEX:
00001cb4: 11 49 a0 79 08 70 19 20 09 f0 0e fc f8 bd 00 00  |.I.y.p. ........|
00001cc4: a0 30 00 20 9e 30 00 20 6a 26 00 20 ac 30 00 20  |.0. .0. j&. .0. |
00001cd4: 44 41 54 53 4f 4b 00 00 44 41 54 43 50 4f 4b 00  |DATSOK..DATCPOK.|
00001ce4: 45 52 52 4f 52 30 30 00 6e 26 00 20 9c 30 00 20  |ERROR00.n&. .0. |

ARM (approximatif):
00001cb4: 79a04911
00001cb8: 20197008
00001cbc: fc0ef009
00001cc0: 0000bdf8
00001cc4: 200030a0
00001cc8: 2000309e
00001ccc: 2000266a
00001cd0: 200030ac
00001cd4: 53544144
00001cd8: 00004b4f
00001cdc: 43544144
00001ce0: 004b4f50
00001ce4: 4f525245
00001ce8: 00303052
00001cec: 2000266e
00001cf0: 2000309c

---
- **0x00001cdc**: `4441544350` (Commande DATCP)

📍 ANALYSE ARM @ 0x00001cdc:
Contexte: 0x00001cbc - 0x00001cfc

HEX:
00001cbc: 09 f0 0e fc f8 bd 00 00 a0 30 00 20 9e 30 00 20  |.........0. .0. |
00001ccc: 6a 26 00 20 ac 30 00 20 44 41 54 53 4f 4b 00 00  |j&. .0. DATSOK..|
00001cdc: 44 41 54 43 50 4f 4b 00 45 52 52 4f 52 30 30 00  |DATCPOK.ERROR00.|
00001cec: 6e 26 00 20 9c 30 00 20 ac 36 00 20 6b 26 00 20  |n&. .0. .6. k&. |

ARM (approximatif):
00001cbc: fc0ef009
00001cc0: 0000bdf8
00001cc4: 200030a0
00001cc8: 2000309e
00001ccc: 2000266a
00001cd0: 200030ac
00001cd4: 53544144
00001cd8: 00004b4f
00001cdc: 43544144
00001ce0: 004b4f50
00001ce4: 4f525245
00001ce8: 00303052
00001cec: 2000266e
00001cf0: 2000309c
00001cf4: 200036ac
00001cf8: 2000266b

---

## 📊 Statistiques
- **Chaînes totales**: 650
- **Motifs upload**: 3
- **Motifs hex**: 2

## 🎯 CONCLUSIONS PRÉLIMINAIRES
✅ **Motifs trouvés** - Analyse approfondie possible
🔍 **Prochaines étapes**: Analyse ARM détaillée des zones identifiées
