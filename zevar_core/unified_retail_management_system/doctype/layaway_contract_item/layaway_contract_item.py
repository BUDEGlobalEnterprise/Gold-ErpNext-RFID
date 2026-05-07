# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt


class LayawayContractItem(Document):
	def before_insert(self):
		self._set_item_details()

	def validate(self):
		if flt(self.qty) > 0 and flt(self.rate) > 0:
			self.amount = flt(self.qty) * flt(self.rate)

	def _set_item_details(self):
		"""Auto-populate item details from item code."""
		if self.item_code:
			import frappe

			if not frappe.db.exists("Item", self.item_code):
				return
			item = frappe.get_doc("Item", self.item_code)
			self.item_name = item.item_name
			self.description = getattr(item, "description", "") or ""
