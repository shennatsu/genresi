# PRD v1.1 — Genresi

**Sistem Manajemen Stok, Kas & Piutang Harian — Studi Kasus CV Generasi Restu Ibu**

Program Magang SOLID · Project Manager: Asha · Versi 1.1 · 10 Oktober 2026 · Status: Developing

## 0. Ringkasan Perubahan dari v1.0

Versi ini merombak v1.0 berdasarkan (a) skripsi sistem Bookbot sebagai baseline resmi, (b) fakta operasional dari rekap WhatsApp dan laporan PDF, serta (c) batasan nyata Odoo 17 Community.

| # | Temuan di v1.0 | Perubahan di v1.1 |
| --- | --- | --- |
| 1 | Rutinitas harian yang sebenarnya (rekap per varian per penjual, barang gak laku, rekonsiliasi cash/QRIS dengan selisih) tidak tercakup. | Ditambah modul **Tutup Kas Harian** sebagai fitur utama. |
| 2 | Neraca dan arus kas diasumsikan keluar otomatis dari Accounting bawaan. Di Community 17 laporan tersebut bukan fitur bawaan (setahu penulis ada di Enterprise), dan double-entry berlebihan untuk UKM ini. | Accounting/Inventory bawaan **tidak dipakai**. Dibuat laporan **Arus Kas** dan **Laba Rugi sederhana** sebagai custom report. Neraca formal dikeluarkan dari cakupan. |
| 3 | Pengurangan stok bahan baku otomatis dari "setiap transaksi" tidak punya penghubung antara roti yang dijual dan bahan yang dipakai. | Ditambah **Resep** dan **Produksi Harian**. Stok bahan masuk dari transaksi pengeluaran, keluar dari produksi. |
| 4 | Integrasi Bookbot bertentangan antara Bagian 5–6 dan Bagian 9. | Odoo menjadi **sumber data utama**. Input manual di Odoo dan impor data lama adalah Must. Endpoint untuk n8n adalah Could. |
| 5 | Reminder dikirim ke mentor/peserta magang. | Reminder dikirim ke **pemilik usaha** (dan staf), lewat Aktivitas Odoo. |
| 6 | Dashboard, role, dan audit trail belum ada, padahal syarat program. | Ditambah 3 role, dashboard, dan chatter (log perubahan). |
| 7 | Piutang diasumsikan khusus lini SPPG. | Piutang berlaku untuk **semua** transaksi yang belum dibayar atau QRIS-nya belum masuk. |

## 1. Latar Belakang & Tujuan

CV Generasi Restu Ibu adalah UMKM bakery dengan dua lini bisnis, Reguler dan SPPG (Sistem Penyediaan Pangan Gotong Royong). Penelitian skripsi sebelumnya membangun **Bookbot**: Telegram Bot + n8n (40 node) + FastAPI + Google Gemini (OCR/NLP) + Google Sheets, di-deploy di VPS Hostinger. UAT skala Guttman terhadap pemilik usaha menghasilkan penerimaan 100%.

Bookbot sudah baik sebagai alat *pencatatan*, tetapi skripsinya sendiri mencatat batas ruang lingkup: tidak ada manajemen stok bahan baku, piutang/hutang, laporan keuangan formal, analitik, dan integrasi pembayaran/POS. Selain itu ada saran lanjutan: lini bisnis dinamis, basis data terstruktur, dan reminder otomatis.

**Tujuan studi kasus magang:** membangun **Genresi**, aplikasi di atas Odoo 17 Community dengan custom module, yang melengkapi Bookbot pada area di atas. Sekaligus melatih auth, CRUD multi-modul, role, dashboard, dan laporan sesuai arahan Program Magang SOLID.

**Tujuan terukur:**

- Seluruh transaksi historis dari Google Sheets berhasil diimpor, dan total laporan bulan yang sama **identik** dengan laporan PDF Bookbot.
- Rekonsiliasi Tutup Kas menghasilkan angka selisih yang sama dengan hitungan manual pada contoh rekap 23/08/2026.
- Laporan PDF dapat digenerate untuk **bulan atau rentang tanggal mana pun**.
- Pemilik menerima reminder jika belum ada transaksi tercatat hari itu.

