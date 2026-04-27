"""
Unit Tests for Layaway, In-House Finance, and POS Session Reconciliation

Covers:
- R13: Layaway payment, cancellation, and store credit generation
- R14: In-House Finance account payments, balance tracking, statements
- R7: POS session open/close with cash variance reconciliation
"""

import json
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, flt, today

from zevar_core.tests.utils import (
	ensure_customer,
	ensure_item,
	ensure_item_group,
	ensure_mode_of_payment,
	ensure_warehouse,
)

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required (Sales Invoice DocType not found)",
)


def _get_test_company():
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)


# ==========================================================================
# R13: LAYAWAY PAYMENT + CANCELLATION TESTS
# ==========================================================================


@erpnext_required
class TestLayawayCreation(FrappeTestCase):
	"""Test Layaway contract creation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = _get_test_company()
		cls.customer = ensure_customer("Layaway Test Cust")
		cls.warehouse = ensure_warehouse("Layaway Test WH", company=cls.company)
		cls.item = ensure_item("LAY-TEST-ITEM-01", "Layaway Test Gold Ring", rate=1000.0)
		ensure_mode_of_payment("Cash", payment_type="Cash")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def test_create_layaway_contract(self):
		from zevar_core.api.layaway import create_layaway

		result = create_layaway(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			deposit_amount=200.0,
			duration_months=3,
			warehouse=self.warehouse,
		)

		self.assertTrue(result["success"])
		self.assertIsNotNone(result["layaway_id"])

		doc = frappe.get_doc("Layaway Contract", result["layaway_id"])
		self.assertEqual(doc.status, "Active")
		self.assertEqual(flt(doc.total_amount), 1000.0)
		self.assertEqual(flt(doc.deposit_amount), 200.0)
		self.assertEqual(flt(doc.balance_amount), 800.0)
		self.assertEqual(len(doc.items), 1)

	def test_create_layaway_generates_payment_schedule(self):
		from zevar_core.api.layaway import create_layaway

		result = create_layaway(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			deposit_amount=200.0,
			duration_months=3,
			warehouse=self.warehouse,
		)

		doc = frappe.get_doc("Layaway Contract", result["layaway_id"])
		paid_entries = [s for s in doc.payment_schedule if s.status == "Paid"]
		pending_entries = [s for s in doc.payment_schedule if s.status == "Pending"]

		self.assertEqual(len(paid_entries), 1)
		self.assertEqual(flt(paid_entries[0].paid_amount), 200.0)
		self.assertEqual(len(pending_entries), 2)

	def test_create_layaway_invalid_duration(self):
		from zevar_core.api.layaway import create_layaway

		with self.assertRaises(frappe.ValidationError):
			create_layaway(
				customer=self.customer,
				items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
				deposit_amount=200.0,
				duration_months=5,
				warehouse=self.warehouse,
			)

	def test_create_layaway_deposit_exceeds_total(self):
		from zevar_core.api.layaway import create_layaway

		with self.assertRaises(frappe.ValidationError):
			create_layaway(
				customer=self.customer,
				items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
				deposit_amount=1000.0,
				duration_months=3,
				warehouse=self.warehouse,
			)

	def test_create_layaway_zero_deposit(self):
		from zevar_core.api.layaway import create_layaway

		with self.assertRaises(frappe.ValidationError):
			create_layaway(
				customer=self.customer,
				items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
				deposit_amount=0.0,
				duration_months=3,
				warehouse=self.warehouse,
			)

	def test_get_layaway_details(self):
		from zevar_core.api.layaway import create_layaway, get_layaway_details

		result = create_layaway(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			deposit_amount=200.0,
			duration_months=3,
			warehouse=self.warehouse,
		)

		details = get_layaway_details(result["layaway_id"])
		self.assertEqual(details["status"], "Active")
		self.assertEqual(flt(details["total_amount"]), 1000.0)
		self.assertEqual(len(details["items"]), 1)
		self.assertGreater(len(details["payment_schedule"]), 0)


@erpnext_required
class TestLayawayPayment(FrappeTestCase):
	"""Test Layaway payment processing."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = _get_test_company()
		cls.customer = ensure_customer("Layaway Pay Cust")
		cls.warehouse = ensure_warehouse("Layaway Pay WH", company=cls.company)
		cls.item = ensure_item("LAY-PAY-ITEM-01", "Layaway Pay Item", rate=1000.0)
		ensure_mode_of_payment("Cash", payment_type="Cash")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def _create_active_layaway(self):
		from zevar_core.api.layaway import create_layaway

		return create_layaway(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			deposit_amount=200.0,
			duration_months=3,
			warehouse=self.warehouse,
		)

	def test_partial_payment_reduces_balance(self):
		from zevar_core.api.layaway import process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		result = process_layaway_payment(lid, 300.0, "Cash")
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["new_balance"]), 500.0)
		self.assertEqual(result["status"], "Active")

	def test_full_payment_completes_layaway(self):
		from zevar_core.api.layaway import process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		result = process_layaway_payment(lid, 800.0, "Cash")
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["new_balance"]), 0.0)
		self.assertEqual(result["status"], "Completed")

	def test_payment_exceeds_balance_throws(self):
		from zevar_core.api.layaway import process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		with self.assertRaises(frappe.ValidationError):
			process_layaway_payment(lid, 900.0, "Cash")

	def test_zero_payment_throws(self):
		from zevar_core.api.layaway import process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		with self.assertRaises(frappe.ValidationError):
			process_layaway_payment(lid, 0.0, "Cash")

	def test_payment_on_completed_layaway_throws(self):
		from zevar_core.api.layaway import process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		process_layaway_payment(lid, 800.0, "Cash")

		with self.assertRaises(frappe.ValidationError):
			process_layaway_payment(lid, 100.0, "Cash")

	def test_multiple_incremental_payments(self):
		from zevar_core.api.layaway import process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		process_layaway_payment(lid, 200.0, "Cash")
		result = process_layaway_payment(lid, 200.0, "Cash")
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["new_balance"]), 400.0)

		result = process_layaway_payment(lid, 400.0, "Cash")
		self.assertEqual(result["status"], "Completed")


