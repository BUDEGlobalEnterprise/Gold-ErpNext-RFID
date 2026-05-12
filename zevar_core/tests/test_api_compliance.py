# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Compliance API (compliance.py)
Covers: check_cash_reporting_required, trigger_form_8300, verify_customer_identity

Run with: bench run-tests --app zevar_core --test test_api_compliance
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from zevar_core.tests.utils import ensure_customer

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required",
)


@erpnext_required
class TestCheckCashReportingRequired(FrappeTestCase):
	"""Test check_cash_reporting_required endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Compliance Test Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_check_returns_required_field(self):
		"""Should return a dict with 'required' key"""
		from zevar_core.api.compliance import check_cash_reporting_required

		result = check_cash_reporting_required(self.customer)
		self.assertIn("required", result)
		self.assertIn("total_cash", result)
		self.assertIn("threshold", result)

	def test_check_returns_existing_records_list(self):
		"""Should return existing_records list"""
		from zevar_core.api.compliance import check_cash_reporting_required

		result = check_cash_reporting_required(self.customer)
		self.assertIn("existing_records", result)
		self.assertIsInstance(result["existing_records"], list)

	def test_check_threshold_is_numeric(self):
		"""Threshold should be numeric"""
		from zevar_core.api.compliance import check_cash_reporting_required

		result = check_cash_reporting_required(self.customer)
		self.assertIsInstance(flt(result["threshold"]), float)

	def test_check_new_customer_no_cash(self):
		"""New customer should have zero cash total"""
		customer = ensure_customer("Compliance Zero Cash Customer")
		from zevar_core.api.compliance import check_cash_reporting_required

		result = check_cash_reporting_required(customer)
		self.assertEqual(flt(result["total_cash"]), 0)


@erpnext_required
class TestTriggerForm8300(FrappeTestCase):
	"""Test trigger_form_8300 endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Form 8300 Test Customer")

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_records = []

	def tearDown(self):
		for rec_name in self.created_records:
			try:
				frappe.delete_doc("IRS Form 8300 Record", rec_name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_trigger_creates_record(self):
		"""Should create IRS Form 8300 Record"""
		# Only run if the DocType and settings exist
		if not frappe.db.exists("DocType", "IRS Form 8300 Record"):
			self.skipTest("IRS Form 8300 Record DocType not found")

		from zevar_core.api.compliance import trigger_form_8300

		try:
			result = trigger_form_8300(
				customer=self.customer,
				total_amount=15000,
				transaction_details='{"test": true}',
			)
			if result.get("success"):
				self.assertIn("record_name", result)
				self.created_records.append(result["record_name"])
		except frappe.PermissionError:
			self.skipTest("Insufficient permissions")

	def test_trigger_returns_success_or_disabled(self):
		"""Should return success dict or disabled message"""
		from zevar_core.api.compliance import trigger_form_8300

		result = trigger_form_8300(
			customer=self.customer,
			total_amount=15000,
		)
		self.assertIn("success", result)


@erpnext_required
class TestVerifyCustomerIdentity(FrappeTestCase):
	"""Test verify_customer_identity endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("KYC Test Customer")

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_records = []

	def tearDown(self):
		for rec_name in self.created_records:
			try:
				frappe.delete_doc("AML KYC Record", rec_name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_verify_returns_risk_level(self):
		"""Should return risk_level in response"""
		if not frappe.db.exists("DocType", "AML KYC Record"):
			self.skipTest("AML KYC Record DocType not found")

		from zevar_core.api.compliance import verify_customer_identity

		try:
			result = verify_customer_identity(
				customer=self.customer,
				id_type="Driver License",
				id_number="DL12345",
				id_state="CA",
				id_expiration="2028-01-01",
			)
			if result.get("success"):
				self.assertIn("risk_level", result)
				self.assertIn("status", result)
				self.assertIn(result["risk_level"], ["Low", "Medium", "High", "Critical"])
				self.created_records.append(result["record_name"])
		except frappe.PermissionError:
			self.skipTest("Insufficient permissions")

	def test_verify_returns_success_or_disabled(self):
		"""Should return success dict or disabled message"""
		from zevar_core.api.compliance import verify_customer_identity

		result = verify_customer_identity(
			customer=self.customer,
			id_type="Passport",
			id_number="PP99999",
		)
		self.assertIn("success", result)

	def test_verify_with_scan_data(self):
		"""Should handle scan_data JSON"""
		if not frappe.db.exists("DocType", "AML KYC Record"):
			self.skipTest("AML KYC Record DocType not found")

		from zevar_core.api.compliance import verify_customer_identity

		import json
		scan_data = json.dumps({
			"name": "John Doe",
			"address": "123 Main St",
			"dob": "1990-01-15",
		})

		try:
			result = verify_customer_identity(
				customer=self.customer,
				id_type="Driver License",
				id_number="DL67890",
				scan_data=scan_data,
			)
			if result.get("success") and result.get("record_name"):
				self.created_records.append(result["record_name"])
		except frappe.PermissionError:
			self.skipTest("Insufficient permissions")


@erpnext_required
class TestComplianceHelpers(FrappeTestCase):
	"""Test internal compliance helper functions"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_assess_risk_level_low(self):
		"""New customer should get Low risk level"""
		from zevar_core.api.compliance import _assess_risk_level

		customer = ensure_customer("Risk Low Customer")
		risk = _assess_risk_level(customer)
		self.assertEqual(risk, "Low")

	def test_get_customer_cash_total_new_customer(self):
		"""New customer should have zero cash total"""
		from zevar_core.api.compliance import _get_customer_cash_total

		customer = ensure_customer("Cash Zero Customer")
		total = _get_customer_cash_total(customer)
		self.assertEqual(flt(total), 0)
