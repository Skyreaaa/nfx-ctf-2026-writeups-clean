# Notulen Senin Pagi

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / PDF Forensics
- **Difficulty:** Baby
- **Points:** 280
- **Author:** Syahril
- **Attachment:** `laporan_kegiatan_bulan_november.pdf`
- **Status:** Solved

## Description

Di petunjuk soal, sekretaris bilang semua sudah ditulis, tapi bosnya tidak bisa melihat apa-apa. Dari situ aku curiga ada tulisan yang sebenarnya tersimpan di PDF, cuma tidak kelihatan waktu dibuka biasa.

## Analysis

Awalnya aku buka PDF-nya. Isinya terlihat seperti laporan kegiatan November biasa, lengkap dengan ringkasan, rapat, dan rencana bulan berikutnya. Flag-nya tidak kelihatan. Karena itu aku coba ekstrak semua teks yang tersimpan, bukan cuma baca halaman yang tampil.

## Solution

### 1. Memeriksa PDF
Pertama, aku menggunakan tools dari Poppler:

~~~bash
pdfinfo laporan_kegiatan_bulan_november.pdf
~~~

### 2. Mengekstrak teks

Terus aku meminta `pdftotext` mencetak konten dokumen tanpa bergantung pada warna teksnya:

~~~bash
pdftotext -layout laporan_kegiatan_bulan_november.pdf -
~~~

Di bagian akhir hasil ekstraksi aku menemukan:

~~~text
NFX{M4kHLuK_T4k_K4s4T_M4T4}
~~~

### 3. Memahami penyembunyian

Teks flag disembunyikan secara visual dengan warna putih pada latar putih. Dalam konten grafis PDF, operator `g` mengatur warna fill dalam grayscale; nilai `1 g` merepresentasikan putih. Karena objek teks tetap berada di dalam PDF, ekstraksi teks masih dapat membacanya.

Masalah challenge ini bukan dekripsi, melainkan membaca data yang tidak ditampilkan secara visual.

## Flag

~~~text
NFX{M4kHLuK_T4k_K4s4T_M4T4}
~~~

## Conclusion

Ternyata flagnya memang ada di PDF, cuma warna tulisannya dibuat putih. Begitu aku ekstrak teksnya, flag langsung kelihatan. Jadi kalau ada PDF yang terlihat biasa saja, aku perlu cek juga isi teks di balik tampilannya.
