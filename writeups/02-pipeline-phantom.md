# Pipeline Phantom

## Challenge Information
- **Event:** NFX CTF 2026
- **Category:** Misc / Git Forensics & CI/CD
- **Difficulty:** Easy
- **Points:** 480
- **Status:** Solved
- **Repository target:** https://github.com/netmetrics-net/c2-deploy-pipeline

## Description

Di soal ini ceritanya ada operator C2 yang pakai GitHub Actions dan merasa secret-nya aman karena otomatis ditutup di log. Aku langsung fokus ke workflow sama Actions run, karena kemungkinan ada secret yang dicetak dengan cara yang tidak kena masking.

## Analysis

Aku urutkan pengecekannya dari file workflow, log Actions, lalu riwayat commit Git. Aku cuma baca repository publiknya, tidak menjalankan workflow atau mengubah file di sana.

## Solution

### 1. Membaca workflow GitHub Actions

Aku membuka [`.github/workflows/deploy.yml`](https://github.com/netmetrics-net/c2-deploy-pipeline/blob/main/.github/workflows/deploy.yml) dan menemukan langkah **Validate Deployment Secrets** yang memuat nilai secret `C2_API_KEY` ke variabel `C2_KEY`.

Di bagian debug, workflow menjalankan:

~~~bash
echo -n "[DEBUG_PAYLOAD]: "
echo "$C2_KEY" | sed 's/./& /g'
~~~

Perintah `sed` menambahkan spasi setelah setiap karakter. Secret yang sudah diubah representasinya tidak sama dengan string asli yang hendak disamarkan.

### 2. Mencari fragmen di Actions log

Aku membaca [Run #2](https://github.com/netmetrics-net/c2-deploy-pipeline/actions/runs/40221200390) dan membandingkannya dengan [Run #1](https://github.com/netmetrics-net/c2-deploy-pipeline/actions/runs/40221195968).

Nilai environment terlihat disamarkan:

~~~text
C2_KEY: ***
~~~

Tetapi baris debug masih mencetak:

~~~text
[DEBUG_PAYLOAD]: N F X { g h _ 4 c t 1 0 n s _ m 4 s k _ b y p 4 s s _
~~~

Aku menghapus spasi yang sengaja ditambahkan dan mendapatkan fragmen pertama:

~~~text
NFX{gh_4ct10ns_m4sk_byp4ss_
~~~

Karena belum ada tanda `}`, aku tahu flag ini belum lengkap.

### 3. Menemukan SHA pada issue keamanan

Selanjutnya, aku mengecek [Issue #1](https://github.com/netmetrics-net/c2-deploy-pipeline/issues/1), yang mencatat branch sementara dan commit yang sempat dikembalikan:

~~~text
Branch: feature/credential-cleanup (deleted)
Reverted Commit Hash: 62d3ad55d0cd1d95c64fc0168e317b928b0b4d95
~~~

Dari sini aku sadar penghapusan branch tidak otomatis menghapus seluruh objek commit yang masih bisa dijangkau dengan SHA.

### 4. Membaca commit lama

Aku membuka [commit 62d3ad5](https://github.com/netmetrics-net/c2-deploy-pipeline/commit/62d3ad55d0cd1d95c64fc0168e317b928b0b4d95), lalu menemukan fragmen kedua pada `config/c2_endpoint.json`:

~~~json
{
  "backup_key_fragment": "4nd_0rph4n_c0mm1t_l34k_9f82}"
}
~~~

### 5. Menggabungkan fragmen

~~~python
prefix = "NFX{gh_4ct10ns_m4sk_byp4ss_"
suffix = "4nd_0rph4n_c0mm1t_l34k_9f82}"
print(prefix + suffix)
~~~

Output:

~~~text
NFX{gh_4ct10ns_m4sk_byp4ss_4nd_0rph4n_c0mm1t_l34k_9f82}
~~~

## Flag

~~~text
NFX{gh_4ct10ns_m4sk_byp4ss_4nd_0rph4n_c0mm1t_l34k_9f82}
~~~

## Conclusion

Aku tidak menemukan flag dari satu file saja. Aku perlu menggabungkan bocoran dari GitHub Actions dengan fragmen dari commit branch yang dihapus. Dari challenge ini aku jadi paham bahwa masking secret bukan alasan untuk mencetak kredensial ke log, dan menghapus branch bukan jaminan riwayat sensitif langsung hilang.

> Catatan: pada draft investigasi awal challenge ini sempat dinamai *Velox Phantom*. Aku memakai judul *Pipeline Phantom* yang muncul di halaman profil CTF.
