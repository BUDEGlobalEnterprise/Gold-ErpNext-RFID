import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class PerformanceTarget(Document):
	"""Defines performance targets and compensation parameters for an employee in a period."""

	def validate(self):
		self._validate_dates()
		self._validate_weights()
		self._validate_hourly_rates()
		self._validate_thresholds()
		self._check_overlapping_targets()

	def before_save(self):
		# Auto-populate employee_name and designation
		if self.employee:
			emp = frappe.db.get_value(
				"Employee", self.employee, ["employee_name", "designation"], as_dict=True
			)
			if emp:
				self.employee_name = emp.employee_name
				self.designation = emp.designation

	def on_submit(self):
		self.db_set("status", "Active")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	def _validate_dates(self):
		if not self.period_start or not self.period_end:
			return
		if getdate(self.period_end) <= getdate(self.period_start):
			frappe.throw(_("Period End must be after Period Start"))

	def _validate_weights(self):
		total_weight = flt(self.revenue_weight) + flt(self.activity_weight) + flt(self.quality_weight)
		if abs(total_weight - 100) > 0.01:
			frappe.throw(
				_("Revenue, Activity, and Quality weights must sum to 100%. Currently: {0}%").format(
					total_weight
				)
			)

	def _validate_hourly_rates(self):
		guaranteed = flt(self.guaranteed_hourly_rate)
		target = flt(self.target_hourly_rate)
		superior = flt(self.superior_hourly_rate)

		if guaranteed < 0:
			frappe.throw(_("Guaranteed Hourly Rate cannot be negative"))

		if target < guaranteed:
			frappe.throw(
				_("Target Hourly Rate ({0}) must be >= Guaranteed Rate ({1})").format(target, guaranteed)
			)

		if superior < target:
			frappe.throw(
				_("Superior Hourly Rate ({0}) must be >= Target Rate ({1})").format(superior, target)
			)

	def _validate_thresholds(self):
		min_pct = flt(self.minimum_performance_pct)
		term_pct = flt(self.termination_threshold_pct)

		if min_pct <= 0 or min_pct > 100:
			frappe.throw(_("Minimum Performance % must be between 1 and 100"))

		if term_pct < 0 or term_pct >= min_pct:
			frappe.throw(
				_("Termination Threshold % ({0}) must be less than Minimum Performance % ({1})").format(
					term_pct, min_pct
				)
			)

	def _check_overlapping_targets(self):
		"""Prevent overlapping periods for the same employee and period type."""
		if not self.employee or not self.period_start or not self.period_end:
			return

		overlapping = frappe.get_all(
			"Performance Target",
			filters={
				"employee": self.employee,
				"period_type": self.period_type,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name],
				"period_start": ["<=", self.period_end],
				"period_end": [">=", self.period_start],
			},
			fields=["name", "period_start", "period_end"],
			limit=1,
		)

		if overlapping:
			frappe.throw(
				_(
					"Overlapping target exists: {0} ({1} to {2}). "
					"An employee can only have one active target per period type at a time."
				).format(
					overlapping[0].name,
					overlapping[0].period_start,
					overlapping[0].period_end,
				)
			)
