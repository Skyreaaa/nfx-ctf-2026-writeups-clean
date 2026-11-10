# My Lovely Freya — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Image Forensics & Encryption
- **Difficulty:** Hard
- **Points:** 380
- **Attachments:** `freya_sayangkuh.png`, `surat_untuk_freya.enc`
- **Status:** Solved pada profil; log accepted flag tidak disimpan

## Description

Aku dikasih gambar PNG sama surat yang terenkripsi. Awalnya aku coba cari petunjuk dari metadata gambar, karena dua file ini kelihatannya saling berhubungan.

## Analysis

Awalnya aku mulai dengan membaca metadata PNG dan mendapat field:

~~~text
Secret: QXlhbWdHb3Jlbmc0NQ==
~~~

Data itu berbentuk Base64. Hasil decode:

~~~text
AyamgGoreng45
~~~

Ini tampak seperti password, sehingga aku mengujinya pada berkas terenkripsi.

## Solution

### 1. Decode metadata

~~~python
import base64
print(base64.b64decode("QXlhbWdHb3Jlbmc0NQ==").decode())
~~~

Output:

~~~text
AyamgGoreng45
~~~

### 2. Menguji dekripsi langsung
Aku sempat mencoba:

~~~bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
  -in surat_untuk_freya.enc -out surat.txt \
  -pass pass:AyamgGoreng45
~~~

Percobaan ini **gagal** dengan `bad decrypt`. Artinya aku tidak boleh menyimpulkan parameter AES, KDF, IV, atau password akhir telah terverifikasi hanya dari metadata tersebut.

### 3. Memeriksa data gambar yang tidak tampak
Investigasi berikutnya menemukan kejanggalan ukuran: tinggi yang dideklarasikan pada gambar adalah **1.200 baris**, sedangkan analisis raw data menunjukkan **1.536 baris**. Perbedaan **336 baris** itu menjadi petunjuk adanya konten di luar tampilan PNG normal.

Habis itu aku mengalihkan fokus ke data baris tersembunyi, bukan terus mengulang tebakan parameter OpenSSL.

### 4. Memperoleh plaintext surat
Aku menyimpan hasilnya di file `surat_untuk_freya_decrypted.txt` adalah:

~~~text
NXCTF{FR3Y4_MY_L0V3LY!}
~~~

Alur ekstraksi lengkap dari baris tambahan hingga artefak plaintext **tidak tersimpan sebagai script reproduksi final** di arsip yang tersedia. Karena itu aku tidak menuliskan langkah dekripsi buatan seolah-olah sudah diuji.

## Flag hasil dekripsi asli

~~~text
NXCTF{FR3Y4_MY_L0V3LY!}
~~~

## Kandidat penyesuaian format portal

~~~text
NFX{FR3Y4_MY_L0V3LY!}
~~~

**Ketelitian:** Catatan pengerjaan aku sebelumnya menyarankan penyesuaian prefix `NXCTF` ke `NFX`, tetapi aku belum dapat memastikan string mana yang cocok dengan submit yang diterima. Screenshot terbaru hanya membuktikan challenge telah solved.

## Conclusion

Dari sini aku belajar untuk tidak terpaku pada password metadata ketika percobaan dekripsi gagal. Anomali struktur gambar juga dapat menyembunyikan data penting. Dalam write-up ini aku memisahkan temuan yang terbukti (metadata, anomali baris, plaintext) dari parameter dekripsi yang belum terdokumentasi.
