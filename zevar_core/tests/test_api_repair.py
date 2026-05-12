# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Repair API modules
Covers: repair.py (40 endpoints), repair_calendar.py (9),
         repair_accounting.py (7), repair_customer_portal.py (10),
         repair_dashboard.py (2)

Run with: bench run-tests --app zevar_core --test test_api_repair
"""

import json
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today

from zevar_core.tests.utils import (
	ensure_customer,
	ensure_item,
	ensure_warehouse,
	get_test_company,
)

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Repair Order"),
	"ERPNext required (Repair Order DocType not found)",
)


def _ensure_repair_type(name="Test Repair Type"):
	"""Create a test repair type if it doesn't exist."""
	if frappe.db.exists("Repair Type", name):
		return name
	doc = frappe.new_doc("Repair Type")
	doc.repair_type_name = name
	doc.is_active = 1
	doc.insert(ignore_permissions=True, ignore_mandatory=True)
	return name


# ─── REPAIR API TESTS ───────────────────────────────────────────────────────────


@erpnext_required
class TestRepairAPI(FrappeTestCase):
	"""Test repair.py endpoints"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = get_test_company()
		cls.customer = ensure_customer("Repair API Test Customer")
		cls.warehouse = ensure_warehouse("Repair API Test WH")
		cls.item_code = ensure_item("REPAIR-API-001", "Repair API Test Item", rate=200)
		cls.repair_type = _ensure_repair_type()

	def setUp(self):
		frappe.set_user("Administrator")
		self._created_orders = []

	def tearDown(self):
		for name in self._created_orders:
			try:
				doc = frappe.get_doc("Repair Order", name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Repair Order", name, ignore_permissions=True, force=True)
			except Exception:
				pass

	# ── get_repair_types ──

	def test_get_repair_types_returns_list(self):
		from zevar_core.api.repair import get_repair_types
		result = get_repair_types()
		self.assertIsInstance(result, list)

	def test_get_repair_types_active_only(self):
		from zevar_core.api.repair import get_repair_types
		result = get_repair_types(active_only=True)
		self.assertIsInstance(result, list)

	def test_get_repair_types_all(self):
		from zevar_core.api.repair import get_repair_types
		result = get_repair_types(active_only=False)
		self.assertIsInstance(result, list)

	# ── get_repair_orders ──

	def test_get_repair_orders_returns_list(self):
		from zevar_core.api.repair import get_repair_orders
		result = get_repair_orders()
		self.assertIsInstance(result, list)

	def test_get_repair_orders_with_status_filter(self):
		from zevar_core.api.repair import get_repair_orders
		result = get_repair_orders(status="Received")
		self.assertIsInstance(result, list)
		for order in result:
			self.assertEqual(order["status"], "Received")

	def test_get_repair_orders_with_search(self):
		from zevar_core.api.repair import get_repair_orders
		result = get_repair_orders(search_term="NONEXISTENT-REPAIR-99999")
		self.assertIsInstance(result, list)

	def test_get_repair_orders_with_customer_filter(self):
		from zevar_core.api.repair import get_repair_orders
		result = get_repair_orders(customer=self.customer)
		self.assertIsInstance(result, list)

	def test_get_repair_orders_pagination(self):
		from zevar_core.api.repair import get_repair_orders
		result = get_repair_orders(start=0, page_length=5)
		self.assertIsInstance(result, list)
		self.assertLessEqual(len(result), 5)

	# ── get_repair_order_details ──

	def test_get_details_nonexistent_raises(self):
		from zevar_core.api.repair import get_repair_order_details
		with self.assertRaises(frappe.DoesNotExistError):
			get_repair_order_details("NONEXISTENT-RO-99999")

	# ── get_repair_stats ──

	def test_get_repair_stats_returns_dict(self):
		from zevar_core.api.repair import get_repair_stats
		result = get_repair_stats()
		self.assertIsInstance(result, dict)

	# ── get_customer_repair_history ──

	def test_get_customer_history(self):
		from zevar_core.api.repair import get_customer_repair_history
		result = get_customer_repair_history(customer=self.customer)
		self.assertIsInstance(result, list)

	# ── lookup_repair_by_number ──

	def test_lookup_by_number_nonexistent(self):
		from zevar_core.api.repair import lookup_repair_by_number
		result = lookup_repair_by_number("NONEXISTENT-99999")
		self.assertIsInstance(result, (dict, list, type(None)))

	def test_lookup_by_number_empty(self):
		from zevar_core.api.repair import lookup_repair_by_number
		result = lookup_repair_by_number("")
		self.assertIsInstance(result, (dict, list, type(None)))

	# ── lookup_repair_by_phone ──

	def test_lookup_by_phone_nonexistent(self):
		from zevar_core.api.repair import lookup_repair_by_phone
		result = lookup_repair_by_phone("999-999-9999")
		self.assertIsInstance(result, list)

	def test_lookup_by_phone_short(self):
		from zevar_core.api.repair import lookup_repair_by_phone
		result = lookup_repair_by_phone("12")
		self.assertIsInstance(result, list)

	# ── check_warranty_status ──

	def test_check_warranty_nonexistent(self):
		from zevar_core.api.repair import check_warranty_status
		result = check_warranty_status("NONEXISTENT-99999")
		self.assertIsInstance(result, dict)

	# ── get_warranty_repairs ──

	def test_get_warranty_repairs(self):
		from zevar_core.api.repair import get_warranty_repairs
		result = get_warranty_repairs(customer=self.customer)
		self.assertIsInstance(result, list)

	# ── get_customer_warranties ──

	def test_get_customer_warranties(self):
		from zevar_core.api.repair import get_customer_warranties
		result = get_customer_warranties(customer=self.customer)
		self.assertIsInstance(result, list)

	# ── get_payment_summary ──

	def test_get_payment_summary_nonexistent(self):
		from zevar_core.api.repair import get_payment_summary
		with self.assertRaises(Exception):
			get_payment_summary("NONEXISTENT-99999")

	# ── get_communications ──

	def test_get_communications_nonexistent(self):
		from zevar_core.api.repair import get_communications
		result = get_communications("NONEXISTENT-99999")
		self.assertIsInstance(result, list)

	# ── get_multi_store_stats ──

	def test_get_multi_store_stats(self):
		from zevar_core.api.repair import get_multi_store_stats
		result = get_multi_store_stats()
		self.assertIsInstance(result, dict)

	# ── get_store_transfers ──

	def test_get_store_transfers(self):
		from zevar_core.api.repair import get_store_transfers
		result = get_store_transfers()
		self.assertIsInstance(result, list)


# ─── REPAIR CALENDAR API TESTS ───────────────────────────────────────────────────


@erpnext_required
class TestRepairCalendarAPI(FrappeTestCase):
	"""Test repair_calendar.py endpoints"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_calendar_events(self):
		from zevar_core.api.repair_calendar import get_calendar_events
		result = get_calendar_events()
		self.assertIsInstance(result, list)

	def test_get_calendar_events_with_warehouse(self):
		from zevar_core.api.repair_calendar import get_calendar_events
		wh = ensure_warehouse("Calendar Test WH")
		result = get_calendar_events(warehouse=wh)
		self.assertIsInstance(result, list)

	def test_get_technician_schedule(self):
		from zevar_core.api.repair_calendar import get_technician_schedule
		result = get_technician_schedule()
		self.assertIsInstance(result, (dict, list))

	def test_get_overdue_alerts(self):
		from zevar_core.api.repair_calendar import get_overdue_alerts
		result = get_overdue_alerts()
		self.assertIsInstance(result, list)

	def test_get_overdue_alerts_with_min_days(self):
		from zevar_core.api.repair_calendar import get_overdue_alerts
		result = get_overdue_alerts(min_days_overdue=7)
		self.assertIsInstance(result, list)

	def test_get_daily_summary(self):
		from zevar_core.api.repair_calendar import get_daily_summary
		result = get_daily_summary()
		self.assertIsInstance(result, dict)

	def test_get_daily_summary_specific_date(self):
		from zevar_core.api.repair_calendar import get_daily_summary
		result = get_daily_summary(date=today())
		self.assertIsInstance(result, dict)


