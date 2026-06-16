"""
Quick-Win Sprint Q5 — Profit UI<->API contract tests.

Covers the four contracts that were broken between the Profit frontend and
profit_intelligence.py:
  - create_recommendation (previously a 404 - the endpoint did not exist)
  - review_recommendation action casing (UI sends 'Approved'/'Rejected')
  - get_margin_heatmap pivoted shape (array of {jewelry_type, margins:{metal:{margin_pct}}})
  - confidence_level string -> numeric `confidence` for the badge
"""

import json
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today

from zevar_core.tests.utils import ensure_customer, ensure_item, ensure_warehouse

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required (Sales Invoice DocType not found)",
)


def _create_test_employee(first_name: str) -> str:
	return (
		frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": first_name,
				"last_name": "Contract",
				"gender": "Other",
				"date_of_birth": add_days(today(), -12000),
				"date_of_joining": today(),
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


def _flat_commission_rule(employee: str, rate: float = 5.0) -> str:
	doc = frappe.new_doc("Commission Rule")
	doc.rule_name = f"QW5 {employee}"
	doc.calculation_type = "Flat Rate"
	doc.flat_rate = rate
	doc.employee = employee
	doc.insert(ignore_permissions=True)
	return doc.name


@erpnext_required
class TestProfitContracts(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		cls.employee = _create_test_employee("Qw5Contract")
		_flat_commission_rule(cls.employee)
		cls.customer = ensure_customer("QW5 Contract Customer")
		cls.warehouse = ensure_warehouse("QW5 Contract Warehouse", company=cls.company)
		cls.item = ensure_item("QW5-CONTRACT-001", "QW5 Contract Item", rate=1000.0)
		# Heatmap joins on these; create_recommendation reads custom_msrp as current price.
		frappe.db.set_value(
			"Item",
			cls.item,
			{"custom_jewelry_type": "Ring", "custom_metal_type": "Gold", "custom_msrp": 1000.0},
		)
		frappe.db.commit()  # nosemgrep

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_confidence_label_to_score(self):
		"""_confidence_to_score maps High/Medium/Low to a 0-100 number."""
		from zevar_core.api.profit_intelligence import _confidence_to_score

		self.assertEqual(_confidence_to_score("High"), 90)
		self.assertEqual(_confidence_to_score("medium"), 70)
		self.assertEqual(_confidence_to_score("LOW"), 50)
		self.assertEqual(_confidence_to_score(None), 0)
		self.assertEqual(_confidence_to_score(""), 0)

	def test_create_recommendation_creates_record(self):
		"""create_recommendation (was 404) now creates a Pricing Recommendation."""
		from zevar_core.api.profit_intelligence import create_recommendation

		result = create_recommendation(
			item_code=self.item,
			new_price=1200.0,
			simulation_data=json.dumps({"margin_pct": 55.0}),
		)
		self.assertTrue(result.get("success"))
		name = result["name"]

		rec = frappe.db.get_value(
			"Pricing Recommendation",
			name,
			["recommended_price", "price_change_pct", "projected_margin_pct", "status"],
			as_dict=True,
		)
		self.assertEqual(flt(rec.recommended_price), 1200.0)
		self.assertEqual(flt(rec.price_change_pct, 1), 20.0)  # (1200-1000)/1000
		self.assertEqual(flt(rec.projected_margin_pct, 1), 55.0)
		self.assertEqual(rec.status, "Pending Review")

	def test_get_recommendations_has_numeric_confidence(self):
		"""The UI badge reads `confidence` as a number, not the High/Medium/Low string."""
		from zevar_core.api.profit_intelligence import create_recommendation, get_recommendations

		name = create_recommendation(item_code=self.item, new_price=1100.0)["name"]
		recs = get_recommendations(status="Pending Review")["recommendations"]
		mine = [r for r in recs if r["name"] == name]
		self.assertEqual(len(mine), 1)
		self.assertIsInstance(mine[0]["confidence"], (int, float))

	def test_review_recommendation_accepts_ui_casing(self):
		"""UI sends 'Approved'/'Rejected' (Pascal, past-tense); backend must accept it."""
		from zevar_core.api.profit_intelligence import create_recommendation, review_recommendation

		# approve path (auto-applies the price)
		rec1 = create_recommendation(item_code=self.item, new_price=1300.0)["name"]
		approved = review_recommendation(rec1, "Approved")
		self.assertEqual(approved["status"], "Applied")
		self.assertEqual(flt(frappe.db.get_value("Item", self.item, "custom_msrp")), 1300.0)

		# reject path
		rec2 = create_recommendation(item_code=self.item, new_price=900.0)["name"]
		rejected = review_recommendation(rec2, "Rejected", notes="nope")
		self.assertEqual(rejected["status"], "Rejected")

		# lower-case present-tense still works
		rec3 = create_recommendation(item_code=self.item, new_price=950.0)["name"]
		rejected2 = review_recommendation(rec3, "reject")
		self.assertEqual(rejected2["status"], "Rejected")

	def test_get_margin_heatmap_is_pivoted_array(self):
		"""Heatmap returns an array of {jewelry_type, margins:{metal:{margin_pct}}}, not a flat list."""
		from zevar_core.api.profit_intelligence import get_margin_heatmap

		# seed an SCB via a submitted POS invoice for the Ring/Gold item
		from zevar_core.api.pos import create_pos_invoice  # noqa: F401  (ensures import path)

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Receipt"
		se.company = self.company
		se.append(
			"items",
			{
				"item_code": self.item,
				"t_warehouse": self.warehouse,
				"qty": 5,
				"basic_rate": 1000.0,
				"conversion_factor": 1.0,
				"stock_uom": "Nos",
				"uom": "Nos",
			},
		)
		se.insert(ignore_permissions=True)
		se.submit()

		si = frappe.new_doc("Sales Invoice")
		si.customer = self.customer
		si.company = self.company
		si.is_pos = 1
		si.update_stock = 1
		si.set_warehouse = self.warehouse
		si.posting_date = today()
		si.due_date = today()
		si.append("items", {"item_code": self.item, "qty": 1, "rate": 1000.0, "warehouse": self.warehouse})
		si.append("payments", {"mode_of_payment": "Cash", "amount": 1000.0})
		si.append("custom_salesperson_splits", {"employee": self.employee, "split_percent": 100})
		si.insert(ignore_permissions=True)
		si.submit()

		hm = get_margin_heatmap()
		self.assertIsInstance(hm, list)
		ring = next((r for r in hm if r.get("jewelry_type") == "Ring"), None)
		self.assertIsNotNone(ring)
		self.assertIn("Gold", ring["margins"])
		self.assertIn("margin_pct", ring["margins"]["Gold"])
