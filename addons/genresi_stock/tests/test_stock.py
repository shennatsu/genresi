"""Transaction tests for Genresi stock and production rules."""

# pylint: disable=too-many-arguments

from odoo import fields
from odoo.tests.common import TransactionCase


class TestGenresiStock(TransactionCase):
    """Verify stock movements, HPP calculations, and production consumption."""

    def setUp(self):
        super().setUp()
        self.gram = self.env.ref("uom.product_uom_gram")
        self.pcs = self.env.ref("genresi_base.uom_genresi_pcs")
        self.business_line = self.env.ref("genresi_base.business_line_reguler")
        self.env["ir.config_parameter"].sudo().set_param(
            "genresi.overhead_production_per_piece", "1913.567995680438"
        )

    def _material(self, name, price, min_stock=0, uom=None):
        return self.env["genresi.material"].create(
            {
                "name": name,
                "uom_id": (uom or self.gram).id,
                "price_per_unit": price,
                "min_stock": min_stock,
            }
        )

    def _recipe(self, name, recipe_type, batch_output_qty, lines, additional_cost=0):
        return self.env["genresi.recipe"].create(
            {
                "name": name,
                "recipe_type": recipe_type,
                "batch_output_qty": batch_output_qty,
                "additional_cost": additional_cost,
                "line_ids": [
                    (0, 0, {"material_id": material.id, "quantity": quantity})
                    for material, quantity in lines
                ],
            }
        )

    def _product(self, name, dough, filling=None, packaging=None, sale_price=0):
        packaging = packaging or self._recipe(f"{name} Kemasan", "packaging", 1, [])
        return self.env["genresi.product"].create(
            {
                "name": name,
                "business_line_id": self.business_line.id,
                "dough_recipe_id": dough.id,
                "filling_recipe_id": filling.id if filling else False,
                "packaging_recipe_id": packaging.id,
                "uom_id": self.pcs.id,
                "sale_price": sale_price,
            }
        )

    def test_stock_movements_and_adjustment(self):
        """Incoming, outgoing, and opname movements update stock and critical state."""
        material = self._material("Bahan Uji Stok", 15, min_stock=200)
        move_model = self.env["genresi.stock.move"]
        date = fields.Date.to_date("2026-08-01")
        move_model.create(
            {
                "material_id": material.id,
                "date": date,
                "move_type": "in",
                "quantity": 180,
            }
        )
        move_model.create(
            {
                "material_id": material.id,
                "date": date,
                "move_type": "out",
                "quantity": 25,
            }
        )
        adjustment = self.env["genresi.stock.adjustment"].create(
            {
                "material_id": material.id,
                "date": date,
                "quantity": -5,
                "reason": "Koreksi stok fisik",
            }
        )
        adjustment.action_apply()

        self.assertAlmostEqual(material.stock_qty, 150)
        self.assertEqual(material.stock_state, "critical")
        self.assertEqual(
            material.stock_move_ids.filtered(lambda move: move.move_type == "adjust").quantity,
            -5,
        )

    def test_hpp_matches_workbook_reference(self):
        """The Keju Bungasari HPP must match the workbook's reference amount."""
        dough_materials = [
            ("Terigu gandum whole wheat bungasari", 39.6, 300),
            ("Terigu Golden eagle", 15, 1200),
            ("Ragi permifan 2 in 1", 107, 30),
            ("Gula pasir", 18, 200),
            ("Telor", 30, 180),
            ("Mother choice", 35, 225),
            ("Garam", 17.5, 26),
        ]
        dough = self._recipe(
            "Adonan Bungasari Uji",
            "dough",
            8,
            [(self._material(name, price), quantity) for name, price, quantity in dough_materials],
        )
        filling = self._recipe(
            "Filling Keju Uji",
            "filling",
            15,
            [
                (self._material("Keju Uji", 60), 300),
                (self._material("Elmer glaze Uji", 75), 500),
                (self._material("SKM Uji", 124), 100),
            ],
        )
        packaging = self._recipe(
            "Kemasan Uji",
            "packaging",
            1,
            [
                (self._material("Lunch box Uji", 1200, uom=self.pcs), 1),
                (self._material("Kresek Uji", 260, uom=self.pcs), 1),
            ],
        )
        product = self._product(
            "Roti Keju - Adonan Bungasari Uji",
            dough,
            filling,
            packaging,
            sale_price=25000,
        )

        self.assertAlmostEqual(dough.total_cost, 50420, places=6)
        self.assertAlmostEqual(dough.cost_per_piece, 6302.5, places=6)
        self.assertAlmostEqual(filling.cost_per_piece, 4526.666666666667, places=6)
        self.assertAlmostEqual(product.hpp_per_piece, 14202.734662347106, delta=0.000001)
        self.assertAlmostEqual(product.margin, 10797.265337652894, delta=0.000001)

    def test_production_consumes_recipe_quantity_and_warns_without_blocking(self):
        """Production scales batch quantities and confirms even with insufficient stock."""
        material = self._material("Bahan Produksi Uji", 15)
        self.env["genresi.stock.move"].create(
            {
                "material_id": material.id,
                "date": fields.Date.to_date("2026-08-23"),
                "move_type": "in",
                "quantity": 100,
            }
        )
        dough = self._recipe("Adonan Produksi Uji", "dough", 8, [(material, 300)])
        product = self._product("Produk Produksi Uji", dough)
        production = self.env["genresi.production"].create(
            {
                "date": fields.Date.to_date("2026-08-23"),
                "product_id": product.id,
                "quantity": 16,
            }
        )

        production.action_confirm()

        self.assertEqual(production.state, "done")
        self.assertEqual(len(production.move_ids), 1)
        self.assertAlmostEqual(production.move_ids.quantity, 600)
        self.assertAlmostEqual(material.stock_qty, -500)
        self.assertIn("stok", production.warning.lower())
