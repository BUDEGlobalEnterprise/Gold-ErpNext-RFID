import frappe
from frappe import _
from frappe.utils import getdate


class TaxExemptionCertificate(frappe.model.document.Document):
	def validate(self):
		if self.expiry_date and getdate(self.expiry_date) < getdate():
			self.status = "Expired"
			frappe.msgprint(
				_("Certificate expiry date is in the past. Status set to Expired."),
				indicator="orange",
			)

		if self.issue_date and self.expiry_date and getdate(self.expiry_date) <= getdate(self.issue_date):
			frappe.throw(_("Expiry date must be after issue date."))

		existing = frappe.get_all(
			"Tax Exemption Certificate",
			filters={
				"customer": self.customer,
				"certificate_number": self.certificate_number,
				"name": ["!=", self.name],
				"status": "Active",
			},
			limit=1,
		)
		if existing:
			frappe.throw(
				_("An active certificate with number {0} already exists for this customer.").format(
					self.certificate_number
				)
			)
