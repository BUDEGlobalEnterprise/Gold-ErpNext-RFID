# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Stock API (stock.py)
Covers: get_supplier_orders, get_supplier_order_detail, and stock endpoints

Run with: bench run-tests --app zevar_core --test test_api_stock
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Purchase Order"),
	"ERPNext required (Purchase Order DocType not found)",
)


@erpnext_required
class TestGetSupplierOrders(FrappeTestCase):
	"""Test get_supplier_orders endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_orders_returns_paginated(self):
		"""Should return paginated order list"""
		from zevar_core.api.stock import get_supplier_orders

		result = get_supplier_orders(page=1, page_size=5)
		self.assertTrue(result["success"])
		self.assertIn("orders", result)
		self.assertIn("total", result)
		self.assertEqual(result["page"], 1)

	def test_get_orders_page_size_capped(self):
		"""Page size should be capped at 100"""
		from zevar_core.api.stock import get_supplier_orders

		result = get_supplier_orders(page=1, page_size=999)
		self.assertLessEqual(result["page_size"], 100)

	def test_get_orders_negative_page_clamped(self):
		"""Negative page should be clamped to 1"""
		from zevar_core.api.stock import get_supplier_orders

		result = get_supplier_orders(page=-1, page_size=10)
		self.assertEqual(result["page"], 1)

	def test_get_orders_with_status_filter(self):
		"""Should filter by status"""
		from zevar_core.api.stock import get_supplier_orders

		result = get_supplier_orders(status="Completed")
		self.assertTrue(result["success"])
		for order in result["orders"]:
			self.assertEqual(order["status"], "Completed")


@erpnext_required
class TestGetSupplierOrderDetail(FrappeTestCase):
	"""Test get_supplier_order_detail endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_detail_nonexistent_raises(self):
		"""Should raise for nonexistent order"""
		from zevar_core.api.stock import get_supplier_order_detail

		with self.assertRaises(frappe.ValidationError):
			get_supplier_order_detail("NONEXISTENT-PO-99999")

	def test_get_detail_empty_name_raises(self):
		"""Should raise for empty name"""
		from zevar_core.api.stock import get_supplier_order_detail

		with self.assertRaises(frappe.ValidationError):
			get_supplier_order_detail("")
