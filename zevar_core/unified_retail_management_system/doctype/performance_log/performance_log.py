import frappe
from frappe import _
from frappe.model.document import Document


class PerformanceLog(Document):
	"""Immutable performance event log — system-generated, cannot be edited or deleted."""

	def before_insert(self):
		# Auto-populate employee_name
		if self.employee and not self.employee_name:
			self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")

	def before_save(self):
		# Allow only new inserts — prevent any modifications to existing records
		if not self.is_new():
			frappe.throw(_("Performance Logs are immutable and cannot be modified."))

	def on_trash(self):
		frappe.throw(_("Performance Logs are immutable and cannot be deleted."))

	def on_cancel(self):
		frappe.throw(_("Performance Logs cannot be cancelled."))
