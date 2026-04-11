# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LayawayContractItem(Document):
	def before_insert(self):
		self._set_item_details()

	def _set_item_details(self):
		"""Auto-populate item details from item code."""
		if self.item_code:
			import frappe

			item = frappe.get_doc("Item", self.item_code)
			self.item_name = item.item_name
			self.description = item.description
