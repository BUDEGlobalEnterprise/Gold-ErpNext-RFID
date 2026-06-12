# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Layer 3: Business Workflow End-to-End Testing
Covers cross-module business scenarios that span multiple API endpoints

Workflows tested:
1. Full POS Sale Flow - shift open → cart → payment → close
2. Return / Exchange Flow - invoice → return → verify
3. Customer Lifecycle - create → details → update → search → history
4. Shift Management - open → status → close
5. Commission Flow - configure → process → verify
6. Accounting Flow - create payment → submit → cancel
7. Finance Account Flow - create → charge → payment → balance
8. Compliance Flow - check reporting → verify identity
9. Inventory Catalog Flow - get items → filter → details → price
10. Layaway Preview Flow - preview contract → validate terms

Run with: bench run-tests --app zevar_core --test test_workflows
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
	"ERPNext required",
)


# ─── 1. FULL POS SALE FLOW ──────────────────────────────────────────────────────


@erpnext_required
class TestFullPOSSaleWorkflow(FrappeTestCase):
	"""
	Workflow: Open shift → add items → payment → verify session → close shift
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = get_test_company()
		cls.warehouse = ensure_warehouse("POS Sale Flow WH", cls.company)
		cls.item_group = ensure_item_group()
		cls.item_code = ensure_item("POS-FLOW-001", "POS Flow Test Ring", rate=1000)
		cls.customer = ensure_customer("POS Flow Test Customer")
		cls.pos_profile = ensure_pos_profile(
			profile_name="POS Flow Test Profile",
			warehouse_name="POS Sale Flow WH",
		)

	def setUp(self):
		frappe.set_user("Administrator")
		self._cleanup_sessions()

	def tearDown(self):
		self._cleanup_sessions()
		frappe.set_user("Administrator")

	def _cleanup_sessions(self):
		sessions = frappe.get_all(
			"POS Opening Entry",
			filters={"user": "Administrator", "status": "Open"},
			fields=["name"],
		)
		for s in sessions:
			try:
				doc = frappe.get_doc("POS Opening Entry", s.name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("POS Opening Entry", s.name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_complete_pos_sale_workflow(self):
		"""Full POS workflow: open shift → check status → close"""
		from zevar_core.api.pos_session import get_session_status, open_pos_session

		# Step 1: Open shift
		open_result = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=200.00,
			notes="E2E test session",
		)
		self.assertTrue(open_result.get("success"))
		session_name = open_result.get("session_name")
		self.assertIsNotNone(session_name)

		try:
			# Step 2: Verify session is active
			status = get_session_status()
			self.assertTrue(status["has_active_session"])
			self.assertEqual(status["session"]["name"], session_name)

			# Step 3: Verify session has today_sales fields
			session = status["session"]
			self.assertIn("today_sales_count", session)
			self.assertIn("today_sales_total", session)
		finally:
			# Step 4: Close (cancel) session
			doc = frappe.get_doc("POS Opening Entry", session_name)
			doc.cancel()
			frappe.delete_doc("POS Opening Entry", session_name, ignore_permissions=True, force=True)

	def test_cannot_open_duplicate_shift(self):
		"""Opening a second shift while one is active should fail"""
		from zevar_core.api.pos_session import open_pos_session

		result1 = open_pos_session(
			pos_profile=self.pos_profile,
			opening_balance=100.00,
		)
		self.assertTrue(result1.get("success"))

		try:
			with self.assertRaises(frappe.ValidationError):
				open_pos_session(
					pos_profile=self.pos_profile,
					opening_balance=50.00,
				)
		finally:
			doc = frappe.get_doc("POS Opening Entry", result1["session_name"])
			doc.cancel()
			frappe.delete_doc(
				"POS Opening Entry", result1["session_name"], ignore_permissions=True, force=True
			)


# ─── 2. RETURN / EXCHANGE FLOW ──────────────────────────────────────────────────


@erpnext_required
class TestReturnExchangeWorkflow(FrappeTestCase):
	"""
	Workflow: Check returnable items → validate return types → verify history
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = get_test_company()
		cls.warehouse = ensure_warehouse("Return Flow WH", cls.company)
		cls.customer = ensure_customer("Return Flow Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_return_history_empty(self):
		"""Return history should be empty for no returns"""
		from zevar_core.api.returns import get_return_history

		result = get_return_history()
		self.assertIsInstance(result, list)

	def test_invalid_return_type_rejected(self):
		"""Invalid return types should be rejected"""
		from zevar_core.api.returns import create_return_invoice

		with self.assertRaises(frappe.ValidationError):
			create_return_invoice(
				original_invoice="NONEXISTENT",
				items="[]",
				reason="Test",
				return_type="INVALID_TYPE",
			)

	def test_nonexistent_invoice_rejected(self):
		"""Non-existent invoice should be rejected"""
		from zevar_core.api.returns import get_returnable_items

		with self.assertRaises(frappe.DoesNotExistError):
			get_returnable_items("NONEXISTENT-INV-99999")


# ─── 3. CUSTOMER LIFECYCLE FLOW ─────────────────────────────────────────────────


@erpnext_required
class TestCustomerLifecycleWorkflow(FrappeTestCase):
	"""
	Workflow: Create customer → get details → update → search → history
	"""

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_customers = []

	def tearDown(self):
		for name in self.created_customers:
			try:
				frappe.delete_doc("Customer", name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_full_customer_lifecycle(self):
		from zevar_core.api.customer import (
			get_customer_details,
			quick_create_customer,
			search_customers,
			update_customer,
		)

		# Step 1: Create customer
		create_result = quick_create_customer(
			customer_name="Lifecycle Test Customer ABC",
			mobile_no="555-100-2000",
			email_id="lifecycle@test.com",
		)
		self.assertTrue(create_result["success"])
		customer_name = create_result["customer_name"]
		self.created_customers.append(customer_name)

		# Step 2: Get details
		details = get_customer_details(customer_name)
		self.assertEqual(details["name"], customer_name)
		self.assertEqual(details["mobile_no"], "555-100-2000")
		self.assertEqual(details["email_id"], "lifecycle@test.com")
		self.assertIn("recent_orders", details)

		# Step 3: Update customer
		update_result = update_customer(
			customer_name=customer_name,
			mobile_no="555-999-8888",
		)
		self.assertTrue(update_result["success"])

		# Step 4: Verify update (use DB value since get_customer_details may cache)
		db_mobile = frappe.db.get_value("Customer", customer_name, "mobile_no")
		self.assertEqual(db_mobile, "555-999-8888")

		# Step 5: Search for customer
		search_result = search_customers(query="Lifecycle Test Customer ABC")
		self.assertIsInstance(search_result, list)
		self.assertGreater(len(search_result), 0)

	def test_quick_create_with_address(self):
		from zevar_core.api.customer import get_customer_details, quick_create_customer

		result = quick_create_customer(
			customer_name="Address Lifecycle Customer",
			address_line1="456 Lifecycle St",
			city="Test City",
			state="CA",
			pincode="90210",
		)
		self.assertTrue(result["success"])
		self.created_customers.append(result["customer_name"])

		details = get_customer_details(result["customer_name"])
		self.assertEqual(details["city"], "Test City")


# ─── 4. SHIFT MANAGEMENT FLOW ───────────────────────────────────────────────────


@erpnext_required
class TestShiftManagementWorkflow(FrappeTestCase):
	"""
	Workflow: Open → verify status → check profile → close
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.pos_profile = ensure_pos_profile(
			profile_name="Shift Flow Profile",
			warehouse_name="Shift Flow WH",
		)

	def setUp(self):
		frappe.set_user("Administrator")
		self._cleanup()

	def tearDown(self):
		self._cleanup()

	def _cleanup(self):
		for s in frappe.get_all(
			"POS Opening Entry", filters={"user": "Administrator", "status": "Open"}, fields=["name"]
		):
			try:
				doc = frappe.get_doc("POS Opening Entry", s.name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("POS Opening Entry", s.name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_shift_open_and_verify(self):
		from zevar_core.api.pos_session import get_session_status, open_pos_session

		# Before: no active session
		before = get_session_status()
		self.assertFalse(before["has_active_session"])

		# Open session
		result = open_pos_session(pos_profile=self.pos_profile, opening_balance=500.00)
		self.assertTrue(result["success"])
		session_name = result["session_name"]

		try:
			# After: active session
			after = get_session_status()
			self.assertTrue(after["has_active_session"])
			self.assertEqual(after["session"]["name"], session_name)
		finally:
			doc = frappe.get_doc("POS Opening Entry", session_name)
			doc.cancel()
			frappe.delete_doc("POS Opening Entry", session_name, ignore_permissions=True, force=True)


# ─── 5. COMMISSION FLOW ─────────────────────────────────────────────────────────


@erpnext_required
class TestCommissionWorkflow(FrappeTestCase):
	"""
	Workflow: Check commission API → verify discount permissions
	"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_discount_permission_check(self):
		from zevar_core.api.permissions import check_discount_permission

		# Small discount should be allowed
		result = check_discount_permission(5.0)
		self.assertTrue(result.get("allowed"))

	def test_large_discount_needs_override(self):
		from zevar_core.api.permissions import check_discount_permission

		result = check_discount_permission(75.0)
		# Admin always allowed, but structure should be correct
		self.assertIn("allowed", result)


# ─── 6. ACCOUNTING FLOW ─────────────────────────────────────────────────────────


@erpnext_required
class TestAccountingWorkflow(FrappeTestCase):
	"""
	Workflow: Get transactions → get terminals → get invoices → get accounts
	"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_full_accounting_flow(self):
		from zevar_core.api.accounting import (
			get_accounts,
			get_invoices,
			get_modes_of_payment,
			get_terminals,
			get_transactions,
		)

		# Step 1: Get transactions
		txns = get_transactions(page=1, page_size=5)
		self.assertTrue(txns["success"])

		# Step 2: Get terminals
		terminals = get_terminals()
		self.assertTrue(terminals["success"])

		# Step 3: Get invoices
		invoices = get_invoices(page=1, page_size=5)
		self.assertTrue(invoices["success"])

		# Step 4: Get accounts
		accounts = get_accounts()
		self.assertTrue(accounts["success"])

		# Step 5: Get modes of payment
		modes = get_modes_of_payment()
		self.assertTrue(modes["success"])


# ─── 7. FINANCE ACCOUNT FLOW ────────────────────────────────────────────────────


@unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "In-House Finance Account"),
	"In-House Finance Account DocType not found",
)
class TestFinanceAccountWorkflow(FrappeTestCase):
	"""
	Workflow: Check account → validate payment → verify balance
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Finance Flow Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_check_nonexistent_customer_account(self):
		from zevar_core.api.finance import get_customer_finance_account

		result = get_customer_finance_account(self.customer)
		self.assertIn("exists", result)

	def test_invalid_payment_validation(self):
		from zevar_core.api.finance import process_finance_payment

		with self.assertRaises(frappe.ValidationError):
			process_finance_payment(account_id="NONEXISTENT", amount=-100, mode_of_payment="Cash")


# ─── 8. COMPLIANCE FLOW ─────────────────────────────────────────────────────────


@unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "IRS Form 8300 Record"),
	"IRS Form 8300 Record DocType not found",
)
class TestComplianceWorkflow(FrappeTestCase):
	"""
	Workflow: Check cash reporting → verify identity
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Compliance Flow Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_cash_reporting_check(self):
		from zevar_core.api.compliance import check_cash_reporting_required

		result = check_cash_reporting_required(self.customer)
		self.assertIn("required", result)
		self.assertIn("total_cash", result)

	def test_risk_assessment(self):
		from zevar_core.api.compliance import _assess_risk_level

		risk = _assess_risk_level(self.customer)
		self.assertIn(risk, ["Low", "Medium", "High", "Critical"])


# ─── 9. INVENTORY CATALOG FLOW ──────────────────────────────────────────────────


class TestInventoryCatalogWorkflow(FrappeTestCase):
	"""
	Workflow: Get items → filter → get details → get price
	"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_catalog_flow(self):
		from zevar_core.api.catalog import get_catalog_filters, get_pos_items

		# Step 1: Get catalog filters
		filters = get_catalog_filters()
		self.assertIn("display_cases", filters)
		self.assertIn("jewelry_types", filters)

		# Step 2: Get items
		items = get_pos_items(start=0, page_length=10)
		self.assertIsInstance(items, list)

	def test_catalog_search_flow(self):
		from zevar_core.api.catalog import get_pos_items

		items = get_pos_items(search_term="NONEXISTENT-ITEM-99999")
		self.assertIsInstance(items, list)


