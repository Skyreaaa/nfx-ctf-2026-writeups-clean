"""NFX CTF 2026 - Frekuensi Sunyi (manual transcription + ROT13).

Usage:
    pip install numpy scipy soundfile pillow
    python scripts/solve_frekuensi_sunyi.py rekaman_lobi.wav

Does not perform OCR; the spectrogram text below is a manual reading.
"""
from pathlib import Path
import codecs
import sys
import numpy as np
import soundfile as sf
from PIL import Image
from scipy.ndimage import binary_closing
from scipy.signal import stft

wav = Path(sys.argv[1] if len(sys.argv) > 1 else "rekaman_lobi.wav")
audio, fs = sf.read(wav, dtype="float32", always_2d=True)
if fs != 44100:
    raise ValueError(f"Unexpected sample rate: {fs}")

period = 2_268_000
if len(audio) < 2 * period:
    raise ValueError("Audio is too short for two full periods")

mono = audio[:, 0]
residual = mono[period:2 * period] - mono[:period]
segment = residual[:36 * fs]
f, t, z = stft(segment, fs=fs, nperseg=4096, noverlap=3584, boundary=None)
band = (f >= 11000) & (f <= 18800)
db = 20 * np.log10(np.abs(z[band]) + 1e-8)
scaled = np.flipud(np.clip((db + 95) * (255 / 23), 0, 255).astype(np.uint8))
raw = Image.fromarray(scaled).resize((3600, 650))
raw.save("frekuensi_sunyi_raw.png")
closed = binary_closing(np.asarray(raw) > 40, structure=np.ones((22, 3), dtype=bool))
Image.fromarray((closed * 255).astype(np.uint8)).save("frekuensi_sunyi_hasil.png")

encoded = "ASK{o0fP4_Pr01Y}"
flag = codecs.decode(encoded, "rot_13")
print("Spectrogram (manual transcription):", encoded)
print("ROT13 result / reconstructed candidate:", flag)
print("Check the CTF submission history to confirm the exact accepted spelling.")
