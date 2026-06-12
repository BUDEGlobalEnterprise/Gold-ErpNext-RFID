# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for POS Profile API

Run with: bench run-tests --app zevar_core --doctype "POS Profile" --test test_pos_profile
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

from zevar_core.tests.utils import ensure_pos_profile, ensure_warehouse

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "POS Profile"),
	"ERPNext required (POS Profile DocType not found)",
)


@erpnext_required
class TestPOSProfileAPI(FrappeTestCase):
	"""Test cases for POS Profile API"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Create test POS Profile if not exists
		cls.test_profile_name = "Test POS Profile"
		cls.test_profile_name = ensure_pos_profile(
			profile_name=cls.test_profile_name,
			warehouse_name="Test POS Warehouse",
		)
		cls.created_profile = False

	@classmethod
	def _get_test_warehouse(cls):
		"""Get or create test warehouse"""
		return ensure_warehouse("Test POS Warehouse")

	@classmethod
	def tearDownClass(cls):
		if cls.created_profile:
			frappe.delete_doc("POS Profile", cls.test_profile_name, ignore_permissions=True)
		super().tearDownClass()

	def setUp(self):
		"""Set up test fixtures"""
		frappe.set_user("Administrator")

	def tearDown(self):
		"""Clean up after test"""
		frappe.set_user("Administrator")

	def test_get_pos_profiles(self):
		"""Test getting list of POS profiles"""
		from zevar_core.api.pos_profile import get_pos_profiles

		result = get_pos_profiles()

		self.assertIn("profiles", result)
		self.assertIn("count", result)
		self.assertIsInstance(result["profiles"], list)
		self.assertGreaterEqual(result["count"], 1)

	def test_get_active_profile(self):
		"""Test getting active profile"""
		from zevar_core.api.pos_profile import get_active_profile, set_active_profile

		# Set active profile first
		set_active_profile(self.test_profile_name)

		# Get active profile
		result = get_active_profile()

		self.assertIn("active_profile", result)
		if result["active_profile"]:
			self.assertEqual(result["active_profile"]["name"], self.test_profile_name)

	def test_set_active_profile(self):
		"""Test setting active profile"""
		from zevar_core.api.pos_profile import get_active_profile, set_active_profile

		result = set_active_profile(self.test_profile_name)

		self.assertTrue(result.get("success"))

		# Verify it was set
		active = get_active_profile()
		if active.get("active_profile"):
			self.assertEqual(active["active_profile"]["name"], self.test_profile_name)

	def test_set_invalid_profile(self):
		"""Test setting invalid profile raises error"""
		from zevar_core.api.pos_profile import set_active_profile

		with self.assertRaises(frappe.ValidationError):
			set_active_profile("Non-existent Profile")


@erpnext_required
class TestPOSSessionAPI(FrappeTestCase):
	"""Test cases for POS Session API"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_profile = "Test POS Profile"
		cls._ensure_test_profile()

	@classmethod
	def _ensure_test_profile(cls):
		"""Ensure test POS profile exists"""
		cls.test_profile = ensure_pos_profile(
			profile_name=cls.test_profile,
			warehouse_name="Test POS Session Warehouse",
		)

	def setUp(self):
		frappe.set_user("Administrator")
		# Close any existing open sessions
		self._cleanup_sessions()

	def tearDown(self):
		self._cleanup_sessions()
		frappe.set_user("Administrator")

	def _cleanup_sessions(self):
		"""Clean up test sessions"""
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
				pass

	def test_open_pos_session(self):
		"""Test opening a POS session"""
		from zevar_core.api.pos_session import open_pos_session

		result = open_pos_session(
			pos_profile=self.test_profile,
			opening_balance=100.00,
			notes="Test session",
		)

		self.assertTrue(result.get("success"))
		self.assertIsNotNone(result.get("session_name"))

		# Clean up
		if result.get("session_name"):
			doc = frappe.get_doc("POS Opening Entry", result["session_name"])
			doc.cancel()
			frappe.delete_doc("POS Opening Entry", result["session_name"], ignore_permissions=True)

	def test_get_session_status(self):
		"""Test getting session status"""
		from zevar_core.api.pos_session import get_session_status

		result = get_session_status()

		self.assertIn("has_active_session", result)

	def test_session_status_includes_today_sales(self):
		"""Test that session status includes today's sales separate from cumulative"""
		from zevar_core.api.pos_session import get_session_status, open_pos_session

		# Open a session
		result = open_pos_session(
			pos_profile=self.test_profile,
			opening_balance=100.00,
		)
		session_name = result.get("session_name")
		self.assertTrue(result.get("success"))

		try:
			# Get status
			status = get_session_status()
			self.assertTrue(status["has_active_session"])
			session = status["session"]

			# Verify new today_sales fields exist
			self.assertIn("today_sales_count", session)
			self.assertIn("today_sales_total", session)
			self.assertIn("sales_count", session)
			self.assertIn("sales_total", session)

			# Today's sales should be 0 if no invoices created today
			self.assertEqual(session["today_sales_count"], 0)
			self.assertEqual(session["today_sales_total"], 0)

		finally:
			# Clean up
			if session_name:
				doc = frappe.get_doc("POS Opening Entry", session_name)
				doc.cancel()
				frappe.delete_doc("POS Opening Entry", session_name, ignore_permissions=True)

	def test_open_session_already_exists(self):
		"""Test that opening session when one exists raises error"""
		from zevar_core.api.pos_session import open_pos_session

		# Open first session
		result1 = open_pos_session(
			pos_profile=self.test_profile,
			opening_balance=100.00,
		)
		self.assertTrue(result1.get("success"))

		# Try to open second session
		with self.assertRaises(frappe.ValidationError):
			open_pos_session(
				pos_profile=self.test_profile,
				opening_balance=50.00,
			)

		# Clean up
		if result1.get("session_name"):
			doc = frappe.get_doc("POS Opening Entry", result1["session_name"])
			doc.cancel()
			frappe.delete_doc("POS Opening Entry", result1["session_name"], ignore_permissions=True)


