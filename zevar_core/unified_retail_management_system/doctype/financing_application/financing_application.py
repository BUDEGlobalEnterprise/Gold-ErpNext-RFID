import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class FinancingApplication(Document):
	def validate(self):
		self._validate_amounts()
		self._validate_status_transition()

	def _validate_amounts(self):
		if flt(self.requested_amount) <= 0:
			frappe.throw(_("Requested amount must be greater than zero."))
		if flt(self.approved_amount) > flt(self.requested_amount):
			frappe.throw(_("Approved amount cannot exceed requested amount."))

	def _validate_status_transition(self):
		if not self.is_new() and self.has_value_changed("status"):
			valid_transitions = {
				"Draft": ["Submitted", "Cancelled"],
				"Submitted": ["Pending", "Prequalified", "Approved", "Denied"],
				"Pending": ["Prequalified", "Approved", "Denied", "Expired"],
				"Prequalified": ["Approved", "Denied", "Expired", "Cancelled"],
				"Approved": ["Completed", "Cancelled", "Expired"],
				"Denied": [],
				"Expired": [],
				"Cancelled": [],
				"Completed": [],
			}
			old_status = self.get_db_value("status")
			if old_status in valid_transitions:
				if self.status not in valid_transitions[old_status]:
					frappe.throw(_("Cannot transition from {0} to {1}.").format(old_status, self.status))

	def on_update(self):
		if self.status == "Approved" and not self.approval_date:
			self.db_set("approval_date", now_datetime())
			if self.approved_amount:
				self.db_set("remaining_balance", flt(self.approved_amount) - flt(self.initial_payment))
