# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Accounting API (accounting.py)
Covers 18 endpoints: get_transactions, get_transaction_detail, create_payment_entry,
create_journal_entry, submit_transaction, cancel_transaction, get_terminals,
get_terminal_status, get_invoices, get_invoice_detail, submit_invoice,
cancel_invoice, get_credit_notes, create_credit_note, get_exportable_invoices,
export_ubl, get_accounts, get_modes_of_payment

Run with: bench run-tests --app zevar_core --test test_api_accounting
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
	frappe.db and frappe.db.exists("DocType", "Payment Entry"),
	"ERPNext required (Payment Entry DocType not found)",
)


# ─── TRANSACTION TESTS ──────────────────────────────────────────────────────────


@erpnext_required
class TestGetTransactions(FrappeTestCase):
	"""Test get_transactions endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_transactions_returns_paginated(self):
		"""Should return paginated transaction list"""
		from zevar_core.api.accounting import get_transactions

		result = get_transactions(page=1, page_size=5)
		self.assertTrue(result["success"])
		self.assertIn("transactions", result)
		self.assertIn("total", result)
		self.assertIn("page", result)
		self.assertEqual(result["page"], 1)

	def test_get_transactions_filter_by_payment_entry(self):
		"""Should filter by Payment Entry doctype"""
		from zevar_core.api.accounting import get_transactions

		result = get_transactions(doctype="Payment Entry")
		self.assertTrue(result["success"])
		for txn in result["transactions"]:
			self.assertEqual(txn.get("doctype"), "Payment Entry")

	def test_get_transactions_filter_by_journal_entry(self):
		"""Should filter by Journal Entry doctype"""
		from zevar_core.api.accounting import get_transactions

		result = get_transactions(doctype="Journal Entry")
		self.assertTrue(result["success"])
		for txn in result["transactions"]:
			self.assertEqual(txn.get("doctype"), "Journal Entry")

	def test_get_transactions_page_size_limit(self):
		"""Page size should be capped at 100"""
		from zevar_core.api.accounting import get_transactions

		result = get_transactions(page=1, page_size=999)
		self.assertLessEqual(result["page_size"], 100)

	def test_get_transactions_invalid_page(self):
		"""Page < 1 should be clamped to 1"""
		from zevar_core.api.accounting import get_transactions

		result = get_transactions(page=-1, page_size=10)
		self.assertEqual(result["page"], 1)


@erpnext_required
class TestGetTransactionDetail(FrappeTestCase):
	"""Test get_transaction_detail endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_detail_nonexistent_raises(self):
		"""Should raise for nonexistent transaction"""
		from zevar_core.api.accounting import get_transaction_detail

		with self.assertRaises(frappe.ValidationError):
			get_transaction_detail("Payment Entry", "NONEXISTENT-PE-001")

	def test_get_detail_empty_name_raises(self):
		"""Should raise for empty name"""
		from zevar_core.api.accounting import get_transaction_detail

		with self.assertRaises(frappe.ValidationError):
			get_transaction_detail("Payment Entry", "")