@erpnext_required
class TestLayawayCancellation(FrappeTestCase):
	"""Test Layaway cancellation and store credit generation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = _get_test_company()
		cls.customer = ensure_customer("Layaway Cancel Cust")
		cls.warehouse = ensure_warehouse("Layaway Cancel WH", company=cls.company)
		cls.item = ensure_item("LAY-CANCEL-ITEM-01", "Layaway Cancel Item", rate=1000.0)
		ensure_mode_of_payment("Cash", payment_type="Cash")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def _create_active_layaway(self):
		from zevar_core.api.layaway import create_layaway

		return create_layaway(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			deposit_amount=200.0,
			duration_months=3,
			warehouse=self.warehouse,
		)

	def test_cancel_generates_store_credit_gift_card(self):
		from zevar_core.api.layaway import cancel_layaway

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		result = cancel_layaway(lid)
		self.assertTrue(result["success"])
		self.assertIsNotNone(result["store_credit_id"])
		self.assertEqual(flt(result["amount_refunded"]), 180.0)

		gc = frappe.get_doc("Gift Card", result["store_credit_id"])
		self.assertEqual(gc.source, "Layaway Cancellation")
		self.assertEqual(flt(gc.balance), 180.0)
		self.assertEqual(gc.status, "Active")

	def test_cancel_updates_layaway_status(self):
		from zevar_core.api.layaway import cancel_layaway

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		cancel_layaway(lid)

		doc = frappe.get_doc("Layaway Contract", lid)
		self.assertEqual(doc.status, "Cancelled")
		self.assertIsNotNone(doc.store_credit_reference)

	def test_cancel_completed_layaway_throws(self):
		from zevar_core.api.layaway import cancel_layaway, process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		process_layaway_payment(lid, 800.0, "Cash")

		with self.assertRaises(frappe.ValidationError):
			cancel_layaway(lid)

	def test_cancel_already_cancelled_throws(self):
		from zevar_core.api.layaway import cancel_layaway

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		cancel_layaway(lid)

		with self.assertRaises(frappe.ValidationError):
			cancel_layaway(lid)

	def test_cancel_with_additional_payments_refunds_total(self):
		from zevar_core.api.layaway import cancel_layaway, process_layaway_payment

		layaway = self._create_active_layaway()
		lid = layaway["layaway_id"]

		process_layaway_payment(lid, 300.0, "Cash")

		result = cancel_layaway(lid)
		self.assertEqual(flt(result["amount_refunded"]), 480.0)

		gc = frappe.get_doc("Gift Card", result["store_credit_id"])
		self.assertEqual(flt(gc.balance), 480.0)


# ==========================================================================
# R14: IN-HOUSE FINANCE TESTS
# ==========================================================================


@erpnext_required
class TestFinanceAccountCreation(FrappeTestCase):
	"""Test In-House Finance Account creation and lookup."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Finance Test Cust")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def test_create_finance_account(self):
		doc = frappe.new_doc("In-House Finance Account")
		doc.customer = self.customer
		doc.status = "Active"
		doc.credit_limit = 5000.0
		doc.interest_rate = 12.0
		doc.minimum_payment_percent = 5.0
		doc.insert(ignore_permissions=True)

		self.assertTrue(frappe.db.exists("In-House Finance Account", doc.name))
		self.assertEqual(doc.status, "Active")
		self.assertEqual(flt(doc.credit_limit), 5000.0)

	def test_lookup_nonexistent_account(self):
		from zevar_core.api.finance import get_customer_finance_account

		temp_customer = ensure_customer("No Finance Account Cust")
		result = get_customer_finance_account(temp_customer)
		self.assertFalse(result["exists"])

	def test_lookup_existing_account(self):
		from zevar_core.api.finance import get_customer_finance_account

		doc = frappe.new_doc("In-House Finance Account")
		doc.customer = self.customer
		doc.status = "Active"
		doc.credit_limit = 5000.0
		doc.interest_rate = 12.0
		doc.minimum_payment_percent = 5.0
		doc.insert(ignore_permissions=True)

		frappe.db.commit()

		result = get_customer_finance_account(self.customer)
		self.assertTrue(result["exists"])
		self.assertEqual(flt(result["credit_limit"]), 5000.0)
		self.assertEqual(result["status"], "Active")


