# Tragedi 9/11 — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** OSINT
- **Difficulty:** Hard
- **Points:** 400
- **Author:** salep88
- **Status:** Solved (profil; flag ditemukan dalam riwayat GitHub)

## Description

Di soal ini aku mulai dari video 9/11 sekitar 58,5 detik. Dari situ aku telusuri jejak digitalnya sampai ke akun Reddit, repository GitHub, dan akhirnya ke commit lama yang menyimpan flag.

## Analysis

Aku memperlakukan setiap petunjuk sebagai titik sambung antarplatform. Satu akun atau repository tidak otomatis menjadi jawaban; aku harus mengikuti hubungan yang dapat diperiksa dan mencari artefak tempat flag benar-benar tersimpan.

## Solution

### 1. Memulai dari petunjuk video
Aku meninjau video 9/11 yang diberikan challenge dan mencari jejak yang menghubungkannya dengan aktivitas komunitas/forum.

### 2. Menelusuri Reddit
Petunjuk berlanjut ke akun Reddit:

~~~text
PigParkerPt2
~~~

Dari profil dan jejak digitalnya, aku memperoleh arah pencarian berikutnya menuju GitHub.

### 3. Menemukan repository
Repository yang muncul dalam penelusuran:

~~~text
xor-operation
~~~

Aku tidak berhenti pada file yang terlihat di branch saat ini. Karena challenge menekankan jejak digital, aku memeriksa **commit history**.

### 4. Memeriksa commit lama
Di riwayat Git, aku menemukan commit dengan prefix SHA:

~~~text
df34505b8a8c
~~~

Commit lama tersebut mengandung file `.env` dengan konfigurasi aplikasi. Di dalamnya juga tersimpan flag. Commit sesudahnya, dengan prefix `ea765a9c0925`, menghapus data tersebut dari versi terkini.

Bagian konfigurasi yang tercatat:

~~~dotenv
SERVER_HOST=localhost
SERVER_PORT=3002
~~~

Flag yang muncul dalam riwayat file:

~~~text
NFX{OS1NT_DU4R_D34_D0R}
~~~

## Flag

~~~text
NFX{OS1NT_DU4R_D34_D0R}
~~~

## Conclusion

Flagnya ternyata ada di file `.env` pada commit lama, bukan di branch terbaru. Aku bisa sampai ke sana lewat video, lalu Reddit, lalu repository GitHub. Jadi walaupun file itu sudah dihapus, jejaknya masih bisa dilihat dari history commit.