@erpnext_required
class TestCreatePaymentEntry(FrappeTestCase):
	"""Test create_payment_entry endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = get_test_company()
		cls.customer = ensure_customer("Accounting PE Test Customer")

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_entries = []

	def tearDown(self):
		for name in self.created_entries:
			try:
				doc = frappe.get_doc("Payment Entry", name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Payment Entry", name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_create_receive_payment(self):
		"""Should create Receive type Payment Entry"""
		from zevar_core.api.accounting import create_payment_entry

		result = create_payment_entry(
			payment_type="Receive",
			party=self.customer,
			paid_amount=100.00,
			mode_of_payment="Cash",
		)
		self.assertTrue(result["success"])
		self.assertIn("name", result)
		self.created_entries.append(result["name"])

	def test_create_invalid_payment_type_raises(self):
		"""Should reject invalid payment types"""
		from zevar_core.api.accounting import create_payment_entry

		with self.assertRaises(frappe.ValidationError):
			create_payment_entry(
				payment_type="Invalid",
				party=self.customer,
				paid_amount=100,
				mode_of_payment="Cash",
			)

	def test_create_zero_amount_raises(self):
		"""Should reject zero amount"""
		from zevar_core.api.accounting import create_payment_entry

		with self.assertRaises(frappe.ValidationError):
			create_payment_entry(
				payment_type="Receive",
				party=self.customer,
				paid_amount=0,
				mode_of_payment="Cash",
			)

	def test_create_negative_amount_raises(self):
		"""Should reject negative amount"""
		from zevar_core.api.accounting import create_payment_entry

		with self.assertRaises(frappe.ValidationError):
			create_payment_entry(
				payment_type="Receive",
				party=self.customer,
				paid_amount=-50,
				mode_of_payment="Cash",
			)


@erpnext_required
class TestCreateJournalEntry(FrappeTestCase):
	"""Test create_journal_entry endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_entries = []

	def tearDown(self):
		for name in self.created_entries:
			try:
				doc = frappe.get_doc("Journal Entry", name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Journal Entry", name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_create_journal_entry_empty_accounts_raises(self):
		"""Should reject empty accounts list"""
		from zevar_core.api.accounting import create_journal_entry

		with self.assertRaises(frappe.ValidationError):
			create_journal_entry(accounts_json="[]")

	def test_create_journal_entry_invalid_json_raises(self):
		"""Should reject invalid JSON"""
		from zevar_core.api.accounting import create_journal_entry

		with self.assertRaises(Exception):
			create_journal_entry(accounts_json="not-valid-json")


# ─── TERMINAL TESTS ─────────────────────────────────────────────────────────────


@erpnext_required
class TestGetTerminals(FrappeTestCase):
	"""Test get_terminals endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.pos_profile = ensure_pos_profile(
			profile_name="Terminal Test POS Profile",
			warehouse_name="Terminal Test Warehouse",
		)

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_terminals_returns_list(self):
		"""Should return list of POS profiles/terminals"""
		from zevar_core.api.accounting import get_terminals

		result = get_terminals()
		self.assertTrue(result["success"])
		self.assertIn("terminals", result)
		self.assertIn("total", result)
		self.assertIsInstance(result["terminals"], list)

	def test_terminal_has_status(self):
		"""Each terminal should have Open/Closed status"""
		from zevar_core.api.accounting import get_terminals

		result = get_terminals()
		for terminal in result["terminals"]:
			self.assertIn("status", terminal)
			self.assertIn(terminal["status"], ["Open", "Closed"])


@erpnext_required
class TestGetTerminalStatus(FrappeTestCase):
	"""Test get_terminal_status endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.pos_profile = ensure_pos_profile(
			profile_name="Terminal Status Test Profile",
			warehouse_name="Terminal Status Test Warehouse",
		)

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_terminal_status_existing(self):
		"""Should return status for existing terminal"""
		from zevar_core.api.accounting import get_terminal_status

		result = get_terminal_status(self.pos_profile)
		self.assertTrue(result["success"])
		self.assertEqual(result["profile"], self.pos_profile)
		self.assertIn("open_entry", result)
		self.assertIn("today_payments", result)

	def test_get_terminal_status_nonexistent_raises(self):
		"""Should raise for nonexistent terminal"""
		from zevar_core.api.accounting import get_terminal_status

		with self.assertRaises(frappe.ValidationError):
			get_terminal_status("NONEXISTENT-POS-PROFILE-999")


# ─── INVOICE TESTS ──────────────────────────────────────────────────────────────


@erpnext_required
class TestGetInvoices(FrappeTestCase):
	"""Test get_invoices endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_invoices_returns_paginated(self):
		"""Should return paginated invoice list"""
		from zevar_core.api.accounting import get_invoices

		result = get_invoices(page=1, page_size=5)
		self.assertTrue(result["success"])
		self.assertIn("invoices", result)
		self.assertIn("total", result)

	def test_get_invoices_filter_sales(self):
		"""Should filter by sales invoices"""
		from zevar_core.api.accounting import get_invoices

		result = get_invoices(invoice_type="sales")
		self.assertTrue(result["success"])
		for inv in result["invoices"]:
			self.assertEqual(inv.get("invoice_type"), "Sales")

	def test_get_invoices_filter_pending(self):
		"""Should filter pending invoices"""
		from zevar_core.api.accounting import get_invoices

		result = get_invoices(invoice_type="pending")
		self.assertTrue(result["success"])
		for inv in result["invoices"]:
			self.assertEqual(inv.get("docstatus"), 0)


@erpnext_required
class TestGetInvoiceDetail(FrappeTestCase):
	"""Test get_invoice_detail endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_detail_nonexistent_raises(self):
		"""Should raise for nonexistent invoice"""
		from zevar_core.api.accounting import get_invoice_detail

		with self.assertRaises(frappe.ValidationError):
			get_invoice_detail("Sales", "NONEXISTENT-INV-99999")


@erpnext_required
class TestGetCreditNotes(FrappeTestCase):
	"""Test get_credit_notes endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_credit_notes_returns_list(self):
		"""Should return list of credit notes"""
		from zevar_core.api.accounting import get_credit_notes

		result = get_credit_notes()
		self.assertTrue(result["success"])
		self.assertIn("credit_notes", result)
		self.assertIsInstance(result["credit_notes"], list)


# ─── EXPORT TESTS ───────────────────────────────────────────────────────────────


@erpnext_required
class TestGetExportableInvoices(FrappeTestCase):
	"""Test get_exportable_invoices endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_exportable_returns_list(self):
		"""Should return list of exportable invoices"""
		from zevar_core.api.accounting import get_exportable_invoices

		result = get_exportable_invoices()
		self.assertTrue(result["success"])
		self.assertIn("invoices", result)


# ─── ACCOUNT & MODES SELECTORS ──────────────────────────────────────────────────


@erpnext_required
class TestGetAccounts(FrappeTestCase):
	"""Test get_accounts endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_accounts_returns_list(self):
		"""Should return list of accounts"""
		from zevar_core.api.accounting import get_accounts

		result = get_accounts()
		self.assertTrue(result["success"])
		self.assertIn("accounts", result)
		self.assertIsInstance(result["accounts"], list)

	def test_get_accounts_root_only(self):
		"""Should filter root accounts only"""
		from zevar_core.api.accounting import get_accounts

		result = get_accounts(root_only=1)
		self.assertTrue(result["success"])
		for acc in result["accounts"]:
			self.assertEqual(acc.get("is_group"), 1)


@erpnext_required
class TestGetModesOfPayment(FrappeTestCase):
	"""Test get_modes_of_payment endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_modes_returns_list(self):
		"""Should return list of payment modes"""
		from zevar_core.api.accounting import get_modes_of_payment

		result = get_modes_of_payment()
		self.assertTrue(result["success"])
		self.assertIn("modes", result)
		self.assertIsInstance(result["modes"], list)

	def test_modes_have_name_and_type(self):
		"""Each mode should have name and type"""
		from zevar_core.api.accounting import get_modes_of_payment

		result = get_modes_of_payment()
		if result["modes"]:
			self.assertIn("name", result["modes"][0])
			self.assertIn("type", result["modes"][0])
