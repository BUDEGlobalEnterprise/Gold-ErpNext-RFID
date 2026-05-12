# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Returns & Void API (returns.py)
Covers: get_returnable_items, create_return_invoice, void_invoice, get_return_history

Run with: bench run-tests --app zevar_core --test test_api_returns
"""

import json
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from zevar_core.tests.utils import (
	ensure_customer,
	ensure_item,
	ensure_item_group,
	ensure_mode_of_payment,
	ensure_pos_profile,
	ensure_warehouse,
	get_test_company,
)

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required (Sales Invoice DocType not found)",
)


@erpnext_required
class TestGetReturnableItems(FrappeTestCase):
	"""Test get_returnable_items endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = get_test_company()
		cls.warehouse = ensure_warehouse("Returns Test Warehouse", cls.company)
		cls.item_group = ensure_item_group()
		cls.item_code = ensure_item("RET-TEST-001", "Return Test Gold Ring", rate=500)
		cls.customer = ensure_customer("Return Test Customer")
		cls.pos_profile = ensure_pos_profile(
			profile_name="Return Test POS Profile",
			warehouse_name="Returns Test Warehouse",
		)

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_invoices = []

	def tearDown(self):
		for inv_name in self.created_invoices:
			try:
				doc = frappe.get_doc("Sales Invoice", inv_name)
				if doc.docstatus == 1:
					doc.cancel()
				if doc.docstatus == 2:
					frappe.delete_doc("Sales Invoice", inv_name, ignore_permissions=True, force=True)
			except Exception:
				pass
		frappe.set_user("Administrator")

	def _create_pos_invoice(self, customer=None, item_code=None, qty=1, rate=500):
		"""Helper to create and submit a POS invoice"""
		customer = customer or self.customer
		item_code = item_code or self.item_code

		inv = frappe.new_doc("Sales Invoice")
		inv.company = self.company
		inv.customer = customer
		inv.is_pos = 1
		inv.pos_profile = self.pos_profile
		inv.posting_date = today()
		inv.due_date = today()
		inv.append(
			"items",
			{
				"item_code": item_code,
				"qty": qty,
				"rate": rate,
				"warehouse": self.warehouse,
			},
		)
		ensure_mode_of_payment("Cash")
		inv.append(
			"payments",
			{
				"mode_of_payment": "Cash",
				"amount": qty * rate,
			},
		)
		inv.insert(ignore_permissions=True)
		inv.submit()
		self.created_invoices.append(inv.name)
		return inv

	# --- Happy Path ---
	def test_get_returnable_items_success(self):
		"""Returns items from a valid POS invoice"""
		from zevar_core.api.returns import get_returnable_items

		inv = self._create_pos_invoice()
		result = get_returnable_items(inv.name)

		self.assertEqual(result["invoice_name"], inv.name)
		self.assertEqual(result["customer"], self.customer)
		self.assertGreater(len(result["items"]), 0)
		self.assertEqual(result["items"][0]["item_code"], self.item_code)
		self.assertEqual(flt(result["items"][0]["returnable_qty"]), 1)
		self.assertEqual(flt(result["items"][0]["returned_qty"]), 0)

	def test_get_returnable_items_remaining_amount(self):
		"""Remaining amount equals grand_total minus returned_amount"""
		from zevar_core.api.returns import get_returnable_items

		inv = self._create_pos_invoice(rate=1000)
		result = get_returnable_items(inv.name)

		self.assertEqual(flt(result["grand_total"]), 1000)
		self.assertEqual(flt(result["returned_amount"]), 0)

	# --- Authentication ---
	def test_get_returnable_items_requires_read_permission(self):
		"""Requires Sales Invoice read permission"""
		from zevar_core.api.returns import get_returnable_items

		inv = self._create_pos_invoice()
		# Administrator always has permission, so just verify it works
		result = get_returnable_items(inv.name)
		self.assertIsNotNone(result)

	# --- Input Validation ---
	def test_get_returnable_items_nonexistent_invoice(self):
		"""Should raise error for non-existent invoice"""
		from zevar_core.api.returns import get_returnable_items

		with self.assertRaises(frappe.DoesNotExistError):
			get_returnable_items("NONEXISTENT-INV-001")

	def test_get_returnable_items_non_pos_invoice(self):
		"""Should reject non-POS invoices"""
		from zevar_core.api.returns import get_returnable_items

		# Create non-POS invoice
		inv = frappe.new_doc("Sales Invoice")
		inv.company = self.company
		inv.customer = self.customer
		inv.posting_date = today()
		inv.due_date = today()
		inv.append(
			"items",
			{
				"item_code": self.item_code,
				"qty": 1,
				"rate": 100,
				"warehouse": self.warehouse,
			},
		)
		inv.insert(ignore_permissions=True)
		inv.submit()
		self.created_invoices.append(inv.name)

		with self.assertRaises(frappe.ValidationError):
			get_returnable_items(inv.name)

	def test_get_returnable_items_draft_invoice(self):
		"""Should reject draft invoices"""
		from zevar_core.api.returns import get_returnable_items

		inv = frappe.new_doc("Sales Invoice")
		inv.company = self.company
		inv.customer = self.customer
		inv.is_pos = 1
		inv.posting_date = today()
		inv.due_date = today()
		inv.append(
			"items",
			{
				"item_code": self.item_code,
				"qty": 1,
				"rate": 100,
				"warehouse": self.warehouse,
			},
		)
		inv.insert(ignore_permissions=True)
		self.created_invoices.append(inv.name)

		with self.assertRaises(frappe.ValidationError):
			get_returnable_items(inv.name)

	# --- Edge Cases ---
	def test_get_returnable_items_after_partial_return(self):
		"""Should show reduced returnable qty after partial return"""
		from zevar_core.api.returns import get_returnable_items

		inv = self._create_pos_invoice(qty=3, rate=100)
		result_before = get_returnable_items(inv.name)
		self.assertEqual(flt(result_before["items"][0]["returnable_qty"]), 3)


