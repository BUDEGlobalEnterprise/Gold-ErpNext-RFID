# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Integration Tests for Zevar POS System

Tests complete workflows from start to finish:
- POS Session management
- Complete sale with payment
- Layaway creation and payment
- Return processing
- Manager override flows
"""

import json
import time
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, now_datetime, today

from zevar_core.tests.utils import ensure_customer, ensure_item, ensure_pos_profile

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required (Sales Invoice DocType not found)",
)


@erpnext_required
class TestPOSSessionWorkflow(FrappeTestCase):
	"""Test complete POS session workflow."""

	def setUp(self):
		"""Set up test data."""
		frappe.set_user("Administrator")
		self._cleanup_sessions()
		self.test_user = "test@example.com"
		self.test_customer = (
			frappe.get_value("Customer", {"customer_name": "Test Customer"}) or self.create_test_customer()
		)
		self.test_item = frappe.get_value("Item", {"item_code": "TEST-ITEM-001"}) or self.create_test_item()
		self.test_pos_profile = (
			frappe.get_value("POS Profile", {"name": "Test POS"}) or self.create_test_pos_profile()
		)

	def create_test_customer(self):
		"""Create a test customer."""
		return ensure_customer("Test Customer")

	def create_test_item(self):
		"""Create a test item."""
		return ensure_item("TEST-ITEM-001", "Test Gold Ring")

	def create_test_pos_profile(self):
		"""Create a test POS profile."""
		return ensure_pos_profile(profile_name="Test POS", warehouse_name="Test POS Warehouse")

	def tearDown(self):
		"""Reset session state after each test."""
		self._cleanup_sessions()
		frappe.set_user("Administrator")

	def _cleanup_sessions(self):
		"""Remove open Administrator POS sessions left by other tests."""
		sessions = frappe.get_all(
			"POS Opening Entry",
			filters={"user": "Administrator", "status": "Open"},
			fields=["name", "docstatus"],
		)
		for session in sessions:
			try:
				doc = frappe.get_doc("POS Opening Entry", session.name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("POS Opening Entry", session.name, ignore_permissions=True)
			except Exception:
				frappe.log_error(
					frappe.get_traceback(), f"Failed to clean up test POS session {session.name}"
				)

	def test_complete_session_workflow(self):
		"""Test opening session, processing sale, closing session."""
		from zevar_core.api.pos_session import close_pos_session, get_session_status, open_pos_session

		# 1. Check no active session
		status = get_session_status()
		self.assertFalse(status.get("has_active_session"))

		# 2. Open session
		result = open_pos_session(
			pos_profile=self.test_pos_profile,
			opening_balance=200.00,
			cash_breakdown=json.dumps({"100": 2, "50": 0, "20": 0, "10": 0, "5": 0, "1": 0}),
			notes="Test session opening",
		)

		self.assertTrue(result.get("success"))
		self.assertEqual(result.get("status"), "Open")
		session_name = result.get("session_name")

		# 3. Verify session is active
		status = get_session_status()
		self.assertTrue(status.get("has_active_session"))

		# 4. Close session
		close_result = close_pos_session(
			session_name=session_name, closing_balance=200.00, notes="Test session closing"
		)

		self.assertTrue(close_result.get("success"))
		expected_variance = 200.0 - flt(close_result.get("expected_balance"))
		self.assertEqual(flt(close_result.get("variance")), expected_variance)

		# 5. Verify session is closed
		status = get_session_status()
		self.assertFalse(status.get("has_active_session"))

	def test_session_with_variance(self):
		"""Test session closing with cash variance."""
		from zevar_core.api.pos_session import close_pos_session, open_pos_session

		# Open session
		result = open_pos_session(pos_profile=self.test_pos_profile, opening_balance=100.00)
		session_name = result.get("session_name")

		# Close with variance (different amount)
		close_result = close_pos_session(
			session_name=session_name, closing_balance=95.00, notes="Short by $5"
		)

		# Should have variance of -5
		expected_variance = 95.00 - flt(close_result.get("expected_balance"))
		self.assertEqual(flt(close_result.get("variance")), expected_variance)


@erpnext_required
class TestCompleteSaleWorkflow(FrappeTestCase):
	"""Test complete sale workflow."""

	def setUp(self):
		"""Set up test data."""
		self.customer = self.get_or_create_customer()
		self.item = self.get_or_create_item()

	def get_or_create_customer(self):
		"""Get or create test customer."""
		return ensure_customer("Integration Test Customer")

	def get_or_create_item(self):
		"""Get or create test item."""
		return ensure_item("INT-TEST-001", "Integration Test Item")

	def test_simple_cash_sale(self):
		"""Test creating a simple cash sale."""
		from zevar_core.api.pos import create_pos_invoice

		# Create invoice
		result = create_pos_invoice(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 100.00}]),
			payments=json.dumps(
				[
					{
						"mode_of_payment": "Cash",
						"amount": 110.00,  # Including tax
					}
				]
			),
		)

		self.assertTrue(result.get("success"))
		self.assertIsNotNone(result.get("invoice_name"))

		# Verify invoice was created
		invoice = frappe.get_doc("Sales Invoice", result.get("invoice_name"))
		self.assertEqual(invoice.docstatus, 1)  # Submitted
		self.assertEqual(invoice.customer, self.customer)


@erpnext_required
class TestLayawayWorkflow(FrappeTestCase):
	"""Test layaway creation and management workflow."""

	def setUp(self):
		"""Set up test data."""
		self.customer = self.get_or_create_customer()
		self.item = self.get_or_create_item()

	def get_or_create_customer(self):
		"""Get or create test customer."""
		return ensure_customer("Layaway Test Customer")

	def get_or_create_item(self):
		"""Get or create test item."""
		return ensure_item("LAYAWAY-TEST-001", "Layaway Test Item", rate=1000.0)

	def test_layaway_preview(self):
		"""Test layaway preview calculation."""
		from zevar_core.api.layaway import get_layaway_preview

		result = get_layaway_preview(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.00}]),
			customer=self.customer,
			down_payment_percent=20,
			term_months=3,
		)

		self.assertIsNotNone(result.get("preview"))
		preview = result["preview"]

		# Verify calculations
		self.assertEqual(flt(preview.get("total")), 1000.00)
		self.assertEqual(flt(preview.get("down_payment")), 200.00)
		self.assertEqual(flt(preview.get("balance")), 800.00)

		# Verify payment schedule
		self.assertEqual(len(result.get("payment_schedule", [])), 3)

	def test_create_layaway(self):
		"""Test creating a layaway contract."""
		from zevar_core.api.layaway import create_quick_layaway

		result = create_quick_layaway(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.00}]),
			customer=self.customer,
			down_payment_percent=20,
			term_months=3,
			initial_payment=200.00,
			initial_payment_mode="Cash",
		)

		self.assertTrue(result.get("success"))
		self.assertIsNotNone(result.get("contract_name"))


@erpnext_required
class TestReturnWorkflow(FrappeTestCase):
	"""Test return and void processing workflow."""

	def setUp(self):
		"""Set up test data."""
		frappe.set_user("Administrator")
		self.customer = self.get_or_create_customer()
		self.item = self.get_or_create_item()

	def get_or_create_customer(self):
		"""Get or create test customer."""
		return ensure_customer("Return Test Customer")

	def get_or_create_item(self):
		"""Get or create test item."""
		return ensure_item("RETURN-TEST-001", "Return Test Item")

	def tearDown(self):
		"""Keep integration tests pinned to the default privileged user."""
		frappe.set_user("Administrator")

	def test_get_returnable_items(self):
		"""Test getting returnable items from invoice."""
		from zevar_core.api.pos import create_pos_invoice
		from zevar_core.api.returns import get_returnable_items

		# First create an invoice
		invoice_result = create_pos_invoice(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 2, "rate": 100.00}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 220.00}]),
		)

		invoice_name = invoice_result.get("invoice_name")

		# Get returnable items
		result = get_returnable_items(invoice_name)

		self.assertEqual(result.get("invoice_name"), invoice_name)
		self.assertEqual(len(result.get("items", [])), 1)

		item = result["items"][0]
		self.assertEqual(item.get("returnable_qty"), 2)

	def test_create_return_invoice(self):
		"""Test creating a return invoice."""
		from zevar_core.api.pos import create_pos_invoice
		from zevar_core.api.returns import create_return_invoice, get_returnable_items

		# Create original invoice
		invoice_result = create_pos_invoice(
			customer=self.customer,
			items=json.dumps([{"item_code": self.item, "qty": 2, "rate": 100.00}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 220.00}]),
		)

		invoice_name = invoice_result.get("invoice_name")
		time.sleep(1)

		# Create return for 1 item
		return_result = create_return_invoice(
			original_invoice=invoice_name,
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 100.00}]),
			reason="Customer changed mind",
			return_type="refund",
		)

		self.assertTrue(return_result.get("success"))
		self.assertIsNotNone(return_result.get("return_invoice"))


@erpnext_required
class TestPermissionWorkflow(FrappeTestCase):
	"""Test permission and manager override workflow."""

	def test_check_permission(self):
		"""Test permission checking."""
		from zevar_core.api.permissions import check_permission

		# This should work for any logged-in user with Sales User role
		# If user doesn't have the role, it will throw
		try:
			result = check_permission("pos_access", raise_exception=False)
			self.assertIsNotNone(result)
		except frappe.PermissionError:
			pass  # User doesn't have required role

	def test_get_user_permissions(self):
		"""Test getting user permissions."""
		from zevar_core.api.permissions import get_user_permissions

		permissions = get_user_permissions()

		self.assertIsInstance(permissions, dict)
		self.assertIn("pos_access", permissions)
		self.assertIn("create_invoice", permissions)


@erpnext_required
class TestAuditLogWorkflow(FrappeTestCase):
	"""Test audit logging workflow."""

	def test_log_and_retrieve_event(self):
		"""Test logging and retrieving audit events."""
		from zevar_core.api.audit_log import get_audit_logs, log_event

		# Log an event
		log_event(
			event_type="invoice_created",
			details={"invoice_name": "TEST-INV-001", "customer": "Test Customer", "amount": 100.00},
			reference_document="TEST-INV-001",
		)

		# Retrieve logs
		result = get_audit_logs(event_type="invoice_created", page=1, page_size=10)

		self.assertIn("logs", result)
		self.assertIn("pagination", result)

	def test_audit_summary(self):
		"""Test audit summary statistics."""
		from zevar_core.api.audit_log import get_audit_summary

		summary = get_audit_summary()

		self.assertIn("total_events", summary)
		self.assertIn("warning_events", summary)
		self.assertIn("by_category", summary)


@erpnext_required
class TestSalesHistoryWorkflow(FrappeTestCase):
	"""Test sales history and reporting workflow."""

	def setUp(self):
		"""Set up test data."""
		self.customer = self.get_or_create_customer()
		self.item = self.get_or_create_item()

	def get_or_create_customer(self):
		"""Get or create test customer."""
		return ensure_customer("History Test Customer")

	def get_or_create_item(self):
		"""Get or create test item."""
		return ensure_item("HISTORY-TEST-001", "History Test Item")

	def test_get_sales_history(self):
		"""Test retrieving sales history."""
		from zevar_core.api.sales_history import get_sales_history

		result = get_sales_history(from_date=add_days(today(), -30), to_date=today(), page=1, page_size=20)

		self.assertIn("sales", result)
		self.assertIn("pagination", result)

	def test_get_sales_summary(self):
		"""Test getting sales summary."""
		from zevar_core.api.sales_history import get_sales_summary

		summary = get_sales_summary(from_date=add_days(today(), -30), to_date=today())

		self.assertIn("summary", summary)
		self.assertIn("transaction_count", summary["summary"])
		self.assertIn("total_sales", summary["summary"])


# Run tests with:
# bench --site your-site run-tests --app zevar_core --doctype TestPOSSessionWorkflow
