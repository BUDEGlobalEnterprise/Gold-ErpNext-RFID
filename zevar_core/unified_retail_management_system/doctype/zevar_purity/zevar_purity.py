# Copyright (c) 2025, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ZevarPurity(Document):
	def validate(self):
		if self.fine_metal_content is not None:
			if not (0 < self.fine_metal_content <= 1):
				frappe.throw(_("Fine Metal Content must be between 0 and 1"))

		if self.purity_code and self.metal:
			existing = frappe.db.exists("Zevar Purity", {
				"purity_code": self.purity_code,
				"metal": self.metal,
				"name": ["!=", self.name],
			})
			if existing:
				frappe.throw(
					_("Purity code {0} already exists for metal {1}").format(
						self.purity_code, self.metal
					)
				)

	def on_trash(self):
		if frappe.db.exists("Item", {"custom_purity": self.purity_name, "disabled": 0}):
			frappe.throw(_("Cannot delete: active Items reference this purity"))