## 2. Baseline Sistem Eksisting (dari Skripsi)

| Aspek | Kondisi Bookbot |
| --- | --- |
| Pengguna | Satu jenis pengguna: pemilik, dibatasi whitelist Chat ID Telegram |
| Input | Teks tunggal, teks bulk, foto struk (Gemini OCR/NLP) |
| Klasifikasi | Jenis (Pemasukan/Pengeluaran) dan lini bisnis (Reguler/SPPG), lini bisnis statis di dalam prompt |
| Penyimpanan | Google Sheets: *Data Transaksi*, *Rekap Bulanan*, *Rekap Lini Bisnis* (formula SUMIFS) |
| Kolom Data Transaksi | No, Tanggal, Waktu, Jenis, Nama Item, Qty, Satuan, Harga Satuan, Total, Lini Bisnis, Sumber Input (Struk / Manual / Manual Bulk), Bulan–Tahun |
| Rekap | `/rekap_hari_ini`, `/rekap_bulan_ini`, masing-masing teks atau PDF. Hanya hari dan bulan berjalan |
| Operasional | Berjalan 24 jam di VPS, rotasi 10 API key Gemini untuk kuota gratis |

Struktur kolom ini menjadi **acuan model data transaksi di Odoo** agar impor dan kompatibilitas terjaga.

## 3. Gap dan Keputusan Scope

| Gap (dari skripsi dan temuan tambahan) | Keputusan | Prioritas |
| --- | --- | --- |
| Rekap hanya hari/bulan berjalan | Laporan historis, periode custom | Must |
| Tidak ada piutang/hutang | Status pembayaran, cicilan, daftar per partner | Must |
| Tidak ada stok bahan baku | Bahan baku, resep, produksi harian | Must |
| Rekonsiliasi kas harian di WhatsApp | Modul Tutup Kas Harian | Must |
| Lini bisnis statis | Master data Lini Bisnis | Must |
| Google Sheets | PostgreSQL native Odoo | Must (otomatis) |
| Tidak ada reminder | Cron dan Aktivitas Odoo | Should |
| Tidak ada dashboard | Dashboard OWL | Should |
| Laporan keuangan formal | Arus Kas dan Laba Rugi sederhana. Neraca formal dikeluarkan | Should |
| Integrasi input Bookbot ke Odoo | Endpoint API untuk n8n | Could |
| POS, pembayaran digital, analitik/prediksi | Di luar cakupan | Won't |

## 4. Prinsip Desain di Ekosistem Odoo

Odoo dipilih karena arahan program, bukan karena kompleksitas masalahnya. Karena itu desainnya sengaja **tipis dan custom**:

1. **Pakai yang gratis dan relevan:** `base` (user, group, partner), `mail` (chatter dan activity), `uom` (satuan), `web` (view, export, import). Fitur bawaan seperti **import CSV**, **export list ke Excel**, **filter/group by/pivot/graph**, dan **chatter** langsung didapat tanpa kode.
2. **Jangan pakai yang berat:** modul Inventory dan Accounting tidak diinstal. Stok dan kas dimodelkan sendiri agar ringan dan sekaligus melatih ORM dan business logic.
3. **Satu sumber data:** Odoo/PostgreSQL menggantikan Google Sheets. Formula SUMIFS di Sheets digantikan field computed (stored) dan `read_group`.
4. **Pola standar Odoo:** model dengan `_inherit = ['mail.thread', 'mail.activity.mixin']`, `ir.model.access.csv`, `ir.rule`, `ir.sequence`, `ir.cron`, wizard (`TransientModel`), laporan QWeb PDF, dan data demo lewat XML.
5. **Tema:** warna brand Genresi dipasang lewat override variabel SCSS pada bundle `web._assets_primary_variables`, sehingga komponen standar Odoo ikut berubah warna tanpa menimpa CSS satu per satu.

## 5. Arsitektur Modul

