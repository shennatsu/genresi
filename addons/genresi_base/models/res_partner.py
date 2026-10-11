"""Genresi partner classification fields."""

# pylint: disable=abstract-method

from odoo import fields, models


class ResPartner(models.Model):
    """Extend partners with Genresi customer and supplier flags."""

    _inherit = "res.partner"

    genresi_partner_type = fields.Selection(
        selection=[
            ("customer", "Pelanggan"),
            ("supplier", "Supplier"),
            ("both", "Pelanggan & Supplier"),
        ],
        string="Tipe Genresi",
        default="customer",
        required=True,
    )
    genresi_is_fixed_customer = fields.Boolean(string="Pelanggan Tetap")
