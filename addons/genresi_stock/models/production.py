"""Daily production and stock consumption."""

# pylint: disable=abstract-method,import-error,protected-access

from collections import defaultdict

from odoo import api, fields, models
from odoo.addons.genresi_base.models.date_utils import genresi_today
from odoo.exceptions import UserError, ValidationError


class GenresiProduction(models.Model):
    """Production order that consumes recipe ingredients on confirmation."""

    _name = "genresi.production"
    _description = "Produksi Harian Genresi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Referensi", required=True, default="/", copy=False, tracking=True)
    date = fields.Date(
        string="Tanggal", required=True, default=lambda self: genresi_today(self.env)
    )
    product_id = fields.Many2one(
        "genresi.product", string="Produk", required=True, ondelete="restrict", tracking=True
    )
    quantity = fields.Float(string="Jumlah Produksi", required=True, digits=(16, 3), tracking=True)
    uom_id = fields.Many2one(related="product_id.uom_id", string="Satuan", readonly=True)
    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Selesai")],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    warning = fields.Text(string="Peringatan Stok", readonly=True)
    move_ids = fields.One2many(
        "genresi.stock.move", "production_id", string="Bahan Terpakai", readonly=True
    )
    company_id = fields.Many2one(
        "res.company", string="Perusahaan", required=True, default=lambda self: self.env.company
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Assign the PRD sequence using the configured business date."""
        for vals in vals_list:
            production_date = vals.get("date") or genresi_today(self.env)
            vals["date"] = production_date
            if not vals.get("name") or vals["name"] == "/":
                vals["name"] = (
                    self.env["ir.sequence"]
                    .with_context(ir_sequence_date=production_date)
                    .next_by_code("genresi.production")
                    or "/"
                )
        return super().create(vals_list)

    @api.constrains("quantity")
    def _check_quantity(self):
        for production in self:
            if production.quantity <= 0:
                raise ValidationError("Jumlah produksi harus lebih besar dari nol.")

    def _material_requirements(self):
        """Return required material quantities for the requested production."""
        self.ensure_one()
        requirements = defaultdict(float)
        recipes = self.product_id._component_recipes()
        if not recipes:
            raise UserError("Produk belum memiliki resep yang lengkap.")
        for recipe in recipes:
            for line in recipe.line_ids:
                requirements[line.material_id] += (
                    line.quantity * self.quantity / recipe.batch_output_qty
                )
        return requirements

    def action_confirm(self):
        """Create outgoing movements and complete production without stock blocking."""
        for production in self:
            if production.state != "draft":
                continue
            requirements = production._material_requirements()
            warnings = []
            move_values = []
            for material, required_qty in requirements.items():
                if material.stock_qty < required_qty:
                    warnings.append(
                        f"{material.name}: stok {material.stock_qty:g}, "
                        f"butuh {required_qty:g} {material.uom_id.name}."
                    )
                move_values.append(
                    {
                        "material_id": material.id,
                        "date": production.date,
                        "move_type": "out",
                        "quantity": required_qty,
                        "reference": production.name,
                        "production_id": production.id,
                        "note": "Konfirmasi Produksi Harian",
                    }
                )
            self.env["genresi.stock.move"].create(move_values)
            production.write(
                {
                    "state": "done",
                    "warning": "\n".join(warnings) if warnings else False,
                }
            )
            body = "Produksi dikonfirmasi dan pergerakan bahan dibuat."
            if warnings:
                body += " Stok kurang ditandai sebagai peringatan dan tidak memblokir."
            production.message_post(body=body)
        return True
