# Frekuensi Sunyi

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Audio Steganography
- **Difficulty:** Medium
- **Points:** 460
- **Author:** Kesatria baja ringan
- **Attachment:** `rekaman_lobi.wav`
- **Status:** Solved (profil peserta)

## Description

> Musik lobi ini diputar setiap hari, dan tidak ada yang pernah merasa terganggu. Sampai suatu hari, seorang teknisi suara bilang ada yang “menempel” di dalamnya. Katanya, pesan itu tidak untuk didengar.

## Analysis

Karena petunjuknya bilang pesan itu tidak untuk didengar, aku coba lihat bentuk audionya lewat **spectrogram**, bukan mencari ucapan. Dari file yang aku analisis, aku dapat informasi ini:

- WAV PCM 16-bit stereo, sample rate **44.100 Hz**.
- Durasi sekitar **120,09 detik**.
- Musik latar berulang dengan interval **2.268.000 sampel** (sekitar 51,43 detik).

Pengulangan tersebut aku manfaatkan untuk mengurangi komponen musik, agar sinyal tambahan lebih mudah terlihat pada domain frekuensi.

## Solution

### 1. Membaca WAV dan mengurangi dua segmen berulang

~~~python
import soundfile as sf
audio, fs = sf.read("rekaman_lobi.wav", dtype="float32", always_2d=True)
period = 2_268_000
mono = audio[:, 0]
residual = mono[period:2 * period] - mono[:period]
~~~

Aku memakai channel pertama, lalu mengurangkan dua segmen yang selaras. Ini tidak menjamin seluruh musik hilang, tetapi meningkatkan visibilitas perbedaan antarkeduanya.

### 2. Membuat spectrogram STFT

Aku memfokuskan analisis pada rentang **11.000–18.800 Hz**, dengan `nperseg=4096` dan hop 512.

~~~python
import numpy as np
from scipy.signal import stft

segment = residual[:36 * fs]
f, t, z = stft(segment, fs=fs, nperseg=4096, noverlap=3584, boundary=None)
band = (f >= 11000) & (f <= 18800)
db = 20 * np.log10(np.abs(z[band]) + 1e-8)
~~~

### 3. Memperjelas pola karakter

Aku meningkatkan kontras citra lalu menerapkan *morphological closing* agar garis-garis frekuensi lebih menyatu.

~~~python
from PIL import Image
from scipy.ndimage import binary_closing

scaled = np.flipud(np.clip((db + 95) * (255 / 23), 0, 255).astype(np.uint8))
raw = Image.fromarray(scaled).resize((3600, 650))
raw.save("frekuensi_sunyi_raw.png")
closed = binary_closing(
    np.asarray(raw) > 40,
    structure=np.ones((22, 3), dtype=bool)
)
Image.fromarray((closed * 255).astype(np.uint8)).save("frekuensi_sunyi_hasil.png")
~~~

Dari gambar hasilnya, aku membaca secara manual:

~~~text
ASK{o0fP4_Pr01Y}
~~~

Ini adalah **transkripsi visual**, bukan output OCR otomatis.

### 4. Decode ROT13

Aku mengenali bahwa ROT13 mengubah `ASK` menjadi `NFX`, sehingga aku mendekode seluruh teks:

~~~python
import codecs
print(codecs.decode("ASK{o0fP4_Pr01Y}", "rot_13"))
~~~

Output:

~~~text
NFX{b0sC4_Ce01L}
~~~

## Flag hasil rekonstruksi

~~~text
NFX{b0sC4_Ce01L}
~~~

**Catatan bukti:** Profil challenge menunjukkan *Solved*, tetapi arsip aku tidak menyimpan log submit yang mengonfirmasi string spesifik ini. Karena transkripsi berasal dari gambar spectrogram, aku mempertahankan keterangan kandidat hasil analisis agar akurat.

## Reproduction

~~~bash
pip install numpy scipy soundfile pillow
python scripts/solve_frekuensi_sunyi.py rekaman_lobi.wav
~~~

Script menghasilkan `frekuensi_sunyi_raw.png`, `frekuensi_sunyi_hasil.png`, dan hasil ROT13 di terminal.

## Conclusion

Dari sini aku belajar bahwa file audio dapat menyembunyikan pesan sebagai bentuk visual pada frekuensi tinggi. Untuk challenge ini, kombinasi pengurangan pola latar, STFT, pemrosesan gambar, dan ROT13 mengungkap pesan.
