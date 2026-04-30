"""
Zelle Payment API Endpoints
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.zelle import utils as zelle_utils


@frappe.whitelist()
def generate_zelle_qr(amount, invoice_reference=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.zelle_enabled:
		frappe.throw(_("Zelle payments are not enabled."))
	if flt(amount) <= 0:
		frappe.throw(_("Amount must be greater than zero."))
	return zelle_utils.generate_qr_code(flt(amount), invoice_reference)


@frappe.whitelist()
def check_zelle_payment(amount, reference=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	result = zelle_utils.check_payment_received(flt(amount), reference)
	return result
