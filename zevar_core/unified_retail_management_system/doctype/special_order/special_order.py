# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now


class SpecialOrder(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_deposit()

	def before_submit(self):
		if flt(self.deposit_amount) > 0 and flt(self.deposit_paid) == 0:
			frappe.throw(_("Record deposit payment before submitting the order."))

	def on_submit(self):
		self.db_set("status", "Pending Deposit")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	def calculate_totals(self):
		total = 0
		for item in self.items:
			item.amount = item.qty * item.rate
			total += item.amount
		self.total_amount = total
		self.balance_due = total - flt(self.deposit_paid)

	def validate_deposit(self):
		if flt(self.deposit_amount) > flt(self.total_amount):
			frappe.throw(_("Deposit cannot exceed total order amount."))

	def record_deposit(self, amount, mode_of_payment="Cash"):
		if flt(amount) <= 0:
			frappe.throw(_("Deposit amount must be greater than zero."))
		if flt(amount) > flt(self.balance_due):
			frappe.throw(
				_("Deposit of {0} exceeds balance due of {1}").format(
					amount, self.balance_due
				)
			)
		self.deposit_paid = flt(self.deposit_paid) + flt(amount)
		self.balance_due = flt(self.total_amount) - flt(self.deposit_paid)

		if self.status == "Pending Deposit":
			self.status = "Ordered from Vendor"
		self.save()
		self._log_event("deposit", {"amount": flt(amount), "mode": mode_of_payment})

	def mark_received(self, received_items):
		for ri in received_items:
			for item in self.items:
				if item.name == ri.get("name"):
					item.qty_filled = ri.get("qty_filled", item.qty)

		total_ordered = sum(i.qty for i in self.items)
		total_filled = sum(i.qty_filled for i in self.items)
		self.qty_ordered = total_ordered
		self.qty_received = total_filled

		if total_filled >= total_ordered:
			self.status = "Received at Store"
			if self.enable_notifications:
				self.send_arrival_notification()
		else:
			self.status = "Partially Received"
		self.save()
		self._log_event("received", {"qty_filled": total_filled, "qty_ordered": total_ordered})

	def send_arrival_notification(self):
		email = self._get_customer_email()
		if not email:
			return
		subject = f"Your Special Order {self.name} Has Arrived!"
		body = (
			f"<p>Dear {self.customer_name},</p>"
			f"<p>Great news! Your special order <strong>{self.name}</strong> "
		 f"has arrived at our store.</p>"
			f"<p>Please visit us at your earliest convenience to pick up your item(s).</p>"
			f"<p>Balance due: <strong>${flt(self.balance_due):,.2f}</strong></p>"
		)
		frappe.sendmail(
			recipients=[email],
			subject=subject,
			message=body,
			reference_doctype=self.doctype,
			reference_name=self.name,
			queued=True,
		)
		self.customer_notified_arrival = 1
		self.last_notification_date = now()
		self.status = "Customer Notified"
		self.save()
		self._log_event("notified", {"email": email})

	def mark_picked_up(self):
		if flt(self.balance_due) > 0:
			frappe.throw(_("Outstanding balance must be settled before pickup."))
		self.status = "Picked Up"
		self.save()
		self._log_event("picked_up", {})

	def close_order(self):
		if self.status != "Picked Up":
			frappe.throw(_("Order must be picked up before closing."))
		self.status = "Closed"
		self.save()
		self._log_event("closed", {})

	def _get_customer_email(self):
		return frappe.db.get_value("Customer", self.customer, "email_id")

	def _log_event(self, event_type, details):
		try:
			from zevar_core.api.audit_log import log_event_safely

			log_event_safely(
				event_type=f"special_order_{event_type}",
				details=details,
				reference_document=self.name,
				reference_type="Special Order",
			)
		except Exception:
			frappe.log_error(f"Failed to log special order event: {event_type}")
