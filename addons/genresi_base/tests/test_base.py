"""Transaction tests for the Genresi base foundation."""

from odoo.tests.common import TransactionCase


class TestGenresiBase(TransactionCase):
    """Verify the roles, standard menu visibility, and company defaults."""

    def test_roles_imply_each_other(self):
        """Owner, Staf, and Viewer must form the expected implication chain."""
        owner = self.env.ref("genresi_base.group_genresi_owner")
        staf = self.env.ref("genresi_base.group_genresi_staf")
        viewer = self.env.ref("genresi_base.group_genresi_viewer")

        self.assertIn(staf, owner.implied_ids)
        self.assertIn(viewer, staf.implied_ids)
        self.assertIn(self.env.ref("base.group_user"), viewer.implied_ids)

    def test_standard_menus_are_admin_only(self):
        """Standard root menus must be visible only to system administrators."""
        system_group = self.env.ref("base.group_system")
        standard_menu_ids = (
            "mail.menu_root_discuss",
            "base.menu_management",
            "base.menu_administration",
            "spreadsheet_dashboard.spreadsheet_dashboard_menu_root",
        )

        for xmlid in standard_menu_ids:
            menu = self.env.ref(xmlid)
            self.assertIn(system_group, menu.groups_id)
            self.assertNotIn(self.env.ref("base.group_user"), menu.groups_id)

    def test_company_uses_idr(self):
        """The main company must use IDR with unit rounding."""
        company = self.env.company
        idr = self.env.ref("base.IDR")

        self.assertEqual(company.currency_id, idr)
        self.assertEqual(idr.rounding, 1.0)
