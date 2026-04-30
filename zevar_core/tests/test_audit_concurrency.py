"""Tests for Feature 2 — Audit Concurrency.

Covers:
- Two users scanning the same session simultaneously
- Both scans accepted
- No duplicate check-off
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.api.inventory_audit import finalize_audit, start_audit, submit_scan


class TestAuditConcurrency(FrappeTestCase):
	def setUp(self):
		frappe.db.sql("DELETE FROM `tabCase Audit Session`")
		frappe.db.sql("DELETE FROM `tabCase Audit Scan`")

		self.warehouse = "Stores - ZJ"
		self.company = "Zevar Jewelers"

		# Create test items
		self.items = []
		for i in range(10):
			item_code = f"TEST-CONC-ITEM-{i}"
			if not frappe.db.exists("Item", item_code):
				doc = frappe.new_doc("Item")
				doc.item_code = item_code
				doc.item_name = f"Test Conc Item {i}"
				doc.item_group = "Products"
				doc.is_stock_item = 1
				doc.stock_uom = "Nos"
				doc.custom_rfid_epc = f"CONC-EPC-{i}"
				doc.standard_rate = 100.0
				doc.insert(ignore_permissions=True)
			else:
				frappe.db.set_value(
					"Item",
					item_code,
					{
						"custom_rfid_epc": f"CONC-EPC-{i}",
						"standard_rate": 100.0,
					},
				)
			self.items.append(item_code)

		# Add stock
		if not frappe.db.exists("Stock Entry", {"purpose": "Material Receipt", "remarks": "Test Conc Stock"}):
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Receipt"
			se.purpose = "Material Receipt"
			se.company = self.company
			se.remarks = "Test Conc Stock"
			for item in self.items:
				se.append("items", {"item_code": item, "qty": 1, "t_warehouse": self.warehouse})
			se.insert(ignore_permissions=True)
			se.submit()

	def test_two_users_same_session(self):
		"""Two users can scan different items in the same session simultaneously."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# User A scans items 0-4
		results_a = []
		for i in range(5):
			result = submit_scan(session_name, f"CONC-EPC-{i}")
			results_a.append(result)

		# User B scans items 5-9
		results_b = []
		for i in range(5, 10):
			result = submit_scan(session_name, f"CONC-EPC-{i}")
			results_b.append(result)

		# All scans should be successful and matched
		for r in results_a:
			self.assertTrue(r["success"])
			self.assertEqual(r["match_status"], "Matched")

		for r in results_b:
			self.assertTrue(r["success"])
			self.assertEqual(r["match_status"], "Matched")

		# Total scanned count should be 10
		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.scanned_count, 10)

	def test_no_duplicate_check_off(self):
		"""Same barcode scanned by two users should not create duplicates."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# User A scans item 0
		result_a = submit_scan(session_name, "CONC-EPC-0")
		self.assertEqual(result_a["match_status"], "Matched")

		# User B also scans item 0 (same EPC)
		result_b = submit_scan(session_name, "CONC-EPC-0")
		self.assertEqual(result_b["match_status"], "Duplicate")

		# Scanned count should be 1 (not 2)
		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.scanned_count, 1)

	def test_interleaved_scans(self):
		"""Interleaved scans from multiple items should all be accepted."""
		start_res = start_audit(self.warehouse, scope="Spot")
		session_name = start_res["session_name"]

		# Interleave scans: A0, B5, A1, B6, A2, B7
		pairs = [(0, 5), (1, 6), (2, 7)]
		for a, b in pairs:
			result_a = submit_scan(session_name, f"CONC-EPC-{a}")
			result_b = submit_scan(session_name, f"CONC-EPC-{b}")
			self.assertEqual(result_a["match_status"], "Matched")
			self.assertEqual(result_b["match_status"], "Matched")

		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.scanned_count, 6)

		# Finalize should reconcile cleanly since we scanned 6 of 10
		final_res = finalize_audit(session_name)
		self.assertTrue(final_res["success"])
		self.assertGreater(final_res["missing_count"], 0)
