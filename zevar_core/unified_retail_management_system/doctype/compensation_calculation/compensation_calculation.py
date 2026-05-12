import frappe
from frappe import _
from frappe.model.document import Document


class CompensationCalculation(Document):
	"""Auto-generated pay calculation for an employee in a period."""

	def validate(self):
		# Verify the linked Performance Target exists and is active
		if self.performance_target:
			target = frappe.get_doc("Performance Target", self.performance_target)
			if target.docstatus != 1:
				frappe.throw(_("Linked Performance Target must be submitted"))

		# Prevent duplicate calculations for the same target
		self._check_duplicate()

	def on_submit(self):
		self.db_set("status", "Calculated")

	def _check_duplicate(self):
		"""Ensure only one calculation per target per employee."""
		existing = frappe.get_all(
			"Compensation Calculation",
			filters={
				"employee": self.employee,
				"performance_target": self.performance_target,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name],
			},
			limit=1,
		)
		if existing:
			frappe.throw(
				_("Compensation Calculation {0} already exists for this target").format(existing[0]["name"])
			)
