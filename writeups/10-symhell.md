# SymHell — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Bash Jail
- **Difficulty:** Medium
- **Points:** 400
- **Target terbaru dalam riwayat:** `s1.nfx.my.id:49501`
- **Status:** Solved — waktu itu aku lupa mencatat flag finalnya

## Description

Di soal ini aku berhadapan dengan sebuah shell terbatas yang memblokir karakter umum untuk perintah shell. Targetnya adalah membuat Bash membaca file flag walaupun huruf, angka, dan sejumlah metakarakter terlarang dalam input langsung.

## Analysis

Validasi input yang aku identifikasi menggunakan pola berikut:

~~~python
r"[a-zA-Z0-9?*#]|\<{3}"
~~~

Artinya, aku tidak dapat mengetik perintah normal seperti `cat /flag.txt` begitu saja. Aku perlu memanfaatkan fitur ekspansi Bash dengan karakter yang masih diizinkan filter.

Dari probe ke server, aku berhasil mengidentifikasi keberadaan:

~~~text
/flag.txt
~~~

## Solution

### 1. Mengenali batas filter
Aku mengevaluasi perbedaan antara teks input sebelum dieksekusi dan interpretasinya oleh Bash. Filter memeriksa karakter input, tetapi Bash masih dapat melakukan ekspansi dan menghasilkan kata/perintah sesudah proses validasi.

### 2. Menghasilkan perintah tanpa mengetik huruf langsung
Waktu ngerjain, aku memakai payload berbasis simbol dan operasi Bash untuk merekonstruksi utilitas `cat`. Teknik utamanya adalah **membentuk string/perintah secara tidak langsung**, sehingga perintah baru terwujud saat dievaluasi shell.

### 3. Memanfaatkan pola path
Aku juga mencoba glob berbasis negated character class agar nama file tidak perlu diketik:

~~~bash
/[!^][!^][!^][!^].[!^][!^][!^]
~~~

Pola tersebut dibangun untuk mencocokkan nama file berformat empat karakter, titik, tiga karakter. Ia merupakan bagian dari strategi membaca `/flag.txt` tanpa menuliskan nama file secara literal pada input yang disaring.

### 4. Memperbarui endpoint
Endpoint yang dipakai pada investigasi awal:

~~~text
s1.nfx.my.id:48867
~~~

Kemudian server challenge dipindahkan ke:

~~~bash
nc s1.nfx.my.id 49501
~~~

Aku menyesuaikan payload pengiriman PowerShell/Python ke port baru tersebut. Percobaan pada endpoint lama sempat gagal dengan `ConnectionRefusedError`, jadi error koneksi tidak otomatis berarti payload salah.

## Flag

**Catatan:** SymHell sudah berhasil aku solve, tapi waktu itu aku **lupa menyimpan atau mencatat flag finalnya**. Jadi untuk sekarang aku belum bisa mencantumkan string `NFX{...}` yang tepat. Aku tetap tulis proses pengerjaannya, daripada mengisi flag yang belum tentu benar.

## Conclusion

Di soal ini aku pakai celah antara filter input dan ekspansi Bash. Walaupun perintah biasa diblokir, Bash masih bisa membentuk perintah dari simbol tertentu. Challenge-nya sudah solved, cuma hasil flag terakhirnya lupa aku simpan.
