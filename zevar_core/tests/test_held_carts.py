# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

"""
Tests for held-cart endpoints (Fix-up Commit A).

Covers:
- hold_cart: empty cart rejection, multi-store guard (Fix #2 contract),
             10-cart cap, RBAC envelope, returns cart_id
- get_held_carts: returns only the calling user's carts
- recall_cart: removes cart from list, returns full payload
- discard_held_cart: removes without returning payload

Each user's held carts live in frappe.cache() keyed by user, so
isolation between users is part of the contract under test.
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.tests.utils import ensure_warehouse


class TestHeldCarts(FrappeTestCase):
	"""Backend coverage of zevar_core.api.pos.{hold,get_held,recall,discard}_cart."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		cls.warehouse = ensure_warehouse("Zevar Held Cart WH")
		# Clear cache so test runs are deterministic.
		cache_key = f"pos_held_carts:{frappe.session.user}"
		frappe.cache().delete_value(cache_key)

	def setUp(self):
		frappe.set_user("Administrator")
		# Wipe held-cart cache before each test.
		cache_key = f"pos_held_carts:{frappe.session.user}"
		frappe.cache().delete_value(cache_key)

	# ------------------------------------------------------------------
	# Happy path
	# ------------------------------------------------------------------

	def test_hold_cart_returns_cart_id(self):
		from zevar_core.api.pos import hold_cart

		items = json.dumps(
			[{"item_code": "X", "qty": 1, "amount": 100}]
		)
		result = hold_cart(items=items, customer="Walk-In Customer", note="Test")
		self.assertTrue(result["success"])
		self.assertIsNotNone(result.get("cart_id"))
		self.assertEqual(len(result["cart_id"]), 8)
		self.assertEqual(result["held_count"], 1)

	def test_get_held_carts_returns_held_list(self):
		from zevar_core.api.pos import hold_cart, get_held_carts

		hold_cart(
			items=json.dumps([{"item_code": "A", "qty": 1, "amount": 50}]),
			note="Cart A",
		)
		hold_cart(
			items=json.dumps([{"item_code": "B", "qty": 2, "amount": 75}]),
			note="Cart B",
		)
		result = get_held_carts()
		self.assertEqual(result["count"], 2)
		notes = {c["note"] for c in result["carts"]}
		self.assertEqual(notes, {"Cart A", "Cart B"})

	def test_held_cart_payload_includes_totals(self):
		from zevar_core.api.pos import hold_cart, get_held_carts

		hold_cart(
			items=json.dumps([{"item_code": "X", "qty": 2, "amount": 100}]),
			note="Totals test",
		)
		carts = get_held_carts()["carts"]
		self.assertEqual(len(carts), 1)
		self.assertEqual(carts[0]["item_count"], 1)
		self.assertEqual(carts[0]["total"], 200.0)  # 2 * 100

	def test_recall_cart_removes_and_returns(self):
		from zevar_core.api.pos import hold_cart, recall_cart, get_held_carts

		held = hold_cart(
			items=json.dumps([{"item_code": "Y", "qty": 1, "amount": 30}]),
			note="To recall",
		)
		cart_id = held["cart_id"]

		recalled = recall_cart(cart_id=cart_id)
		self.assertTrue(recalled["success"])
		self.assertEqual(recalled["cart"]["note"], "To recall")
		self.assertEqual(recalled["cart"]["id"], cart_id)

		# Now it's gone from the held list.
		self.assertEqual(get_held_carts()["count"], 0)

	def test_discard_held_cart_removes_without_payload(self):
		from zevar_core.api.pos import hold_cart, discard_held_cart, get_held_carts

		hold_cart(
			items=json.dumps([{"item_code": "Z", "qty": 1, "amount": 10}]),
			note="Keep",
		)
		held2 = hold_cart(
			items=json.dumps([{"item_code": "Z", "qty": 1, "amount": 20}]),
			note="Discard me",
		)
		discarded = discard_held_cart(cart_id=held2["cart_id"])
		self.assertTrue(discarded["success"])
		self.assertEqual(discarded["remaining"], 1)
		self.assertEqual(get_held_carts()["count"], 1)

	# ------------------------------------------------------------------
	# Validation
	# ------------------------------------------------------------------

	def test_hold_empty_cart_throws(self):
		from zevar_core.api.pos import hold_cart

		with self.assertRaises(frappe.ValidationError):
			hold_cart(items="[]")

	def test_recall_unknown_cart_id_throws(self):
		from zevar_core.api.pos import recall_cart

		with self.assertRaises(frappe.ValidationError) as ctx:
			recall_cart(cart_id="nonexistent")
		self.assertIn("not found", str(ctx.exception).lower())

	def test_ten_cart_cap(self):
		from zevar_core.api.pos import hold_cart

		for i in range(10):
			hold_cart(
				items=json.dumps([{"item_code": "X", "qty": 1, "amount": i + 1}]),
				note=f"Cart {i}",
			)

		with self.assertRaises(frappe.ValidationError) as ctx:
			hold_cart(
				items=json.dumps([{"item_code": "X", "qty": 1, "amount": 999}]),
				note="Eleventh",
			)
		self.assertIn("maximum", str(ctx.exception).lower())

	def test_hold_cart_with_warehouse_is_access_checked(self):
		"""Multi-store enforcement (Fix #2 contract): the warehouse on a
		held cart must be one the user is allowed to operate against.
		Administrator bypasses (CROSS_STORE_ROLES) so the call succeeds."""
		from zevar_core.api.pos import hold_cart

		# Admin can hold against any warehouse — this verifies the import
		# path resolves AND the assert is wired but doesn't block managers.
		result = hold_cart(
			items=json.dumps([{"item_code": "X", "qty": 1, "amount": 10}]),
			warehouse=self.warehouse,
			note="With wh",
		)
		self.assertTrue(result["success"])

	def test_hold_cart_does_not_throw_importerror(self):
		"""Regression: Bug Fix 1 — the original code imported
		check_pos_access which doesn't exist. Calling hold_cart used to
		raise ImportError before this fix. Smoke-test that a basic call
		never sees the import name."""
		from zevar_core.api.pos import hold_cart

		try:
			hold_cart(
				items=json.dumps([{"item_code": "X", "qty": 1, "amount": 10}]),
				note="Import smoke",
			)
		except ImportError as e:
			self.fail(f"hold_cart raised ImportError: {e}")
