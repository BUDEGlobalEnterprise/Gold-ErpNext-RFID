# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

"""
Tests for the pre-submit cart validator (Fix #3).

validate_pos_cart is the gate the POS UI calls right before "Submit" so the
cashier hears about sold-out / price-changed / inactive-serial situations as
clear, actionable errors instead of an opaque Sales Invoice failure.

Each issue type from api.pos has a focused test here.
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.tests.utils import ensure_item, ensure_warehouse


def _make_bin_qty(item_code: str, warehouse: str, qty: float) -> None:
	"""Force a Bin row for tests so we can exercise out_of_stock vs in-stock.

	We avoid the full Stock Entry pipeline because that pulls in cost
	centers / accounts that the test site doesn't have configured.
	"""
	if frappe.db.exists("Bin", {"item_code": item_code, "warehouse": warehouse}):
		frappe.db.set_value(
			"Bin",
			{"item_code": item_code, "warehouse": warehouse},
			"actual_qty",
			qty,
		)
		return

	bin_doc = frappe.new_doc("Bin")
	bin_doc.item_code = item_code
	bin_doc.warehouse = warehouse
	bin_doc.actual_qty = qty
	bin_doc.insert(ignore_permissions=True, ignore_mandatory=True)


class TestValidatePosCart(FrappeTestCase):
	"""Each test exercises one issue type so a regression points at the cause."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")

		cls.warehouse = ensure_warehouse("Zevar Cart Test Warehouse")

		cls.in_stock = ensure_item("ZEVAR-CART-IN-001", "In-Stock Test Item", rate=150.0)
		cls.out_of_stock = ensure_item("ZEVAR-CART-OOS-001", "Out-of-Stock Test Item", rate=120.0)
		cls.disabled_item = ensure_item("ZEVAR-CART-DIS-001", "Disabled Test Item", rate=80.0)

		_make_bin_qty(cls.in_stock, cls.warehouse, 5)
		_make_bin_qty(cls.out_of_stock, cls.warehouse, 0)

		# Mark one item disabled.
		frappe.db.set_value("Item", cls.disabled_item, "disabled", 1)

		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		# Don't leave the disabled flag set, in case other tests reuse the item.
		try:
			frappe.db.set_value("Item", cls.disabled_item, "disabled", 0)
			frappe.db.commit()
		except Exception:
			pass
		super().tearDownClass()

	def setUp(self):
		frappe.set_user("Administrator")

	def _validate(self, lines, warehouse=None):
		from zevar_core.api.pos import validate_pos_cart

		return validate_pos_cart(
			items=json.dumps(lines),
			warehouse=warehouse if warehouse is not None else self.warehouse,
		)

	# ------------------------------------------------------------------
	# Happy path
	# ------------------------------------------------------------------

	def test_in_stock_item_at_current_price_is_ok(self):
		current_rate = frappe.db.get_value("Item", self.in_stock, "standard_rate")
		result = self._validate([{"item_code": self.in_stock, "qty": 1, "rate": current_rate}])
		self.assertTrue(result["ok"])
		self.assertEqual(result["issues"], [])

	# ------------------------------------------------------------------
	# Availability issues (blocking)
	# ------------------------------------------------------------------

	def test_out_of_stock_is_flagged_blocking(self):
		result = self._validate(
			[{"item_code": self.out_of_stock, "qty": 1, "rate": 100.0}]
		)
		self.assertFalse(result["ok"])
		types = {i["type"] for i in result["issues"] if i.get("blocking")}
		self.assertIn("out_of_stock", types)

	def test_unknown_item_is_flagged(self):
		result = self._validate([{"item_code": "ZEVAR-DOES-NOT-EXIST", "qty": 1, "rate": 50.0}])
		self.assertFalse(result["ok"])
		types = {i["type"] for i in result["issues"]}
		self.assertIn("item_missing", types)

	def test_disabled_item_is_flagged(self):
		result = self._validate(
			[{"item_code": self.disabled_item, "qty": 1, "rate": 80.0}]
		)
		self.assertFalse(result["ok"])
		types = {i["type"] for i in result["issues"]}
		self.assertIn("item_disabled", types)

	def test_qty_zero_is_flagged(self):
		current_rate = frappe.db.get_value("Item", self.in_stock, "standard_rate")
		result = self._validate(
			[{"item_code": self.in_stock, "qty": 0, "rate": current_rate}]
		)
		self.assertFalse(result["ok"])
		types = {i["type"] for i in result["issues"]}
		self.assertIn("qty_invalid", types)

	def test_rate_zero_is_flagged(self):
		result = self._validate([{"item_code": self.in_stock, "qty": 1, "rate": 0}])
		self.assertFalse(result["ok"])
		types = {i["type"] for i in result["issues"]}
		self.assertIn("rate_invalid", types)

	# ------------------------------------------------------------------
	# Price drift (informational)
	# ------------------------------------------------------------------

	def test_price_drift_is_flagged_non_blocking(self):
		# Cart rate 75, current price 150 → drift; cart still passes since
		# drift is informational (cashier may have applied a discount).
		result = self._validate([{"item_code": self.in_stock, "qty": 1, "rate": 75.0}])
		drift = [i for i in result["issues"] if i["type"] == "price_drift"]
		self.assertEqual(len(drift), 1)
		self.assertFalse(drift[0]["blocking"])
		self.assertEqual(drift[0]["details"]["cart_rate"], 75.0)
		self.assertEqual(drift[0]["details"]["current_price"], 150.0)
		# Drift alone does not flip ok=False.
		self.assertTrue(result["ok"])

	def test_no_price_drift_within_floating_point_tolerance(self):
		# 150.001 vs canonical 150 — within 0.005 tolerance.
		result = self._validate(
			[{"item_code": self.in_stock, "qty": 1, "rate": 150.001}]
		)
		drift_types = {i["type"] for i in result["issues"]}
		self.assertNotIn("price_drift", drift_types)

	# ------------------------------------------------------------------
	# Multi-line carts mix issue types correctly
	# ------------------------------------------------------------------

	def test_mixed_cart_aggregates_all_issues(self):
		current_rate = frappe.db.get_value("Item", self.in_stock, "standard_rate")
		result = self._validate(
			[
				{"item_code": self.in_stock, "qty": 1, "rate": current_rate},  # ok
				{"item_code": self.out_of_stock, "qty": 1, "rate": 120.0},  # blocking
				{"item_code": self.disabled_item, "qty": 1, "rate": 80.0},  # blocking
			]
		)
		self.assertFalse(result["ok"])
		types = {i["type"] for i in result["issues"]}
		self.assertIn("out_of_stock", types)
		self.assertIn("item_disabled", types)
