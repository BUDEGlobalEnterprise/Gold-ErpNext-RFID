import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class IRSForm8300Record(Document):
	def validate(self):
		settings = frappe.get_single("Payment Gateway Settings")
		threshold = flt(settings.get("cash_threshold_8300") or 10000)
		if flt(self.total_cash_amount) < threshold:
			frappe.throw(_("Total cash amount is below the reporting threshold of ${0}.").format(threshold))
		if not self.recipient_name:
			frappe.throw(_("Recipient full legal name is required for Form 8300."))
