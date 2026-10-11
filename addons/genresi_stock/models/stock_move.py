"""Genresi stock movements."""

# pylint: disable=abstract-method,import-error

from odoo import api, fields, models
from odoo.addons.genresi_base.models.date_utils import genresi_today
from odoo.exceptions import ValidationError


class GenresiStockMove(models.Model):
    """Incoming, outgoing, and adjustment movements for raw materials."""

    _name = "genresi.stock.move"
    _description = "Pergerakan Stok Genresi"
    _order = "date desc, id desc"

    material_id = fields.Many2one(
        "genresi.material", string="Bahan Baku", required=True, ondelete="restrict"
    )
    date = fields.Date(
        string="Tanggal", required=True, default=lambda self: genresi_today(self.env)
    )
    move_type = fields.Selection(
        selection=[
            ("in", "Masuk"),
            ("out", "Keluar"),
            ("adjust", "Penyesuaian"),
        ],
        string="Jenis",
        required=True,
        default="in",
    )
    quantity = fields.Float(string="Jumlah", digits=(16, 3), required=True)
    signed_quantity = fields.Float(
        string="Jumlah Bertanda", digits=(16, 3), compute="_compute_signed_quantity", store=True
    )
    uom_id = fields.Many2one(related="material_id.uom_id", string="Satuan", readonly=True)
    reference = fields.Char(string="Referensi")
    note = fields.Char(string="Catatan")
    production_id = fields.Many2one(
        "genresi.production", string="Produksi", ondelete="cascade", readonly=True
    )
    company_id = fields.Many2one(
        related="material_id.company_id", string="Perusahaan", store=True, readonly=True
    )

    @api.depends("move_type", "quantity")
    def _compute_signed_quantity(self):
        """Convert movement type into a signed stock quantity."""
        for move in self:
            move.signed_quantity = {
                "in": move.quantity,
                "out": -move.quantity,
                "adjust": move.quantity,
            }[move.move_type]

    @api.constrains("move_type", "quantity")
    def _check_quantity(self):
        for move in self:
            if move.move_type in ("in", "out") and move.quantity <= 0:
                raise ValidationError("Pergerakan masuk/keluar harus memiliki jumlah positif.")