| Addon | Tanggung jawab | Depends |
| --- | --- | --- |
| `genresi_base` | Lini Bisnis, Penjual, grup role, menu root, tema | `base`, `mail`, `uom` |
| `genresi_cash` | Transaksi, Pembayaran, Piutang/Hutang, Tutup Kas | `genresi_base` |
| `genresi_stock` | Bahan Baku, Pergerakan Stok, Resep, Produksi Harian | `genresi_base`, `genresi_cash` |
| `genresi_report` | Wizard laporan, QWeb PDF, Arus Kas, Laba Rugi, Dashboard OWL, cron reminder | semua di atas |
| `genresi_api` (opsional) | Endpoint inbound untuk n8n/Bookbot | `genresi_cash` |

## 6. Kebutuhan Fungsional

Prioritas: **M** = Must, **S** = Should, **C** = Could.

| ID | Kebutuhan | P |
| --- | --- | --- |
| FR-01 | Login dengan Odoo Auth dan tiga role: Owner, Staf, Viewer | M |
| FR-02 | CRUD master Lini Bisnis (ditambah tanpa ubah kode; SPPG diarsipkan karena sudah tidak aktif, data historis tetap ada) dan Penjual | M |
| FR-10 | CRUD Transaksi (Pemasukan/Pengeluaran) dengan total otomatis = qty × harga satuan | M |
| FR-11 | Impor riwayat transaksi dari CSV hasil ekspor Google Sheets | M |
| FR-12 | Filter dan pengelompokan transaksi per bulan, lini, jenis, sumber input; ekspor ke Excel | M |
| FR-13 | Chatter pada Transaksi dan Tutup Kas untuk jejak perubahan | M |
| FR-20 | Status pembayaran otomatis: Belum Lunas, Sebagian, Lunas | M |
| FR-21 | Pencatatan pembayaran/cicilan per transaksi | M |
| FR-22 | Daftar Piutang (pemasukan) dan Hutang (pengeluaran) per partner, lengkap dengan sisa tagihan dan umur hari | M |
| FR-23 | Tanggal jatuh tempo (default 3 hari, bisa diubah) dan penanda terlambat | S |
| FR-30 | CRUD Bahan Baku dengan satuan dan stok minimum | M |
| FR-31 | Transaksi pengeluaran yang dikaitkan ke bahan baku otomatis menambah stok saat dikonfirmasi | M |
| FR-32 | Resep berbasis batch: adonan, filling, dan kemasan, masing-masing dengan hasil (yield) dan daftar bahan; produk = adonan + filling + kemasan | M |
| FR-33 | Produksi Harian: konfirmasi memotong stok bahan sesuai resep × jumlah produksi | M |
| FR-34 | Penyesuaian stok manual dengan alasan | S |
| FR-35 | Penanda stok kritis dan reminder restock | S |
| FR-40 | Tutup Kas: tabel varian × penjual (dibawa, gak laku) | M |
| FR-41 | Tutup Kas: input Cash, QRIS, Kembalian, perhitungan otomatis omset dan selisih | M |
| FR-42 | Tutup Kas: status Draft dan Dikunci (setelah dikunci tidak bisa diubah, kecuali Owner membuka kembali) | M |
| FR-50 | Wizard laporan: pilih bulan/tahun atau rentang tanggal dan lini, hasil PDF QWeb | M |
| FR-51 | Laporan Arus Kas (berbasis pembayaran yang benar-benar diterima/dikeluarkan) | S |
| FR-52 | Laporan Laba Rugi sederhana (berbasis transaksi) | S |
| FR-60 | Dashboard: KPI, grafik penjualan per lini, kas masuk vs keluar, stok kritis, piutang jatuh tempo | S |
| FR-70 | Cron harian: jika belum ada transaksi hari ini, buat Aktivitas untuk Owner/Staf | S |
| FR-72 | Reminder diteruskan ke Telegram | C |
| FR-80 | Endpoint API untuk menerima transaksi dari n8n dengan API key | C |

**Tambahan kebutuhan fungsional (pembaruan 10 Okt 2026)**

