import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ClearanceOutcome(Document):
	def validate(self):
		if self.recovered_amount and self.cost_basis:
			self.roi = flt(
				(flt(self.recovered_amount) - flt(self.cost_basis)) / flt(self.cost_basis) * 100, 2
			)
		else:
			self.roi = 0
