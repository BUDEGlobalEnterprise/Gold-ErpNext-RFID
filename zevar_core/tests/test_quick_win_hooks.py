"""
Quick-Win Sprint (Q1–Q5) — data-integrity tests.

Q1/Q2 wiring: Sales Invoice on_submit must create
  - a Sale Cost Breakdown (profit spine)
  - a "Sale Completed" Performance Log per salesperson (workforce revenue axis)
and on_cancel must clean them up (and create a "Return Processed" log).

These tests exercise the real doc_event hook path through ``create_pos_invoice``.
They are written to run under the standard Frappe test runner (fresh ``test_site``);
locally they require a site where ERPNext master data can be created.
"""

import json
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today

from zevar_core.tests.utils import (
	ensure_customer,
	ensure_item,
	ensure_warehouse,
)

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required (Sales Invoice DocType not found)",
)


def _create_test_employee(first_name: str, last_name: str) -> str:
	employee = frappe.get_doc(
		{
			"doctype": "Employee",
			"first_name": first_name,
			"last_name": last_name,
			"gender": "Other",
			"date_of_birth": add_days(today(), -12000),
			"date_of_joining": today(),
		}
	).insert(ignore_permissions=True)
	return employee.name


def _create_flat_commission_rule(employee: str, rate: float = 5.0) -> str:
	doc = frappe.new_doc("Commission Rule")
	doc.rule_name = f"QW Flat {employee}"
	doc.calculation_type = "Flat Rate"
	doc.flat_rate = rate
	doc.employee = employee
	doc.insert(ignore_permissions=True)
	return doc.name


@erpnext_required
class TestQuickWinHooks(FrappeTestCase):
	"""Q1 (SCB) + Q2 (Performance Log) submit/cancel lifecycle."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		cls.employee_id = _create_test_employee("QwSubmit", "Test")
		_create_flat_commission_rule(cls.employee_id, rate=5.0)
		cls.customer = ensure_customer("QW Hooks Customer")
		cls.warehouse = ensure_warehouse("QW Hooks Warehouse", company=cls.company)
		cls.item = ensure_item("QW-HOOKS-001", "QW Hooks Test Item", rate=1000.0)
		frappe.db.commit()  # nosemgrep

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def _make_pos_invoice(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1000.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			tax_exempt=True,
		)
		self.assertTrue(result.get("success"), f"POS invoice creation failed: {result}")
		return result["invoice_name"]

	# ---- Q1 + Q2: on_submit ----
	def test_scb_created_on_submit(self):
		"""Q1: Sale Cost Breakdown is created when a POS invoice is submitted."""
		inv = self._make_pos_invoice()

		scb = frappe.db.get_value(
			"Sale Cost Breakdown",
			{"sales_invoice": inv},
			["name", "total_revenue", "gross_profit", "gross_margin_pct"],
			as_dict=True,
		)
		self.assertIsNotNone(scb, "Sale Cost Breakdown was not created on submit")
		self.assertEqual(flt(scb.total_revenue, 2), 1000.0)

	def test_performance_log_created_on_submit(self):
		"""Q2: a 'Sale Completed' Performance Log is created for the salesperson."""
		inv = self._make_pos_invoice()

		logs = frappe.get_all(
			"Performance Log",
			filters={
				"employee": self.employee_id,
				"event_type": "Sale Completed",
				"reference_document": inv,
			},
			fields=["revenue_amount", "commission_amount"],
		)
		self.assertEqual(len(logs), 1, "Expected exactly one 'Sale Completed' Performance Log")
		self.assertGreater(flt(logs[0].revenue_amount), 0)
		# commission was calculated by the commission hook before log_sale_event ran
		self.assertEqual(flt(logs[0].commission_amount, 2), 50.0)

	# ---- Q1 + Q2 + reverse_commissions: on_cancel ----
	def test_cancel_cleans_scb_and_commission_and_logs_return(self):
		"""On cancel: SCB + commission splits removed; a 'Return Processed' log is added."""
		inv = self._make_pos_invoice()
		# sanity: created on submit
		self.assertTrue(frappe.db.exists("Sale Cost Breakdown", {"sales_invoice": inv}))
		self.assertTrue(
			frappe.db.exists(
				"Sales Commission Split", {"sales_invoice": inv, "employee": self.employee_id}
			)
		)

		frappe.get_doc("Sales Invoice", inv).cancel()

		# Q1: SCB removed
		self.assertFalse(
			frappe.db.exists("Sale Cost Breakdown", {"sales_invoice": inv}),
			"SCB should be deleted on cancel",
		)
		# reverse_commissions: commission split removed
		self.assertFalse(
			frappe.db.exists("Sales Commission Split", {"sales_invoice": inv}),
			"Commission split should be deleted on cancel (reverse_commissions)",
		)
		# Q2: a 'Return Processed' Performance Log with negative revenue
		return_logs = frappe.get_all(
			"Performance Log",
			filters={
				"employee": self.employee_id,
				"event_type": "Return Processed",
				"reference_document": inv,
			},
			fields=["revenue_amount"],
		)
		self.assertEqual(len(return_logs), 1, "Expected a 'Return Processed' Performance Log")
		self.assertLess(flt(return_logs[0].revenue_amount), 0)
