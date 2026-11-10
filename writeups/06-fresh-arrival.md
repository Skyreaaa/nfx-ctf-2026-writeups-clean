# Fresh Arrival — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** OSINT
- **Difficulty:** Medium
- **Points:** 440
- **Status:** Solved (terlihat pada profil)

## Description

Pada challenge ini aku harus menelusuri identitas dan jejak sebuah pesawat dari petunjuk visual, lalu merangkai informasi operator terdahulunya dan fotografer ke dalam format flag yang **case-sensitive**.

## Analysis

Aku mulai dari identitas pesawat, bukan menebak nama maskapai dari desain badan pesawat saja. Registrasi merupakan pengenal yang lebih konkret untuk menghubungkan foto dengan riwayat operator.

Dari penelusuran sebelumnya, aku memperoleh identitas berikut:

| Atribut | Temuan |
| --- | --- |
| Registration | `PK-ADL` |
| Model | Boeing 737-341(SF) |
| Manufacturer Serial Number (MSN) | `26854` |
| First operator | China Xinhua Airlines |
| IATA code | `XW` |
| ICAO code | `CXH` |
| Lokasi terkait | Beijing |
| Photographer | Raihan Al Faris |

Informasi yang aku cari bukan hanya operator pada saat foto diambil. Aku perlu membedakan **first operator** dari operator belakangan karena riwayat pesawat dapat berubah setelah penjualan atau konversi ke kargo.

## Solution

### 1. Mengidentifikasi pesawat
Aku memakai registrasi `PK-ADL` sebagai jangkar pencarian. Model `737-341(SF)` dan MSN `26854` membantu memastikan identitas tidak tertukar dengan pesawat dengan livery serupa.

### 2. Memeriksa riwayat operator
Aku telusuri operator awal dan menemukan **China Xinhua Airlines**. Dari identitas maskapai itu, aku memperoleh kode IATA **XW** serta kode ICAO **CXH** dan konteks kota **Beijing**.

### 3. Mengidentifikasi fotografer
Jejak atribusi foto mengarah pada nama **Raihan Al Faris**. Sesuai pola flag challenge, nama depan dipakai sebagai `raihan`.

### 4. Memperbaiki kapitalisasi
Pada percobaan awal aku memakai kode maskapai dengan huruf kecil. Nilai tersebut salah. Habis itu aku mempertahankan kode resmi dalam huruf kapital, sedangkan kota dan nama fotografer menggunakan huruf kecil:

~~~text
XW_CXH_beijing_raihan
~~~

Perbedaan huruf besar dan kecil penting karena platform menganggap flag **case-sensitive**.

## Flag yang dikonfirmasi benar dalam riwayat

~~~text
NFX{XW_CXH_beijing_raihan}
~~~

## Conclusion

Bagian yang sempat bikin aku salah ternyata kapitalisasi. Informasinya sudah ketemu, tetapi kode maskapai harus pakai huruf besar. Setelah aku perbaiki jadi `XW_CXH_beijing_raihan`, flag-nya benar.
