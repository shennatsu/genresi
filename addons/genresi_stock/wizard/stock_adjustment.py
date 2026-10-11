"""Stock opname adjustment wizard."""

# pylint: disable=abstract-method,import-error

from odoo import fields, models
from odoo.addons.genresi_base.models.date_utils import genresi_today


class GenresiStockAdjustment(models.TransientModel):
    """Create a signed adjustment movement for one raw material."""

    _name = "genresi.stock.adjustment"
    _description = "Penyesuaian Stok Genresi"

    material_id = fields.Many2one("genresi.material", string="Bahan Baku", required=True)
    date = fields.Date(
        string="Tanggal", required=True, default=lambda self: genresi_today(self.env)
    )
    quantity = fields.Float(
        string="Selisih Stok",
        digits=(16, 3),
        required=True,
        help="Positif menambah, negatif mengurangi.",
    )
    reason = fields.Char(string="Alasan", required=True)

    def action_apply(self):
        """Create the adjustment movement and close the wizard."""
        self.ensure_one()
        self.env["genresi.stock.move"].create(
            {
                "material_id": self.material_id.id,
                "date": self.date,
                "move_type": "adjust",
                "quantity": self.quantity,
                "reference": "Penyesuaian Stok",
                "note": self.reason,
            }
        )
        return {"type": "ir.actions.act_window_close"}
