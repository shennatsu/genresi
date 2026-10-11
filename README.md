# Genresi

Kerangka Genresi untuk Odoo 17.0 Community, sistem stok, produksi, kas, piutang, dan laporan harian CV Generasi Restu Ibu.

Fase 0A menyiapkan environment dan empat addon installable tanpa fitur bisnis:

- `genresi_base` — dasar dan dependensi bersama.
- `genresi_stock` — kerangka stok dan produksi.
- `genresi_cash` — kerangka kas dan piutang.
- `genresi_report` — kerangka laporan.

## Menjalankan dari nol di Windows PowerShell

1. Pastikan source Odoo 17 tersedia di `D:\odoo\Odoo17` dan PostgreSQL aktif.
2. Salin `.env.example` menjadi `.env`, lalu isi `ODOO_ADMIN_PASSWD` dan kredensial PostgreSQL yang benar. Jangan commit `.env`.
3. Jalankan inisialisasi database pengembangan:

   ```powershell
   .\scripts\init_demo_db.ps1
   ```

   Script membuat `genresi_dev` bila belum ada dan memasang empat addon Genresi. Script tidak menyentuh database di luar pola `genresi_*`.

4. Jalankan Odoo:

   ```powershell
   .\scripts\run_odoo.ps1
   ```

5. Buka [http://127.0.0.1:8073](http://127.0.0.1:8073) untuk memastikan service aktif, lalu login ke database pengembangan melalui [http://127.0.0.1:8073/web/login?db=genresi_dev](http://127.0.0.1:8073/web/login?db=genresi_dev) dengan user `admin` dan password dari `ODOO_ADMIN_PASSWD`. Karena `dbfilter` mengizinkan `genresi_dev` dan `genresi_test` sekaligus, Odoo tidak memilih database secara otomatis dari URL root.

6. Jalankan test:

   ```powershell
   .\scripts\run_tests.ps1
   ```

   Database `genresi_test` dibuat ulang setiap run setelah konfirmasi eksplisit.

## Kualitas kode

Install `pre-commit`, lalu jalankan:

```powershell
pre-commit run --all-files
```

Source Odoo tidak disalin ke repository ini. Runtime proyek dan konfigurasi lokal (`.odoo_runtime`, `odoo.conf`, `.env`) di-ignore oleh git.

## Status fase

Fase 0A selesai setelah database `genresi_dev` berhasil dibuat dengan empat addon terpasang, Odoo dapat diakses di port 8073, test berjalan, dan pre-commit lolos. Setelah itu berhenti untuk review sebelum Fase 0B.
