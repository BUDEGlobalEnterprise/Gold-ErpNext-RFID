import frappe
from frappe import _
from frappe.model.document import Document


class ZevarAppraisalTemplate(Document):
	def validate(self):
		existing = frappe.db.exists(
			"Zevar Appraisal Template",
			{
				"template_name": self.template_name,
				"template_type": self.template_type,
				"name": ["!=", self.name],
			},
		)
		if existing:
			frappe.throw(
				_("Template {0} already exists for type {1}").format(self.template_name, self.template_type)
			)
