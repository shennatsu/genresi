{
    "name": "Genresi - Dasar",
    "summary": "Kerangka dasar Genresi",
    "version": "17.0.1.0.0",
    "category": "Genresi",
    "author": "CV Generasi Restu Ibu",
    "website": "https://github.com/shennatsu/genresi",
    "license": "LGPL-3",
    "depends": ["base", "mail", "uom", "muk_web_theme"],
    "data": [
        "security/genresi_security.xml",
        "data/company_branding.xml",
        "data/menu_data.xml",
        "views/branding_templates.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "genresi_base/static/src/scss/primary_variables.scss",
        ],
        "web.assets_backend": [
            "genresi_base/static/src/scss/branding.scss",
            "genresi_base/static/src/xml/navbar.xml",
        ],
        "web.assets_frontend": [
            "genresi_base/static/src/scss/branding.scss",
        ],
    },
    "installable": True,
    "application": True,
}
