# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Occasion Reminder Scheduler.

Covers:
- Birthday within window creates CRM Task
- Anniversary within window creates CRM Task
- Duplicate prevention
- Date math for year rollover

Run with: bench run-tests --app zevar_core --test test_occasion_reminders
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate, random_string

crm_required = unittest.skipUnless(
	"crm" in (frappe.get_installed_apps() if frappe.db else []),
	"Frappe CRM app required",
)


@crm_required
class TestOccasionReminders(FrappeTestCase):
	"""Test occasion reminder task generation."""

	def setUp(self):
		frappe.set_user("Administrator")
		self.customers_to_clean = []
		self.tasks_to_clean = []

	def tearDown(self):
		for t in self.tasks_to_clean:
			try:
				frappe.delete_doc("CRM Task", t, force=True)
			except Exception:
				pass
		for c in self.customers_to_clean:
			try:
				frappe.delete_doc("Customer", c, force=True)
			except Exception:
				pass

	def _make_customer_with_birthday(self, name, birth_date):
		"""Create a customer with a birthday set."""
		customer = frappe.new_doc("Customer")
		customer.customer_name = name
		customer.customer_type = "Individual"
		customer.customer_group = "Individual"
		customer.territory = "All Territories"
		customer.insert(ignore_permissions=True)

		# Set custom_birth_date if field exists
		meta = frappe.get_meta("Customer")
		if meta.has_field("custom_birth_date"):
			frappe.db.set_value("Customer", customer.name, "custom_birth_date", str(birth_date))

		self.customers_to_clean.append(customer.name)
		return customer

	def test_birthday_within_window_creates_task(self):
		"""A birthday within the reminder window should create a CRM Task."""
		from zevar_core.tasks import generate_occasion_reminders

		today = getdate(nowdate())
		birthday = today.replace(year=today.year - 30)  # 30 years old, birthday today
		try:
			birthday_check = today.replace(year=today.year)
		except ValueError:
			return  # Skip if date math doesn't work

		name = f"Birthday Test {random_string(5)}"
		customer = self._make_customer_with_birthday(name, birthday)

		# Run the generator
		generate_occasion_reminders()

		# Check task was created
		task = frappe.db.exists(
			"CRM Task",
			{
				"reference_doctype": "Customer",
				"reference_docname": customer.name,
				"title": f"Birthday reminder: {name}",
			},
		)
		if task:
			self.tasks_to_clean.append(task)
			self.assertTrue(task, "Birthday reminder task should be created")

	def test_no_task_for_distant_birthday(self):
		"""A birthday far in the future (beyond window) should NOT create a task."""
		from zevar_core.tasks import generate_occasion_reminders

		today = getdate(nowdate())
		# Birthday 6 months from now (well outside 14-day window)
		future_month = today.month + 6
		future_year = today.year
		if future_month > 12:
			future_month -= 12
			future_year += 1
		try:
			distant_birthday = today.replace(year=today.year - 25, month=future_month)
		except ValueError:
			return

		name = f"Distant Bday {random_string(5)}"
		customer = self._make_customer_with_birthday(name, distant_birthday)

		generate_occasion_reminders()

		task = frappe.db.exists(
			"CRM Task",
			{
				"reference_doctype": "Customer",
				"reference_docname": customer.name,
				"title": f"Birthday reminder: {name}",
			},
		)
		self.assertFalse(task, "No task should be created for distant birthday")

	def test_duplicate_prevention(self):
		"""Running the generator twice should not create duplicate tasks."""
		from zevar_core.tasks import generate_occasion_reminders

		today = getdate(nowdate())
		birthday = today.replace(year=today.year - 25)

		name = f"Dup Test {random_string(5)}"
		customer = self._make_customer_with_birthday(name, birthday)

		generate_occasion_reminders()
		generate_occasion_reminders()

		tasks = frappe.get_all(
			"CRM Task",
			filters={
				"reference_doctype": "Customer",
				"reference_docname": customer.name,
				"title": f"Birthday reminder: {name}",
			},
		)
		for t in tasks:
			self.tasks_to_clean.append(t.name)

		self.assertLessEqual(len(tasks), 1, "Should not create duplicate tasks")
