import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.api.layaway import _create_layaway_final_invoice, _create_layaway_payment_entry


class TestStreamSegregation(FrappeTestCase):
	def test_sales_invoice_validation_hook(self):
		company = "Zevar Jewelers"

		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": "Test Stream Customer",
				"customer_type": "Individual",
				"customer_group": "All Customer Groups",
			}
		)
		if not frappe.db.exists("Customer", customer.customer_name):
			customer.insert(ignore_permissions=True)

		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-STOCK-ITEM",
				"item_name": "Test Stock Item",
				"item_group": "Products",
				"is_stock_item": 1,
				"stock_uom": "Nos",
			}
		)
		if not frappe.db.exists("Item", item.item_code):
			item.insert(ignore_permissions=True)

		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = customer.customer_name
		invoice.company = company
		invoice.custom_transaction_stream = "Repair"

		invoice.append(
			"items",
			{
				"item_code": item.item_code,
				"qty": 1,
				"rate": 100,
			},
		)

		# Should raise exception because it contains a stock item and stream is Repair
		self.assertRaises(frappe.ValidationError, invoice.insert)

	def test_eod_stream_summary_report(self):
		from zevar_core.unified_retail_management_system.report.eod_stream_summary.eod_stream_summary import (
			execute,
		)

		_columns, data = execute(
			{"from_date": frappe.utils.today(), "to_date": frappe.utils.today(), "company": "Zevar Jewelers"}
		)

		self.assertTrue(len(data) == 3)
		self.assertEqual(data[0]["stream"], "Jewelry Sales")
		self.assertEqual(data[1]["stream"], "Repairs")
		self.assertEqual(data[2]["stream"], "Layaway Deposits")