- FR-36 (M): impor 19 bahan baku dan resep (adonan, filling, kemasan) dari file HPP Roti
- FR-37 (S): HPP otomatis per produk dari resep, harga bahan, dan overhead
- FR-43 (M): Tutup Kas mencatat nasib tiap unit gak laku: dibagikan, dijual ulang, atau dibuang
- FR-44 (M): unit yang dijual ulang muncul otomatis sebagai sisa kemarin di Tutup Kas berikutnya, maksimal satu kali
- FR-53 (C): laporan margin per produk (harga jual dikurangi HPP)
- FR-54 (S): biaya barang gak laku tampil terpisah di Laba Rugi

* FR-45 (S): master Penjual punya skema bayar (gaji tetap atau komisi hasil jualan); Tutup Kas menghitung nilai terjual dan komisi per penjual

## 7. Model Data (Ringkas)

**`genresi.business.line`**: name, active.

**`genresi.transaction`** (mail.thread): date, create\_date (waktu), type (in/out), name (item), qty, uom\_id, unit\_price, total (computed, stored), business\_line\_id, source (struk/manual/bulk/odoo), partner\_id, payment\_method (cash/qris/unpaid), due\_date, paid\_amount (computed dari pembayaran), residual (computed), payment\_state (computed), bahan\_id (opsional), period (computed, stored, pengganti kolom Bulan–Tahun).

**`genresi.payment`**: transaction\_id, date, amount, method (cash/qris).

**`genresi.material`**: name, uom\_id, min\_qty, qty\_on\_hand (computed dari pergerakan), state kritis (computed).

**`genresi.stock.move`**: material\_id, date, type (in/out/adjust), qty, ref (transaksi/produksi/penyesuaian), note.

**`genresi.product`**: name, price, adonan\_recipe\_id, filling\_recipe\_id (opsional), aktif/arsip, business\_line\_id default. **`genresi.recipe.line`**: recipe\_id, material\_id, qty (takaran per batch).

**`genresi.production`**: date, product\_id, qty, state (draft/done), baris bahan terpakai (computed saat konfirmasi).

**`genresi.seller`**: name.

**`genresi.closing`** (mail.thread): date (unik per hari), state, cash, qris, change (kembalian), dan semua field computed pada Bagian 8. **`genresi.closing.line`**: closing\_id, product\_id, seller\_id, qty\_fresh, qty\_carryover, qty\_unsold, qty\_shared, qty\_discard, qty\_resale, price (snapshot harga).

**Tambahan model (pembaruan 10 Okt 2026).** `genresi.recipe`: name, type (adonan/filling/kemasan), yield\_qty (hasil batch dalam pcs), baris bahan. `genresi.config`: overhead produksi per pcs, opex jualan per pcs, default jatuh tempo (hari). Pada `genresi.material` ditambah cost\_per\_uom (harga per gram atau pcs, mengikuti file HPP) dan pack\_size (isi kemasan). Pada genresi.seller ditambah pay\_type (gaji tetap atau komisi hasil jualan) dan commission\_pct.

## 8. Aturan Bisnis dan Rumus

**Transaksi**

- `total = qty × unit_price`.
- Jika metode Cash/QRIS, sistem membuat pembayaran penuh otomatis. Jika Belum Dibayar, `residual = total` dan **partner wajib diisi**.
- `payment_state`: Lunas jika `residual = 0`, Sebagian jika `0 < paid < total`, selain itu Belum Lunas.
- Piutang = pemasukan dengan residual > 0. Hutang = pengeluaran dengan residual > 0.

**Stok**

- Konfirmasi transaksi pengeluaran yang punya `bahan_id` membuat pergerakan stok *in*.
- Konfirmasi produksi membuat pergerakan stok *out* sebesar `(takaran resep ÷ hasil batch) × jumlah produksi` untuk setiap bahan resep. Jika stok tidak cukup, tampilkan peringatan (tidak memblokir, karena stok awal mungkin belum diinput).
- Penjualan roti **tidak** mengubah stok. Stok produk jadi tidak dilacak, karena roti dibuat dan dijual pada hari yang sama. Barang yang tidak laku dicatat di Tutup Kas.

