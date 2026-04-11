# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class RepairOrderItem(Document):
	def validate(self):
		"""Auto-calculate amount = qty * rate"""
		self.amount = (self.qty or 0) * (self.rate or 0)

	def on_change(self):
		"""Recalculate when qty or rate changes"""
		self.amount = (self.qty or 0) * (self.rate or 0)
