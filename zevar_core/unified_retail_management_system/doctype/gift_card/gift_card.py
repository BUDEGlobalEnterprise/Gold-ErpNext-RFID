# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today

VALID_SOURCES = ("Purchase", "Layaway Cancellation", "Promotion")


class GiftCard(Document):
	def before_insert(self) -> None:
		self.balance = flt(self.initial_value)

	def validate(self) -> None:
		self._validate_initial_value()
		self._validate_balance()
		self._validate_source()
		self._auto_expire()

	def _validate_initial_value(self) -> None:
		if flt(self.initial_value) < 0:
			frappe.throw(frappe._("Initial value cannot be negative."))

	def _validate_balance(self) -> None:
		if flt(self.balance) < 0:
			frappe.throw(frappe._("Balance cannot be negative."))
		if flt(self.balance) > flt(self.initial_value):
			frappe.throw(frappe._("Balance cannot exceed initial value."))

	def _validate_source(self) -> None:
		if self.source and self.source not in VALID_SOURCES:
			frappe.throw(frappe._("Invalid source. Must be one of: {0}").format(", ".join(VALID_SOURCES)))

	def _auto_expire(self) -> None:
		"""Auto-set status to Expired if past expiry date."""
		if self.expiry_date and self.status == "Active" and getdate(self.expiry_date) < getdate(today()):
			self.status = "Expired"
