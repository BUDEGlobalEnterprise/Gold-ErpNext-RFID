# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

import json
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from zevar_core.tests.utils import (
	ensure_customer,
	ensure_pos_profile,
	ensure_warehouse,
	get_test_company,
)
from zevar_core.api.pos_session import submit_blind_close_step1, submit_blind_close_step2


class TestBlindCloseFlow(FrappeTestCase):
	"""Test suite for Step 1 and Step 2 of the Blind Close EOD workflow."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		cls.company = get_test_company()
		cls.warehouse = ensure_warehouse("Zevar E2E Warehouse", cls.company)
		cls.customer = ensure_customer("Zevar E2E Customer")
		cls.pos_profile = ensure_pos_profile(
			profile_name="Zevar E2E Profile",
			warehouse_name="Zevar E2E Warehouse",
		)
		# Enable manager threshold customization in POS Profile
		frappe.db.set_value(
			"POS Profile",
			cls.pos_profile,
			"custom_variance_alert_threshold",
			10.0,
		)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		# Clear any existing open session for this user to bypass "Cashier is currently assigned to another POS"
		frappe.db.delete("POS Opening Entry", {"user": frappe.session.user, "status": "Open"})
		frappe.db.commit()
		# Create a clean open session
		self.session_name = self._open_test_session()

	def tearDown(self):
		# Clean up any POS Opening Entries and Audit Logs
		frappe.db.delete("POS Opening Entry", {"name": self.session_name})
		frappe.db.delete("POS Audit Log", {"reference_document": self.session_name})
		frappe.db.commit()

	def _open_test_session(self) -> str:
		"""Create and submit a POS Opening Entry session."""
		from frappe.utils import now_datetime
		session = frappe.new_doc("POS Opening Entry")
		session.pos_profile = self.pos_profile
		session.company = self.company
		session.user = frappe.session.user
		session.posting_date = today()
		session.period_start_date = now_datetime()
		session.append("balance_details", {"mode_of_payment": "Cash", "opening_amount": 150.0})
		session.insert(ignore_permissions=True)
		session.submit()
		return session.name

	def _get_test_expected_cash(self) -> float:
		"""Calculate the exact server-side expected balance for this session."""
		start_date = today()
		payments = frappe.db.sql(
			"""
			SELECT SUM(sip.amount) as amount
			FROM `tabSales Invoice Payment` sip
			JOIN `tabSales Invoice` si ON sip.parent = si.name
			WHERE si.owner = %s
			AND si.docstatus = 1
			AND si.posting_date >= %s
			""",
			(frappe.session.user, start_date),
		)[0][0] or 0.0
		# POS Profile default custom_fixed_opening_float is 300.0
		return 300.0 + flt(payments)

	def test_submit_blind_close_step1_seals_count(self):
		"""Test that Step 1 successfully registers and seals physical count inside POS Audit Log details."""
		expected_cash = self._get_test_expected_cash()

		# Submitting physical count blindly
		result = submit_blind_close_step1(
			session_name=self.session_name,
			total_cash_counted=expected_cash,
			breakdown=[{"denomination": 100, "count": int(expected_cash // 100)}],
			notes="Exact match",
		)
		self.assertTrue(result["success"])
		self.assertEqual(result["closing_balance"], expected_cash)
		self.assertEqual(result["variance"], 0.0)
		self.assertEqual(result["variance_status"], "balanced")

		# Check that a POS Audit Log entry was created with details and event_type "blind_close_step1"
		audit_logs = frappe.get_all(
			"POS Audit Log",
			filters={
				"event_type": "blind_close_step1",
				"reference_document": self.session_name,
				"user": frappe.session.user,
			},
			fields=["name", "details"],
		)
		self.assertEqual(len(audit_logs), 1)
		details = frappe.parse_json(audit_logs[0].details)
		self.assertEqual(details.get("total_counted"), expected_cash)
		self.assertEqual(details.get("variance"), 0.0)

	def test_submit_blind_close_step2_without_variance(self):
		"""Test that Step 2 successfully closes the session and creates a finalized audit log when variance is zero."""
		expected_cash = self._get_test_expected_cash()

		# Step 1: Seal the count
		submit_blind_close_step1(
			session_name=self.session_name,
			total_cash_counted=expected_cash,
			breakdown=[{"denomination": 100, "count": int(expected_cash // 100)}],
			notes="No variance",
		)

		# Step 2: Finalize closing without any reason code (since variance is 0.0)
		result = submit_blind_close_step2(
			session_name=self.session_name,
			variance_reason_code="",
			notes="Closing session cleanly",
		)
		self.assertTrue(result["success"])
		self.assertEqual(result["closing_balance"], expected_cash)
		self.assertEqual(result["variance"], 0.0)

		# Verify that the opening entry status is updated to Closed
		status = frappe.db.get_value("POS Opening Entry", self.session_name, "status")
		self.assertEqual(status, "Closed")

		# Verify that the final audit log entry exists
		final_logs = frappe.get_all(
			"POS Audit Log",
			filters={
				"event_type": "blind_close_sealed_final",
				"reference_document": result["closing_entry"],
			},
		)
		self.assertEqual(len(final_logs), 1)

	def test_submit_blind_close_requires_variance_reason_for_mismatch(self):
		"""Test that Step 2 requires a reason code if there is cash variance."""
		expected_cash = self._get_test_expected_cash()

		# Step 1: Seal with mismatch (variance is non-zero)
		submit_blind_close_step1(
			session_name=self.session_name,
			total_cash_counted=expected_cash + 5.0, # $5 excess
			breakdown=[],
			notes="With variance",
		)

		# Step 2: Finalizing without reason code should throw ValidationError
		with self.assertRaises(frappe.ValidationError):
			submit_blind_close_step2(
				session_name=self.session_name,
				variance_reason_code="", # Empty reason code
				notes="Closing with discrepancy",
			)

		# Finalizing with a valid reason code (variance $5 is <= threshold $10) should succeed
		result = submit_blind_close_step2(
			session_name=self.session_name,
			variance_reason_code="Counting Error",
			notes="Closing with discrepancy",
		)
		self.assertTrue(result["success"])

	def test_session_reporting_apis(self):
		"""Test the new and enhanced session reporting and activity endpoints."""
		from zevar_core.api.pos_session import (
			get_session_payment_breakdown,
			get_session_layaway_activity,
			get_session_repair_activity,
			get_session_sales,
			get_session_status,
		)

		# 1. Get Session Status
		status_res = get_session_status()
		self.assertTrue(status_res.get("has_active_session"))
		session_data = status_res.get("session", {})
		self.assertEqual(session_data.get("name"), self.session_name)
		self.assertEqual(session_data.get("status"), "Open")
		self.assertIn("non_cash_payments", session_data)
		self.assertIn("non_cash_total", session_data)
		self.assertIn("layaway_count", session_data)
		self.assertIn("repair_count", session_data)

		# 2. Get Payment Breakdown
		pb_res = get_session_payment_breakdown(self.session_name)
		self.assertEqual(pb_res.get("session_name"), self.session_name)
		self.assertIn("payment_modes", pb_res)
		self.assertIn("cash_total", pb_res)
		self.assertIn("non_cash_total", pb_res)
		self.assertIn("layaway_payments", pb_res)
		self.assertIn("layaway_total", pb_res)
		self.assertIn("repair_invoices", pb_res)
		self.assertIn("repair_total", pb_res)

		# 3. Get Layaway Activity
		layaway_res = get_session_layaway_activity(self.session_name)
		self.assertEqual(layaway_res.get("session_name"), self.session_name)
		self.assertIn("new_contracts", layaway_res)
		self.assertIn("payments_received", layaway_res)
		self.assertIn("layaway_invoices", layaway_res)

		# 4. Get Repair Activity
		repair_res = get_session_repair_activity(self.session_name)
		self.assertEqual(repair_res.get("session_name"), self.session_name)
		self.assertIn("repairs_with_invoice", repair_res)
		self.assertIn("repair_count", repair_res)
		self.assertIn("total_repair_revenue", repair_res)

		# 5. Get Sales (enhanced)
		sales_res = get_session_sales(self.session_name)
		self.assertEqual(sales_res.get("session_name"), self.session_name)
		self.assertIn("sales", sales_res)
		self.assertIn("total_amount", sales_res)
		self.assertIn("payment_mode_totals", sales_res)
		self.assertIn("layaway_sales_count", sales_res)
		self.assertIn("repair_sales_count", sales_res)


def run_manual_test():
	import unittest
	suite = unittest.TestLoader().loadTestsFromTestCase(TestBlindCloseFlow)
	runner = unittest.TextTestRunner(verbosity=2)
	runner.run(suite)
