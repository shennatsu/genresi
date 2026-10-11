"""Finished product HPP and margin."""

# pylint: disable=abstract-method,no-member,protected-access

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GenresiProduct(models.Model):
    """Product assembled from dough, optional filling, and packaging recipes."""

    _name = "genresi.product"
    _description = "Produk Genresi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Nama Produk", required=True, tracking=True)
    business_line_id = fields.Many2one(
        "genresi.business.line",
        string="Lini Bisnis",
        required=True,
        default=lambda self: self.env.ref("genresi_base.business_line_reguler"),
    )
    dough_recipe_id = fields.Many2one(
        "genresi.recipe",
        string="Resep Adonan",
        required=True,
        domain='[("recipe_type", "=", "dough")]',
        ondelete="restrict",
    )
    filling_recipe_id = fields.Many2one(
        "genresi.recipe",
        string="Resep Filling",
        domain='[("recipe_type", "=", "filling")]',
        ondelete="restrict",
    )
    packaging_recipe_id = fields.Many2one(
        "genresi.recipe",
        string="Resep Kemasan",
        required=True,
        domain='[("recipe_type", "=", "packaging")]',
        ondelete="restrict",
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Satuan Jual",
        required=True,
        default=lambda self: self.env.ref("genresi_base.uom_genresi_pcs"),
    )
    sale_price = fields.Monetary(string="Harga Jual", currency_field="currency_id", tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Perusahaan", required=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    hpp_per_piece = fields.Monetary(
        string="HPP per pcs",
        currency_field="currency_id",
        compute="_compute_cost",
        store=True,
    )
    margin = fields.Monetary(
        string="Margin",
        currency_field="currency_id",
        compute="_compute_cost",
        store=True,
    )
    margin_pct = fields.Float(string="Margin (%)", compute="_compute_cost", store=True)
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
    production_count = fields.Integer(string="Produksi", compute="_compute_production_count")

    def _component_recipes(self):
        """Return the recipes used by this product in costing order."""
        self.ensure_one()
        return self.dough_recipe_id | self.filling_recipe_id | self.packaging_recipe_id

    def _get_overhead(self):
        value = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("genresi.overhead_production_per_piece", default="0")
        )
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @api.depends(
        "dough_recipe_id.cost_per_piece",
        "dough_recipe_id.has_incomplete_cost",
        "filling_recipe_id.cost_per_piece",
        "filling_recipe_id.has_incomplete_cost",
        "packaging_recipe_id.cost_per_piece",
        "packaging_recipe_id.has_incomplete_cost",
        "sale_price",
    )
    def _compute_cost(self):
        """Compute HPP from recipe components and the configured overhead."""
        overhead = self._get_overhead()
        for product in self:
            recipes = product._component_recipes()
            product.hpp_per_piece = sum(recipes.mapped("cost_per_piece")) + overhead
            product.has_incomplete_cost = any(recipes.mapped("has_incomplete_cost"))
            if product.has_incomplete_cost or not product.sale_price:
                product.margin = False
                product.margin_pct = 0
            else:
                product.margin = product.sale_price - product.hpp_per_piece
                product.margin_pct = product.margin / product.sale_price * 100

    def _compute_production_count(self):
        for product in self:
            product.production_count = self.env["genresi.production"].search_count(
                [("product_id", "=", product.id)]
            )

    @api.constrains("dough_recipe_id", "filling_recipe_id", "packaging_recipe_id")
    def _check_recipe_types(self):
        for product in self:
            if product.dough_recipe_id.recipe_type != "dough":
                raise ValidationError("Resep adonan harus bertipe Adonan.")
            if product.filling_recipe_id and product.filling_recipe_id.recipe_type != "filling":
                raise ValidationError("Resep filling harus bertipe Filling.")
            if product.packaging_recipe_id.recipe_type != "packaging":
                raise ValidationError("Resep kemasan harus bertipe Kemasan.")

    def action_view_productions(self):
        """Open productions for this product."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Produksi Harian",
            "res_model": "genresi.production",
            "view_mode": "tree,form",
            "domain": [("product_id", "=", self.id)],
            "context": {"default_product_id": self.id},
        }
