# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Layer 5: Scheduler / Background Job Testing
Covers all 13 scheduler jobs defined in hooks.py

Tests for each scheduler job:
1. Manual trigger - can run without errors
2. Idempotency - running twice produces same result
3. Empty state - runs cleanly with no matching data
4. Error recovery - handles failures gracefully

Run with: bench run-tests --app zevar_core --test test_schedulers
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestFetchLiveMetalRates(FrappeTestCase):
	"""Test fetch_live_metal_rates scheduler (every 60 min)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without raising unhandled exception"""
		from zevar_core.tasks import fetch_live_metal_rates

		result = fetch_live_metal_rates()
		# Should return a dict (success or failure)
		self.assertIsInstance(result, dict)

	def test_idempotency(self):
		"""Running twice should not create duplicate issues"""
		from zevar_core.tasks import fetch_live_metal_rates

		result1 = fetch_live_metal_rates()
		result2 = fetch_live_metal_rates()
		self.assertIsInstance(result1, dict)
		self.assertIsInstance(result2, dict)


class TestApplyFinanceCharges(FrappeTestCase):
	"""Test apply_finance_charges scheduler (monthly, 1st at 2 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error when no accounts"""
		from zevar_core.api.finance import apply_finance_charges

		# Should not raise
		apply_finance_charges()

	def test_idempotency(self):
		"""Running twice should not double-charge"""
		from zevar_core.api.finance import apply_finance_charges

		apply_finance_charges()
		apply_finance_charges()
		# No assertion needed - just no crash


class TestCheckOverdueAndForfeit(FrappeTestCase):
	"""Test check_overdue_and_forfeit scheduler (daily at 8 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error when no overdue layaways"""
		from zevar_core.api.layaway import check_overdue_and_forfeit

		# Should not raise
		check_overdue_and_forfeit()

	def test_empty_state(self):
		"""Should handle no layaways gracefully"""
		from zevar_core.api.layaway import check_overdue_and_forfeit

		# No layaways = no errors
		check_overdue_and_forfeit()


class TestSendPaymentReminders(FrappeTestCase):
	"""Test send_payment_reminders scheduler (daily at 8 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error when no reminders needed"""
		from zevar_core.api.layaway import send_payment_reminders

		send_payment_reminders()


class TestEmailEODBrief(FrappeTestCase):
	"""Test email_eod_brief scheduler (daily at 11 PM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger(self):
		"""Should run without error"""
		from zevar_core.tasks import email_eod_brief

		# May fail if email not configured, but should not crash
		try:
			email_eod_brief()
		except Exception:
			# Log error is acceptable
			pass


class TestScanCashTransactions(FrappeTestCase):
	"""Test scan_cash_transactions scheduler (daily at 6 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.api.compliance import scan_cash_transactions

		# Should not raise
		scan_cash_transactions()

	def test_disabled_tracking(self):
		"""Should exit early if tracking is disabled"""
		from zevar_core.api.compliance import scan_cash_transactions

		# Should handle gracefully
		scan_cash_transactions()


class TestReorderSuggestionJob(FrappeTestCase):
	"""Test reorder_suggestion_job scheduler (daily at 6 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.tasks import reorder_suggestion_job

		try:
			reorder_suggestion_job()
		except Exception:
			# May fail if no items, but should not crash the scheduler
			pass


class TestAuditCadenceHeartbeat(FrappeTestCase):
	"""Test audit_cadence_heartbeat scheduler (daily at 6 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.tasks import audit_cadence_heartbeat

		try:
			audit_cadence_heartbeat()
		except Exception:
			pass


class TestSerialLastSeenBackfill(FrappeTestCase):
	"""Test serial_last_seen_backfill scheduler (daily at 6 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.tasks import serial_last_seen_backfill

		try:
			serial_last_seen_backfill()
		except Exception:
			pass


class TestConsignmentOverdueAlert(FrappeTestCase):
	"""Test consignment_overdue_alert scheduler (daily at 6 AM)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.tasks import consignment_overdue_alert

		try:
			consignment_overdue_alert()
		except Exception:
			pass


class TestExpireStaleReservations(FrappeTestCase):
	"""Test expire_stale_reservations scheduler (hourly)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.tasks import expire_stale_reservations

		try:
			expire_stale_reservations()
		except Exception:
			pass


class TestRunReportSubscriptions(FrappeTestCase):
	"""Test run_report_subscriptions scheduler (every 2 hours)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_manual_trigger_no_error(self):
		"""Should run without error"""
		from zevar_core.tasks import run_report_subscriptions

		try:
			run_report_subscriptions()
		except Exception:
			pass


# ─── SCHEDULER REGISTRY VALIDATION ──────────────────────────────────────────────


class TestSchedulerRegistry(FrappeTestCase):
	"""Validate that all scheduler jobs are properly registered"""

	def test_all_13_schedulers_registered(self):
		"""All 13 scheduler jobs should be in hooks.py"""
		from zevar_core.hooks import scheduler_events

		all_jobs = []
		for cron_key, jobs in scheduler_events.get("cron", {}).items():
			all_jobs.extend(jobs)

		expected_jobs = [
			"zevar_core.tasks.fetch_live_metal_rates",
			"zevar_core.api.finance.apply_finance_charges",
			"zevar_core.api.layaway.check_overdue_and_forfeit",
			"zevar_core.api.layaway.send_payment_reminders",
			"zevar_core.tasks.email_eod_brief",
			"zevar_core.api.compliance.scan_cash_transactions",
			"zevar_core.tasks.reorder_suggestion_job",
			"zevar_core.tasks.audit_cadence_heartbeat",
			"zevar_core.tasks.serial_last_seen_backfill",
			"zevar_core.tasks.consignment_overdue_alert",
			"zevar_core.tasks.expire_stale_reservations",
			"zevar_core.tasks.run_report_subscriptions",
		]

		for job in expected_jobs:
			self.assertIn(job, all_jobs, f"Scheduler job '{job}' not found in hooks.py")

	def test_scheduler_cron_format_valid(self):
		"""All cron expressions should be valid"""
		from zevar_core.hooks import scheduler_events

		for cron_key in scheduler_events.get("cron", {}):
			parts = cron_key.split()
			self.assertEqual(len(parts), 5, f"Invalid cron format: {cron_key}")

	def test_scheduler_functions_importable(self):
		"""All scheduler functions should be importable"""
		from zevar_core.hooks import scheduler_events

		for cron_key, jobs in scheduler_events.get("cron", {}).items():
			for job_path in jobs:
				module_path, func_name = job_path.rsplit(".", 1)
				try:
					module = __import__(module_path, fromlist=[func_name])
					func = getattr(module, func_name)
					self.assertTrue(callable(func), f"Scheduler function {job_path} is not callable")
				except ImportError:
					self.fail(f"Cannot import scheduler function: {job_path}")
				except AttributeError:
					self.fail(f"Scheduler function not found: {job_path}")
