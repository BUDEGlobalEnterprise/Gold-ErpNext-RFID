# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RepairPayment(Document):
	def validate(self):
		if not self.payment_date:
			from frappe.utils import now
			self.payment_date = now()

		if not self.received_by:
			self.received_by = frappe.session.user
