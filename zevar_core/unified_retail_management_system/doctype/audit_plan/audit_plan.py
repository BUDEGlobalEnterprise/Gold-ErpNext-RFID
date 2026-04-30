# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AuditPlan(Document):
	def on_update(self):
		# If linked session completed, mark this plan completed too
		if self.audit_session and self.status == "In Progress":
			session_status = frappe.db.get_value("Case Audit Session", self.audit_session, "status")
			if session_status in ("Reconciled", "Discrepancy"):
				self.db_set("status", "Completed")
