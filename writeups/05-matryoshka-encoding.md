# Matryoshka Encoding

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Encoding
- **Difficulty:** Easy
- **Points:** 460
- **Author:** Illal
- **Attachment:** `capsule.dat`
- **Status:** Solved (profil peserta)

## Description

Challenge menggambarkan kapsul data yang dibungkus berlapis-lapis seperti boneka Matryoshka. Aku menafsirkan ini sebagai rangkaian encoding dan transformasi byte yang harus dibongkar dalam urutan tepat.

## Analysis

Aku tidak berharap mendapatkan flag setelah satu kali decode. Berdasarkan hasil analisis, urutan lapisannya:

~~~text
capsule.dat
  └── Pairwise byte swap
        └── Base64 decode
              └── zlib decompress
                    └── Base85 decode
                          └── Repeating-key XOR ("NFX!")
                                └── Flag
~~~

## Solution

### 1. Membaca file dan membalik pasangan byte

Data awal terdiri dari 80 karakter. Aku melakukan *swap* dalam setiap pasangan byte. Contoh: `BADC` menjadi `ABCD`.

~~~python
from pathlib import Path
data = Path("capsule.dat").read_bytes().strip()
if len(data) % 2 != 0:
    raise ValueError("Data harus memiliki panjang genap")
data = bytes(
    x
    for i in range(0, len(data), 2)
    for x in (data[i + 1], data[i])
)
~~~

### 2. Base64 decoding

~~~python
import base64
data = base64.b64decode(data)
~~~

Hasilnya masih berupa data biner.

### 3. zlib decompression

~~~python
import zlib
data = zlib.decompress(data)
~~~

### 4. Base85 decoding

~~~python
data = base64.b85decode(data)
~~~

Hasil tahap ini tercatat sepanjang **40 byte**.

### 5. Repeating-key XOR

Kunci XOR yang aku pakai adalah `NFX!`, diulang hingga sepanjang ciphertext.

~~~python
key = b"NFX!"
decoded = bytes(value ^ key[i % len(key)] for i, value in enumerate(data))
print(decoded.decode("utf-8"))
~~~

Output mentah:

~~~text
NFXCTF{m4try0shk4_0n10n_p33l3d_c309b71e}
~~~

### 6. Memeriksa format flag

Pada ringkasan pengerjaan sebelumnya aku sempat menormalkan prefix `NFXCTF{` menjadi `NFX{`, sesuai format challenge lain. Tetapi **output decoding asli** tetap `NFXCTF{`. Aku tidak memiliki rekaman submit per-string, sehingga kedua nilai ini aku tuliskan terpisah dan tidak mengklaim normalisasi itu bagian dari algoritma.

**Output raw:**

~~~text
NFXCTF{m4try0shk4_0n10n_p33l3d_c309b71e}
~~~

**Kandidat dengan format NFX:**

~~~text
NFX{m4try0shk4_0n10n_p33l3d_c309b71e}
~~~

## Reproduction

~~~bash
python scripts/solve_matryoshka.py capsule.dat
~~~

## Conclusion

Aku baru bisa dapat pesannya setelah urutannya benar: swap byte, Base64, zlib, Base85, lalu XOR. Kalau ada satu langkah yang keliru, hasil berikutnya tidak kebaca. Output aslinya juga tetap aku simpan supaya tidak tertukar dengan flag yang prefix-nya disesuaikan.