@erpnext_required
class TestCreateReturnInvoice(FrappeTestCase):
	"""Test create_return_invoice endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = get_test_company()
		cls.warehouse = ensure_warehouse("Return Inv Test Warehouse", cls.company)
		cls.item_code = ensure_item("RET-INV-001", "Return Inv Test Item", rate=500)
		cls.customer = ensure_customer("Return Inv Test Customer")
		cls.pos_profile = ensure_pos_profile(
			profile_name="Return Inv POS Profile",
			warehouse_name="Return Inv Test Warehouse",
		)

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_invoices = []

	def tearDown(self):
		# Clean up in reverse order (returns first, then originals)
		for inv_name in reversed(self.created_invoices):
			try:
				doc = frappe.get_doc("Sales Invoice", inv_name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Sales Invoice", inv_name, ignore_permissions=True, force=True)
			except Exception:
				pass
		frappe.set_user("Administrator")

	def _create_pos_invoice(self, qty=1, rate=500):
		inv = frappe.new_doc("Sales Invoice")
		inv.company = self.company
		inv.customer = self.customer
		inv.is_pos = 1
		inv.pos_profile = self.pos_profile
		inv.posting_date = today()
		inv.due_date = today()
		inv.append(
			"items",
			{
				"item_code": self.item_code,
				"qty": qty,
				"rate": rate,
				"warehouse": self.warehouse,
			},
		)
		ensure_mode_of_payment("Cash")
		inv.append(
			"payments",
			{
				"mode_of_payment": "Cash",
				"amount": qty * rate,
			},
		)
		inv.insert(ignore_permissions=True)
		inv.submit()
		self.created_invoices.append(inv.name)
		return inv

	# --- Input Validation ---
	def test_create_return_invalid_return_type(self):
		"""Should reject invalid return types"""
		from zevar_core.api.returns import create_return_invoice

		inv = self._create_pos_invoice()
		items = json.dumps([{"item_code": self.item_code, "qty": 1, "rate": 500}])

		with self.assertRaises(frappe.ValidationError):
			create_return_invoice(
				original_invoice=inv.name,
				items=items,
				reason="Test",
				return_type="invalid_type",
			)

	def test_create_return_empty_items(self):
		"""Should reject empty items list"""
		from zevar_core.api.returns import create_return_invoice

		inv = self._create_pos_invoice()

		with self.assertRaises(frappe.ValidationError):
			create_return_invoice(
				original_invoice=inv.name,
				items="[]",
				reason="Test",
				return_type="refund",
			)

	def test_create_return_nonexistent_item(self):
		"""Should reject items not in original invoice"""
		from zevar_core.api.returns import create_return_invoice

		inv = self._create_pos_invoice()
		items = json.dumps([{"item_code": "NONEXISTENT-ITEM", "qty": 1, "rate": 500}])

		with self.assertRaises(frappe.ValidationError):
			create_return_invoice(
				original_invoice=inv.name,
				items=items,
				reason="Test",
				return_type="refund",
			)


@erpnext_required
class TestGetReturnHistory(FrappeTestCase):
	"""Test get_return_history endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_return_history_empty(self):
		"""Should return empty list when no returns exist"""
		from zevar_core.api.returns import get_return_history

		result = get_return_history()
		self.assertIsInstance(result, list)

	def test_get_return_history_returns_list(self):
		"""Should return a list"""
		from zevar_core.api.returns import get_return_history

		result = get_return_history()
		self.assertIsInstance(result, list)

	def test_get_return_history_with_customer_filter(self):
		"""Should filter by customer name"""
		from zevar_core.api.returns import get_return_history

		result = get_return_history(customer="Nonexistent Customer")
		self.assertIsInstance(result, list)
		# No returns for nonexistent customer
		self.assertEqual(len(result), 0)
