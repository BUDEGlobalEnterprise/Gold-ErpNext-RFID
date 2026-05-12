# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for User Info API (user_info.py)
Covers: get_user_info

Run with: bench run-tests --app zevar_core --test test_api_user_info
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestGetUserInfo(FrappeTestCase):
	"""Test get_user_info endpoint"""

	def test_get_user_info_admin(self):
		"""Should return admin user info"""
		frappe.set_user("Administrator")
		from zevar_core.api.user_info import get_user_info

		result = get_user_info()
		self.assertIsInstance(result, dict)
		self.assertEqual(result["user"], "Administrator")
		self.assertIn("roles", result)
		self.assertIn("full_name", result)
		self.assertIsInstance(result["roles"], list)

	def test_get_user_info_has_roles(self):
		"""Should include user roles"""
		frappe.set_user("Administrator")
		from zevar_core.api.user_info import get_user_info

		result = get_user_info()
		self.assertGreater(len(result["roles"]), 0)
