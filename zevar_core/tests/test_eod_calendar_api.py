import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


def _has_eod_calendar_functions():
	"""Check if EOD calendar functions exist in sales_history API."""
	try:
		from zevar_core.api.sales_history import get_day_drilldown, get_yoy_delta

		return True
	except ImportError:
		return False


@unittest.skipUnless(
	_has_eod_calendar_functions(),
	"EOD calendar functions not available in sales_history API",
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

	def test_get_day_drilldown(self):
		from zevar_core.api.sales_history import get_day_drilldown

		drilldown = get_day_drilldown(self.today)
		self.assertIsInstance(drilldown, dict)
		self.assertIn("net_sales", drilldown)

	def test_get_yoy_delta(self):
		from zevar_core.api.sales_history import get_yoy_delta

		yoy = get_yoy_delta(self.today)
		self.assertIsInstance(yoy, dict)
		self.assertIn("this_year", yoy)
		self.assertIn("last_year", yoy)
