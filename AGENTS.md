# Aturan permanen Genresi

## Konteks proyek

- Genresi berjalan di Odoo 17.0 Community untuk CV Generasi Restu Ibu.
- Sumber aturan bisnis, angka, dan penerimaan adalah `docs/PRD v1.1 — Genresi Sistem Manajemen Stok, Kas & Piutang Harian.md`.
- Referensi Figma hanya dipakai untuk fitur dan user flow, bukan angka atau pixel-perfect UI.
- Source Odoo direferensikan dari instalasi yang sudah ada. Jangan menyalin source Odoo atau kode proyek lama.
- Database di luar pola `genresi_*`, terutama `project_akhir_magang_*`, tidak boleh disentuh, di-upgrade, di-drop, atau diubah.
- Jangan memakai port 8071 atau 8072. Port pengembangan Genresi adalah 8073.
- Jangan menebak kredensial. Rahasia hanya berada di `.env`, yang di-ignore git.

## Stack dan batas UI

- Stack utama: Python dan XML untuk model, view, menu, security, data, cron, dan report QWeb PDF.
- Dilarang memakai JS/OWL, halaman QWeb/website custom, CSS besar, navbar sendiri, atau layout sendiri.
- SCSS hanya boleh kecil untuk branding dan harus meng-override token Odoo yang sudah ada.
- Jika kebutuhan tidak bisa dipenuhi secara native Odoo Community, jelaskan alasannya dan tunggu persetujuan sebelum membuat kustomisasi.

## Struktur addon

Gunakan struktur Odoo standar:

- `models/`: satu file per model.
- `views/`: view, action, dan menu.
- `security/`: access CSV dan record rule.
- `data/`: seed master yang tidak bergantung pada demo.
- `demo/`: data contoh dengan tanggal tetap Agustus 2026.
- `wizard/`: transient model dan view wizard.
- `report/`: template dan action report QWeb.
- `tests/`: test `TransactionCase`.

Fase awal hanya membuat skeleton installable; jangan menambahkan model bisnis placeholder.

## Konvensi kode

- Ikuti konvensi Odoo 17, gunakan ruff dan pylint-odoo.
- Identifier Python/XML berbahasa Inggris; label pengguna (`string=`) berbahasa Indonesia.
- Logika bisnis hanya berada di method model.
- Method publik singkat dan memiliki satu tugas; beri docstring singkat pada method publik.
- Definisikan setiap Selection satu kali.
- Gunakan `@api.depends`; pakai `store=True` jika computed field dipakai laporan atau pencarian.
- Validasi aturan data memakai `@api.constrains`.
- Dilarang raw SQL; gunakan ORM dan `_read_group`.
- Dilarang ID hardcoded, duplikasi, kode yang dikomentari, dan dead code.

## Data, uang, tanggal, dan cron

- Seed master ada di `data/`; data contoh ada di `demo/` dengan tanggal tetap Agustus 2026.
- Sediakan satu helper “hari ini” yang membaca `ir.config_parameter` bernama `genresi.demo_today`. Helper ini dipakai cron, jatuh tempo, dan dashboard.
- Semua nilai uang menggunakan `fields.Monetary` dan mata uang IDR.
- Satuan bahan yang didukung: gram, pcs, dan biji.
- Cron wajib idempotent.
- Setiap fitur wajib memiliki `TransactionCase` yang memeriksa angka acuan PRD.

## Dependensi dan alur kerja

- Arah dependensi addon: `genresi_base <- genresi_stock <- genresi_cash <- genresi_report`.
- Dependensi core hanya `base`, `mail`, dan `uom`; `board` hanya boleh menjadi dependensi `genresi_report`.
- Buat commit kecil dengan conventional commits.
- Setiap fase berhenti dan laporkan hasilnya. Jangan push tanpa izin pengguna.