**Tutup Kas** (diverifikasi terhadap rekap 23/08/2026)

- Nilai Goods = Σ((qty\_fresh + qty\_carryover) × price) → Rp1.085.000
- Nilai Gak Laku = Σ(qty\_unsold × price) → Rp70.000
- Omset Seharusnya = Goods − Gak Laku → Rp1.015.000
- Cash Bersih = Cash − Kembalian → Rp240.000 (500.000 − 260.000)
- Omset Aktual = Cash Bersih + QRIS + piutang hari itu → Rp1.135.000 (240.000 + 895.000 + 0)
- **Selisih = Omset Aktual − Omset Seharusnya** → +Rp120.000, ditandai merah jika tidak nol.
- Piutang hari itu = residual transaksi pemasukan bertanggal sama. Dengan begitu penjualan tempo tidak lagi tampak sebagai "selisih misterius".

**Laporan**

- *Arus Kas*: Σ pembayaran masuk − Σ pembayaran keluar pada periode.
- *Laba Rugi sederhana*: Σ pemasukan − Σ pengeluaran pada periode, per lini bisnis.
- Kedua laporan memakai periode custom, tidak terbatas bulan berjalan.

**Barang gak laku** (aturan dari pemilik)

- Setiap unit gak laku punya satu dari tiga nasib: dibagikan (paling sering), dijual ulang besok, atau dibuang (jarang). Jumlah ketiganya harus sama dengan qty\_unsold.
- Dijual ulang maksimal satu kali. Unit yang dijual ulang muncul otomatis sebagai qty\_carryover di Tutup Kas hari berikutnya. Jika masih gak laku, sisa kemarin wajib dibagikan atau dibuang: qty\_resale ≤ qty\_unsold − min(qty\_unsold, qty\_carryover).
- Biaya barang gak laku = (qty\_shared + qty\_discard) × HPP produk, tampil terpisah di Laba Rugi (dibagikan = biaya, dibuang = rugi). Barang dijual ulang tidak dihitung rugi.

**Jatuh tempo**

- Berlaku untuk semua lini, karena SPPG sudah tidak aktif. Default = tanggal transaksi + 3 hari (parameter Konfigurasi, kisaran normal 1–3 hari), bisa diubah per transaksi. Transaksi belum lunas yang lewat jatuh tempo diberi badge Terlambat.

**HPP**

- HPP produk = biaya adonan per pcs + biaya filling per pcs + kemasan + overhead produksi per pcs (Bagian 17). Opex jualan tidak masuk HPP dan hanya tampil di kolom HPP Gabungan.

**Komisi penjual**

- Nilai terjual per penjual = Σ((qty\_fresh + qty\_carryover − qty\_unsold) × price) pada baris penjual itu. Untuk penjual berskema komisi (mis. Teh Reni), komisi harian = nilai terjual × commission\_pct. Penjual bergaji tetap tidak dihitung harian.
- Komisi masuk biaya jualan di luar HPP. Opex jualan di file HPP (Rp1.155,90 per pcs) belum memuat komisi ini, sehingga angkanya perlu diperbarui setelah persentase ditetapkan.

## 9. Role dan Hak Akses

| Fitur | Owner | Staf | Viewer |
| --- | --- | --- | --- |
| Transaksi, Pembayaran | CRUD | CRUD | Lihat |
| Produksi, Bahan, Resep | CRUD | Produksi: CRUD; lainnya lihat | Lihat |
| Tutup Kas | CRUD, buka kunci | Buat dan kunci | Lihat |
| Laporan dan Dashboard | Penuh | Dashboard saja | Dashboard |
| Konfigurasi dan Pengguna | Penuh | Tidak ada | Tidak ada |

Diimplementasikan lewat `res.groups` yang saling mewarisi, `ir.model.access.csv`, `ir.rule`, dan visibilitas menu per grup.

## 10. Alur Proses To-Be

**Harian**

