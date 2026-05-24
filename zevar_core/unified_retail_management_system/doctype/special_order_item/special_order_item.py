from frappe.model.document import Document


class SpecialOrderItem(Document):
	def before_save(self):
		self.amount = self.qty * self.rate
