import frappe
from frappe import _
from frappe.model.document import Document


class ZevarGemstone(Document):
	def on_update(self):
		if self.has_value_changed("status"):
			log = frappe.new_doc("POS Audit Log")
			log.user = frappe.session.user
			log.event_type = "gemstone_status_changed"
			log.category = "Inventory"
			log.reference_type = "Zevar Gemstone"
			log.reference_document = self.name
			log.details = f"Status changed to {self.status}"
			log.insert(ignore_permissions=True)
