# The Alchemist's Sandbox — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Python Jail & Cryptography
- **Difficulty:** Medium
- **Points:** 320
- **Author:** Illal
- **Attachment sumber:** `chall.py`
- **Status:** Solved pada profil; hasil solver diverifikasi lokal dengan round-trip

## Description

Di soal ini aku harus melewati Python sandbox yang membatasi banyak sintaks: angka, tanda petik, import, sampai akses atribut privat. Setelah berhasil baca state yang disembunyikan, aku masih perlu membalik enkripsi 32 ronde untuk mendapatkan flag.

## Analysis

Dalam `chall.py`, fungsi `run_sandbox()` memberi akses pada objek fungsi `als` (referensi ke `_encrypt_vault`) dan built-in `getattr` serta `chr`.

Filter AST melarang penulisan atribut seperti `als.__globals__` **sebagai node `ast.Attribute`**. Namun aku melihat celah: `getattr(als, nama_yang_dibangun)` dapat mengambil atribut yang sama jika aku membangun namanya secara dinamis.

Data target adalah `_VAULT_STATE`, berisi **21 word 16-bit** yang merepresentasikan flag 42 byte setelah 32 ronde.

## Solution

### 1. Bypass pembatasan karakter
Aku memakai nilai boolean `True` sebagai bilangan `1`, lalu menggunakan bit shifting dan assignment expression `:=` untuk menciptakan kode karakter yang dibutuhkan oleh `chr`. Dengan cara itu aku tidak perlu menulis literal angka maupun string di dalam payload sandbox.

Payload aku merekonstruksi `__globals__` dan key `_VAULT_STATE` melalui `chr`, lalu secara konseptual melakukan:

~~~python
als.__globals__["_VAULT_STATE"]
~~~

Payload asli berukuran **315 karakter**, lebih pendek dari batas **1024 karakter**. Bentuk persisnya tersedia dalam [`scripts/alchemist_solve.py`](../scripts/alchemist_solve.py).

### 2. Membaca vault state
Hasil bypass:

~~~text
[29406, 62193, 3550, 51604, 54474, 58556, 5807,
 62536, 3004, 10962, 33499, 52037, 51010, 45605,
 6009, 18571, 21884, 35367, 29761, 57118, 51549]
~~~

### 3. Membalik 32 ronde enkripsi
Konstanta ronde:

~~~python
rc = ((r * 0x9E37) + 0x7F4A) & 0xFFFF
~~~

Setiap ronde melakukan operasi aritmetika modular, XOR, rotasi 16-bit, serta permutasi:

~~~python
w = [w[(i * 4) % 21] for i in range(21)]
~~~

Aku melakukan **inverse round** dari `31` menuju `0`. Pada setiap ronde:

1. Membalik permutasi indeks `(4 * i) % 21`.
2. Memproses word mundur dari indeks 20 menuju 0.
3. Menerapkan `ror16(value, 5)`, pengurangan konstanta modular, dan XOR dengan hasil mix.
4. Mengemas ulang 21 word big-endian menjadi 42 byte plaintext menggunakan `struct.pack(">21H", *words)`.

### 4. Memverifikasi dengan enkripsi ulang
Aku tidak hanya mengandalkan hasil plaintext yang tampak seperti flag. Aku mengecek:

~~~python
assert _encrypt_vault(flag_bytes) == _VAULT_STATE
~~~

Log solver:

~~~text
Sandbox bypass: PASS (315 characters)
Encryption round-trip: PASS
Flag: NFXCTF{pyj41l_4st_4lch3my_vm_pwn_d84f216a}
~~~

Reproduksi (dengan `chall.py` asli diletakkan sejajar solver):

~~~bash
python scripts/alchemist_solve.py
~~~

**Catatan reproduksi:** Solver yang diarsipkan mengimpor `chall.py` dari direktori script. Jika dijalankan dengan perintah di atas, letakkan `chall.py` di folder `scripts/` atau gunakan perintah `cd scripts && python alchemist_solve.py` setelah menyalinnya ke lokasi itu.

## Flag hasil dekripsi

~~~text
NFXCTF{pyj41l_4st_4lch3my_vm_pwn_d84f216a}
~~~

Hasil terenkripsi asli berawalan **NFXCTF**, sedangkan panduan portal mencontohkan **NFX**. Aku mempertahankan hasil asli karena tidak ada log submission spesifik yang menunjukkan apakah prefix perlu disesuaikan.

## Conclusion

Aku bisa mengambil `_VAULT_STATE` lewat `getattr()` tanpa menulis akses atribut privat secara langsung. Setelah datanya dapat, aku balik 32 ronde enkripsinya. Hasilnya aku cek lagi dengan mengenkripsi ulang, dan hasilnya cocok dengan state awal.