@erpnext_required
class TestSalesHistoryAPI(FrappeTestCase):
	"""Test cases for Sales History API"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_sales_history(self):
		"""Test getting sales history"""
		from zevar_core.api.sales_history import get_sales_history

		result = get_sales_history(page=1, page_size=10)

		self.assertIn("sales", result)
		self.assertIn("pagination", result)
		self.assertIsInstance(result["sales"], list)

	def test_get_sales_summary(self):
		"""Test getting sales summary"""
		from zevar_core.api.sales_history import get_sales_summary

		result = get_sales_summary()

		self.assertIn("summary", result)
		self.assertIn("transaction_count", result["summary"])
		self.assertIn("total_sales", result["summary"])

	def test_get_sales_history_with_filters(self):
		"""Test getting sales history with filters"""
		from frappe.utils import add_days, today

		from zevar_core.api.sales_history import get_sales_history

		result = get_sales_history(
			from_date=add_days(today(), -7),
			to_date=today(),
			status="Paid",
		)

		self.assertIn("sales", result)
		for sale in result["sales"]:
			self.assertEqual(sale.get("status"), "Paid")


@erpnext_required
class TestQuickLayawayAPI(FrappeTestCase):
	"""Test cases for Quick Layaway API"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_layaway_preview(self):
		"""Test layaway preview calculation"""
		from zevar_core.api.layaway import get_layaway_preview

		items = [{"item_code": "TEST-001", "qty": 1, "rate": 1000}]

		result = get_layaway_preview(
			items=items,
			customer="Test Customer",
			down_payment_percent=20,
			term_months=3,
		)

		self.assertIn("preview", result)
		self.assertIn("payment_schedule", result)
		self.assertEqual(result["preview"]["total"], 1000)
		self.assertEqual(result["preview"]["down_payment"], 200)
		self.assertEqual(len(result["payment_schedule"]), 3)

	def test_valid_terms(self):
		"""Test that only valid terms are accepted"""
		from zevar_core.api.layaway import get_layaway_preview

		items = [{"item_code": "TEST-001", "qty": 1, "rate": 1000}]

		# Valid terms
		for term in [3, 6, 9, 12]:
			result = get_layaway_preview(
				items=items,
				customer="Test Customer",
				term_months=term,
			)
			self.assertEqual(len(result["payment_schedule"]), term)

		# Invalid term
		with self.assertRaises(frappe.ValidationError):
			get_layaway_preview(
				items=items,
				customer="Test Customer",
				term_months=5,
			)


@erpnext_required
class TestPermissionsAPI(FrappeTestCase):
	"""Test cases for Permissions API"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_check_permission_as_admin(self):
		"""Test permission check as administrator"""
		from zevar_core.api.permissions import check_permission

		# Admin should have all permissions
		self.assertTrue(check_permission("pos_access", raise_exception=False))
		self.assertTrue(check_permission("create_invoice", raise_exception=False))
		self.assertTrue(check_permission("void_invoice", raise_exception=False))

	def test_get_user_permissions(self):
		"""Test getting user permissions"""
		from zevar_core.api.permissions import get_user_permissions

		permissions = get_user_permissions()

		self.assertIsInstance(permissions, dict)
		self.assertIn("pos_access", permissions)
		self.assertIn("create_invoice", permissions)

	def test_check_discount_permission(self):
		"""Test discount permission checking"""
		from zevar_core.api.permissions import check_discount_permission

		# Small discount
		result = check_discount_permission(5.0)
		self.assertTrue(result.get("allowed"))

		# Large discount (needs override for non-manager)
		result = check_discount_permission(50.0)
		self.assertTrue(result.get("allowed") or result.get("needs_override"))


@erpnext_required
class TestAuditLogAPI(FrappeTestCase):
	"""Test cases for Audit Log API"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_audit_logs(self):
		"""Test getting audit logs"""
		from zevar_core.api.audit_log import get_audit_logs

		result = get_audit_logs(page=1, page_size=10)

		self.assertIn("logs", result)
		self.assertIn("pagination", result)

	def test_get_audit_summary(self):
		"""Test getting audit summary"""
		from zevar_core.api.audit_log import get_audit_summary

		result = get_audit_summary()

		self.assertIn("total_events", result)
		self.assertIn("by_category", result)
		self.assertIn("by_severity", result)
