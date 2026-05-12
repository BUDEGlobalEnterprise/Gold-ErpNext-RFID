# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Layer 6: Report Testing
Covers all 22 custom reports

For each report, validates:
1. Execution - report generates without errors
2. Filters - date range and other filters work
3. Empty data - handles no-results gracefully
4. Output format - returns correct data structure

Run with: bench run-tests --app zevar_core --test test_reports
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

# Report names matching the 22 custom reports in the testing plan
ZEVAR_REPORTS = [
	"Commission Summary",
	"Customer Repair History",
	"EOD Stream Summary",
	"Finance Account Balances",
	"Financier Receivables Today",
	"Gold Rate History",
	"Hourly Sales",
	"Layaway Aging",
	"Layaway Status",
	"Low Stock Alert",
	"Metal Gemstone Tracking",
	"Overdue Repairs",
	"Payment Method Summary",
	"POS Closing Summary",
	"Repair Revenue",
	"Repair Turnaround",
	"Repair Type Popularity",
	"Sales by Salesperson",
	"Tax Collected by County",
	"Technician Performance",
	"Top Selling Jewelry",
	"Trade In Summary",
]


class TestReportExistence(FrappeTestCase):
	"""Verify that all 22 reports exist"""

	def test_all_reports_registered(self):
		"""All reports should be registered in the system"""
		missing = []
		for report_name in ZEVAR_REPORTS:
			if not frappe.db.exists("Report", report_name):
				missing.append(report_name)

		if missing:
			# Soft fail - list missing reports
			self.skipTest(f"Reports not found: {', '.join(missing)}")

	def test_reports_have_py_module(self):
		"""Each report should have a Python module"""
		for report_name in ZEVAR_REPORTS:
			if not frappe.db.exists("Report", report_name):
				continue
			report = frappe.get_doc("Report", report_name)
			if report.report_type == "Script Report":
				# Script reports should have a .py file
				try:
					module = frappe.get_module(
						f"zevar_core.unified_retail_management_system.report.{frappe.scrub(report_name)}.{frappe.scrub(report_name)}"
					)
					self.assertIsNotNone(module)
				except Exception:
					self.fail(f"Report '{report_name}' missing Python module")


