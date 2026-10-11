"""Seller master data."""

# pylint: disable=abstract-method

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GenresiSeller(models.Model):
    """Seller and commission configuration."""

    _name = "genresi.seller"
    _description = "Penjual Genresi"
    _order = "name"

    name = fields.Char(string="Nama", required=True)
    pay_type = fields.Selection(
        selection=[
            ("fixed", "Gaji tetap"),
            ("commission", "Komisi"),
        ],
        string="Tipe Pembayaran",
        required=True,
        default="fixed",
    )
    commission_pct = fields.Float(string="Komisi (%)", digits=(16, 2))
    active = fields.Boolean(string="Aktif", default=True)

    @api.constrains("commission_pct", "pay_type")
    def _check_commission(self):
        for seller in self:
            if not 0 <= seller.commission_pct <= 100:
                raise ValidationError("Komisi harus berada di antara 0 dan 100 persen.")
            if seller.pay_type == "fixed" and seller.commission_pct:
                raise ValidationError("Penjual bergaji tetap tidak boleh memiliki komisi.")