1. Staf/Owner mencatat transaksi di Odoo (atau, jika integrasi aktif, masuk dari Bookbot).
2. Transaksi pengeluaran bahan baku menambah stok. Produksi harian memotong stok sesuai resep.
3. Pembayaran yang belum lunas muncul otomatis di Piutang/Hutang. Cicilan dicatat kemudian.
4. Akhir hari: staf mengisi **Tutup Kas** (dibawa dan gak laku per varian per penjual, Cash, QRIS, Kembalian), lalu sistem menghitung selisih. Setelah sesuai, status dikunci.
5. Cron malam memeriksa kelengkapan: jika belum ada transaksi hari ini atau stok di bawah minimum, Aktivitas dibuat untuk Owner/Staf.

**Pelaporan** 6. Owner membuka Laporan, memilih bulan atau rentang tanggal dan lini, lalu mencetak PDF atau melihat Arus Kas dan Laba Rugi.

## 11. Integrasi dengan Bookbot

- **Tahap 1 (Must):** impor satu kali dari Google Sheets lewat CSV. Bookbot tetap berjalan seperti biasa selama transisi.
- **Tahap 2 (Could):** di workflow n8n, node Google Sheets "simpan transaksi" diganti HTTP Request ke endpoint Odoo (`genresi_api`, autentikasi API key) atau memakai API eksternal bawaan Odoo (JSON-RPC). Parsing Gemini tidak berubah, hanya tujuan penyimpanan yang berpindah.
- **Tahap 3 (Could):** whitelist Chat ID dipetakan ke pengguna Odoo, dan reminder diteruskan ke Telegram.

## 12. Kebutuhan Non-Fungsional dan Deployment

| Aspek | Ketentuan |
| --- | --- |
| Platform | Odoo 17 Community, Python, OWL/QWeb, PostgreSQL |
| Deployment | Docker Compose (Odoo + PostgreSQL) di VPS, HTTPS via reverse proxy |
| Keamanan | Odoo Auth, grup dan record rule, API key untuk endpoint, backup database terjadwal |
| Antarmuka | Desktop-first, bahasa Indonesia, tema oren Genresi |
| Data awal | Data demo (XML): lini, varian, bahan, resep, contoh transaksi dan Tutup Kas |
| Dokumentasi | README, panduan pengguna, ERD, dokumentasi model dan endpoint |

## 13. Pengujian dan Kriteria Penerimaan

- **Unit test** (`TransactionCase`): total transaksi, status pembayaran, stok masuk/keluar, rumus Tutup Kas, penguncian.
- **Uji rekonsiliasi data:** hasil impor Agustus 2026 menghasilkan total pemasukan sama dengan laporan PDF Bookbot (Rp4.541.000).
- **Uji rumus:** skenario 23/08/2026 menghasilkan selisih Rp120.000.
- **Uji hak akses:** tiap role hanya melihat menu dan melakukan aksi sesuai tabel Bagian 9.
- **UAT:** meniru metode skripsi (skala Guttman) dengan pernyataan yang disesuaikan, dijalankan bersama pemilik usaha di Minggu 15.

## 14. Timeline (16 Minggu)

| Minggu | Fase | Fokus Genresi |
| --- | --- | --- |
| 1 | Onboarding | Setup environment, finalisasi study case |
| 2–4 | Perencanaan | PRD v1.1, ERD, mockup Figma, setup repo dan Docker, sharing knowledge |
| 5–8 | Sprint 1 | `genresi_base`, auth dan role, Transaksi, impor CSV, Pembayaran dan Piutang/Hutang |
| 9–12 | Sprint 2 | Stok, Resep, Produksi, Tutup Kas, Laporan PDF, Dashboard, reminder |
| 13–14 | Sprint 3 | Tema dan polishing UI, Arus Kas/Laba Rugi, endpoint API (jika sempat), dokumentasi |
| 15 | UAT | Stock opname bahan baku (hitung fisik) sebelum UAT, UAT dengan pemilik, deploy, user manual |
| 16 | Wrap-up | Presentasi dan handover |

