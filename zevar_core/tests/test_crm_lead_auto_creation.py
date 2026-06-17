# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for CRM Lead Auto-Creation from POS Customer.

Covers:
- New walk-in customer creates CRM Lead
- CRM-origin customer (with crm_deal) is skipped
- Duplicate prevention by email/mobile
- Manual lead creation API

Run with: bench run-tests --app zevar_core --test test_crm_lead_auto_creation
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import random_string

crm_required = unittest.skipUnless(
	"crm" in (frappe.get_installed_apps() if frappe.db else []),
	"Frappe CRM app required",
)


@crm_required
class TestWalkInLeadAutoCreation(FrappeTestCase):
	"""Test that new POS customers automatically get a CRM Lead."""

	def setUp(self):
		frappe.set_user("Administrator")
		# Ensure CRM Lead Source exists
		if not frappe.db.exists("CRM Lead Source", "Walk-in"):
			frappe.get_doc({
				"doctype": "CRM Lead Source",
				"source_name": "Walk-in",
				"details": "Test",
			}).insert(ignore_permissions=True)
		if not frappe.db.exists("CRM Lead Status", "Open"):
			frappe.get_doc({
				"doctype": "CRM Lead Status",
				"lead_status": "Open",
				"color": "blue",
				"position": 1,
				"type": "Open",
			}).insert(ignore_permissions=True)

	def _make_customer(self, name=None, mobile=None, email=None, **kwargs):
		"""Helper to create a test customer."""
		suffix = random_string(6)
		customer = frappe.new_doc("Customer")
		customer.customer_name = name or f"Test Walkin {suffix}"
		customer.customer_type = "Individual"
		customer.customer_group = "Individual"
		customer.territory = "All Territories"
		if mobile:
			customer.mobile_no = mobile
		if email:
			customer.email_id = email
		for k, v in kwargs.items():
			setattr(customer, k, v)
		customer.insert(ignore_permissions=True)
		return customer

	def test_new_customer_creates_lead(self):
		"""A brand-new walk-in customer should auto-create a CRM Lead."""
		from zevar_core.api.crm_hooks import on_customer_created

		mobile = f"555{random_string(7)}"
		customer = self._make_customer(mobile=mobile)
		on_customer_created(customer)

		# Should have created a CRM Lead
		lead = frappe.db.exists("CRM Lead", {"mobile_no": mobile, "converted": 0})
		self.assertTrue(lead, "CRM Lead should be created for walk-in customer")

		# Customer should be back-linked
		lead_link = frappe.db.get_value("Customer", customer.name, "custom_crm_lead")
		self.assertEqual(lead_link, lead)

		# Cleanup
		frappe.delete_doc("CRM Lead", lead, force=True)
		frappe.delete_doc("Customer", customer.name, force=True)

	def test_crm_origin_customer_is_skipped(self):
		"""A customer created from CRM Deal flow should NOT get a new lead."""
		from zevar_core.api.crm_hooks import on_customer_created

		customer = self._make_customer()
		# Simulate CRM-origin by setting crm_deal
		frappe.db.set_value("Customer", customer.name, "crm_deal", "FAKE-DEAL-001")
		customer.reload()

		# Should not create lead
		lead_count_before = frappe.db.count("CRM Lead", {"custom_pos_customer": customer.name})
		on_customer_created(customer)
		lead_count_after = frappe.db.count("CRM Lead", {"custom_pos_customer": customer.name})

		self.assertEqual(lead_count_before, lead_count_after, "CRM-origin customer should be skipped")

		frappe.delete_doc("Customer", customer.name, force=True)

	def test_duplicate_prevention_by_email(self):
		"""Should not create a second lead if one already exists for the same email."""
		from zevar_core.api.crm_hooks import on_customer_created

		email = f"test{random_string(5)}@example.com"

		# Create first customer + lead
		cust1 = self._make_customer(email=email)
		on_customer_created(cust1)

		# Create second customer with same email
		cust2 = self._make_customer(email=email)
		on_customer_created(cust2)

		# Should only have one lead for this email
		leads = frappe.get_all("CRM Lead", filters={"email": email, "converted": 0})
		self.assertEqual(len(leads), 1, "Should not create duplicate leads for same email")

		# Cleanup
		for l in leads:
			frappe.delete_doc("CRM Lead", l.name, force=True)
		frappe.delete_doc("Customer", cust1.name, force=True)
		frappe.delete_doc("Customer", cust2.name, force=True)

	def test_manual_lead_creation_api(self):
		"""Manual lead creation API should work for existing customers."""
		from zevar_core.api.crm_hooks import create_lead_for_customer

		customer = self._make_customer()
		result = create_lead_for_customer(customer.name)

		self.assertTrue(result["success"])
		self.assertTrue(result["lead"])

		lead = frappe.get_doc("CRM Lead", result["lead"])
		self.assertEqual(lead.custom_pos_customer, customer.name)
		self.assertEqual(lead.custom_lead_origin, "POS Walk-in")

		# Cleanup
		frappe.delete_doc("CRM Lead", result["lead"], force=True)
		frappe.delete_doc("Customer", customer.name, force=True)