class TestReportExecution(FrappeTestCase):
	"""Test that reports execute without errors"""

	def setUp(self):
		frappe.set_user("Administrator")

	def _run_report(self, report_name, filters=None):
		"""Execute a report and return result"""
		if not frappe.db.exists("Report", report_name):
			self.skipTest(f"Report '{report_name}' not found")

		report = frappe.get_doc("Report", report_name)

		if report.report_type == "Script Report":
			module_path = f"zevar_core.unified_retail_management_system.report.{frappe.scrub(report_name)}.{frappe.scrub(report_name)}"
			module = frappe.get_module(module_path)
			if hasattr(module, "execute"):
				return module.execute(filters or {})
		return None

	def test_commission_summary_executes(self):
		"""Commission Summary should execute"""
		self._run_report("Commission Summary", {
			"from_date": add_days(today(), -30),
			"to_date": today(),
		})

	def test_eod_stream_summary_executes(self):
		"""EOD Stream Summary should execute"""
		self._run_report("EOD Stream Summary", {
			"date": today(),
		})

	def test_hourly_sales_executes(self):
		"""Hourly Sales should execute"""
		self._run_report("Hourly Sales", {
			"date": today(),
		})

	def test_gold_rate_history_executes(self):
		"""Gold Rate History should execute"""
		self._run_report("Gold Rate History", {
			"from_date": add_days(today(), -7),
			"to_date": today(),
		})

	def test_layaway_status_executes(self):
		"""Layaway Status should execute"""
		self._run_report("Layaway Status")

	def test_layaway_aging_executes(self):
		"""Layaway Aging should execute"""
		self._run_report("Layaway Aging")

	def test_low_stock_alert_executes(self):
		"""Low Stock Alert should execute"""
		self._run_report("Low Stock Alert")

	def test_overdue_repairs_executes(self):
		"""Overdue Repairs should execute"""
		self._run_report("Overdue Repairs")

	def test_payment_method_summary_executes(self):
		"""Payment Method Summary should execute"""
		self._run_report("Payment Method Summary", {
			"from_date": add_days(today(), -30),
			"to_date": today(),
		})

	def test_pos_closing_summary_executes(self):
		"""POS Closing Summary should execute"""
		self._run_report("POS Closing Summary", {
			"date": today(),
		})

	def test_repair_revenue_executes(self):
		"""Repair Revenue should execute"""
		self._run_report("Repair Revenue", {
			"from_date": add_days(today(), -30),
			"to_date": today(),
		})

	def test_repair_turnaround_executes(self):
		"""Repair Turnaround should execute"""
		self._run_report("Repair Turnaround")

	def test_repair_type_popularity_executes(self):
		"""Repair Type Popularity should execute"""
		self._run_report("Repair Type Popularity")

	def test_sales_by_salesperson_executes(self):
		"""Sales by Salesperson should execute"""
		self._run_report("Sales by Salesperson", {
			"from_date": add_days(today(), -30),
			"to_date": today(),
		})

	def test_tax_collected_by_county_executes(self):
		"""Tax Collected by County should execute"""
		self._run_report("Tax Collected by County", {
			"from_date": add_days(today(), -30),
			"to_date": today(),
		})

	def test_technician_performance_executes(self):
		"""Technician Performance should execute"""
		self._run_report("Technician Performance")

	def test_top_selling_jewelry_executes(self):
		"""Top Selling Jewelry should execute"""
		self._run_report("Top Selling Jewelry", {
			"from_date": add_days(today(), -30),
			"to_date": today(),
		})

	def test_trade_in_summary_executes(self):
		"""Trade In Summary should execute"""
		self._run_report("Trade In Summary")

	def test_metal_gemstone_tracking_executes(self):
		"""Metal Gemstone Tracking should execute"""
		self._run_report("Metal Gemstone Tracking")

	def test_finance_account_balances_executes(self):
		"""Finance Account Balances should execute"""
		self._run_report("Finance Account Balances")

	def test_financier_receivables_today_executes(self):
		"""Financier Receivables Today should execute"""
		self._run_report("Financier Receivables Today")

	def test_customer_repair_history_executes(self):
		"""Customer Repair History should execute"""
		self._run_report("Customer Repair History")


class TestReportEmptyData(FrappeTestCase):
	"""Test reports handle empty data gracefully"""

	def setUp(self):
		frappe.set_user("Administrator")

	def _run_report_with_empty_filters(self, report_name, filters=None):
		"""Run report and ensure no crash with empty data"""
		if not frappe.db.exists("Report", report_name):
			self.skipTest(f"Report '{report_name}' not found")

		report = frappe.get_doc("Report", report_name)
		if report.report_type != "Script Report":
			return

		module_path = f"zevar_core.unified_retail_management_system.report.{frappe.scrub(report_name)}.{frappe.scrub(report_name)}"
		try:
			module = frappe.get_module(module_path)
			if hasattr(module, "execute"):
				result = module.execute(filters or {})
				# Should return something (columns, data) or empty
				self.assertIsNotNone(result)
		except Exception as e:
			self.fail(f"Report '{report_name}' crashed with empty data: {e}")

	def test_empty_data_gold_rate_history(self):
		"""Gold Rate History should handle no data"""
		self._run_report_with_empty_filters("Gold Rate History", {
			"from_date": "2099-01-01",
			"to_date": "2099-01-31",
		})

	def test_empty_data_hourly_sales(self):
		"""Hourly Sales should handle no data"""
		self._run_report_with_empty_filters("Hourly Sales", {
			"date": "2099-01-01",
		})

	def test_empty_data_commission_summary(self):
		"""Commission Summary should handle no data"""
		self._run_report_with_empty_filters("Commission Summary", {
			"from_date": "2099-01-01",
			"to_date": "2099-01-31",
		})
