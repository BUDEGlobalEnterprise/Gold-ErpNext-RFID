# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Helpdesk API (helpdesk.py)
Covers: issue/ticket creation and management endpoints

Run with: bench run-tests --app zevar_core --test test_api_helpdesk
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHelpdeskAPI(FrappeTestCase):
	"""Test helpdesk endpoints"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_create_issue_without_helpdesk(self):
		"""Should handle missing Helpdesk gracefully"""
		from zevar_core.api.helpdesk import _try_create_hd_ticket

		# This should not raise regardless of whether Helpdesk is installed
		result = _try_create_hd_ticket(
			subject="Test Issue",
			description="Test description",
			raised_by="test@example.com",
			priority="Medium",
			category="General",
		)
		# Returns None if HD Ticket DocType doesn't exist
		if not frappe.db.exists("DocType", "HD Ticket"):
			self.assertIsNone(result)

	def test_field_exists_check(self):
		"""Should check if field exists on doctype"""
		from zevar_core.api.helpdesk import _field_exists

		# Check a known field on Customer
		result = _field_exists("Customer", "customer_name")
		self.assertTrue(result)

		# Check a nonexistent field
		result = _field_exists("Customer", "nonexistent_field_xyz")
		self.assertFalse(result)
