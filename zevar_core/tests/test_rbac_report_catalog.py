import frappe
from frappe.tests.utils import FrappeTestCase


class TestRBACReportCatalog(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()

	def _get_visible_report_ids(self, roles):
		from zevar_core.api.reports import REPORT_CATALOG, _has_access

		return [r["id"] for r in REPORT_CATALOG if _has_access(r, set(roles))]

	def test_admin_sees_all_reports(self):
		from zevar_core.api.reports import REPORT_CATALOG

		visible = self._get_visible_report_ids(["Administrator", "System Manager"])
		all_ids = [r["id"] for r in REPORT_CATALOG]
		self.assertEqual(set(visible), set(all_ids))

	def test_sales_user_sees_limited_reports(self):
		visible = self._get_visible_report_ids(["Sales User"])
		self.assertIn("sales_history", visible)
		self.assertIn("overdue_repairs", visible)
		self.assertNotIn("eod_stream_summary", visible)
		self.assertNotIn("audit_log", visible)

	def test_store_manager_sees_most_reports(self):
		visible = self._get_visible_report_ids(["Store Manager"])
		self.assertIn("eod_stream_summary", visible)
		self.assertIn("hourly_sales", visible)
		self.assertIn("low_stock_alert", visible)
		self.assertIn("overdue_layaway_payments", visible)
		self.assertIn("shrinkage_trend", visible)
		self.assertIn("audit_compliance", visible)
		self.assertNotIn("audit_log", visible)
		self.assertNotIn("manager_overrides", visible)

	def test_stock_manager_sees_inventory_reports(self):
		visible = self._get_visible_report_ids(["Stock Manager", "Inventory Manager"])
		self.assertIn("low_stock_alert", visible)
		self.assertIn("inventory_timeline", visible)
		self.assertIn("shrinkage_trend", visible)
		self.assertIn("reorder_suggestions", visible)
		self.assertIn("transfer_in_transit", visible)
		self.assertNotIn("eod_stream_summary", visible)
		self.assertNotIn("commission_summary", visible)

	def test_accounts_manager_sees_financial_reports(self):
		visible = self._get_visible_report_ids(["Accounts Manager"])
		self.assertIn("eod_stream_summary", visible)
		self.assertIn("cash_drawer_reconciliation", visible)
		self.assertIn("payment_method_summary", visible)
		self.assertIn("layaway_aging", visible)
		self.assertIn("finance_account_balances", visible)
		self.assertIn("audit_log", visible)

	def test_hr_user_sees_employee_reports(self):
		visible = self._get_visible_report_ids(["HR User"])
		self.assertIn("employee_portal_reports", visible)
		self.assertNotIn("eod_stream_summary", visible)
		self.assertNotIn("hourly_sales", visible)

	def test_employee_sees_own_reports(self):
		visible = self._get_visible_report_ids(["Employee"])
		self.assertIn("employee_portal_reports", visible)
		self.assertIn("my_sales", visible)

	def test_new_reports_have_roles(self):
		from zevar_core.api.reports import REPORT_CATALOG

		new_report_ids = [
			"inventory_timeline",
			"shrinkage_trend",
			"audit_compliance",
			"reorder_suggestions",
			"reservation_aging",
			"transfer_in_transit",
			"store_scorecard",
			"yoy_day_compare",
			"high_risk_customers",
		]
		for report in REPORT_CATALOG:
			if report["id"] in new_report_ids:
				self.assertTrue(
					len(report.get("roles", [])) > 0,
					f"Report {report['id']} has no roles defined",
				)

	def test_get_row_actions_for_report(self):
		from zevar_core.api.reports import get_row_actions

		actions = get_row_actions(report_id="reorder_suggestions")
		self.assertIsInstance(actions, list)
		action_ids = [a["action"] for a in actions]
		self.assertIn("raise_mr", action_ids)

	def test_get_row_actions_empty_for_non_actionable(self):
		from zevar_core.api.reports import get_row_actions

		actions = get_row_actions(report_id="gold_rate_history")
		self.assertEqual(actions, [])