# ─── REPAIR ACCOUNTING API TESTS ─────────────────────────────────────────────────


@erpnext_required
class TestRepairAccountingAPI(FrappeTestCase):
	"""Test repair_accounting.py endpoints"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_revenue_recognition(self):
		from zevar_core.api.repair_accounting import get_revenue_recognition
		result = get_revenue_recognition()
		self.assertIsInstance(result, (dict, list))

	def test_get_revenue_recognition_with_warehouse(self):
		from zevar_core.api.repair_accounting import get_revenue_recognition
		wh = ensure_warehouse("Acct Test WH")
		result = get_revenue_recognition(warehouse=wh)
		self.assertIsInstance(result, (dict, list))

	def test_get_materials_consumed(self):
		from zevar_core.api.repair_accounting import get_materials_consumed
		result = get_materials_consumed()
		self.assertIsInstance(result, (dict, list))

	def test_get_technician_commission(self):
		from zevar_core.api.repair_accounting import get_technician_commission
		result = get_technician_commission()
		self.assertIsInstance(result, (dict, list))

	def test_get_payment_reconciliation(self):
		from zevar_core.api.repair_accounting import get_payment_reconciliation
		result = get_payment_reconciliation()
		self.assertIsInstance(result, dict)

	def test_get_profitability_report(self):
		from zevar_core.api.repair_accounting import get_profitability_report
		result = get_profitability_report()
		self.assertIsInstance(result, dict)

	def test_create_journal_entry_nonexistent(self):
		from zevar_core.api.repair_accounting import create_journal_entry_for_repair
		result = create_journal_entry_for_repair("NONEXISTENT-99999")
		self.assertFalse(result.get("success", True))

	def test_process_commission_payment_no_data(self):
		from zevar_core.api.repair_accounting import process_commission_payment
		result = process_commission_payment(technician="NONEXISTENT", amount=0)
		self.assertIsInstance(result, (dict, bool))


# ─── REPAIR CUSTOMER PORTAL API TESTS ────────────────────────────────────────────


@erpnext_required
class TestRepairPortalAPI(FrappeTestCase):
	"""Test repair_customer_portal.py endpoints"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_customer_lookup_by_phone_nonexistent(self):
		from zevar_core.api.repair_customer_portal import customer_lookup
		result = customer_lookup(phone="999-999-9999")
		self.assertIsInstance(result, (dict, list, type(None)))

	def test_customer_lookup_empty(self):
		from zevar_core.api.repair_customer_portal import customer_lookup
		result = customer_lookup()
		self.assertIsInstance(result, (dict, list, type(None)))

	def test_verify_session_empty_token(self):
		from zevar_core.api.repair_customer_portal import verify_session
		result = verify_session(token="", code="")
		self.assertIsInstance(result, (dict, type(None)))

	def test_verify_session_invalid_token(self):
		from zevar_core.api.repair_customer_portal import verify_session
		result = verify_session(token="INVALID-TOKEN-99999", code="1234")
		self.assertIsInstance(result, (dict, type(None)))

	def test_get_customer_repairs_invalid_token(self):
		from zevar_core.api.repair_customer_portal import get_customer_repairs
		result = get_customer_repairs(session_token="INVALID-TOKEN-99999")
		self.assertIsInstance(result, (dict, list, type(None)))

	def test_get_repair_detail_invalid_token(self):
		from zevar_core.api.repair_customer_portal import get_repair_detail
		result = get_repair_detail(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, type(None)))

	def test_upload_reference_photo_invalid_token(self):
		from zevar_core.api.repair_customer_portal import upload_reference_photo
		result = upload_reference_photo(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, type(None)))

	def test_customer_approve_estimate_invalid_token(self):
		from zevar_core.api.repair_customer_portal import customer_approve_estimate
		result = customer_approve_estimate(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, type(None)))

	def test_customer_reject_estimate_invalid_token(self):
		from zevar_core.api.repair_customer_portal import customer_reject_estimate
		result = customer_reject_estimate(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, type(None)))

	def test_request_repair_update_invalid_token(self):
		from zevar_core.api.repair_customer_portal import request_repair_update
		result = request_repair_update(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, type(None)))

	def test_get_repair_history_invalid_token(self):
		from zevar_core.api.repair_customer_portal import get_repair_history
		result = get_repair_history(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, list, type(None)))

	def test_schedule_pickup_invalid_token(self):
		from zevar_core.api.repair_customer_portal import schedule_pickup
		result = schedule_pickup(session_token="INVALID-TOKEN-99999", repair_id="NONEXISTENT")
		self.assertIsInstance(result, (dict, type(None)))


