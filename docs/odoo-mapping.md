# Pemetaan PRD v1.1 ke Odoo 17 Community

Dokumen ini memetakan seluruh kebutuhan fungsional PRD v1.1 ke komponen Odoo yang
tersedia pada edisi Community. Fase 0B hanya menyiapkan fondasi; model bisnis dan
aksi menu akan ditambahkan pada fase berikutnya.

Fondasi UI menggunakan `muk_web_theme` dan dependensi LGPL-3 vendored resmi MuK:
`muk_web_appsbar`, `muk_web_chatter`, `muk_web_colors`, dan `muk_web_dialog`.
Modul terpasang yang diizinkan tetap terbatas pada `base`, `mail`, `uom`, `board`,
`muk_*`, `genresi_*`, serta dependensi teknis langsungnya. Tidak ada modul bisnis
MuK lain yang dipasang.

| ID | Fitur PRD v1.1 | Komponen Odoo / alternatif | Kategori | Butuh Enterprise? |
| --- | --- | --- | --- | --- |
| FR-01 | Login Odoo dan tiga role Owner, Staf, Viewer | `res.users`, `res.groups`, `ir.ui.menu`; implied groups kustom; `muk_web_theme` + `muk_web_appsbar` untuk sidebar | Sedikit kustom | Tidak |
| FR-02 | CRUD Lini Bisnis dan Penjual | Model kustom, form/list view, access CSV, record rule | Sedikit kustom | Tidak |
| FR-10 | CRUD Transaksi dengan total `qty x harga` | Model kustom `genresi.transaction`, computed stored field, form/list view | Sedikit kustom | Tidak |
| FR-11 | Impor riwayat dari CSV Google Sheets | Import CSV native Odoo dan mapping field | Native | Tidak |
| FR-12 | Filter, group, dan ekspor transaksi | Search view, filter/group-by/pivot/graph, export list native | Native | Tidak |
| FR-13 | Chatter pada Transaksi dan Tutup Kas | `mail.thread`, `mail.activity.mixin`, tracking fields | Native | Tidak |
| FR-20 | Status pembayaran otomatis | Field computed dan constraint pada model kustom | Sedikit kustom | Tidak |
| FR-21 | Pembayaran dan cicilan per transaksi | Model kustom `genresi.payment`, one2many, business methods | Sedikit kustom | Tidak |
| FR-22 | Daftar Piutang dan Hutang dengan residual/umur | Action dan search view kustom berbasis transaksi/pembayaran | Sedikit kustom | Tidak |
| FR-23 | Jatuh tempo dan penanda terlambat | `due_date`, computed state, filter dan activity | Sedikit kustom | Tidak |
| FR-30 | CRUD Bahan Baku dan stok minimum | Model kustom `genresi.material`, UoM native, access rules | Sedikit kustom | Tidak |
| FR-31 | Pengeluaran bahan menambah stok | Model kustom `genresi.stock.move` dari transaksi terkonfirmasi | Sedikit kustom | Tidak |
| FR-32 | Resep produk dan takaran bahan | Model kustom `genresi.product` dan `genresi.recipe.line` | Sedikit kustom | Tidak |
| FR-33 | Produksi Harian memotong stok | Model kustom `genresi.production` dan ORM transaction | Sedikit kustom | Tidak |
| FR-34 | Penyesuaian stok manual dengan alasan | Model kustom stock move bertipe `adjust` dan wizard | Sedikit kustom | Tidak |
| FR-35 | Stok kritis dan reminder restock | Computed state, scheduled action, activity | Sedikit kustom | Tidak |
| FR-40 | Tutup Kas varian x penjual | Model kustom `genresi.closing` dan `genresi.closing.line` | Sedikit kustom | Tidak |
| FR-41 | Cash, QRIS, kembalian, omset, selisih | Computed fields dan constraint pada Tutup Kas | Sedikit kustom | Tidak |
| FR-42 | Draft/Dikunci dan buka kembali oleh Owner | Selection state, access rights, record rule, method Owner | Sedikit kustom | Tidak |
| FR-50 | Wizard laporan periode/lini dan PDF | `TransientModel`, `ir.actions.report`, QWeb PDF | Sedikit kustom | Tidak |
| FR-51 | Laporan Arus Kas berbasis pembayaran | Query ORM/read group dan QWeb report kustom | Sedikit kustom | Tidak |
| FR-52 | Laporan Laba Rugi sederhana | Aggregation transaksi dan QWeb report kustom | Sedikit kustom | Tidak |
| FR-60 | Dashboard KPI, grafik, stok, piutang | Kanban/graph native untuk dasar; dashboard kustom sebagai alternatif | Tidak bisa native penuh + alternatif | Tidak; Spreadsheet Dashboard Enterprise tidak dipakai |
| FR-70 | Cron membuat Activity bila transaksi/stok belum lengkap | `ir.cron`, `mail.activity`, helper tanggal demo | Sedikit kustom | Tidak |
| FR-72 | Reminder diteruskan ke Telegram | Endpoint/integrasi n8n atau gateway Telegram eksternal | Tidak bisa native | Tidak; integrasi eksternal |
| FR-80 | Endpoint inbound dengan API key | Controller HTTP kustom, API key, validasi ORM | Sedikit kustom | Tidak |

## Keputusan Enterprise dan batas Community

Accounting penuh/double-entry, **Spreadsheet Dashboard**, dan laporan formal **Balance
Sheet** merupakan fitur Enterprise atau berada di luar keputusan scope PRD. Genresi tidak
memasang `accounting`/Accounting dan tidak memakai Spreadsheet Dashboard Enterprise.
Kas, pembayaran, Arus Kas, dan Laba Rugi sederhana dimodelkan sendiri dengan model
kustom tipis. Neraca formal tetap di luar cakupan.

`board` tetap dipakai sebagai dependensi teknis `genresi_report`. Karena `board` memakai
`spreadsheet_dashboard`, maka `spreadsheet` dan `spreadsheet_dashboard` ikut terpasang
sebagai dependensi teknis; keduanya bukan indikasi bahwa fitur Enterprise dipakai.
