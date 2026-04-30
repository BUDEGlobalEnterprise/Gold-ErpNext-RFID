# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AuditPolicy(Document):
	def validate(self):
		if self.showcase_cadence_days and self.showcase_cadence_days < 1:
			frappe.throw("Showcase cadence must be at least 1 day")
		if self.backstock_cadence_days and self.backstock_cadence_days < 1:
			frappe.throw("Backstock cadence must be at least 1 day")
		if self.full_store_cadence_days and self.full_store_cadence_days < 1:
			frappe.throw("Full store cadence must be at least 1 day")
		if self.variance_threshold_dollars and self.variance_threshold_dollars < 0:
			frappe.throw("Variance threshold cannot be negative")
		if self.variance_pieces_hard_stop and self.variance_pieces_hard_stop < 1:
			frappe.throw("Variance pieces hard stop must be at least 1")
