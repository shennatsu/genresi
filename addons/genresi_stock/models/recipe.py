"""Batch recipes and ingredient costing."""

# pylint: disable=abstract-method,duplicate-code,no-member

from odoo import api, fields, models
from odoo.exceptions import ValidationError

RECIPE_TYPES = [
    ("dough", "Adonan"),
    ("filling", "Filling"),
    ("packaging", "Kemasan"),
]


class GenresiRecipe(models.Model):
    """Recipe whose ingredient quantities produce a batch of pieces."""

    _name = "genresi.recipe"
    _description = "Resep Genresi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Nama Resep", required=True, tracking=True)
    recipe_type = fields.Selection(
        selection=RECIPE_TYPES, string="Jenis Resep", required=True, tracking=True
    )
    batch_output_qty = fields.Float(
        string="Hasil Batch (pcs)", required=True, digits=(16, 0), default=1, tracking=True
    )
    additional_cost = fields.Monetary(
        string="Biaya Langsung Tambahan",
        currency_field="currency_id",
        digits=(16, 0),
        help="Dipakai untuk biaya batch yang tidak memiliki bahan tersendiri.",
    )
    line_ids = fields.One2many("genresi.recipe.line", "recipe_id", string="Bahan Resep", copy=True)
    company_id = fields.Many2one(
        "res.company", string="Perusahaan", required=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    total_cost = fields.Monetary(
        string="Subtotal Batch",
        currency_field="currency_id",
        digits=(16, 0),
        compute="_compute_cost",
        store=True,
    )
    cost_per_piece = fields.Monetary(
        string="Biaya per pcs",
        currency_field="currency_id",
        digits=(16, 0),
        compute="_compute_cost",
        store=True,
    )
    has_incomplete_cost = fields.Boolean(
        string="Harga Belum Lengkap", compute="_compute_cost", store=True
    )
    active = fields.Boolean(string="Aktif", default=True, tracking=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Aktif"),
            ("archived", "Diarsipkan"),
        ],
        string="Status",
        default="active",
        required=True,
        tracking=True,
    )
    product_count = fields.Integer(string="Produk", compute="_compute_product_count")

    @api.depends("line_ids.subtotal", "line_ids.unit_price", "additional_cost", "batch_output_qty")
    def _compute_cost(self):
        """Compute batch cost, unit cost, and incomplete-price flag."""
        for recipe in self:
            recipe.total_cost = sum(recipe.line_ids.mapped("subtotal")) + recipe.additional_cost
            recipe.cost_per_piece = (
                recipe.total_cost / recipe.batch_output_qty if recipe.batch_output_qty else 0
            )
            recipe.has_incomplete_cost = any(line.unit_price <= 0 for line in recipe.line_ids)

    def _compute_product_count(self):
        for recipe in self:
            recipe.product_count = self.env["genresi.product"].search_count(
                [
                    "|",
                    ("dough_recipe_id", "=", recipe.id),
                    "|",
                    ("filling_recipe_id", "=", recipe.id),
                    ("packaging_recipe_id", "=", recipe.id),
                ]
            )

    @api.constrains("batch_output_qty", "additional_cost")
    def _check_batch(self):
        for recipe in self:
            if recipe.batch_output_qty <= 0:
                raise ValidationError("Hasil batch harus lebih besar dari nol.")
            if recipe.additional_cost < 0:
                raise ValidationError("Biaya langsung tambahan tidak boleh negatif.")

    def action_view_products(self):
        """Open products that use this recipe."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Produk",
            "res_model": "genresi.product",
            "view_mode": "tree,form",
            "domain": [
                "|",
                ("dough_recipe_id", "=", self.id),
                "|",
                ("filling_recipe_id", "=", self.id),
                ("packaging_recipe_id", "=", self.id),
            ],
        }


class GenresiRecipeLine(models.Model):
    """Ingredient quantity and subtotal within a batch recipe."""

    _name = "genresi.recipe.line"
    _description = "Baris Resep Genresi"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    recipe_id = fields.Many2one("genresi.recipe", string="Resep", required=True, ondelete="cascade")
    material_id = fields.Many2one(
        "genresi.material", string="Bahan Baku", required=True, ondelete="restrict"
    )
    quantity = fields.Float(string="Takaran Batch", required=True, digits=(16, 2))
    uom_id = fields.Many2one(related="material_id.uom_id", string="Satuan", readonly=True)
    currency_id = fields.Many2one(related="recipe_id.currency_id", readonly=True)
    unit_price = fields.Monetary(
        string="Harga per Satuan",
        related="material_id.price_per_unit",
        currency_field="currency_id",
        digits=(16, 0),
        store=True,
        readonly=True,
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        currency_field="currency_id",
        digits=(16, 0),
        compute="_compute_subtotal",
        store=True,
    )

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Takaran bahan harus lebih besar dari nol.")
