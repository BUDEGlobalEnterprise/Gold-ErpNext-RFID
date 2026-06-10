# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today


class TestSpecialOrder(FrappeTestCase):
	def setUp(self):
		self.customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": "_Test SO Customer",
				"customer_group": "All Customer Groups",
				"territory": "All Territories",
			}
		).insert(ignore_if_duplicate=1)
		self.item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "_Test SO Item",
				"item_name": "_Test SO Item",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
			}
		).insert(ignore_if_duplicate=1)

	def _make_order(self, total=500, deposit=0):
		doc = frappe.get_doc(
			{
				"doctype": "Special Order",
				"customer": self.customer.name,
				"order_date": today(),
				"deposit_amount": deposit,
				"items": [{"item_code": self.item.name, "qty": 1, "rate": total}],
			}
		)
		doc.insert()
		return doc

	def test_create_special_order(self):
		doc = self._make_order(total=500)
		self.assertEqual(doc.total_amount, 500)
		self.assertEqual(doc.balance_due, 500)
		self.assertEqual(doc.status, "Draft")

	def test_calculate_totals_multiple_items(self):
		doc = frappe.get_doc(
			{
				"doctype": "Special Order",
				"customer": self.customer.name,
				"order_date": today(),
				"items": [
					{"item_code": self.item.name, "qty": 2, "rate": 250},
					{"item_code": self.item.name, "qty": 1, "rate": 100},
				],
			}
		)
		doc.insert()
		self.assertEqual(doc.total_amount, 600)

	def test_deposit_exceeds_total(self):
		with self.assertRaises(frappe.ValidationError):
			self._make_order(total=500, deposit=600)

	def test_deposit_reduces_balance(self):
		doc = self._make_order(total=500)
		doc.submit()
		self.assertEqual(doc.status, "Pending Deposit")
		doc.record_deposit(200)
		self.assertEqual(flt(doc.deposit_paid), 200)
		self.assertEqual(flt(doc.balance_due), 300)
		self.assertEqual(doc.status, "Ordered from Vendor")

	def test_deposit_exceeds_balance(self):
		doc = self._make_order(total=500)
		doc.submit()
		doc.record_deposit(200)
		with self.assertRaises(frappe.ValidationError):
			doc.record_deposit(400)

	def test_mark_received_full(self):
		doc = self._make_order(total=500)
		doc.submit()
		doc.record_deposit(200)
		doc.mark_received([{"name": doc.items[0].name, "qty_filled": 1}])
		self.assertEqual(doc.qty_received, 1)
		self.assertEqual(doc.qty_ordered, 1)
		self.assertEqual(doc.status, "Received at Store")

	def test_mark_received_partial(self):
		doc = frappe.get_doc(
			{
				"doctype": "Special Order",
				"customer": self.customer.name,
				"order_date": today(),
				"items": [{"item_code": self.item.name, "qty": 3, "rate": 100}],
			}
		)
		doc.insert()
		doc.submit()
		doc.record_deposit(100)
		doc.mark_received([{"name": doc.items[0].name, "qty_filled": 2}])
		self.assertEqual(doc.status, "Partially Received")
		self.assertEqual(doc.qty_received, 2)

	def test_mark_picked_up_with_balance(self):
		doc = self._make_order(total=500)
		doc.submit()
		doc.record_deposit(200)
		doc.mark_received([{"name": doc.items[0].name, "qty_filled": 1}])
		with self.assertRaises(frappe.ValidationError):
			doc.mark_picked_up()

	def test_full_lifecycle(self):
		doc = self._make_order(total=1000, deposit=300)
		doc.submit()
		self.assertEqual(doc.status, "Pending Deposit")

		doc.record_deposit(300)
		self.assertEqual(doc.status, "Ordered from Vendor")

		doc.mark_received([{"name": doc.items[0].name, "qty_filled": 1}])
		self.assertEqual(doc.status, "Received at Store")

		doc.record_deposit(700)
		self.assertEqual(flt(doc.balance_due), 0)

		doc.mark_picked_up()
		self.assertEqual(doc.status, "Picked Up")

		doc.close_order()
		self.assertEqual(doc.status, "Closed")

	def test_cancel_order(self):
		doc = self._make_order(total=500)
		doc.submit()
		doc.cancel()
		self.assertEqual(doc.status, "Cancelled")
