#!/usr/bin/env python3
"""Stay — NFX CTF 2026. Unicode zero-width -> Base64 -> repeating-key XOR."""
from pathlib import Path
import base64
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else "stay.txt")
content=path.read_text(encoding="utf-8")
mapping={"\u200c":"00","\u2060":"01","\u200b":"10","\u200d":"11"}
hidden=[c for c in content if c in mapping]
bits="".join(mapping[c] for c in hidden)
if len(bits) % 8:
    raise ValueError("Invalid bitstream length")
encoded=bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8))
raw=base64.b64decode(encoded,validate=True)
key=b"falling"
plain=bytes(value ^ key[i % len(key)] for i,value in enumerate(raw))
print("Zero-width characters:",len(hidden))
print("Encoded text:",encoded.decode("ascii"))
print("Decoded raw flag:",plain.decode("ascii"))
if plain.startswith(b"NXCTF{"):
    print("NFX candidate:", ("NFX{" + plain.decode("ascii")[len("NXCTF{"):]))
