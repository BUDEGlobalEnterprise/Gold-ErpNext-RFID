# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, getdate, now_datetime


class MemoContract(Document):
	def validate(self):
		self._calculate_totals()
		self._calculate_aging()
		self._validate_items()

	def before_insert(self):
		if not self.due_date and self.payment_terms_days:
			self.due_date = add_days(getdate(self.contract_date), self.payment_terms_days)

	def on_submit(self):
		self.db_set("status", "Active")
		self._move_items_to_consignment()

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	def _calculate_totals(self):
		total_memo = 0
		sold = 0
		returned = 0
		count = 0
		sold_count = 0
		returned_count = 0

		for item in self.items:
			total_memo += (item.memo_price or 0) * (item.qty or 1)
			count += item.qty or 1

			if item.status == "Sold":
				sold += (item.memo_price or 0) * (item.qty or 1)
				sold_count += item.qty or 1
			elif item.status == "Returned":
				returned += (item.memo_price or 0) * (item.qty or 1)
				returned_count += item.qty or 1

		total_paid = sum(p.amount or 0 for p in self.payments)

		self.total_memo_value = total_memo
		self.total_sold_value = sold
		self.total_returned_value = returned
		self.total_paid = total_paid
		self.balance_due = sold - total_paid
		self.item_count = count
		self.items_sold = sold_count
		self.items_returned = returned_count

	def _calculate_aging(self):
		if not self.due_date:
			return

		today = getdate()
		due = getdate(self.due_date)
		diff = date_diff(today, due)

		self.aging_days = max(diff, 0)

		if diff <= 0:
			self.aging_category = "Current"
		elif diff <= 30:
			self.aging_category = "1-30 Days"
		elif diff <= 60:
			self.aging_category = "31-60 Days"
		elif diff <= 90:
			self.aging_category = "61-90 Days"
		else:
			self.aging_category = "90+ Days"

		if diff > 0 and self.status == "Active":
			self.db_set("status", "Overdue")

	def _validate_items(self):
		if not self.items:
			frappe.throw(_("At least one memo item is required"))

	def _move_items_to_consignment(self):
		store = frappe.get_doc("Store Location", self.store_location)
		warehouse = store.default_warehouse
		if not warehouse:
			return

		for item in self.items:
			if item.serial_no:
				sn = frappe.get_doc("Serial No", item.serial_no)
				sn.warehouse = warehouse
				sn.save(ignore_permissions=True)

	def mark_item_sold(self, item_idx, sales_invoice=None):
		item = self.items[item_idx]
		item.status = "Sold"
		item.date_sold = getdate()
		item.sales_invoice = sales_invoice
		self._calculate_totals()
		self.save()

	def mark_item_returned(self, item_idx):
		item = self.items[item_idx]
		item.status = "Returned"
		item.date_returned = getdate()
		self._calculate_totals()
		self.save()

	def record_payment(self, amount, payment_type="Settlement", reference=None):
		self.append(
			"payments",
			{
				"payment_date": getdate(),
				"payment_type": payment_type,
				"amount": amount,
				"reference": reference,
			},
		)
		self._calculate_totals()
		self.save()

		if self.balance_due <= 0 and self.items_sold == self.item_count - self.items_returned:
			self.db_set("status", "Settled")
		elif self.items_sold > 0:
			self.db_set("status", "Partial Settlement")
