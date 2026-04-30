import frappe
from frappe import _
from frappe.model.document import Document


class AMLKYCRecord(Document):
	def validate(self):
		if self.status == "Flagged" and not self.risk_flags:
			frappe.throw(_("Risk flags are required when status is Flagged."))
		if self.status in ("Verified", "Cleared", "Escalated") and not self.reviewed_by:
			frappe.throw(_("Reviewer is required for {0} status.").format(self.status))