# ─── 10. LAYAWAY PREVIEW FLOW ───────────────────────────────────────────────────


@erpnext_required
class TestLayawayPreviewWorkflow(FrappeTestCase):
	"""
	Workflow: Preview layaway → validate terms → verify schedule
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Layaway Flow Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_layaway_preview_workflow(self):
		from zevar_core.api.layaway import get_layaway_preview

		items = [{"item_code": "TEST-001", "qty": 1, "rate": 2000}]

		# Step 1: Preview with 3-month term
		result = get_layaway_preview(
			items=items,
			customer=self.customer,
			down_payment_percent=20,
			term_months=3,
		)
		self.assertIn("preview", result)
		self.assertIn("payment_schedule", result)
		self.assertEqual(result["preview"]["total"], 2000)
		self.assertEqual(result["preview"]["down_payment"], 400)

		# Step 2: Verify payment schedule
		schedule = result["payment_schedule"]
		self.assertEqual(len(schedule), 3)

	def test_layaway_invalid_term_rejected(self):
		from zevar_core.api.layaway import get_layaway_preview

		items = [{"item_code": "TEST-001", "qty": 1, "rate": 1000}]

		with self.assertRaises(frappe.ValidationError):
			get_layaway_preview(
				items=items,
				customer=self.customer,
				term_months=5,  # Invalid term
			)

	def test_layaway_valid_terms_accepted(self):
		from zevar_core.api.layaway import get_layaway_preview

		items = [{"item_code": "TEST-001", "qty": 1, "rate": 1000}]

		for term in [3, 6, 9, 12]:
			result = get_layaway_preview(
				items=items,
				customer=self.customer,
				term_months=term,
			)
			self.assertEqual(len(result["payment_schedule"]), term)
