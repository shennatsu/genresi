"""Shared Genresi date helpers."""

from odoo import fields


def genresi_today(env):
    """Return the configured business date or the user's current date."""
    configured = env["ir.config_parameter"].sudo().get_param("genresi.demo_today")
    if configured:
        try:
            return fields.Date.to_date(configured)
        except (TypeError, ValueError):
            pass
    return fields.Date.context_today(env.user)
