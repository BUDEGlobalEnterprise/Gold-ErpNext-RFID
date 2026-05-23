import frappe
from frappe import _


class POSTaxExemptionLog(frappe.model.document.Document):
    def on_update(self):
        if self.approval_status == "Approved" and not self.approved_by:
            self.approved_by = frappe.session.user
            self.approved_at = frappe.utils.now_datetime()
