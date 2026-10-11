# Pemetaan PRD v1.1 ke Odoo 17 Community

Dokumen ini memetakan seluruh kebutuhan fungsional PRD v1.1 ke komponen Odoo yang
tersedia pada edisi Community. Fase 0B menyiapkan fondasi; model bisnis ditambahkan
bertahap sesuai fase PRD.

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
| FR-14 | Klasifikasi transaksi menurut jenis, lini, sumber input, partner, dan metode pembayaran | Selection/Many2one pada `genresi.transaction`, search view dan filter native | Sedikit kustom | Tidak |
| FR-20 | Status pembayaran otomatis | Field computed dan constraint pada model kustom | Sedikit kustom | Tidak |
| FR-21 | Pembayaran dan cicilan per transaksi | Model kustom `genresi.payment`, one2many, business methods | Sedikit kustom | Tidak |
| FR-22 | Daftar Piutang dan Hutang dengan residual/umur | Action dan search view kustom berbasis transaksi/pembayaran | Sedikit kustom | Tidak |
| FR-23 | Jatuh tempo dan penanda terlambat | `due_date`, computed state, filter dan activity | Sedikit kustom | Tidak |
| FR-25 | Default tempo, partner wajib untuk transaksi belum dibayar, dan pengingat keterlambatan | `res.config.settings`, constraint transaksi, `mail.activity`/cron | Sedikit kustom | Tidak |
| FR-30 | CRUD Bahan Baku dan stok minimum | Model kustom `genresi.material`, UoM native, access rules | Sedikit kustom | Tidak |
| FR-31 | Pengeluaran bahan menambah stok | Model kustom `genresi.stock.move` dari transaksi terkonfirmasi | Sedikit kustom | Tidak |
| FR-32 | Resep berbasis batch: `genresi.recipe` berisi baris bahan dan hasil batch dalam pcs; produk tersusun dari adonan, filling opsional, dan kemasan; HPP per pcs sudah termasuk overhead | Model kustom `genresi.recipe`, `genresi.recipe.line`, dan `genresi.product` dengan computed cost | Sedikit kustom | Tidak |
| FR-33 | Produksi Harian memotong stok | Model kustom `genresi.production` dan ORM transaction | Sedikit kustom | Tidak |
| FR-34 | Penyesuaian stok manual dengan alasan | Model kustom stock move bertipe `adjust` dan wizard | Sedikit kustom | Tidak |
| FR-35 | Stok kritis dan reminder restock | Computed state, scheduled action, activity | Sedikit kustom | Tidak |
| FR-36 | Produksi menghitung kebutuhan bahan dari takaran batch dan menampilkan peringatan bila stok kurang tanpa memblokir konfirmasi | `genresi.production`, ORM stock moves, warning/chatter native | Sedikit kustom | Tidak |
| FR-37 | HPP, margin, dan penanda harga bahan/resep belum lengkap | Computed Monetary fields pada resep dan produk; margin kosong bila biaya belum lengkap | Sedikit kustom | Tidak |
| FR-40 | Tutup Kas varian x penjual | Model kustom `genresi.closing` dan `genresi.closing.line` | Sedikit kustom | Tidak |
| FR-41 | Cash, QRIS, kembalian, omset, selisih | Computed fields dan constraint pada Tutup Kas | Sedikit kustom | Tidak |
| FR-42 | Draft/Dikunci dan buka kembali oleh Owner | Selection state, access rights, record rule, method Owner | Sedikit kustom | Tidak |
| FR-43 | Rekap barang dibawa dan tidak laku per varian dan penjual | `genresi.closing.line` dengan Many2one produk/penjual dan qty | Sedikit kustom | Tidak |
| FR-44 | Rekonsiliasi omset seharusnya dengan omset aktual, termasuk piutang hari itu | Computed fields pada `genresi.closing` dan relasi transaksi | Sedikit kustom | Tidak |
| FR-45 | Tutup kas unik per hari dan dapat ditelusuri lewat chatter | SQL constraint unik tanggal, `mail.thread`, tracking | Sedikit kustom | Tidak |
| FR-46 | Selisih tutup kas diberi indikator visual dan dapat difilter | Computed signed difference, decoration/search filter native | Sedikit kustom | Tidak |
| FR-50 | Wizard laporan periode/lini dan PDF | `TransientModel`, `ir.actions.report`, QWeb PDF | Sedikit kustom | Tidak |
| FR-51 | Laporan Arus Kas berbasis pembayaran | Query ORM/read group dan QWeb report kustom | Sedikit kustom | Tidak |
| FR-52 | Laporan Laba Rugi sederhana | Aggregation transaksi dan QWeb report kustom | Sedikit kustom | Tidak |
| FR-53 | Laporan memakai rentang tanggal dan filter lini bisnis, bukan hanya bulan berjalan | Transient wizard, domain ORM, filter QWeb report | Sedikit kustom | Tidak |
| FR-54 | Dashboard menampilkan ringkasan angka yang dapat ditelusuri ke data sumber | Action board dengan panel graph/pivot dan form Ringkasan computed | Sedikit kustom | Tidak |
| FR-60 | Dashboard KPI, grafik penjualan per lini, kas masuk vs keluar, stok kritis, piutang jatuh tempo | Modul `board` (panel aksi graph/pivot) + form Ringkasan berisi computed field; tanpa JS/OWL; tanpa dashboard kustom | Sedikit kustom | Tidak |
| FR-70 | Cron membuat Activity bila transaksi/stok belum lengkap | `ir.cron`, `mail.activity`, helper tanggal demo | Sedikit kustom | Tidak |
| FR-72 | Reminder diteruskan ke Telegram | Endpoint/integrasi n8n atau gateway Telegram eksternal | Tidak bisa native | Tidak; integrasi eksternal |
| FR-80 | Endpoint inbound dengan API key | Controller HTTP kustom, API key, validasi ORM | Sedikit kustom | Tidak |

## Keputusan Enterprise dan batas Community

Accounting penuh/double-entry dan laporan formal **Balance Sheet** merupakan fitur
Enterprise atau berada di luar keputusan scope PRD. `spreadsheet_dashboard` tersedia di
Community dan ikut terpasang sebagai dependensi `board`, bersama `spreadsheet`; Genresi
tidak memakai fitur editing spreadsheet maupun Documents yang merupakan fitur Enterprise.
Genresi tidak memasang modul Accounting. Kas, pembayaran, Arus Kas, Laba Rugi sederhana,
dan form Ringkasan dashboard dimodelkan sendiri dengan model kustom tipis. Neraca formal
tetap di luar cakupan.

`board` tetap dipakai sebagai dependensi teknis `genresi_report`. Karena `board` memakai
`spreadsheet_dashboard`, maka `spreadsheet` dan `spreadsheet_dashboard` ikut terpasang
sebagai dependensi teknis; keduanya bukan indikasi bahwa fitur Enterprise dipakai.
