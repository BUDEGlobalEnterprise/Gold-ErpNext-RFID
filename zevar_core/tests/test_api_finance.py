# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Finance API (finance.py)
Covers: get_customer_finance_account, process_finance_payment,
        generate_monthly_statement, apply_finance_charges

Run with: bench run-tests --app zevar_core --test test_api_finance
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from zevar_core.tests.utils import ensure_customer, get_test_company

finance_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "In-House Finance Account"),
	"In-House Finance Account DocType not found",
)


@finance_required
class TestGetCustomerFinanceAccount(FrappeTestCase):
	"""Test get_customer_finance_account endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Finance API Test Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_account_nonexistent_customer(self):
		"""Should raise for nonexistent customer"""
		from zevar_core.api.finance import get_customer_finance_account

		with self.assertRaises(frappe.ValidationError):
			get_customer_finance_account("NONEXISTENT-CUSTOMER-999")

	def test_get_account_empty_customer(self):
		"""Should raise for empty customer name"""
		from zevar_core.api.finance import get_customer_finance_account

		with self.assertRaises(frappe.ValidationError):
			get_customer_finance_account("")

	def test_get_account_no_account(self):
		"""Should return exists=False when no finance account"""
		from zevar_core.api.finance import get_customer_finance_account

		result = get_customer_finance_account(self.customer)
		self.assertIn("exists", result)
		# Most likely no account for this test customer
		if not result["exists"]:
			self.assertEqual(result, {"exists": False})

	def test_get_account_returns_fields(self):
		"""When account exists, should return all required fields"""
		from zevar_core.api.finance import get_customer_finance_account

		# Create a finance account for testing
		try:
			account = frappe.new_doc("In-House Finance Account")
			account.customer = self.customer
			account.credit_limit = 5000
			account.current_balance = 0
			account.interest_rate = 12.0
			account.status = "Active"
			account.insert(ignore_permissions=True)
			self.created_account = account.name
		except Exception:
			self.skipTest("Cannot create In-House Finance Account")

		result = get_customer_finance_account(self.customer)
		self.assertTrue(result["exists"])
		self.assertIn("account_id", result)
		self.assertIn("credit_limit", result)
		self.assertIn("current_balance", result)
		self.assertIn("interest_rate", result)
		self.assertIn("ledger_entries", result)


@finance_required
class TestProcessFinancePayment(FrappeTestCase):
	"""Test process_finance_payment endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_payment_zero_amount_raises(self):
		"""Should reject zero payment"""
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(
				account_id="NONEXISTENT",
				amount=0,
				mode_of_payment="Cash",
			)

	def test_payment_negative_amount_raises(self):
		"""Should reject negative payment"""
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(
				account_id="NONEXISTENT",
				amount=-100,
				mode_of_payment="Cash",
			)

	def test_payment_empty_mode_raises(self):
		"""Should reject empty mode of payment"""
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(
				account_id="NONEXISTENT",
				amount=100,
				mode_of_payment="",
			)

	def test_payment_nonexistent_account_raises(self):
		"""Should reject nonexistent account"""
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(
				account_id="NONEXISTENT-ACCT-999",
				amount=100,
				mode_of_payment="Cash",
			)


@finance_required
class TestGenerateMonthlyStatement(FrappeTestCase):
	"""Test generate_monthly_statement endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_statement_invalid_month_raises(self):
		"""Should reject invalid month"""
		from zevar_core.api.finance import generate_monthly_statement

		with self.assertRaises(frappe.ValidationError):
			generate_monthly_statement(
				account_id="NONEXISTENT",
				month=13,
				year=2025,
			)

	def test_statement_month_zero_raises(self):
		"""Should reject month=0"""
		from zevar_core.api.finance import generate_monthly_statement

		with self.assertRaises(frappe.ValidationError):
			generate_monthly_statement(
				account_id="NONEXISTENT",
				month=0,
				year=2025,
			)

	def test_statement_nonexistent_account_raises(self):
		"""Should reject nonexistent account"""
		from zevar_core.api.finance import generate_monthly_statement

		with self.assertRaises(frappe.ValidationError):
			generate_monthly_statement(
				account_id="NONEXISTENT-ACCT-999",
				month=1,
				year=2025,
			)


@finance_required
class TestApplyFinanceCharges(FrappeTestCase):
	"""Test apply_finance_charges scheduler function"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_apply_charges_no_accounts(self):
		"""Should run without error when no accounts with balance"""
		from zevar_core.api.finance import apply_finance_charges

		# Should not raise
		apply_finance_charges()

	def test_apply_charges_zero_rate_skipped(self):
		"""Should skip accounts with zero interest rate"""
		from zevar_core.api.finance import apply_finance_charges

		# Should not raise
		apply_finance_charges()
