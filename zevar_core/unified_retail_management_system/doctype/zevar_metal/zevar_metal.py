# Copyright (c) 2025, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ZevarMetal(Document):
	def validate(self):
		if self.default_purity:
			purity_metal = frappe.db.get_value("Zevar Purity", self.default_purity, "metal")
			if purity_metal and purity_metal != self.metal_name:
				frappe.throw(_("Default purity must belong to {0}").format(self.metal_name))

	def on_trash(self):
		if frappe.db.exists("Item", {"custom_metal_type": self.metal_name, "disabled": 0}):
			frappe.throw(_("Cannot delete: active Items reference this metal"))
