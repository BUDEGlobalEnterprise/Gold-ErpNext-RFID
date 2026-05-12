# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Reports API (reports.py)
Covers: report catalog, report execution, and data endpoints

Run with: bench run-tests --app zevar_core --test test_api_reports
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestReportCatalog(FrappeTestCase):
	"""Test report catalog and visibility"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_report_groups_defined(self):
		"""Report groups should be defined"""
		from zevar_core.api.reports import REPORT_GROUPS

		self.assertIsInstance(REPORT_GROUPS, list)
		self.assertGreater(len(REPORT_GROUPS), 0)

		for group in REPORT_GROUPS:
			self.assertIn("id", group)
			self.assertIn("label", group)

	def test_report_catalog_defined(self):
		"""Report catalog should be populated"""
		from zevar_core.api.reports import REPORT_CATALOG

		self.assertIsInstance(REPORT_CATALOG, list)
		self.assertGreater(len(REPORT_CATALOG), 0)

	def test_each_report_has_required_fields(self):
		"""Each report entry should have required fields"""
		from zevar_core.api.reports import REPORT_CATALOG

		required_fields = ["id", "group", "title", "roles", "scope"]
		for report in REPORT_CATALOG:
			for field in required_fields:
				self.assertIn(field, report, f"Report '{report.get('id', '?')}' missing '{field}'")

	def test_report_roles_are_sets(self):
		"""Each report's roles should be a set"""
		from zevar_core.api.reports import REPORT_CATALOG

		for report in REPORT_CATALOG:
			self.assertIsInstance(report["roles"], set, f"Report '{report['id']}' roles should be a set")

	def test_report_groups_match_catalog(self):
		"""Every report's group should exist in REPORT_GROUPS"""
		from zevar_core.api.reports import REPORT_CATALOG, REPORT_GROUPS

		group_ids = {g["id"] for g in REPORT_GROUPS}
		for report in REPORT_CATALOG:
			self.assertIn(
				report["group"], group_ids, f"Report '{report['id']}' has unknown group '{report['group']}'"
			)

	def test_admin_sees_all_reports(self):
		"""Administrator should have access to all reports"""
		from zevar_core.api.reports import REPORT_CATALOG

		for report in REPORT_CATALOG:
			self.assertIn("Administrator", report["roles"])


class TestReportAPIEndpoints(FrappeTestCase):
	"""Test report API endpoint execution"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_report_catalog(self):
		"""Should return available reports for current user"""
		if not frappe.db.exists("DocType", "Report"):
			self.skipTest("Report DocType not found")

		from zevar_core.api.reports import get_report_catalog

		result = get_report_catalog()
		self.assertIsInstance(result, dict)
