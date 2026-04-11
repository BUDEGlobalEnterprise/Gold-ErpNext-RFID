# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, flt


class LayawayContract(Document):
	def validate(self):
		self._set_target_completion_date()
		self._set_customer_details()
		self._calculate_amounts()
		self._calculate_payment_stats()
		self._validate_amounts()
		self._validate_deposit_minimum()
		self._validate_duration()

	def before_insert(self):
		self._set_default_store()

	def _set_default_store(self):
		"""Set default store location if not specified."""
		if not self.store_location:
			store_loc = frappe.db.get_value("Store Location", {"is_active": 1}, "name")
			if store_loc:
				self.store_location = store_loc

	def _set_customer_details(self):
		"""Auto-populate customer name from customer link."""
		if self.customer:
			customer_doc = frappe.get_doc("Customer", self.customer)
			self.customer_name = customer_doc.customer_name
			if not self.customer_contact:
				self.customer_contact = customer_doc.mobile_no or customer_doc.phone

	def _set_target_completion_date(self):
		"""Auto-calculate target completion from contract_date + duration."""
		if self.contract_date and self.maximum_duration_months:
			self.target_completion_date = add_months(self.contract_date, int(self.maximum_duration_months))

	def _calculate_amounts(self):
		"""Calculate derived amount fields."""
		if flt(self.total_amount) > 0:
			self.down_payment_percent = (flt(self.deposit_amount) / flt(self.total_amount)) * 100
		self.total_paid = flt(self.deposit_amount)

	def _calculate_payment_stats(self):
		"""Calculate payment statistics from schedule."""
		paid_entries = [p for p in self.payment_schedule if p.status == "Paid"]
		self.payment_count = len(paid_entries)

		if paid_entries:
			last_payment = max(paid_entries, key=lambda row: row.payment_date)
			self.last_payment_date = last_payment.payment_date
			self.last_payment_amount = flt(last_payment.paid_amount)
		else:
			self.last_payment_date = None
			self.last_payment_amount = 0

	def _validate_amounts(self):
		if flt(self.total_amount) <= 0:
			frappe.throw(frappe._("Total amount must be greater than zero."))

		if flt(self.deposit_amount) <= 0:
			frappe.throw(frappe._("Deposit amount must be greater than zero."))

		if flt(self.balance_amount) < 0:
			frappe.throw(frappe._("Balance amount cannot be negative."))

	def _validate_deposit_minimum(self):
		"""Deposit must be at least 10% of total amount."""
		minimum = flt(self.total_amount) * 0.10
		if flt(self.deposit_amount) < minimum:
			frappe.throw(
				frappe._(
					"Deposit must be at least 10% of total amount (minimum ${0:,.2f}, got ${1:,.2f})."
				).format(minimum, flt(self.deposit_amount))
			)

	def _validate_duration(self):
		if self.maximum_duration_months not in ("3", "6", "9", "12"):
			frappe.throw(frappe._("Duration must be 3, 6, 9, or 12 months."))

	def update_overdue_status(self):
		"""Update status to Overdue if payments are overdue."""
		from frappe.utils import getdate, today

		if self.status == "Active":
			overdue = False
			for payment in self.payment_schedule:
				if payment.status == "Pending" and getdate(payment.payment_date) < getdate(today()):
					overdue = True
					break

			if overdue:
				self.status = "Overdue"
				self.save()
