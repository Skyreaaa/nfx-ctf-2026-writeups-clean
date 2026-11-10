# Bluebird Session — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Forensics / Linux Artifact Analysis
- **Difficulty:** Hard
- **Points:** 440
- **Attachment:** `Bluebird_Session.zip`
- **Status:** Solved pada profil; log submit per-string tidak ada di arsip

## Description

Awalnya aku dapat file ZIP berisi barang bukti Linux. Aku perlu cari hubungan antara pengguna, riwayat login, dan file yang mereka simpan. Jadi bukan sekadar ekstrak ZIP lalu cari file flag.

## Analysis

Setelah aku ekstrak file-nya, arsip luar `Bluebird_Session.zip` menggunakan kata sandi `nxctf.id` dan menghasilkan `Evidence.zip`. Waktu aku periksa, dua pengguna Linux penting muncul:

| Linux user | UID | Peran/petunjuk |
| --- | ---: | --- |
| `mizore` | 1001 | Liz / Mizore |
| `nozomi` | 1002 | Blue Bird |

Ini membuat aku memilih `nozomi` sebagai nama pengguna yang terkait dengan Blue Bird, bukan `mizore`.

## Solution

### 1. Membuka evidence
Aku ekstrak arsip sesuai petunjuk sandi dari soal, lalu menelusuri struktur berkas Linux:

~~~bash
7z x Bluebird_Session.zip -pnxctf.id
~~~

### 2. Memeriksa artefak akun
Aku telusuri `/etc/passwd` dan `/etc/shadow`. Untuk pengguna `mizore`, log analisis menyimpan hash bertipe **sha512crypt**. Password Linux yang tercatat berhasil diperoleh adalah:

~~~text
Bluebirds1927!
~~~

Riwayat autentikasi juga memperlihatkan koneksi SSH dari `192.168.56.21`. Bagian tersebut merupakan jejak aktivitas dalam barang bukti, bukan target yang aku akses secara aktif.

### 3. Membaca riwayat shell
Dalam `.bash_history` aku menemukan perintah pengarsipan berikut:

~~~bash
7z a -tzip ../for_nozomi.zip . -p'MizoreCanFly2077!@'
~~~

Perintah ini secara langsung membocorkan password untuk arsip lanjutan:

~~~text
MizoreCanFly2077!@
~~~

### 4. Mengekstrak arsip milik Nozomi
Aku telusuri file `/home/nozomi/Documents/for_nozomi.zip` dan menggunakan password yang muncul di history:

~~~bash
7z x for_nozomi.zip -p'MizoreCanFly2077!@'
~~~

### 5. Memeriksa isi visual
Berkas gambar yang terkait dengan temuan flag adalah:

~~~text
423261422632617826.jpg
~~~

Dari pembacaan teks visual gambar dalam log investigasi aku mendapatkan nilai heksadesimal 32 karakter yang disusun ke dalam format flag.

## Flag hasil transkripsi dari bukti

~~~text
NFX{3220D64291CDFA4B26844C90690E8F1D}
~~~

**Catatan:** String di atas aku salin dari hasil pembacaan gambar. Challenge-nya memang sudah Solved di profil aku, tetapi aku tidak menyimpan log submit yang menunjukkan string persisnya.

## Conclusion

Yang paling membantu di soal ini adalah `.bash_history`. Dari situ aku nemu password ZIP, lalu bisa membuka arsip di folder Nozomi dan lanjut ke gambar yang berisi petunjuk flag.
