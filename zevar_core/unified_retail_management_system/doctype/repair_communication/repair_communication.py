# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RepairCommunication(Document):
	def validate(self):
		"""Validate communication entry"""
		if self.communication_type in ["SMS", "Email"] and not self.sent_via:
			frappe.throw(_("Recipient (phone/email) is required for SMS and Email"))

		if self.direction == "Incoming" and self.status == "Pending":
			self.status = "Delivered"
