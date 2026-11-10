# Stay — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Unicode Steganography
- **Difficulty:** Medium
- **Points:** 380
- **Input teks:** lirik/teks `stay.txt` dalam riwayat investigasi
- **Status:** Solved (profil)

## Description

Awalnya aku lihat file teksnya cuma seperti lirik biasa. Tapi pas aku cek karakter tersembunyinya, ternyata ada zero-width Unicode yang disisipkan di antara huruf-huruf. Dari situlah aku mulai decode pesannya.

## Analysis

Aku nemu **176 karakter zero-width** dari empat jenis:

| Karakter | Bit |
| --- | --- |
| U+200C ZERO WIDTH NON-JOINER | `00` |
| U+2060 WORD JOINER | `01` |
| U+200B ZERO WIDTH SPACE | `10` |
| U+200D ZERO WIDTH JOINER | `11` |

Setiap karakter memuat dua bit, sehingga 176 karakter menjadi 352 bit atau **44 byte ASCII**. Hasil 44 byte tersebut berupa Base64; setelah Base64 masih diperlukan XOR.

## Solution

### 1. Mengubah Unicode tersembunyi menjadi bit

~~~python
from pathlib import Path
text = Path("stay.txt").read_text(encoding="utf-8")
mapping = {
    "\u200c": "00",
    "\u2060": "01",
    "\u200b": "10",
    "\u200d": "11",
}
bits = "".join(mapping[c] for c in text if c in mapping)
assert len(bits) == 352
encoded = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
print(encoded.decode("ascii"))
~~~

Output dari catatan sebelumnya:

~~~text
KDkvOC8VFBJVFTMeXxMOPgFfNl8JORUEXzYKUxQKEQ==
~~~

### 2. Decode Base64

~~~python
import base64
raw = base64.b64decode(encoded, validate=True)
print(raw.hex())
~~~

Hex:

~~~text
28392f382f1514125515331e5f130e3e015f365f093915045f360a53140a11
~~~

### 3. Repeating-key XOR

Aku coba kunci `falling` yang sesuai dengan konteks challenge dan berhasil mendapatkan teks yang dapat dibaca:

~~~python
key = b"falling"
plain = bytes(v ^ key[i % len(key)] for i, v in enumerate(raw))
print(plain.decode("ascii"))
~~~

Output:

~~~text
NXCTF{st4y_w1th_m3_1n_th3_d4rk}
~~~

### 4. Memisahkan raw output dan format portal
String yang benar-benar dihasilkan XOR berawalan `NXCTF`. Format flag di portal dituliskan `NFX`, sehingga kandidat yang sebelumnya aku susun adalah:

~~~text
NFX{st4y_w1th_m3_1n_th3_d4rk}
~~~

## Flag

**Hasil decoding:** `NXCTF{st4y_w1th_m3_1n_th3_d4rk}`  
**Kandidat NFX:** `NFX{st4y_w1th_m3_1n_th3_d4rk}`

Tidak ada log submit per-string yang mengonfirmasi prefix mana yang diterima, meskipun halaman profil menunjukkan challenge berstatus solved.

## Conclusion

Jadi yang aku baca bukan isi liriknya, tapi karakter zero-width yang tidak kelihatan. Setelah aku ubah ke bit, decode Base64, lalu XOR dengan kunci `falling`, baru keluar teks flag.