@erpnext_required
class TestFinancePayment(FrappeTestCase):
	"""Test In-House Finance payment processing and balance tracking."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Finance Pay Cust")
		ensure_mode_of_payment("Cash", payment_type="Cash")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()

		self.account = frappe.new_doc("In-House Finance Account")
		self.account.customer = self.customer
		self.account.status = "Active"
		self.account.credit_limit = 5000.0
		self.account.interest_rate = 12.0
		self.account.minimum_payment_percent = 5.0
		self.account.insert(ignore_permissions=True)

		self.account.append(
			"ledger_entries",
			{
				"entry_date": today(),
				"entry_type": "Purchase",
				"description": "Test Purchase",
				"debit": 1000.0,
			},
		)

		running = 0.0
		for entry in self.account.ledger_entries:
			running += flt(entry.debit) - flt(entry.credit)
			entry.balance = running
		self.account.current_balance = running
		self.account.available_credit = flt(self.account.credit_limit) - running
		self.account.save(ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def test_process_payment_reduces_balance(self):
		from zevar_core.api.finance import process_finance_payment

		result = process_finance_payment(self.account.name, 200.0, "Cash")
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["new_balance"]), 800.0)
		self.assertEqual(flt(result["available_credit"]), 4200.0)

	def test_full_payment_zeros_balance(self):
		from zevar_core.api.finance import process_finance_payment

		result = process_finance_payment(self.account.name, 1000.0, "Cash")
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["new_balance"]), 0.0)
		self.assertEqual(flt(result["available_credit"]), 5000.0)

	def test_payment_exceeds_balance_throws(self):
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(self.account.name, 1500.0, "Cash")

	def test_zero_payment_throws(self):
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(self.account.name, 0.0, "Cash")

	def test_payment_on_closed_account_throws(self):
		from zevar_core.api.finance import process_finance_payment

		self.account.status = "Closed"
		self.account.save(ignore_permissions=True)
		frappe.db.commit()

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(self.account.name, 100.0, "Cash")

	def test_payment_on_suspended_account_throws(self):
		from zevar_core.api.finance import process_finance_payment

		self.account.status = "Suspended"
		self.account.save(ignore_permissions=True)
		frappe.db.commit()

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(self.account.name, 100.0, "Cash")

	def test_multiple_payments_track_balance(self):
		from zevar_core.api.finance import process_finance_payment

		process_finance_payment(self.account.name, 300.0, "Cash")
		result = process_finance_payment(self.account.name, 400.0, "Cash")

		self.assertTrue(result["success"])
		self.assertEqual(flt(result["new_balance"]), 300.0)


@erpnext_required
class TestFinanceStatement(FrappeTestCase):
	"""Test monthly statement generation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Finance Stmt Cust")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()

		self.account = frappe.new_doc("In-House Finance Account")
		self.account.customer = self.customer
		self.account.status = "Active"
		self.account.credit_limit = 5000.0
		self.account.interest_rate = 12.0
		self.account.minimum_payment_percent = 5.0
		self.account.insert(ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def test_generate_statement_empty_account(self):
		from frappe.utils import getdate

		from zevar_core.api.finance import generate_monthly_statement

		now = getdate()
		result = generate_monthly_statement(self.account.name, now.month, now.year)

		self.assertEqual(result["entries"], [])
		self.assertEqual(flt(result["opening_balance"]), 0.0)
		self.assertEqual(flt(result["closing_balance"]), 0.0)

	def test_invalid_month_throws(self):
		from zevar_core.api.finance import generate_monthly_statement

		with self.assertRaises(frappe.ValidationError):
			generate_monthly_statement(self.account.name, 13, 2026)

	def test_statement_structure(self):
		from frappe.utils import getdate

		from zevar_core.api.finance import generate_monthly_statement

		self.account.append(
			"ledger_entries",
			{
				"entry_date": today(),
				"entry_type": "Purchase",
				"description": "Test Purchase",
				"debit": 500.0,
			},
		)
		running = 0.0
		for entry in self.account.ledger_entries:
			running += flt(entry.debit) - flt(entry.credit)
			entry.balance = running
		self.account.current_balance = running
		self.account.available_credit = flt(self.account.credit_limit) - running
		self.account.save(ignore_permissions=True)
		frappe.db.commit()

		now = getdate()
		result = generate_monthly_statement(self.account.name, now.month, now.year)

		self.assertIn("account_id", result)
		self.assertIn("customer", result)
		self.assertIn("month", result)
		self.assertIn("year", result)
		self.assertIn("opening_balance", result)
		self.assertIn("total_debits", result)
		self.assertIn("total_credits", result)
		self.assertIn("closing_balance", result)
		self.assertIn("entries", result)
		self.assertEqual(flt(result["total_debits"]), 500.0)


# ==========================================================================
# R7: POS SESSION CLOSE + CASH RECONCILIATION TESTS
# ==========================================================================


@erpnext_required
class TestPOSSessionOpenClose(FrappeTestCase):
	"""Test opening and closing POS sessions."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = _get_test_company()
		cls.warehouse = ensure_warehouse("Session Test WH", company=cls.company)
		cls.item = ensure_item("SESS-TEST-ITEM-01", "Session Test Item", rate=100.0)
		cls.customer = ensure_customer("Session Test Cust")
		ensure_mode_of_payment("Cash", payment_type="Cash")

		from zevar_core.tests.utils import ensure_pos_profile

		cls.pos_profile = ensure_pos_profile(
			profile_name="Session Test POS",
			warehouse_name="Session Test WH",
		)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()
		self._cleanup_sessions()

	def tearDown(self):
		self._cleanup_sessions()
		frappe.db.rollback()

	def _cleanup_sessions(self):
		sessions = frappe.get_all(
			"POS Opening Entry",
			filters={"user": "Administrator", "status": "Open"},
			fields=["name", "docstatus"],
		)
		for s in sessions:
			try:
				doc = frappe.get_doc("POS Opening Entry", s.name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("POS Opening Entry", s.name, ignore_permissions=True)
			except Exception:
				pass

	def test_open_session(self):
		from zevar_core.api.pos_session import open_pos_session

		result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=200.0,
		)

		self.assertTrue(result["success"])
		self.assertIsNotNone(result["session_name"])
		self.assertEqual(result["status"], "Open")
		self.assertEqual(flt(result["opening_balance"]), 200.0)

	def test_close_session_balanced(self):
		from zevar_core.api.pos_session import close_pos_session, open_pos_session

		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.0,
		)

		close_result = close_pos_session(
			session_name=open_result["session_name"],
			closing_balance=100.0,
		)

		expected_variance = 100.0 - flt(close_result["expected_balance"])
		self.assertTrue(close_result["success"])
		self.assertEqual(flt(close_result["variance"]), expected_variance)
		self.assertEqual(flt(close_result["opening_balance"]), 100.0)

	def test_close_session_with_shortage(self):
		from zevar_core.api.pos_session import close_pos_session, open_pos_session

		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.0,
		)

		close_result = close_pos_session(
			session_name=open_result["session_name"],
			closing_balance=95.0,
		)

		expected_variance = 95.0 - flt(close_result["expected_balance"])
		self.assertTrue(close_result["success"])
		self.assertEqual(flt(close_result["variance"]), expected_variance)

	def test_close_session_with_excess(self):
		from zevar_core.api.pos_session import close_pos_session, open_pos_session

		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.0,
		)

		close_result = close_pos_session(
			session_name=open_result["session_name"],
			closing_balance=110.0,
		)

		expected_variance = 110.0 - flt(close_result["expected_balance"])
		self.assertTrue(close_result["success"])
		self.assertEqual(flt(close_result["variance"]), expected_variance)

	def test_double_open_throws(self):
		from zevar_core.api.pos_session import open_pos_session

		result1 = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.0,
		)
		self.assertTrue(result1["success"])

		with self.assertRaises(frappe.ValidationError):
			open_pos_session(
				pos_profile=self.pos_profile,
				opening_balance=50.0,
			)

	def test_close_nonexistent_session_throws(self):
		from zevar_core.api.pos_session import close_pos_session

		with self.assertRaises(frappe.ValidationError):
			close_pos_session(
				session_name="NONEXISTENT-SESSION-99999",
				closing_balance=100.0,
			)

	def test_session_status_after_open(self):
		from zevar_core.api.pos_session import get_session_status, open_pos_session

		status_before = get_session_status()
		self.assertFalse(status_before["has_active_session"])

		open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.0,
		)

		status_after = get_session_status()
		self.assertTrue(status_after["has_active_session"])
		self.assertIsNotNone(status_after["session"])

	def test_session_status_after_close(self):
		from zevar_core.api.pos_session import close_pos_session, get_session_status, open_pos_session

		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.0,
		)

		close_pos_session(
			session_name=open_result["session_name"],
			closing_balance=100.0,
		)

		status = get_session_status()
		self.assertFalse(status["has_active_session"])


@erpnext_required
class TestPOSSessionWithCashBreakdown(FrappeTestCase):
	"""Test POS session with detailed cash breakdown."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = _get_test_company()
		cls.warehouse = ensure_warehouse("Session Breakdown WH", company=cls.company)

		from zevar_core.tests.utils import ensure_pos_profile

		cls.pos_profile = ensure_pos_profile(
			profile_name="Session Breakdown POS",
			warehouse_name="Session Breakdown WH",
		)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		if hasattr(self, "customer"):
			frappe.db.delete("In-House Finance Account", {"customer": self.customer})
		frappe.db.commit()
		self._cleanup_sessions()

	def tearDown(self):
		self._cleanup_sessions()
		frappe.db.rollback()

	def _cleanup_sessions(self):
		sessions = frappe.get_all(
			"POS Opening Entry",
			filters={"user": "Administrator", "status": "Open"},
			fields=["name", "docstatus"],
		)
		for s in sessions:
			try:
				doc = frappe.get_doc("POS Opening Entry", s.name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("POS Opening Entry", s.name, ignore_permissions=True)
			except Exception:
				pass

	def test_open_with_denomination_breakdown(self):
		from zevar_core.api.pos_session import open_pos_session

		breakdown = json.dumps({"100": 2, "50": 1, "20": 0, "10": 0, "5": 0, "1": 0})

		result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=250.0,
			cash_breakdown=breakdown,
		)

		self.assertTrue(result["success"])
		self.assertEqual(flt(result["opening_balance"]), 250.0)

	def test_close_with_breakdown_and_notes(self):
		from zevar_core.api.pos_session import close_pos_session, open_pos_session

		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=200.0,
		)

		close_result = close_pos_session(
			session_name=open_result["session_name"],
			closing_balance=195.0,
			notes="Short by $5 — register miscount",
		)

		expected_variance = 195.0 - flt(close_result["expected_balance"])
		self.assertTrue(close_result["success"])
		self.assertEqual(flt(close_result["variance"]), expected_variance)

	def test_close_creates_closing_entry(self):
		from zevar_core.api.pos_session import close_pos_session, open_pos_session

		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=150.0,
		)

		close_result = close_pos_session(
			session_name=open_result["session_name"],
			closing_balance=150.0,
		)

		self.assertTrue(close_result["success"])
		self.assertIsNotNone(close_result["closing_entry"])

		closing_entry = frappe.get_doc("POS Closing Entry", close_result["closing_entry"])
		self.assertEqual(closing_entry.docstatus, 1)
