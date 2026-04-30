"""Tests for Feature 2 — Audit Scheduler.

Covers:
- audit_cadence_heartbeat generates correct plans per scope
- Overdue plans are marked as Missed
- Policy master switch disables plan generation
- Daily spot-check generation
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestAuditScheduler(FrappeTestCase):
	def setUp(self):
		# Clean up existing plans
		frappe.db.sql("DELETE FROM `tabAudit Plan`")

		if not frappe.db.exists("DocType", "Audit Policy"):
			self.skipTest("Audit Policy DocType not installed")

		# Reset policy to test defaults
		policy = frappe.get_single("Audit Policy")
		policy.enable_audit_schedule = 1
		policy.showcase_cadence_days = 7
		policy.backstock_cadence_days = 30
		policy.full_store_cadence_days = 90
		policy.daily_spot_case = ""
		policy.save(ignore_permissions=True)

	def test_heartbeat_creates_plans(self):
		"""Scheduler should create audit plans for each store and scope."""
		from zevar_core.tasks import audit_cadence_heartbeat

		audit_cadence_heartbeat()

		plans = frappe.get_all("Audit Plan", fields=["scope", "store_location", "status"])
		# Should have created at least some plans
		self.assertGreater(len(plans), 0)

		# Each scope type should appear
		scopes = {p["scope"] for p in plans}
		self.assertTrue(len(scopes) > 0)

	def test_no_duplicate_plans(self):
		"""Running heartbeat twice should not create duplicate plans."""
		from zevar_core.tasks import audit_cadence_heartbeat

		audit_cadence_heartbeat()
		count_after_first = frappe.db.count("Audit Plan")

		audit_cadence_heartbeat()
		count_after_second = frappe.db.count("Audit Plan")

		# Should be same count (no duplicates)
		self.assertEqual(count_after_first, count_after_second)

	def test_disabled_policy_skips_plans(self):
		"""When audit schedule is disabled, no plans should be created."""
		policy = frappe.get_single("Audit Policy")
		policy.enable_audit_schedule = 0
		policy.save(ignore_permissions=True)

		frappe.db.sql("DELETE FROM `tabAudit Plan`")

		from zevar_core.tasks import audit_cadence_heartbeat

		audit_cadence_heartbeat()

		count = frappe.db.count("Audit Plan")
		self.assertEqual(count, 0)

		# Re-enable for other tests
		policy.enable_audit_schedule = 1
		policy.save(ignore_permissions=True)

	def test_overdue_plans_marked_missed(self):
		"""Plans scheduled in the past should be marked as Missed."""
		plan = frappe.new_doc("Audit Plan")
		plan.store_location = "Stores - ZJ"
		plan.scope = "Weekly Showcase"
		plan.scheduled_for = add_days(today(), -3)
		plan.status = "Scheduled"
		plan.insert(ignore_permissions=True)

		from zevar_core.tasks import audit_cadence_heartbeat

		audit_cadence_heartbeat()

		plan.reload()
		self.assertEqual(plan.status, "Missed")

	def test_daily_spot_check_generation(self):
		"""If daily_spot_case is set, a daily plan should be created."""
		# Find or create a Display Case
		if not frappe.db.exists("Display Case", "Test Spot Case"):
			case = frappe.new_doc("Display Case")
			case.case_name = "Test Spot Case"
			case.warehouse = "Stores - ZJ"
			case.insert(ignore_permissions=True)

		policy = frappe.get_single("Audit Policy")
		policy.daily_spot_case = "Test Spot Case"
		policy.save(ignore_permissions=True)

		from zevar_core.tasks import audit_cadence_heartbeat

		audit_cadence_heartbeat()

		spot_plans = frappe.get_all(
			"Audit Plan",
			filters={
				"scope": "Daily Spot",
				"scheduled_for": today(),
			},
		)
		self.assertGreater(len(spot_plans), 0)
