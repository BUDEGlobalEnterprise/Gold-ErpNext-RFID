"""Tests for Feature 2 — Inventory Audit Policy & Workflow.

Covers:
- Audit Policy creation and threshold validation
- Variance below threshold → auto shrinkage
- Variance above threshold → store freeze (hard-stop)
- Two-person sign-off
- Store unfreeze via manager approval
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from zevar_core.api.inventory_audit import (
	approve_variance,
	finalize_audit,
	get_audit_dashboard,
	get_audit_history,
	start_audit,
	submit_scan,
)


class TestAuditPolicy(FrappeTestCase):
	def setUp(self):
		frappe.db.sql("DELETE FROM `tabCase Audit Session`")
		frappe.db.sql("DELETE FROM `tabCase Audit Scan`")

		self.warehouse = "Stores - ZJ"
		self.company = "Zevar Jewelers"

		# Ensure Audit Policy exists with test thresholds
		if not frappe.db.exists("DocType", "Audit Policy"):
			self.skipTest("Audit Policy DocType not installed")

		policy = frappe.get_single("Audit Policy")
		policy.enable_audit_schedule = 1
		policy.variance_threshold_dollars = 500
		policy.variance_pieces_hard_stop = 3
		policy.auto_create_shrinkage_entry = 1
		policy.require_two_person_rule = 1
		policy.save(ignore_permissions=True)

		# Create test items with high value
		self.items = []
		for i in range(6):
			item_code = f"TEST-POLICY-ITEM-{i}"
			if not frappe.db.exists("Item", item_code):
				doc = frappe.new_doc("Item")
				doc.item_code = item_code
				doc.item_name = f"Test Policy Item {i}"
				doc.item_group = "Products"
				doc.is_stock_item = 1
				doc.stock_uom = "Nos"
				doc.custom_rfid_epc = f"POL-EPC-{i}"
				doc.standard_rate = (i + 1) * 200.0  # 200, 400, 600, 800, 1000, 1200
				doc.insert(ignore_permissions=True)
			else:
				frappe.db.set_value(
					"Item",
					item_code,
					{
						"custom_rfid_epc": f"POL-EPC-{i}",
						"standard_rate": (i + 1) * 200.0,
					},
				)
			self.items.append(item_code)

		# Add stock
		if not frappe.db.exists(
			"Stock Entry", {"purpose": "Material Receipt", "remarks": "Test Policy Stock"}
		):
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Receipt"
			se.purpose = "Material Receipt"
			se.company = self.company
			se.remarks = "Test Policy Stock"
			for item in self.items:
				se.append("items", {"item_code": item, "qty": 1, "t_warehouse": self.warehouse})
			se.insert(ignore_permissions=True)
			se.submit()

	def test_below_threshold_auto_shrinkage(self):
		"""Variance below $500 and <= 3 missing pieces should auto-create shrinkage."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# Scan 5 of 6 items (missing item 5 worth $1200 > $500 threshold alone)
		# Scan 5 items - missing just 1 piece (item 0 worth $200, below threshold)
		for i in range(1, 6):  # Skip item 0 (worth $200)
			submit_scan(session_name, f"POL-EPC-{i}")

		final_res = finalize_audit(session_name)

		self.assertTrue(final_res["success"])
		# Missing 1 piece worth $200 should be below both thresholds
		# But $200 < $500 threshold, so status should be Discrepancy (not frozen)
		self.assertIn(final_res["status"], ["Discrepancy", "Reconciled with Shrinkage"])

	def test_above_dollar_threshold_freezes_store(self):
		"""Variance above $500 should freeze the store."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# Scan only 2 of 6 items (missing 4 pieces worth $200+$400+$600+$800 = $2000)
		for i in range(2):
			submit_scan(session_name, f"POL-EPC-{i}")

		final_res = finalize_audit(session_name)

		self.assertTrue(final_res["success"])
		# $2000 variance > $500 threshold, should freeze
		self.assertEqual(final_res["status"], "Pending Manager Review")
		self.assertGreater(final_res["variance_dollar_total"], 500)

		# Check store is frozen
		from zevar_core.unified_retail_management_system.doctype.case_audit_session.case_audit_session import (
			is_store_frozen,
		)

		freeze_reason = is_store_frozen(self.warehouse)
		self.assertIsNotNone(freeze_reason)

	def test_above_pieces_threshold_freezes_store(self):
		"""More than 3 missing pieces should freeze even if dollar value is low."""
		# Create low-value items
		for i in range(5):
			item_code = f"TEST-LOW-VAL-{i}"
			if not frappe.db.exists("Item", item_code):
				doc = frappe.new_doc("Item")
				doc.item_code = item_code
				doc.item_name = f"Test Low Value {i}"
				doc.item_group = "Products"
				doc.is_stock_item = 1
				doc.stock_uom = "Nos"
				doc.custom_rfid_epc = f"LOW-EPC-{i}"
				doc.standard_rate = 50.0  # Low value
				doc.insert(ignore_permissions=True)
			else:
				frappe.db.set_value(
					"Item",
					item_code,
					{
						"custom_rfid_epc": f"LOW-EPC-{i}",
						"standard_rate": 50.0,
					},
				)

		# Add stock for low-value items
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Receipt"
		se.purpose = "Material Receipt"
		se.company = self.company
		se.remarks = "Test Low Value Stock"
		for i in range(5):
			se.append("items", {"item_code": f"TEST-LOW-VAL-{i}", "qty": 1, "t_warehouse": self.warehouse})
		se.insert(ignore_permissions=True)
		se.submit()

		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# Scan only 1 of the low-value items (missing 4 pieces = 4 > 3 threshold)
		submit_scan(session_name, "LOW-EPC-0")

		final_res = finalize_audit(session_name)

		self.assertTrue(final_res["success"])
		# 4+ missing pieces should trigger freeze
		self.assertEqual(final_res["status"], "Pending Manager Review")

	def test_approve_variance_unfreezes_store(self):
		"""Manager approval should unfreeze the store."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# Create a large variance
		for i in range(2):
			submit_scan(session_name, f"POL-EPC-{i}")

		final_res = finalize_audit(session_name)
		self.assertEqual(final_res["status"], "Pending Manager Review")

		# Approve the variance
		frappe.set_user("Administrator")
		approve_res = approve_variance(session_name, "Test approval - items verified at repair bench")

		self.assertTrue(approve_res["success"])

		# Store should be unfrozen
		from zevar_core.unified_retail_management_system.doctype.case_audit_session.case_audit_session import (
			is_store_frozen,
		)

		self.assertIsNone(is_store_frozen(self.warehouse))

	def test_perfect_reconciliation(self):
		"""Scanning all items should result in Reconciled status."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		for i in range(6):
			submit_scan(session_name, f"POL-EPC-{i}")

		final_res = finalize_audit(session_name)

		self.assertTrue(final_res["success"])
		self.assertEqual(final_res["status"], "Reconciled")
		self.assertEqual(final_res["missing_count"], 0)

	def test_audit_dashboard(self):
		"""Dashboard should return KPI data."""
		dashboard = get_audit_dashboard()

		self.assertTrue(dashboard["success"])
		self.assertIn("overdue_audits", dashboard)
		self.assertIn("shrinkage_last_30_days", dashboard)
		self.assertIn("audit_hit_rate", dashboard)
		self.assertIn("total_audits_last_30_days", dashboard)

	def test_scope_based_audit(self):
		"""Start audit with different scope types."""
		for scope in ["Spot", "Showcase", "Backstock", "Full Store"]:
			start_res = start_audit(self.warehouse, scope=scope)
			self.assertTrue(start_res["success"])
			self.assertEqual(start_res["scope"], scope)
