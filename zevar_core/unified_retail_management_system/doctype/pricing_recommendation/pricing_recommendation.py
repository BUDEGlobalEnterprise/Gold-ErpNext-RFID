import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class PricingRecommendation(Document):
	def on_update(self):
		"""Auto-update item price when recommendation is applied."""
		if self.status == "Applied" and not self.applied_at:
			self.applied_at = now_datetime()
			if self.item_code and self.recommended_price:
				frappe.db.set_value(
					"Item",
					self.item_code,
					"custom_msrp",
					self.recommended_price,
				)

	def before_submit(self):
		"""Validate before submitting."""
		if not self.item_code:
			frappe.throw(_("Item Code is required"))
		if not self.recommended_price or self.recommended_price <= 0:
			frappe.throw(_("Recommended Price must be greater than 0"))
