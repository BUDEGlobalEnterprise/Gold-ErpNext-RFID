# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Export API (export.py)
Covers: export_sales_data, export_customer_data, export_inventory_data, schedule_backup

Run with: bench run-tests --app zevar_core --test test_api_export
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestExportSalesData(FrappeTestCase):
	"""Test export_sales_data endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_export_sales_returns_dict(self):
		"""Should return export result dict"""
		from zevar_core.api.export import export_sales_data

		result = export_sales_data()
		self.assertTrue(result["success"])
		self.assertIn("file_url", result)
		self.assertIn("record_count", result)

	def test_export_sales_with_date_range(self):
		"""Should accept date range"""
		from frappe.utils import add_days, today
		from zevar_core.api.export import export_sales_data

		result = export_sales_data(
			from_date=add_days(today(), -7),
			to_date=today(),
		)
		self.assertTrue(result["success"])


class TestExportCustomerData(FrappeTestCase):
	"""Test export_customer_data endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_export_customers_returns_dict(self):
		"""Should return export result dict"""
		from zevar_core.api.export import export_customer_data

		result = export_customer_data()
		self.assertTrue(result["success"])
		self.assertIn("file_url", result)
		self.assertIn("record_count", result)

	def test_export_customers_with_transactions(self):
		"""Should accept include_transactions flag"""
		from zevar_core.api.export import export_customer_data

		result = export_customer_data(include_transactions=True)
		self.assertTrue(result["success"])


class TestExportInventoryData(FrappeTestCase):
	"""Test export_inventory_data endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_export_inventory_returns_dict(self):
		"""Should return export result dict"""
		from zevar_core.api.export import export_inventory_data

		result = export_inventory_data()
		self.assertTrue(result["success"])
		self.assertIn("file_url", result)
		self.assertIn("record_count", result)
