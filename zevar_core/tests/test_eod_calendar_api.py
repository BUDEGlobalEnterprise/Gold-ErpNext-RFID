import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from zevar_core.api.sales_history import (
	get_daily_sales_heatmap,
	get_day_drilldown,
	get_yoy_delta,
)


class TestEODCalendarAPI(FrappeTestCase):
	def setUp(self):
		self.today = today()
		self.last_year_date = add_days(self.today, -365)
		self.last_year_iso_date = add_days(self.today, -364)

		# Create some invoices for today and last year to test YoY and heatmap
		self._create_invoice(self.today, "Jewelry Sale", 1000.0)
		self._create_invoice(self.today, "Repair", 250.0)

		# Last year exact date
		self._create_invoice(self.last_year_date, "Jewelry Sale", 800.0)

		# Last year iso matched week
		self._create_invoice(self.last_year_iso_date, "Jewelry Sale", 900.0)

	def _create_invoice(self, date, stream, amount):
		item = frappe.get_all("Item", limit=1)[0].name
		customer = frappe.get_all("Customer", limit=1)[0].name

		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.is_pos = 1
		si.posting_date = date
		si.custom_transaction_stream = stream

		si.append("items", {"item_code": item, "qty": 1, "rate": amount, "amount": amount})

		si.append("payments", {"mode_of_payment": "Cash", "amount": amount})

		si.insert(ignore_permissions=True)
		si.submit()

	def test_get_daily_sales_heatmap(self):
		year = int(self.today.split("-")[0])
		month = int(self.today.split("-")[1])

		# Jewelry
		data = get_daily_sales_heatmap(year, month, "Jewelry Sale")
		self.assertGreaterEqual(len(data), 1)

		today_row = next((r for r in data if str(r.date) == self.today), None)
		self.assertIsNotNone(today_row)
		self.assertGreaterEqual(today_row.net, 1000.0)

		# Repair
		repair_data = get_daily_sales_heatmap(year, month, "Repair")
		today_repair = next((r for r in repair_data if str(r.date) == self.today), None)
		self.assertIsNotNone(today_repair)
		self.assertGreaterEqual(today_repair.net, 250.0)

	def test_get_day_drilldown(self):
		drilldown = get_day_drilldown(self.today)

		self.assertGreaterEqual(drilldown["net_sales"], 1000.0)
		self.assertGreaterEqual(drilldown["repairs"], 250.0)
		self.assertGreaterEqual(len(drilldown["tender_breakdown"]), 1)
		self.assertGreaterEqual(len(drilldown["top_items"]), 1)

	def test_get_yoy_delta(self):
		# Default comparison mode
		yoy = get_yoy_delta(self.today)

		self.assertGreaterEqual(yoy["this_year"], 1000.0)
		self.assertGreaterEqual(yoy["last_year"], 800.0)

		# Expected delta
		expected_abs = yoy["this_year"] - yoy["last_year"]
		self.assertEqual(yoy["delta_abs"], expected_abs)

		if yoy["last_year"] > 0:
			expected_pct = (expected_abs / yoy["last_year"]) * 100
			self.assertAlmostEqual(yoy["delta_pct"], expected_pct, places=1)
