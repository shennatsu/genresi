"""Genresi configuration settings."""

# pylint: disable=abstract-method,no-member

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Persist Genresi operating parameters in ir.config_parameter."""

    _inherit = "res.config.settings"

    company_currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    overhead_production_per_piece = fields.Monetary(
        string="Overhead produksi per pcs",
        currency_field="company_currency_id",
    )
    sales_opex_per_piece = fields.Monetary(
        string="Opex jualan per pcs",
        currency_field="company_currency_id",
    )
    due_days_default = fields.Integer(
        string="Default jatuh tempo (hari)",
        default=3,
        config_parameter="genresi.default_due_days",
    )
    demo_today = fields.Date(
        string="Tanggal bisnis contoh",
    )

    @api.model
    def get_values(self):
        """Load monetary and date parameters from the system configuration."""
        values = super().get_values()
        parameters = self.env["ir.config_parameter"].sudo()
        values.update(
            {
                "overhead_production_per_piece": float(
                    parameters.get_param("genresi.overhead_production_per_piece", default="0")
                ),
                "sales_opex_per_piece": float(
                    parameters.get_param("genresi.sales_opex_per_piece", default="0")
                ),
                "demo_today": parameters.get_param("genresi.demo_today") or False,
            }
        )
        return values

    def set_values(self):
        """Persist monetary and date parameters in the system configuration."""
        super().set_values()
        parameters = self.env["ir.config_parameter"].sudo()
        parameters.set_param(
            "genresi.overhead_production_per_piece",
            self.overhead_production_per_piece or 0,
        )
        parameters.set_param("genresi.sales_opex_per_piece", self.sales_opex_per_piece or 0)
        parameters.set_param(
            "genresi.demo_today",
            fields.Date.to_string(self.demo_today) if self.demo_today else "",
        )
