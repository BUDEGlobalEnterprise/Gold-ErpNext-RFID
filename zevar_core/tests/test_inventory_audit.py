import json

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.api.inventory_audit import (
	batch_scan,
	cancel_audit,
	export_audit_results,
	finalize_audit,
	get_audit_history,
	get_audit_progress,
	start_audit,
	submit_scan,
)


class TestInventoryAudit(FrappeTestCase):
	def setUp(self):
		frappe.db.sql("DELETE FROM `tabCase Audit Session`")
		frappe.db.sql("DELETE FROM `tabCase Audit Scan`")

		self.warehouse = "Stores - ZJ"
		self.company = "Zevar Jewelers"

		# Create test items with RFID EPCs and valuation rates
		self.items = []
		for i in range(6):
			item_code = f"TEST-AUDIT-ITEM-{i}"
			if not frappe.db.exists("Item", item_code):
				doc = frappe.new_doc("Item")
				doc.item_code = item_code
				doc.item_name = f"Test Audit Item {i}"
				doc.item_group = "Products"
				doc.is_stock_item = 1
				doc.stock_uom = "Nos"
				doc.custom_rfid_epc = f"EPC-{i}"
				doc.standard_rate = (i + 1) * 100.0
				doc.insert(ignore_permissions=True)
			else:
				frappe.db.set_value("Item", item_code, "custom_rfid_epc", f"EPC-{i}")
			self.items.append(item_code)

		# Add stock via Material Receipt
		if not frappe.db.exists(
			"Stock Entry", {"purpose": "Material Receipt", "remarks": "Test Audit Stock"}
		):
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Receipt"
			se.purpose = "Material Receipt"
			se.company = self.company
			se.remarks = "Test Audit Stock"

			for item in self.items:
				se.append("items", {"item_code": item, "qty": 1, "t_warehouse": self.warehouse})

			se.insert(ignore_permissions=True)
			se.submit()

	def test_inventory_audit_workflow(self):
		"""Test basic audit lifecycle: start -> scan -> finalize."""
		start_res = start_audit(self.warehouse)
		self.assertTrue(start_res["success"])
		session_name = start_res["session_name"]

		self.assertGreaterEqual(start_res["expected_count"], 6)
		self.assertGreater(start_res["total_value_expected"], 0)

		# Scan 4 items via EPC
		for i in range(4):
			scan_res = submit_scan(session_name, f"EPC-{i}")
			self.assertTrue(scan_res["success"])
			self.assertEqual(scan_res["match_status"], "Matched")
			self.assertEqual(scan_res["item_code"], f"TEST-AUDIT-ITEM-{i}")
			self.assertIn("item_name", scan_res)
			self.assertIn("valuation_rate", scan_res)

		# Finalize audit
		final_res = finalize_audit(session_name)
		self.assertTrue(final_res["success"])
		self.assertEqual(final_res["status"], "Discrepancy")
		self.assertGreaterEqual(final_res["missing_count"], 2)

		# Should have created a shrinkage entry
		self.assertIsNotNone(final_res["shrinkage_entry"])

		se = frappe.get_doc("Stock Entry", final_res["shrinkage_entry"])
		self.assertEqual(se.stock_entry_type, "Material Issue")

		# EPC-4 and EPC-5 should be in the shrinkage entry
		found_4 = any(item.item_code == "TEST-AUDIT-ITEM-4" for item in se.items)
		found_5 = any(item.item_code == "TEST-AUDIT-ITEM-5" for item in se.items)
		self.assertTrue(found_4)
		self.assertTrue(found_5)

	def test_deduplication(self):
		"""Scanning the same barcode/EPC twice should return Duplicate."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		# First scan
		scan1 = submit_scan(session_name, "EPC-0")
		self.assertEqual(scan1["match_status"], "Matched")

		# Second scan of same EPC
		scan2 = submit_scan(session_name, "EPC-0")
		self.assertEqual(scan2["match_status"], "Duplicate")

		# Scanned count should still be 1
		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.scanned_count, 1)

	def test_batch_scan(self):
		"""Test RFID batch scan with multiple EPCs."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		epcs = [f"EPC-{i}" for i in range(5)]
		result = batch_scan(session_name, json.dumps(epcs))

		self.assertTrue(result["success"])
		self.assertEqual(result["total_submitted"], 5)
		self.assertEqual(result["duplicates_skipped"], 0)
		self.assertGreater(len(result["results"]), 0)

		# Verify scans were actually saved
		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.scanned_count, 5)
		self.assertEqual(session.audit_type, "RFID")

	def test_batch_scan_deduplication(self):
		"""Batch scan should skip already-scanned codes."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		# First batch of 3
		batch_scan(session_name, json.dumps(["EPC-0", "EPC-1", "EPC-2"]))

		# Second batch with 2 duplicates + 2 new
		result = batch_scan(session_name, json.dumps(["EPC-0", "EPC-1", "EPC-3", "EPC-4"]))

		self.assertEqual(result["duplicates_skipped"], 2)
		self.assertEqual(result["total_submitted"], 2)

		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.scanned_count, 5)

	def test_audit_progress(self):
		"""Test real-time progress endpoint."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		# Scan 3 of 6 items
		for i in range(3):
			submit_scan(session_name, f"EPC-{i}")

		progress = get_audit_progress(session_name)

		self.assertEqual(progress["counts"]["matched"], 3)
		self.assertEqual(progress["counts"]["unexpected"], 0)
		self.assertEqual(len(progress["recent_scans"]), 3)
		self.assertGreater(len(progress["missing_items"]), 0)

		# Verify missing items contain unscanned items
		missing_codes = [m["item_code"] for m in progress["missing_items"]]
		self.assertIn("TEST-AUDIT-ITEM-3", missing_codes)

	def test_audit_history(self):
		"""Test audit history listing."""
		# Create and finalize an audit
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]
		for i in range(6):
			submit_scan(session_name, f"EPC-{i}")
		finalize_audit(session_name)

		# Query history
		history = get_audit_history(page_size=10)

		self.assertTrue(history["success"])
		self.assertGreater(history["total"], 0)

		session = next((s for s in history["sessions"] if s["name"] == session_name), None)
		self.assertIsNotNone(session)
		self.assertEqual(session["status"], "Reconciled")

	def test_export_audit_results(self):
		"""Test CSV export."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]
		submit_scan(session_name, "EPC-0")
		submit_scan(session_name, "EPC-1")
		finalize_audit(session_name)

		result = export_audit_results(session_name)

		self.assertTrue(result["success"])
		self.assertIn(".csv", result["file_url"])
		self.assertIn("file_url", result)

	def test_cancel_audit(self):
		"""Test cancelling a draft audit."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		submit_scan(session_name, "EPC-0")

		result = cancel_audit(session_name)
		self.assertTrue(result["success"])
		self.assertEqual(result["status"], "Cancelled")

		session = frappe.get_doc("Case Audit Session", session_name)
		self.assertEqual(session.status, "Cancelled")
		self.assertIsNotNone(session.cancelled_at)

	def test_value_tracking(self):
		"""Test that value tracking computes correctly during finalize."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		# All items have standard_rate = (i+1)*100, total = 2100
		self.assertGreater(start_res["total_value_expected"], 0)

		# Scan all 6 items (should reconcile perfectly)
		for i in range(6):
			submit_scan(session_name, f"EPC-{i}")

		final_res = finalize_audit(session_name)

		self.assertEqual(final_res["status"], "Reconciled")
		self.assertEqual(final_res["missing_count"], 0)
		self.assertIsNone(final_res["shrinkage_entry"])

		# Values should match since all items were scanned
		self.assertEqual(final_res["total_value_expected"], final_res["total_value_scanned"])
		self.assertEqual(final_res["total_value_discrepancy"], 0)

	def test_reconciled_with_shrinkage(self):
		"""Test that missing items trigger shrinkage and discrepancy value."""
		start_res = start_audit(self.warehouse)
		session_name = start_res["session_name"]

		# Scan only 4 of 6
		for i in range(4):
			submit_scan(session_name, f"EPC-{i}")

		final_res = finalize_audit(session_name)

		self.assertEqual(final_res["status"], "Discrepancy")
		self.assertGreater(final_res["missing_count"], 0)
		self.assertIsNotNone(final_res["shrinkage_entry"])
		self.assertGreater(final_res["total_value_discrepancy"], 0)
