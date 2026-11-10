# Titipan Akhir Tahun

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / PDF Forensics
- **Difficulty:** Easy
- **Points:** 360
- **Author:** Syahril
- **Attachment:** `laporan_kegiatan_bulan_desember.pdf`
- **Status:** Solved

## Description

Aku dikasih PDF laporan bulan Desember. Dari petunjuk soal, aku curiga ada file lain yang ikut disimpan di dalam PDF, bukan cuma tulisan di halaman. Makanya aku langsung cek apakah ada attachment yang disembunyikan.

## Analysis

Awalnya aku mulai dari metadata PDF dan daftar embedded attachment, bukan hanya mengekstrak teks halaman. Dari catatan analisis, file tersebut merupakan PDF 1.7 satu halaman.

## Solution

### 1. Memeriksa metadata dokumen

~~~bash
pdfinfo laporan_kegiatan_bulan_desember.pdf
~~~

### 2. Mendaftar embedded file

~~~bash
pdfdetach -list laporan_kegiatan_bulan_desember.pdf
~~~

Output:

~~~text
1 embedded files
1: doksli.txt
~~~

Aku nemu satu lampiran bernama `doksli.txt`, terhubung melalui struktur `/Names` → `/EmbeddedFiles` pada PDF.

### 3. Mengekstrak lampiran

~~~bash
pdfdetach -save 1 -o doksli.txt laporan_kegiatan_bulan_desember.pdf
cat doksli.txt
~~~

Output:

~~~text
TkZYe0QzQzBEM19ENE5EM0MwRDNfTDRHMX0=
~~~

String ini cocok dengan format Base64, sehingga aku lanjutkan dengan decoding.

### 4. Decode Base64

~~~bash
base64 -d doksli.txt
~~~

Output:

~~~text
NFX{D3C0D3_D4ND3C0D3_L4G1}
~~~

Cara lain yang aku gunakan untuk reproduksi lintas platform:

~~~python
from pathlib import Path
import base64
encoded = Path("doksli.txt").read_bytes().strip()
print(base64.b64decode(encoded, validate=True).decode("utf-8"))
~~~

## Flag

~~~text
NFX{D3C0D3_D4ND3C0D3_L4G1}
~~~

## Conclusion

Dua lapisan yang harus aku buka adalah embedded attachment PDF dan Base64 di dalam attachment. Challenge ini mengingatkan aku bahwa PDF dapat membawa file tambahan yang tidak tampak di halaman utama.
