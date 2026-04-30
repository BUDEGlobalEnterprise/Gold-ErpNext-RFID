import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, nowdate, today


class TestDailyBrief(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
		if not frappe.db.exists("Company", cls.company):
			cls.company = frappe.get_all("Company", limit=1)[0].name

	def setUp(self):
		self.today = today()

	def test_daily_brief_returns_structure(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief()
		self.assertIsInstance(result, dict)
		self.assertIn("date", result)
		self.assertIn("sales", result)
		self.assertIn("repair_revenue", result)
		self.assertIn("layaway_deposits", result)
		self.assertIn("cash_variance_today", result)
		self.assertIn("low_stock_count", result)
		self.assertIn("overdue_repairs", result)
		self.assertIn("financier_ar", result)
		self.assertIn("next_audit", result)
		self.assertIn("pending_approvals", result)
		self.assertIn("live_feed", result)
		self.assertIn("yoy_deltas", result)

	def test_daily_brief_sales_structure(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief()
		self.assertIn("total", result["sales"])
		self.assertIn("count", result["sales"])
		self.assertIsInstance(result["sales"]["total"], (int, float))
		self.assertIsInstance(result["sales"]["count"], int)

	def test_daily_brief_overdue_repairs_structure(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief()
		self.assertIn("count", result["overdue_repairs"])
		self.assertIn("max_days_overdue", result["overdue_repairs"])

	def test_daily_brief_financier_ar_list(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief()
		self.assertIsInstance(result["financier_ar"], list)
		if result["financier_ar"]:
			self.assertIn("financier", result["financier_ar"][0])
			self.assertIn("today_ar", result["financier_ar"][0])

	def test_daily_brief_pending_approvals(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief()
		self.assertIn("variance_overrides", result["pending_approvals"])
		self.assertIn("transfer_receives", result["pending_approvals"])

	def test_daily_brief_yoy_deltas(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief()
		yoy = result.get("yoy_deltas", {})
		self.assertIsInstance(yoy, dict)

	def test_daily_brief_with_store_filter(self):
		from zevar_core.api.reports import get_daily_brief

		result = get_daily_brief(store="NY-01")
		self.assertIsInstance(result, dict)
		self.assertIn("date", result)

	def test_daily_brief_guest_rejected(self):
		from frappe.auth import HTTPRequest

		orig_user = frappe.session.user
		try:
			frappe.set_user("Guest")
			with self.assertRaises(frappe.PermissionError):
				from zevar_core.api.reports import get_daily_brief

				get_daily_brief()
		finally:
			frappe.set_user(orig_user)
