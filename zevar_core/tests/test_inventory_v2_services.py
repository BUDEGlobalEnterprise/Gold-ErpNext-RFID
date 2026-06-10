"""Tests for Inventory v2 service layer.

Validates core business logic for BOM, gemstones, memo lifecycle,
and appraisal services.

Run: bench --site <site> run-tests --app zevar_core --test zevar_core.tests.test_inventory_v2_services
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_months, nowdate


class TestBOMService(FrappeTestCase):
	def test_get_bom_cost_rollup_empty_bom(self):
		"""Cost rollup on empty BOM should return zeros."""
		from zevar_core.services.bom_service import get_bom_cost_rollup

		# Create a minimal BOM doc
		bom = frappe.get_doc(
			{
				"doctype": "Jewelry BOM",
				"bom_name": f"Test BOM {frappe.generate_hash(length=6)}",
				"parent_item_code": "TEST-ITEM",
				"is_active": 1,
				"yield_qty": 1,
			}
		)
		bom.insert(ignore_permissions=True)
		self.addCleanup(frappe.delete_doc, "Jewelry BOM", bom.name, force=True)

		result = get_bom_cost_rollup(bom.name)
		self.assertEqual(result["material_total"], 0)
		self.assertEqual(result["labor_cost"], 0)
		self.assertEqual(result["grand_total"], 0)


class TestMemoLifecycleService(FrappeTestCase):
	def test_create_memo_requires_customer_for_customer_memo(self):
		"""Customer memos must have a customer."""
		from zevar_core.services.memo_lifecycle_service import create_memo

		with self.assertRaises(frappe.ValidationError):
			create_memo(memo_class="Customer", items=[], customer=None)

	def test_create_memo_requires_vendor_for_vendor_memo(self):
		"""Vendor memos must have a vendor."""
		from zevar_core.services.memo_lifecycle_service import create_memo

		with self.assertRaises(frappe.ValidationError):
			create_memo(memo_class="Vendor", items=[], vendor=None)

	def test_invalid_memo_class_rejected(self):
		"""Only 'Vendor' and 'Customer' classes allowed."""
		from zevar_core.services.memo_lifecycle_service import create_memo

		with self.assertRaises(frappe.ValidationError):
			create_memo(memo_class="Invalid", items=[])


class TestAppraisalService(FrappeTestCase):
	def test_appraisal_history_returns_list(self):
		"""History for non-existent item returns empty list."""
		from zevar_core.services.appraisal_service import get_appraisal_history

		result = get_appraisal_history("NONEXISTENT-ITEM-12345")
		self.assertIsInstance(result, list)
		self.assertEqual(len(result), 0)


class TestExternalBenchService(FrappeTestCase):
	def test_get_overdue_empty(self):
		"""No overdue repairs should return empty list."""
		from zevar_core.services.external_bench_service import get_overdue_bench_repairs

		result = get_overdue_bench_repairs(days_threshold=14)
		self.assertIsInstance(result, list)


class TestInventoryLocking(FrappeTestCase):
	def test_check_unlocked_serial_returns_none(self):
		"""An unlocked serial should return None."""
		from zevar_core.services.inventory_locking import check_serial_locked

		result = check_serial_locked("NONEXISTENT-SN-12345")
		self.assertIsNone(result)

	def test_release_nonexistent_lock_is_noop(self):
		"""Releasing a lock that doesn't exist should succeed."""
		from zevar_core.services.inventory_locking import release_serial_lock

		result = release_serial_lock("NONEXISTENT-SN-12345")
		self.assertTrue(result["success"])
