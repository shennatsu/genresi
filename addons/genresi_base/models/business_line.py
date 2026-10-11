"""Business line master data."""

# pylint: disable=abstract-method

from odoo import fields, models


class GenresiBusinessLine(models.Model):
    """Configurable Genresi business line."""

    _name = "genresi.business.line"
    _description = "Lini Bisnis Genresi"
    _order = "name"

    name = fields.Char(string="Nama", required=True)
    active = fields.Boolean(string="Aktif", default=True)

    _sql_constraints = [
        ("name_unique", "unique(name)", "Nama lini bisnis harus unik."),
    ]
