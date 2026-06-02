import frappe
from frappe import _
from frappe.model.document import Document


class ZevarGemstoneType(Document):
	def on_trash(self):
		if frappe.db.exists("DocType", "Zevar Gemstone Detail"):
			refs = frappe.get_all("Zevar Gemstone Detail", filters={"gem_type": self.gemstone_type_name}, limit=1)
			if refs:
				frappe.throw(_("Cannot delete: gemstone details reference this type"))
