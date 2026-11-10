# NarrowGate — Write-up

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Pwn / Binary Exploitation
- **Difficulty:** Insane
- **Points:** 420
- **Author:** Kesatria Baja Ringan
- **Target:** `s1.nfx.my.id:41619`
- **Status:** Solved (profil; flag kemudian diperoleh dari remote)

## Description

Di soal ini aku menghadapi binary x86-64 dengan dua bug yang dapat digabung: **format string** pada input nickname dan validasi panjang **16-bit** yang berbeda dari ukuran baca sebenarnya. Binary juga memakai stack canary, PIE, NX, Full RELRO, dan filter seccomp.

## Analysis

Aku nemu dua primitive berbeda:

1. `printf(nickname)` memproses format string yang aku kontrol, sehingga bisa membocorkan nilai stack.
2. Binary membaca jumlah blok `uint32_t`, menghitung `blocks * 64`, tetapi validasi hanya melihat **16 bit bawah** dari `(blocks * 64) - 1`. Pembacaan data selanjutnya tetap menggunakan ukuran 32-bit sehingga aku bisa menulis jauh melewati buffer stack.

Karena `execve` dibatasi seccomp, target eksploitasi aku bukan shell, melainkan ROP berbasis syscall **open/read/write (ORW)**.

## Solution

### 1. Membocorkan canary, PIE, dan libc
Aku mengirim nickname:

~~~text
%27$p|%29$p|%43$p
~~~

Mapping nilai yang berhasil direkonstruksi:

| Payload | Kebocoran |
| --- | --- |
| `%27$p` | Stack canary |
| `%29$p` | Return address pada `main+0x4e` |
| `%43$p` | Return address ke libc |

Aku menghitung base address:

~~~python
pie_base  = leak_pie_return - 0x154b
libc_base = leak_libc_return - 0x29d90
~~~

Canary harus memiliki low byte nol. PIE/libc base aku cek harus aligned ke page 4 KiB.

### 2. Bypass pengecekan jumlah blok
Dalam disassembly, nilai dibentuk dengan pergeseran dan pengecekan `cmp ax, 0x3f`. Aku memilih:

~~~text
blocks           = 1025
blocks * 64      = 65600 = 0x10040
blocks * 64 - 1  = 65599 = 0x1003f
low 16 bits      = 0x003f
~~~

Validasi melihat `0x003f` dan mengizinkan input, sedangkan `read` mendapat ukuran yang jauh lebih besar dari buffer.

### 3. Menata payload stack
Offset yang aku identifikasi:

~~~text
0x00–0x47 : 72 byte padding
0x48–0x4f : 8 byte stack canary
0x50–0x57 : saved RBP
0x58+     : ROP chain
~~~

Dengan canary yang dibocorkan, aku bisa membangun payload tanpa langsung gagal pada stack protector.

### 4. Membuat ORW ROP
Aku memakai gadget dari libc bawaan challenge untuk melakukan:

~~~text
read(0, writable_bss, 0x80)   # menerima path file
open(path, O_RDONLY, 0)      # syscall no. 2
read(fd, output_buf, 0x100)
write(1, output_buf, 0x100)
exit(0)
~~~

Aku sengaja memakai **raw syscall open**; wrapper glibc dapat memilih `openat` yang tidak sesuai filter seccomp challenge.

### 5. Menguji lokal dan remote
Awalnya aku berhasil membaca fixture lokal `NFX{LOCAL_VALIDATION_ONLY}` pada **3 dari 3** percobaan, tetapi itu bukan flag lomba. Setelah mengubah target file pada service remote dari `/flag` ke `flag.txt`, hasil remote berhasil diperoleh.

~~~bash
python3 scripts/solve_narrowgate.py --remote --path flag.txt
~~~

Flag remote yang tersimpan dalam riwayat:

~~~text
NFX{ex3cve_d3ni3d_but_0pen_r34d_writ3_s4v3d_th3_day}
~~~

Script exploit penuh tersedia di [`scripts/solve_narrowgate.py`](../scripts/solve_narrowgate.py). Untuk menjalankan mode lokal dibutuhkan ELF, loader, dan libc challenge asli di `narrowgate_analysis/peserta/`.

## Flag

~~~text
NFX{ex3cve_d3ni3d_but_0pen_r34d_writ3_s4v3d_th3_day}
~~~

## Conclusion

Awalnya ROP chain aku berhasil membaca file flag uji lokal, tapi itu belum flag kompetisi. Setelah aku sesuaikan path pada server remote menjadi `flag.txt`, baru flag asli terbaca. Intinya aku menggabungkan leak, bug validasi 16-bit, overflow, dan ORW ROP yang tidak diblokir seccomp.