# ─── REPAIR DASHBOARD API TESTS ──────────────────────────────────────────────────


@erpnext_required
class TestRepairDashboardAPI(FrappeTestCase):
	"""Test repair_dashboard.py endpoints"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_dashboard_stats_returns_dict(self):
		from zevar_core.api.repair_dashboard import get_repair_dashboard_stats
		result = get_repair_dashboard_stats()
		self.assertIsInstance(result, dict)

	def test_dashboard_stats_has_required_keys(self):
		from zevar_core.api.repair_dashboard import get_repair_dashboard_stats
		result = get_repair_dashboard_stats()
		expected_keys = [
			"overdue_count", "ready_pickup_count", "weekly_revenue",
			"monthly_revenue", "avg_turnaround_days", "status_breakdown",
			"technician_workload", "recent_overdue", "top_repair_types",
			"pending_collections_amount", "pending_collections_count",
		]
		for key in expected_keys:
			self.assertIn(key, result, f"Dashboard stats missing key: {key}")

	def test_dashboard_stats_types(self):
		from zevar_core.api.repair_dashboard import get_repair_dashboard_stats
		result = get_repair_dashboard_stats()
		self.assertIsInstance(result["overdue_count"], int)
		self.assertIsInstance(result["weekly_revenue"], (int, float))
		self.assertIsInstance(result["monthly_revenue"], (int, float))
		self.assertIsInstance(result["status_breakdown"], dict)

	def test_dashboard_stats_with_warehouse(self):
		from zevar_core.api.repair_dashboard import get_repair_dashboard_stats
		wh = ensure_warehouse("Dashboard Test WH")
		result = get_repair_dashboard_stats(warehouse=wh)
		self.assertIsInstance(result, dict)

	def test_get_chart_data_returns_dict(self):
		from zevar_core.api.repair_dashboard import get_repair_chart_data
		result = get_repair_chart_data()
		self.assertIsInstance(result, dict)

	def test_chart_data_has_required_keys(self):
		from zevar_core.api.repair_dashboard import get_repair_chart_data
		result = get_repair_chart_data()
		self.assertIn("daily_repairs", result)
		self.assertIn("by_status", result)
		self.assertIn("revenue_trend", result)

	def test_chart_data_daily_structure(self):
		from zevar_core.api.repair_dashboard import get_repair_chart_data
		result = get_repair_chart_data()
		daily = result["daily_repairs"]
		self.assertIn("labels", daily)
		self.assertIn("values", daily)
		self.assertEqual(len(daily["labels"]), len(daily["values"]))

	def test_chart_data_with_period(self):
		from zevar_core.api.repair_dashboard import get_repair_chart_data
		result = get_repair_chart_data(period=60)
		self.assertIsInstance(result, dict)
		# 60 days should produce 60 data points
		self.assertEqual(len(result["daily_repairs"]["labels"]), 60)

	def test_chart_data_default_period_30(self):
		from zevar_core.api.repair_dashboard import get_repair_chart_data
		result = get_repair_chart_data()
		self.assertEqual(len(result["daily_repairs"]["labels"]), 30)
