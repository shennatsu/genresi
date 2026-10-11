"""Raw material master and stock indicators."""

# pylint: disable=abstract-method

from odoo import api, fields, models


class GenresiMaterial(models.Model):
    """Material with manually maintained minimum and computed on-hand stock."""

    _name = "genresi.material"
    _description = "Bahan Baku Genresi"
    _order = "name"

    name = fields.Char(string="Nama Bahan", required=True)
    uom_id = fields.Many2one("uom.uom", string="Satuan", required=True, ondelete="restrict")
    price_per_unit = fields.Monetary(
        string="Harga per Satuan",
        currency_field="currency_id",
        required=True,
        default=0,
    )
    min_stock = fields.Float(string="Stok Minimum", digits=(16, 3), default=0)
    pack_size = fields.Float(string="Ukuran Kemasan", digits=(16, 3), default=0)
    company_id = fields.Many2one(
        "res.company", string="Perusahaan", required=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    stock_move_ids = fields.One2many("genresi.stock.move", "material_id", string="Pergerakan Stok")
    stock_qty = fields.Float(
        string="Stok Saat Ini", digits=(16, 3), compute="_compute_stock_qty", store=True
    )
    stock_state = fields.Selection(
        selection=[("normal", "Aman"), ("critical", "Kritis")],
        string="Status Stok",
        compute="_compute_stock_state",
        store=True,
    )

    @api.depends("stock_move_ids.signed_quantity")
    def _compute_stock_qty(self):
        """Sum signed stock movements for each material."""
        for material in self:
            material.stock_qty = sum(material.stock_move_ids.mapped("signed_quantity"))

    @api.depends("stock_qty", "min_stock")
    def _compute_stock_state(self):
        """Mark material critical when on-hand is at or below its minimum."""
        for material in self:
            material.stock_state = (
                "critical" if material.stock_qty <= material.min_stock else "normal"
            )
