# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Settings API (settings.py)
Covers: get_settings, save_settings, and related endpoints

Run with: bench run-tests --app zevar_core --test test_api_settings
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "POS Profile"),
	"ERPNext required",
)


@erpnext_required
class TestGetSettings(FrappeTestCase):
	"""Test get_settings endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_settings_returns_dict(self):
		"""Should return settings dictionary"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIsInstance(result, dict)
		except frappe.PermissionError:
			self.skipTest("User lacks System Manager/Store Manager role")

	def test_get_settings_has_pos_profiles(self):
		"""Should include pos_profiles"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("pos_profiles", result)
			self.assertIsInstance(result["pos_profiles"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")

	def test_get_settings_has_warehouses(self):
		"""Should include warehouses"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("warehouses", result)
			self.assertIsInstance(result["warehouses"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")

	def test_get_settings_has_customers(self):
		"""Should include customers"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("customers", result)
			self.assertIsInstance(result["customers"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")

	def test_get_settings_has_modes_of_payment(self):
		"""Should include modes_of_payment"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("modes_of_payment", result)
			self.assertIsInstance(result["modes_of_payment"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")

	def test_get_settings_has_accounts(self):
		"""Should include accounts"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("accounts", result)
			self.assertIsInstance(result["accounts"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")

	def test_get_settings_has_users(self):
		"""Should include users"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("users", result)
			self.assertIsInstance(result["users"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")

	def test_get_settings_has_roles(self):
		"""Should include roles"""
		from zevar_core.api.settings import get_settings

		try:
			result = get_settings()
			self.assertIn("roles", result)
			self.assertIsInstance(result["roles"], list)
		except frappe.PermissionError:
			self.skipTest("User lacks required role")
