# Vendored MuK modules

Source resmi: `https://github.com/MuK-IT/odoo-modules`, branch `17.0`, commit
`f64a429016e20eda4ed9cfc012bf3acf338dad4b`.

Modul yang divendorkan persis dari commit tersebut:

| Modul | Versi manifest | Lisensi |
| --- | --- | --- |
| `muk_web_theme` | `17.0.1.2.1` | LGPL-3 |
| `muk_web_appsbar` | `17.0.1.1.3` | LGPL-3 |
| `muk_web_chatter` | `17.0.1.2.0` | LGPL-3 |
| `muk_web_colors` | `17.0.1.0.5` | LGPL-3 |
| `muk_web_dialog` | `17.0.1.0.0` | LGPL-3 |

Pohon dependensi MuK pada commit ini:

```text
muk_web_theme
├── muk_web_chatter ── mail
├── muk_web_dialog ── web
├── muk_web_appsbar ── base_setup, web
└── muk_web_colors ── base_setup, web_editor
```

`muk_web_group` tidak ada di branch/commit ini dan tidak diperlukan. Tidak ada
modul MuK lain yang dimasukkan ke `addons_path`. Kode vendored tidak diubah.
