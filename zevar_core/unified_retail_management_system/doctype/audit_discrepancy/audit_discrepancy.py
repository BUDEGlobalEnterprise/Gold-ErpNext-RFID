import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class AuditDiscrepancy(Document):
	def validate(self):
		self.calculate_discrepancy()
		self.set_discrepancy_type()

	def calculate_discrepancy(self):
		if self.expected_qty is not None and self.found_qty is not None:
			self.discrepancy_qty = self.found_qty - self.expected_qty

	def set_discrepancy_type(self):
		if self.discrepancy_qty < 0:
			self.discrepancy_type = "Missing"
		elif self.discrepancy_qty > 0:
			self.discrepancy_type = "Surplus"
		else:
			# If qty matches but flagged, might be damaged or wrong location
			# This will be set manually or by more complex logic
			pass

	@frappe.whitelist()
	def resolve(self, action, notes=None):
		"""Handle discrepancy resolution."""
		if self.status == "Resolved":
			frappe.throw(_("Discrepancy is already resolved."))

		self.resolution_action = action
		self.notes = notes
		self.status = "Resolving"

		# Placeholder for resolution logic (e.g., creating Stock Entry)
		# We'll implement specific handlers in Phase 3

		self.resolved_by = frappe.session.user
		self.resolved_at = now_datetime()
		self.status = "Resolved"
		self.save()

		return self.status
