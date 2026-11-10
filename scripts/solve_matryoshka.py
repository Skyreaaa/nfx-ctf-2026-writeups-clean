"""NFX CTF 2026 - Matryoshka Encoding.

Usage:
    python scripts/solve_matryoshka.py capsule.dat

The raw decoded message is printed before any optional NFX prefix formatting.
"""
from pathlib import Path
import base64
import sys
import zlib

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capsule.dat")
data = path.read_bytes().strip()
if len(data) % 2:
    raise ValueError("Pairwise byte swapping requires even length")

data = bytes(value for i in range(0, len(data), 2) for value in (data[i + 1], data[i]))
data = base64.b64decode(data, validate=True)
data = zlib.decompress(data)
data = base64.b85decode(data)
key = b"NFX!"
data = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
raw = data.decode("utf-8")
print("Raw decoded message:", raw)

if raw.startswith("NFXCTF{"):
    candidate = "NFX{" + raw[len("NFXCTF{"):]
    print("Normalized candidate (not an additional decoding layer):", candidate)
