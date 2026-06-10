import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class JewelryBOM(Document):
	def validate(self):
		total_cost_share = sum(flt(c.cost_share_pct) for c in self.components if c.component_type != "Labor")
		if total_cost_share > 100:
			frappe.throw(_("Total cost share % cannot exceed 100% (currently {0}%)").format(total_cost_share))

		for c in self.components:
			if flt(c.qty_per_build) <= 0:
				frappe.throw(_("Qty per build must be > 0 for {0}").format(c.component_item))

		if self.parent_item_code:
			group = frappe.db.get_value("Item", self.parent_item_code, "item_group")
			self.parent_item_group = group

	def on_update(self):
		if self.is_default and self.parent_item_code:
			siblings = frappe.get_all(
				"Jewelry BOM",
				filters={
					"parent_item_code": self.parent_item_code,
					"is_default": 1,
					"name": ["!=", self.name],
				},
			)
			for s in siblings:
				frappe.db.set_value("Jewelry BOM", s.name, "is_default", 0)

	def on_trash(self):
		if frappe.db.exists("Stock Entry", {"jewelry_bom": self.name, "docstatus": 1}):
			frappe.throw(_("Cannot delete: submitted Stock Entries reference this BOM"))
