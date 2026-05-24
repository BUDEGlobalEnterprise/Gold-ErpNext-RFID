# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CashMovement(Document):
	def validate(self):
		self._validate_session_is_open()
		self._validate_amount()

	def on_submit(self):
		self._log_event()

	def _validate_session_is_open(self):
		if not self.session:
			frappe.throw(_("Session is required"))
		status = frappe.db.get_value("POS Opening Entry", self.session, "status")
		if status != "Open":
			frappe.throw(_("Cannot add cash movement to a closed session"))

	def _validate_amount(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero"))

	def _log_event(self):
		try:
			from zevar_core.api.audit_log import log_event_safely

			log_event_safely(
				event_type="cash_movement",
				details={
					"movement_name": self.name,
					"session": self.session,
					"movement_type": self.movement_type,
					"amount": flt(self.amount),
					"reason": self.reason,
					"authorized_by": self.authorized_by,
				},
				reference_document=self.name,
				reference_type="Cash Movement",
			)
		except Exception:
			frappe.log_error("Failed to log cash movement event")
