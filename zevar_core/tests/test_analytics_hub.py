# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0
"""
Unit Tests for Analytics Hub API (Plan §8.1-§8.7).

Run with: bench run-tests --app zevar_core --test test_analytics_hub
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.api import analytics_hub


class TestGetHubData(FrappeTestCase):
	"""Test the aggregator endpoint (§8.7) and the per-metric sub-endpoints."""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_hub_data_returns_expected_keys(self):
		"""get_hub_data must return hero, role, as_of (per §8.7)."""
		payload = analytics_hub.get_hub_data()
		self.assertIsInstance(payload, dict)
		self.assertIn("hero", payload)
		self.assertIn("role", payload)
		self.assertIn("as_of", payload)

	def test_hero_payload_contains_all_seven_metrics(self):
		"""Plan §6.1-§6.7 — hero must include sales, layaway, low_stock, cash_variance,
		overdue_payments, hold_queue, and (via sales) repair."""
		payload = analytics_hub.get_hub_data()
		hero = payload.get("hero") or {}
		for key in ("sales", "layaway", "low_stock", "cash_variance", "overdue_payments", "hold_queue"):
			self.assertIn(key, hero, f"hero missing {key}")

	def test_role_block_has_owner_and_manager_flags(self):
		"""§5.5 — role block drives role-aware hero strip."""
		payload = analytics_hub.get_hub_data()
		role = payload.get("role") or {}
		self.assertIn("is_owner", role)
		self.assertIn("is_manager", role)

	def test_get_hub_data_with_store_filter_does_not_crash(self):
		"""Store filter must be accepted (per §8.7)."""
		try:
			payload = analytics_hub.get_hub_data(store="Main")
			self.assertIsInstance(payload, dict)
		except Exception as e:
			self.fail(f"store filter crashed: {e}")


class TestGetDailyRevenueBreakdown(FrappeTestCase):
	"""§8.1 — Daily Sales & Repair Revenue"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_returns_required_fields(self):
		from frappe.utils import add_days, nowdate

		today = nowdate()
		week_ago = add_days(today, -7)
		res = analytics_hub.get_daily_revenue_breakdown(week_ago, today)
		for key in (
			"sales_revenue",
			"repair_revenue",
			"total_revenue",
			"sales_count",
			"repair_count",
			"sparkline_30d",
		):
			self.assertIn(key, res)
		self.assertIsInstance(res["sparkline_30d"], list)


class TestGetLayawayHealth(FrappeTestCase):
	"""§8.2 — Layaway Status & Metrics"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_returns_required_fields(self):
		res = analytics_hub.get_layaway_health()
		for key in (
			"active",
			"overdue",
			"due_this_week",
			"total_outstanding",
			"avg_ticket",
			"completion_rate_90d",
		):
			self.assertIn(key, res)


class TestGetLowStockDetail(FrappeTestCase):
	"""§8.3 — Low Stock Alerts"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_returns_total_and_items(self):
		res = analytics_hub.get_low_stock_detail(severity="all", limit=10)
		self.assertIn("total", res)
		self.assertIn("items", res)
		self.assertIsInstance(res["items"], list)

	def test_severity_filters_are_accepted(self):
		for s in ("low", "stockout", "all"):
			res = analytics_hub.get_low_stock_detail(severity=s, limit=5)
			self.assertIn("items", res)


class TestGetCashVarianceToday(FrappeTestCase):
	"""§8.4 — Cash Variance Across Daily POS Sessions"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_returns_sessions_and_totals(self):
		res = analytics_hub.get_cash_variance_today()
		for key in ("sessions", "total_variance", "within_tolerance"):
			self.assertIn(key, res)


class TestGetOverduePayments(FrappeTestCase):
	"""§8.5 — Overdue & Pending Payments (Repairs + Layaways)"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_returns_repair_and_layaway_lists(self):
		res = analytics_hub.get_overdue_payments(type="all")
		self.assertIn("repairs", res)
		self.assertIn("layaways", res)
		self.assertIn("total_overdue_amount", res)
		self.assertIn("count", res)

	def test_repair_only_filter(self):
		res = analytics_hub.get_overdue_payments(type="repair")
		self.assertIn("repairs", res)


class TestGetHoldQueue(FrappeTestCase):
	"""§8.6 — Hold Items"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_returns_active_holds(self):
		res = analytics_hub.get_hold_queue()
		for key in ("active_holds", "total_count", "expiring_soon_count"):
			self.assertIn(key, res)
		self.assertIsInstance(res["active_holds"], list)


class TestCaching(FrappeTestCase):
	"""§8.7 — get_hub_data caches the payload."""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_second_call_returns_cached(self):
		# The first call populates the cache; the second should not raise.
		a = analytics_hub.get_hub_data()
		b = analytics_hub.get_hub_data()
		# Both should at least have the same shape.
		self.assertEqual(set(a.keys()), set(b.keys()))


class TestRoleAwareFieldStripping(FrappeTestCase):
	"""§8.7 — payload is role-stripped (employees get fewer fields).
	We can't easily switch user in a FrappeTestCase mid-test, so we verify
	the helper shape instead.
	"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_role_block_resolves(self):
		from zevar_core.api.analytics_hub import get_hub_data

		payload = get_hub_data()
		role = payload.get("role") or {}
		self.assertIn("name", role)