## 15. Risiko dan Pertanyaan Terbuka

| Risiko | Mitigasi |
| --- | --- |
| Cakupan terlalu besar untuk 16 minggu | Prioritas Must/Should/Could jelas. Dashboard, Arus Kas, dan API boleh dipangkas |
| Odoo terasa berlebihan | Dependensi minimal, modul custom, tanpa Inventory/Accounting |
| Stok awal bahan belum dihitung | Stok awal diinput lewat penyesuaian. Takaran resep diambil dari file HPP Roti di Minggu 2–3 |
| Data historis di Sheets tidak seragam | Skrip pembersihan CSV sebelum impor, uji rekonsiliasi total |

**Keputusan pemilik usaha (10 Okt 2026, via Nanda)**

| # | Pertanyaan | Jawaban | Dampak ke desain |
| --- | --- | --- | --- |
| 1 | Takaran bahan | Ada di file HPP Roti | Resep diimpor dari file, berbasis batch (Bagian 17) |
| 2 | Barang gak laku | Dibagikan (paling sering), dijual ulang besok (maksimal sekali), dibuang (jarang) | Tiga nasib per unit di Tutup Kas, aturan di Bagian 8 |
| 3 | Tempo bayar | Umumnya 1–3 hari; SPPG sudah tidak ada | Default jatuh tempo 3 hari; lini SPPG diarsipkan |
| 4 | Daftar penjual | Mengacu ke file HPP | Master Penjual dinamis dengan skema bayar (gaji tetap atau komisi hasil jualan), awal dari file HPP dan rekap WA |

**Masih terbuka:**

- Stok awal bahan baku dihitung fisik (stock opname) sebelum UAT, lalu diinput lewat penyesuaian stok.
- Persentase atau skema komisi Teh Reni, yang dibayar dari hasil jualannya.

## 16. Di Luar Cakupan

Neraca formal dan akuntansi double-entry, analitik dan prediksi permintaan, integrasi POS dan payment gateway, pelacakan stok produk jadi, aplikasi mobile native, multi-cabang dan SaaS multi-tenant.

## 17. Data HPP Roti: Sumber Resep dan Biaya

File HPP\_ROTI\_REVISI menjadi sumber data awal resep, harga bahan, dan overhead, dan bentuknya menentukan model resep di Genresi.

- 19 bahan dengan harga per gram atau pcs. Harga memakai harga tertinggi yang pernah dibayar, kebijakan konservatif yang disengaja pemilik. Genresi menyimpannya di cost\_per\_uom dan tidak menimpanya otomatis dari transaksi.
- Resep berbasis batch: adonan Varian A (Bungasari) dan Varian B (Natural) masing-masing hasil 8 loyang, filling keju (15 roti), daging (30 loyang), coklat (16 loyang), serta kemasan per pcs (lunch box dan kresek). Produksi memotong stok proporsional terhadap hasil batch.
- 8 kombinasi produk (4 jenis × 2 adonan). Pada simulasi hanya adonan Natural yang dijual, sehingga varian Bungasari diarsipkan.
- Overhead produksi Rp1.913,57 per pcs (tenaga kerja dan gas, depresiasi alat, listrik) dihitung dari kapasitas rata-rata 64 pcs per hari (48 weekday, 96 weekend) dan disimpan sebagai parameter. Opex jualan Rp1.155,90 per pcs berada di luar HPP.
- Staf dalam file: baker Kak Mei dan Mama Farel; jaga toko Nanda dan Owner (baris Farel, gaji Rp0, diganti Teh Reni; besaran gajinya belum diketahui). Menjadi referensi awal master Penjual, ditambah Teh Reni dari rekap WA (membantu jualan dan dibayar dari hasil jualannya).

HPP per pcs sebagai data uji (dibulatkan ke rupiah). Angka ini sudah termasuk overhead produksi, jadi tidak boleh ditambah overhead lagi:

