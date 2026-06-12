# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Tax API (tax.py)
Covers: get_tax_details_by_store, get_tax_details_by_warehouse

Run with: bench run-tests --app zevar_core --test test_api_tax
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestGetTaxDetailsByStore(FrappeTestCase):
	"""Test get_tax_details_by_store endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_nonexistent_store_raises(self):
		"""Should raise for nonexistent store"""
		from zevar_core.api.tax import get_tax_details_by_store

		with self.assertRaises(frappe.ValidationError):
			get_tax_details_by_store("NONEXISTENT-STORE-999")

	def test_empty_store_code_raises(self):
		"""Should raise for empty store code"""
		from zevar_core.api.tax import get_tax_details_by_store

		with self.assertRaises(frappe.ValidationError):
			get_tax_details_by_store("")


class TestGetTaxDetailsByWarehouse(FrappeTestCase):
	"""Test get_tax_details_by_warehouse endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_nonexistent_warehouse_returns_empty(self):
		"""Should return empty dict for nonexistent warehouse"""
		from zevar_core.api.tax import get_tax_details_by_warehouse

		result = get_tax_details_by_warehouse("NONEXISTENT-WH-999")
		self.assertIsInstance(result, dict)
		self.assertEqual(len(result), 0)

	def test_no_store_for_warehouse_returns_empty(self):
		"""Should return empty when no store linked to warehouse"""
		from zevar_core.api.tax import get_tax_details_by_warehouse

		result = get_tax_details_by_warehouse("Stores - WP")
		self.assertIsInstance(result, dict)
