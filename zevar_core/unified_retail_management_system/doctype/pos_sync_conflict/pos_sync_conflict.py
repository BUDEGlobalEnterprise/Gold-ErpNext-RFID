import frappe
from frappe.model.document import Document


class POSSyncConflict(Document):
	def before_insert(self):
		if not self.created_at:
			self.created_at = frappe.utils.now()
		if not self.resolution:
			self.resolution = "pending"

	def resolve(self, resolution, resolved_by=None, notes=None):
		self.resolution = resolution
		self.resolved_by = resolved_by or frappe.session.user
		self.resolved_at = frappe.utils.now()
		if notes:
			self.resolution_notes = notes
		self.save(ignore_permissions=True)
