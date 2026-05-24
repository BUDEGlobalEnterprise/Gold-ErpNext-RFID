# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


class TestDiscountRule(FrappeTestCase):
	def setUp(self):
		# Clean up any test rules
		for name in frappe.get_all("Discount Rule", {"rule_name": ("like", "_Test%")}, pluck="name"):
			frappe.delete_doc("Discount Rule", name)

	def _make_rule(self, rule_type="Global", max_pct=10, **kwargs):
		doc = frappe.get_doc(
			{
				"doctype": "Discount Rule",
				"rule_name": f"_Test {rule_type} {max_pct}%",
				"rule_type": rule_type,
				"discount_method": "Percentage",
				"max_discount_pct": max_pct,
				"is_active": 1,
				**kwargs,
			}
		)
		doc.insert()
		return doc

	def test_no_rules_fallback_10pct(self):
		"""Without rules, default 10% limit applies for non-managers."""
		from zevar_core.api.discount import validate_discount

		result = validate_discount(discount_amount=0, discount_pct=8)
		self.assertTrue(result["valid"])

	def test_no_rules_over_10pct_rejected(self):
		from zevar_core.api.discount import validate_discount

		result = validate_discount(discount_amount=0, discount_pct=15)
		self.assertFalse(result["valid"])

	def test_global_rule_sets_limit(self):
		from zevar_core.api.discount import validate_discount

		self._make_rule(rule_type="Global", max_pct=20)
		result = validate_discount(discount_amount=0, discount_pct=18)
		self.assertTrue(result["valid"])

		result = validate_discount(discount_amount=0, discount_pct=25)
		self.assertFalse(result["valid"])

	def test_higher_priority_wins(self):
		from zevar_core.api.discount import validate_discount

		self._make_rule(rule_type="Global", max_pct=10, priority=0)
		self._make_rule(rule_type="Global", max_pct=25, priority=10)

		result = validate_discount(discount_amount=0, discount_pct=20)
		self.assertTrue(result["valid"])

	def test_flat_amount_rule(self):
		from zevar_core.api.discount import validate_discount

		frappe.get_doc(
			{
				"doctype": "Discount Rule",
				"rule_name": "_Test Flat $50",
				"rule_type": "Global",
				"discount_method": "Flat Amount",
				"max_discount_amt": 50,
				"is_active": 1,
			}
		).insert()

		result = validate_discount(discount_amount=30, discount_pct=0)
		self.assertTrue(result["valid"])

		result = validate_discount(discount_amount=60, discount_pct=0)
		self.assertFalse(result["valid"])

	def test_inactive_rule_ignored(self):
		from zevar_core.api.discount import validate_discount

		frappe.get_doc(
			{
				"doctype": "Discount Rule",
				"rule_name": "_Test Inactive",
				"rule_type": "Global",
				"discount_method": "Percentage",
				"max_discount_pct": 50,
				"is_active": 0,
			}
		).insert()

		# Should fall back to 10% default since no active rules
		result = validate_discount(discount_amount=0, discount_pct=15)
		self.assertFalse(result["valid"])
