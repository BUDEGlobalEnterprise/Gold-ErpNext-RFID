# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for CRM Deal Auto-Creation from High-Value POS Sales.

Covers:
- High-value POS invoice creates CRM Deal
- Below-threshold invoice does not create deal
- Existing deal is updated (not duplicated) on subsequent purchases

Run with: bench run-tests --app zevar_core --test test_crm_deal_auto_creation
"""

import unittest
from unittest.mock import MagicMock

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import random_string

crm_required = unittest.skipUnless(
	"crm" in (frappe.get_installed_apps() if frappe.db else []),
	"Frappe CRM app required",
)


def _make_mock_invoice(customer_name, grand_total, is_pos=True, is_return=False, owner="Administrator"):
	"""Create a mock Sales Invoice for testing."""
	invoice = MagicMock()
	invoice.name = f"SINV-TEST-{random_string(6)}"
	invoice.customer = customer_name
	invoice.customer_name = customer_name
	invoice.grand_total = grand_total
	invoice.is_pos = is_pos
	invoice.is_return = is_return
	invoice.owner = owner
	invoice.sales_team = []
	return invoice


@crm_required
class TestHighValueDealAutoCreation(FrappeTestCase):
	"""Test that high-value POS sales auto-create CRM Deals."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Ensure CRM Deal Status exists
		if not frappe.db.exists("CRM Deal Status", "Qualification"):
			frappe.get_doc({
				"doctype": "CRM Deal Status",
				"deal_status": "Qualification",
				"color": "blue",
				"position": 1,
				"probability": 20,
				"type": "Open",
			}).insert(ignore_permissions=True)
		if not frappe.db.exists("CRM Lead Source", "Walk-in"):
			frappe.get_doc({
				"doctype": "CRM Lead Source",
				"source_name": "Walk-in",
			}).insert(ignore_permissions=True)

	def setUp(self):
		frappe.set_user("Administrator")
		# Create a test customer
		suffix = random_string(6)
		self.customer = frappe.new_doc("Customer")
		self.customer.customer_name = f"Deal Test Customer {suffix}"
		self.customer.customer_type = "Individual"
		self.customer.customer_group = "Individual"
		self.customer.territory = "All Territories"
		self.customer.insert(ignore_permissions=True)

	def tearDown(self):
		# Clean up deals and customer
		deals = frappe.get_all("CRM Deal", filters={"custom_pos_customer": self.customer.name})
		for d in deals:
			frappe.delete_doc("CRM Deal", d.name, force=True)
		frappe.delete_doc("Customer", self.customer.name, force=True)

	def test_high_value_invoice_creates_deal(self):
		"""A POS invoice above the threshold should create a CRM Deal."""
		from zevar_core.api.crm_hooks import on_invoice_submit_crm

		invoice = _make_mock_invoice(self.customer.name, 10000)
		on_invoice_submit_crm(invoice)

		deal = frappe.db.exists("CRM Deal", {"custom_originating_invoice": invoice.name})
		self.assertTrue(deal, "CRM Deal should be created for high-value sale")

		deal_doc = frappe.get_doc("CRM Deal", deal)
		self.assertEqual(deal_doc.deal_value, 10000)
		self.assertEqual(deal_doc.probability, 50)
		self.assertEqual(deal_doc.custom_pos_customer, self.customer.name)

	def test_below_threshold_no_deal(self):
		"""A POS invoice below the threshold should NOT create a CRM Deal."""
		from zevar_core.api.crm_hooks import on_invoice_submit_crm

		invoice = _make_mock_invoice(self.customer.name, 500)  # Below $5000 default
		on_invoice_submit_crm(invoice)

		deal = frappe.db.exists("CRM Deal", {"custom_originating_invoice": invoice.name})
		self.assertFalse(deal, "No deal should be created for below-threshold sale")

	def test_non_pos_invoice_skipped(self):
		"""Non-POS invoices should be skipped entirely."""
		from zevar_core.api.crm_hooks import on_invoice_submit_crm

		invoice = _make_mock_invoice(self.customer.name, 50000, is_pos=False)
		on_invoice_submit_crm(invoice)

		deal = frappe.db.exists("CRM Deal", {"custom_pos_customer": self.customer.name})
		self.assertFalse(deal, "Non-POS invoices should be skipped")

	def test_return_invoice_skipped(self):
		"""Return invoices should be skipped."""
		from zevar_core.api.crm_hooks import on_invoice_submit_crm

		invoice = _make_mock_invoice(self.customer.name, 10000, is_return=True)
		on_invoice_submit_crm(invoice)

		deal = frappe.db.exists("CRM Deal", {"custom_pos_customer": self.customer.name})
		self.assertFalse(deal, "Return invoices should be skipped")

	def test_existing_deal_is_updated(self):
		"""If customer already has an open deal, subsequent purchases update it."""
		from zevar_core.api.crm_hooks import on_invoice_submit_crm

		# First high-value purchase creates deal
		invoice1 = _make_mock_invoice(self.customer.name, 10000)
		on_invoice_submit_crm(invoice1)

		deal = frappe.db.exists("CRM Deal", {"custom_originating_invoice": invoice1.name})
		self.assertTrue(deal)

		# Link the deal to customer
		frappe.db.set_value("Customer", self.customer.name, "custom_crm_deal", deal)

		# Second purchase should update existing deal (not create new one)
		invoice2 = _make_mock_invoice(self.customer.name, 5000)
		on_invoice_submit_crm(invoice2)

		deal_doc = frappe.get_doc("CRM Deal", deal)
		self.assertEqual(deal_doc.deal_value, 15000, "Deal value should accumulate")

		# Should still be only one deal
		all_deals = frappe.get_all("CRM Deal", filters={"custom_pos_customer": self.customer.name})
		self.assertEqual(len(all_deals), 1, "Should not create duplicate deals")
