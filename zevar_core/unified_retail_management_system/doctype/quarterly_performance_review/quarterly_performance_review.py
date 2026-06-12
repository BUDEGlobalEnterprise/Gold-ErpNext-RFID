import frappe
from frappe import _
from frappe.model.document import Document


class QuarterlyPerformanceReview(Document):
	"""Comprehensive quarterly performance review — auto-generated with manager input."""

	def validate(self):
		# Prevent duplicate reviews for same employee/period
		existing = frappe.get_all(
			"Quarterly Performance Review",
			filters={
				"employee": self.employee,
				"review_period": self.review_period,
				"review_year": self.review_year,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name],
			},
			limit=1,
		)
		if existing:
			frappe.throw(
				_("Quarterly review already exists for {0} — {1} {2}").format(
					self.employee_name, self.review_period, self.review_year
				)
			)

	def on_submit(self):
		if self.status in ("Draft", "Generated"):
			self.db_set("status", "Reviewed")
