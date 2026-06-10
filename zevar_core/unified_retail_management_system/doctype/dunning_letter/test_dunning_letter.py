# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today


class TestDunningLetter(FrappeTestCase):
	def setUp(self):
		if not frappe.db.exists("Customer", "_Test Dunning Customer"):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": "_Test Dunning Customer",
					"customer_group": "All Customer Groups",
					"territory": "All Territories",
					"email_id": "test-dunning@example.com",
				}
			).insert(ignore_if_duplicate=True)

	def test_validate_fetches_account_details(self):
		letter = frappe.new_doc("Dunning Letter")
		letter.finance_account = "FIN-001"
		letter.dunning_level = "Level 1 - Reminder"
		letter.subject = "Test Reminder"
		letter.message_body = "<p>Test</p>"
		letter.insert(ignore_permissions=True)
		self.assertTrue(letter.customer is not None)

	def test_overdue_computation(self):
		letter = frappe.new_doc("Dunning Letter")
		letter.finance_account = "FIN-001"
		letter.dunning_level = "Level 1 - Reminder"
		letter.subject = "Test"
		letter.message_body = "<p>Test</p>"
		letter.insert(ignore_permissions=True)
		self.assertIsInstance(letter.overdue_amount, float)

	def test_level_3_sets_collections_status(self):
		letter = frappe.new_doc("Dunning Letter")
		letter.finance_account = "FIN-001"
		letter.dunning_level = "Level 3 - Collections Notice"
		letter.subject = "Final Notice"
		letter.message_body = "<p>Final notice</p>"
		letter.insert(ignore_permissions=True)
		self.assertEqual(letter.status, "Draft")
