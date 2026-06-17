# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for CRM Pipeline data in the Clienteling Intelligence API.

Covers:
- Intelligence API returns pipeline data
- No CRM link returns empty pipeline
- CRM task creation from POS API

Run with: bench run-tests --app zevar_core --test test_clienteling_crm_tab
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
class TestClientelingCRMPipeline(FrappeTestCase):
	"""Test CRM pipeline data in the clienteling intelligence API."""

	def setUp(self):
		frappe.set_user("Administrator")
		# Create a test customer
		suffix = random_string(6)
		self.customer = frappe.new_doc("Customer")
		self.customer.customer_name = f"CRM Tab Test {suffix}"
		self.customer.customer_type = "Individual"
		self.customer.customer_group = "Individual"
		self.customer.territory = "All Territories"
		self.customer.insert(ignore_permissions=True)
		self.cleanup_items = []

	def tearDown(self):
		for item in self.cleanup_items:
			try:
				frappe.delete_doc(item[0], item[1], force=True)
			except Exception:
				pass
		try:
			frappe.delete_doc("Customer", self.customer.name, force=True)
		except Exception:
			pass

	def test_intelligence_returns_pipeline_key(self):
		"""The intelligence API should return a 'pipeline' key."""
		from zevar_core.api.clienteling import get_customer_intelligence

		result = get_customer_intelligence(self.customer.name)
		self.assertIn("pipeline", result)
		self.assertIn("lead", result["pipeline"])
		self.assertIn("deal", result["pipeline"])
		self.assertIn("tasks", result["pipeline"])

	def test_empty_pipeline_for_no_crm_links(self):
		"""A customer with no CRM links should have empty pipeline."""
		from zevar_core.api.clienteling import get_customer_intelligence

		result = get_customer_intelligence(self.customer.name)
		pipeline = result["pipeline"]
		self.assertIsNone(pipeline["lead"])
		self.assertIsNone(pipeline["deal"])
		self.assertEqual(pipeline["tasks"], [])

	def test_pipeline_shows_linked_lead(self):
		"""When customer has a CRM Lead, pipeline should show it."""
		from zevar_core.api.clienteling import get_customer_intelligence

		# Create a CRM Lead linked to this customer
		if not frappe.db.exists("CRM Lead Status", "Open"):
			frappe.get_doc({
				"doctype": "CRM Lead Status",
				"lead_status": "Open",
				"color": "blue",
				"position": 1,
				"type": "Open",
			}).insert(ignore_permissions=True)

		lead = frappe.get_doc({
			"doctype": "CRM Lead",
			"first_name": "Test",
			"last_name": "CRM",
			"lead_name": self.customer.customer_name,
			"status": "Open",
			"custom_pos_customer": self.customer.name,
		})
		lead.insert(ignore_permissions=True)
		self.cleanup_items.append(("CRM Lead", lead.name))

		# Link customer to lead
		frappe.db.set_value("Customer", self.customer.name, "custom_crm_lead", lead.name)

		result = get_customer_intelligence(self.customer.name)
		self.assertIsNotNone(result["pipeline"]["lead"])
		self.assertEqual(result["pipeline"]["lead"]["name"], lead.name)
		self.assertEqual(result["pipeline"]["lead"]["status"], "Open")

	def test_create_crm_task_from_pos(self):
		"""Creating a CRM Task from POS should work."""
		from zevar_core.api.clienteling import create_crm_task_from_pos

		result = create_crm_task_from_pos(
			customer=self.customer.name,
			title="Follow up on ring sizing",
			due_date=None,
			description="Customer asked about ring resizing service",
		)

		self.assertTrue(result["success"])
		self.assertTrue(result["task"])
		self.cleanup_items.append(("CRM Task", result["task"]))

		task = frappe.get_doc("CRM Task", result["task"])
		self.assertEqual(task.title, "Follow up on ring sizing")
		self.assertEqual(task.reference_doctype, "Customer")
		self.assertEqual(task.reference_docname, self.customer.name)
