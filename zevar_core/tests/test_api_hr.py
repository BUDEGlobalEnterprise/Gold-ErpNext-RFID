# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for HR API (hr.py)
Covers: get_employee_profile, get_leave_applications, and related endpoints

Run with: bench run-tests --app zevar_core --test test_api_hr
"""

import frappe
from frappe.tests.utils import FrappeTestCase

erpnext_required = frappe.db and frappe.db.exists("DocType", "Employee")


class TestGetEmployeeProfile(FrappeTestCase):
	"""Test get_employee_profile endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_profile_returns_dict(self):
		"""Should return dict with success flag"""
		from zevar_core.api.hr import get_employee_profile

		result = get_employee_profile()
		self.assertIsInstance(result, dict)
		self.assertIn("success", result)

	def test_admin_may_not_have_employee(self):
		"""Admin may not have linked employee record"""
		from zevar_core.api.hr import get_employee_profile

		result = get_employee_profile()
		# Admin may or may not have an employee record
		self.assertIn("success", result)


class TestGetLeaveApplications(FrappeTestCase):
	"""Test get_leave_applications endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_leaves_returns_dict(self):
		"""Should return dict with applications list"""
		if not erpnext_required:
			self.skipTest("ERPNext required")

		from zevar_core.api.hr import get_leave_applications

		result = get_leave_applications()
		self.assertTrue(result["success"])
		self.assertIn("applications", result)
		self.assertIn("total", result)
		self.assertIsInstance(result["applications"], list)

	def test_get_leaves_with_status_filter(self):
		"""Should filter by status"""
		if not erpnext_required:
			self.skipTest("ERPNext required")

		from zevar_core.api.hr import get_leave_applications

		result = get_leave_applications(status="Approved")
		self.assertTrue(result["success"])

	def test_get_leaves_page_size_capped(self):
		"""Page size should be capped"""
		if not erpnext_required:
			self.skipTest("ERPNext required")

		from zevar_core.api.hr import get_leave_applications

		result = get_leave_applications(page_size=999)
		self.assertLessEqual(result["page_size"], 100)
