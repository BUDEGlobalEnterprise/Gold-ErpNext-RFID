import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class PaymentToken(Document):
	def validate(self):
		if self.is_new():
			self.created_at = now_datetime()
		if self.token_id and not self.label:
			brand = self.card_brand or "Card"
			last4 = self.last_four or "****"
			self.label = f"{brand} ending {last4}"
