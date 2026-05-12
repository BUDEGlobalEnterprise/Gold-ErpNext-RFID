# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Shortcuts API (shortcuts.py)
Covers: get_desk_shortcuts, get_shortcuts, get_shortcut_sections,
        get_quick_stats, get_recent_activity

Run with: bench run-tests --app zevar_core --test test_api_shortcuts
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestGetShortcuts(FrappeTestCase):
	"""Test get_shortcuts endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_shortcuts_returns_list(self):
		"""Should return list of shortcuts"""
		from zevar_core.api.shortcuts import get_shortcuts

		result = get_shortcuts(surface="desk")
		self.assertIsInstance(result, list)

	def test_get_shortcuts_invalid_surface_raises(self):
		"""Should raise for invalid surface"""
		from zevar_core.api.shortcuts import get_shortcuts

		with self.assertRaises(frappe.ValidationError):
			get_shortcuts(surface="invalid_surface")

	def test_get_desk_shortcuts_returns_list(self):
		"""Should return list via backward-compat endpoint"""
		from zevar_core.api.shortcuts import get_desk_shortcuts

		result = get_desk_shortcuts()
		self.assertIsInstance(result, list)

	def test_get_shortcuts_workspace(self):
		"""Should return workspace shortcuts"""
		from zevar_core.api.shortcuts import get_shortcuts

		result = get_shortcuts(surface="workspace")
		self.assertIsInstance(result, list)


class TestGetShortcutSections(FrappeTestCase):
	"""Test get_shortcut_sections endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_sections_returns_list(self):
		"""Should return list of sections"""
		from zevar_core.api.shortcuts import get_shortcut_sections

		result = get_shortcut_sections(surface="desk")
		self.assertIsInstance(result, list)


class TestGetQuickStats(FrappeTestCase):
	"""Test get_quick_stats endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_quick_stats_returns_dict(self):
		"""Should return stats dictionary"""
		from zevar_core.api.shortcuts import get_quick_stats

		result = get_quick_stats()
		self.assertIsInstance(result, dict)

	def test_quick_stats_has_required_fields(self):
		"""Should include expected stat keys"""
		from zevar_core.api.shortcuts import get_quick_stats

		result = get_quick_stats()
		self.assertIn("todays_sales", result)
		self.assertIn("pending_repairs", result)
		self.assertIn("active_layaways", result)
		self.assertIn("todays_customers", result)


class TestGetRecentActivity(FrappeTestCase):
	"""Test get_recent_activity endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_recent_activity_returns_list(self):
		"""Should return list of activities"""
		from zevar_core.api.shortcuts import get_recent_activity

		result = get_recent_activity()
		self.assertIsInstance(result, list)

	def test_get_recent_activity_respects_limit(self):
		"""Should respect limit parameter"""
		from zevar_core.api.shortcuts import get_recent_activity

		result = get_recent_activity(limit=5)
		self.assertLessEqual(len(result), 5)

	def test_activity_items_have_required_fields(self):
		"""Each activity should have type, icon, message, time"""
		from zevar_core.api.shortcuts import get_recent_activity

		result = get_recent_activity(limit=5)
		for activity in result:
			self.assertIn("type", activity)
			self.assertIn("icon", activity)
			self.assertIn("message", activity)
			self.assertIn("time", activity)


class TestBuildRoute(FrappeTestCase):
	"""Test route building helper"""

	def test_doctype_route(self):
		"""Should build DocType route"""
		from zevar_core.api.shortcuts import _build_route

		route = _build_route("DocType", "Sales Invoice")
		self.assertEqual(route, "/app/sales-invoice")

	def test_page_route(self):
		"""Should build Page route"""
		from zevar_core.api.shortcuts import _build_route

		route = _build_route("Page", "POS")
		self.assertEqual(route, "/app/pos")

	def test_report_route(self):
		"""Should build Report route"""
		from zevar_core.api.shortcuts import _build_route

		route = _build_route("Report", "Sales Report")
		self.assertIn("/app/query-report/", route)

	def test_null_link_to(self):
		"""Should return # for null link_to"""
		from zevar_core.api.shortcuts import _build_route

		route = _build_route("DocType", None)
		self.assertEqual(route, "#")
