# Genresi

Kerangka Genresi untuk Odoo 17.0 Community, sistem stok, produksi, kas, piutang,
dan laporan harian CV Generasi Restu Ibu.

## Environment

- Odoo source: `D:\odoo\Odoo17\server\odoo-bin`
- Python runtime Odoo: `D:\odoo\Odoo17\python\python.exe`
- Python proyek: `.venv\Scripts\python.exe` (Python 3.12.3)
- PostgreSQL: 17.x, port 5432
- Odoo: port 8073
- Database yang dikelola script: `genresi_dev` dan `genresi_test`

Rahasia hanya berada di `.env`, yang di-ignore git. Database di luar pola `genresi_*`
tidak boleh disentuh.

## Addon

- `genresi_base`: branding, company defaults, role, dan kerangka menu.
- `genresi_stock`: arah dependensi stok dan produksi.
- `genresi_cash`: arah dependensi kas dan piutang.
- `genresi_report`: arah dependensi laporan dan `board`.
- `genresi_demo`: data dev/presentasi opsional; `auto_install=False` dan semua seed berada
  di `data/`, bukan folder Odoo `demo/`.

Database tetap diinisialisasi dengan `--without-demo=all` dan `--skip-auto-install`.
`spreadsheet` dan `spreadsheet_dashboard` tetap terpasang karena merupakan rantai
dependensi teknis dari `board`, yang diperlukan oleh `genresi_report`; keduanya bukan
fitur Accounting Enterprise.

## Menjalankan dari nol di Windows PowerShell

1. Pastikan source Odoo 17 tersedia di `D:\odoo\Odoo17` dan PostgreSQL aktif.
2. Salin `.env.example` menjadi `.env`, lalu isi `ODOO_ADMIN_PASSWD` dan kredensial
   PostgreSQL. Jangan commit `.env`.
3. Aktifkan environment proyek:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Jalankan inisialisasi database pengembangan dan data contoh Agustus 2026:

   ```powershell
   .\scripts\init_demo_db.ps1
   ```

   Script ini memasang `genresi_demo` hanya di `genresi_dev`. Test database tidak
   memasang addon tersebut.

5. Jalankan Odoo:

   ```powershell
   .\scripts\run_odoo.ps1
   ```

6. Buka [http://127.0.0.1:8073/web/login?db=genresi_dev](http://127.0.0.1:8073/web/login?db=genresi_dev).
   Login memakai user `admin` dan password dari `ODOO_ADMIN_PASSWD`.

7. Jalankan test:

   ```powershell
   .\scripts\run_tests.ps1
   ```

   Database `genresi_test` dibuat ulang setelah konfirmasi eksplisit.

## Branding

Odoo Community primary tokens di-override secara kecil pada bundle
`web._assets_primary_variables`: primary `#A85A14`, hover `#8A4A10`, brand `#D67C25`,
soft `#E2A165`, dan tint `#FBEEDD`. Logo login dan laporan memakai logo lengkap;
navbar serta favicon memakai ikon roti transparan. Tidak ada JavaScript custom.

File `docs/logo.png` yang disebut dalam brief belum tersedia di workspace. Script
`scripts/build_brand_assets.py` memakai `docs/logobaked.png` sebagai fallback yang
tersedia dan mencatat fallback tersebut saat dijalankan.

## Tooling proyek

Tooling dipasang di `.venv`, bukan global:

- `pre-commit 4.1.0`
- `ruff 0.9.10`
- `pylint 3.0.4`
- `pylint-odoo 9.0.0`
- `Pillow 11.1.0`

Pasang hook git dan jalankan semua hook:

```powershell
pre-commit install
pre-commit run --all-files
```

`pylint-odoo 9.0.0` terpasang pada Python 3.12.3 dan digunakan tanpa melonggarkan
aturan lint.

## Dokumentasi

- `AGENTS.md`: aturan permanen proyek.
- `docs/PRD v1.1 — Genresi Sistem Manajemen Stok, Kas & Piutang Harian.md`: sumber
  kebutuhan dan angka penerimaan.
- `docs/odoo-mapping.md`: pemetaan seluruh fitur PRD ke Odoo Community/custom.

Jangan push tanpa izin pengguna. Setiap fase berhenti untuk review sebelum fase berikutnya.
