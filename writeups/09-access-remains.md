# Access Remains — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Forensics / Windows DPAPI
- **Difficulty:** Hard
- **Points:** 400
- **Attachment:** `Access_Remains.zip`
- **Status:** Solved pada profil; string flag terakhir tidak terekam sebagai submit terkonfirmasi

## Description

Di Access Remains aku dapat barang bukti Windows. Awalnya aku cari informasi akunnya dulu, lalu lanjut ke DPAPI dan Credential Manager. Dari sana aku dapat password untuk membuka arsip berikutnya.

## Analysis

Setelah membuka `Access_Remains.zip` dan barang bukti `Evidence.zip`, aku menemukan profil:

~~~text
Evidence/Users/ariaf/
~~~

Nilai penting dari analisis sebelumnya:

| Artefak | Hasil |
| --- | --- |
| Username | `ariaf` |
| RID | `1005` |
| SID | `S-1-5-21-3304503823-3980900213-1333018566-1005` |
| NTLM | `f545ff727c989c387b9d1be6db74ea1c` |
| Password pengguna yang diverifikasi | `ariafe006` |
| Preferred DPAPI masterkey GUID | `bb24f650-d046-439c-a88b-ab8f89ba61a4` |

Nilai-nilai tersebut berasal dari *challenge evidence*, bukan kredensial sistem pengguna sebenarnya.

## Solution

### 1. Mengidentifikasi akun Windows
Awalnya aku mulai dari profil `ariaf`, lalu menghubungkan RID dan SID untuk memastikan artefak credential manager berada di bawah akun yang sama.

### 2. Merekonstruksi kredensial
Dari artefak credential dan hash NTLM, aku memperoleh password pengguna:

~~~text
ariafe006
~~~

### 3. Menelusuri DPAPI
Aku nemu preferred masterkey:

~~~text
bb24f650-d046-439c-a88b-ab8f89ba61a4
~~~

Aku pakai konteks akun dan masterkey tersebut untuk membaca data rahasia yang tersimpan dalam Windows Credential Manager.

### 4. Mendapatkan password arsip
Data credential manager mengarah pada password:

~~~text
KumikoOumae2107!@
~~~

Aku menggunakannya untuk mengakses arsip `Kumiko.zip`, yang berisi lima gambar dan `note.txt`.

### 5. Memeriksa gambar petunjuk
Di antara gambar yang diekstrak, petunjuk flag terletak pada:

~~~text
kumiko03.jpg
~~~

Pada pembacaan awal karakter kedua bagian hex sempat ditafsirkan sebagai `B`. Aku membandingkan kembali karakter tersebut dan mengoreksinya menjadi `E`.

## Flag kandidat terkoreksi dari gambar

~~~text
NFX{3E2D6090E7EEB47D538FC27AC2789C02}
~~~

**Catatan:** Aku sempat salah baca karakter di gambar: awalnya `3B2D...`, lalu aku koreksi jadi `3E2D...`. Challenge ini sudah Solved di profil, tapi aku tidak punya rekaman submit terakhir untuk memastikan string persis yang diterima.

## Conclusion

Dari akun Windows `ariaf`, aku lanjut ke DPAPI sampai dapat password arsip `Kumiko.zip`. Setelah itu aku cek gambarnya. Di tahap akhir, satu karakter hex yang keliru bikin flag salah, jadi aku cek ulang hasil bacaan gambarnya.