| Jenis roti | Harga jual | HPP adonan Natural | HPP adonan Bungasari |
| --- | --- | --- | --- |
| Original | Rp20.000 | Rp8.979 | Rp9.676 |
| Keju | Rp25.000 | Rp13.505 | Rp14.203 |
| Daging | Rp35.000 | Rp14.745 | Rp15.443 |
| Coklat | Rp25.000 | Rp10.541 | Rp11.239 |

**Keputusan atas selisih data:**

- Roti srikaya (Rp25.000) dibuat sebagai resep baru mengikuti pola file HPP: filling satu bahan (selai srikaya) dengan adonan Natural. Takaran awal 500 g untuk 16 loyang dan harga bahan berstatus placeholder (ditandai kuning, seperti di file HPP) sampai dikonfirmasi. HPP srikaya menampilkan peringatan selama harga belum diisi.
- Nama produk disatukan menjadi "Daging" (sesuai file HPP dan rekap WA). Nama "daging teriyaki" dari data transaksi lama dipetakan sebagai alias saat impor.

## 18. Keputusan Tambahan dari Pemilik (10 Okt 2026, putaran 2)

- **Kembalian** adalah uang receh modal yang disiapkan di awal hari, bukan kembalian ke pembeli. Field di Tutup Kas dinamai "Modal Kembalian". Rumus tetap: Cash Bersih = Cash − Modal Kembalian.
- **QRIS belum masuk rekening** dicatat di Tutup Kas sebagai butir rekonsiliasi ("QRIS belum cair"), bukan piutang. Transaksinya tetap Lunas dan nilai QRIS tetap masuk omset aktual. Butir ini hanya untuk mencocokkan saldo rekening.
- **Piutang berdasarkan kepercayaan:** hanya pelanggan lama/tetap yang boleh bayar belakangan, pelanggan baru bayar di muka. Partner diberi tanda "Pelanggan Tetap", dan metode Belum Dibayar hanya bisa dipilih untuk partner bertanda ini. Hutang ke supplier tetap didukung; apakah ada supplier yang benar-benar berhutang belum terjawab.
- **Stok produk jadi:** hanya roti yang dibawa jualan yang dicatat.
- **Kategori pengeluaran:** Bahan, Kemasan, Gas/Listrik, Gaji/Komisi, Sewa tempat, Lainnya. Arus Kas dan Laba Rugi mengelompokkan pengeluaran per kategori.
- **Stok minimum** ditentukan manual per bahan berdasarkan kebutuhan produksi, bukan aturan jumlah hari. Bahan dibeli lagi ketika habis, tanpa rumus otomatis.
- **Satuan resep:** 1 loyang = 1 pcs roti (asumsi di file HPP), sehingga semua hasil batch dihitung dalam pcs.

Kebutuhan fungsional tambahan: FR-14 (M) kategori pada transaksi pengeluaran; FR-25 (M) tanda Pelanggan Tetap dan pembatasan metode Belum Dibayar; FR-46 (M) butir "QRIS belum cair" dan "Modal Kembalian" di Tutup Kas.

**Dasar pencatatan laporan (hasil review prototype, 10 Okt 2026).** Dashboard, Laporan Keuangan (PDF), dan Laba Rugi memakai dasar transaksi (accrual), sehingga total pemasukan Agustus 2026 sebesar Rp4.541.000 sama dengan Bookbot dan sudah memuat piutang Rp670.000. Hanya Arus Kas yang memakai dasar pembayaran (pemasukan terbayar Rp3.871.000, pengeluaran terbayar Rp60.000, arus bersih Rp3.811.000). Saldo kas di Dashboard mengikuti angka Arus Kas. Parameter overhead produksi sudah termasuk dalam HPP produk dan tidak ditambahkan lagi.

**Urutan dependensi addon (revisi implementasi, menggantikan tabel Bagian 5).** Arah dependensi adalah genresi\_base, lalu genresi\_stock, lalu genresi\_cash, lalu genresi\_report. genresi\_stock berdiri di bawah genresi\_cash (bukan sebaliknya) agar tidak terjadi dependensi melingkar, karena Transaksi merujuk ke Bahan Baku dan Tutup Kas merujuk ke Produk.
