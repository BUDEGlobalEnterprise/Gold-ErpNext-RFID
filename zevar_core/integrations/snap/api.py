"""
Snap Finance API Endpoints
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.snap import utils as snap_utils


@frappe.whitelist(methods=["POST"])
def submit_snap_application(
	customer,
	first_name,
	last_name,
	email,
	phone,
	monthly_income=None,
	requested_amount=None,
	bank_routing=None,
	bank_account=None,
	approach="1step",
):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.snap_enabled:
		frappe.throw(_("Snap Finance is not enabled."))
	application_data = {
		"firstName": first_name,
		"lastName": last_name,
		"email": email,
		"phone": phone,
	}
	if requested_amount:
		application_data["requestedAmount"] = flt(requested_amount)
	if approach == "3step":
		application_data["step"] = "personal"
	if monthly_income:
		application_data["income"] = {"monthly": flt(monthly_income)}
	if bank_routing:
		application_data["bank"] = {"routingNumber": bank_routing, "accountNumber": bank_account}
	token = frappe.generate_hash(length=32)
	result = snap_utils.create_application(token, application_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	data = result["data"]
	state = data.get("state", "PENDING")
	return {
		"success": True,
		"application_id": data.get("applicationId"),
		"state": state,
		"approval_limit": flt(data.get("approvalLimit", 0)),
		"checkout_url": data.get("checkoutUrl"),
		"initial_payment": flt(data.get("initialPayment", 0)),
	}


@frappe.whitelist()
def get_snap_application(application_id):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	token = frappe.generate_hash(length=32)
	result = snap_utils.get_application(token, application_id)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	data = result["data"]
	return {
		"success": True,
		"application_id": data.get("applicationId"),
		"state": data.get("state"),
		"total_amount": flt(data.get("totalAmount", 0)),
		"tax_amount": flt(data.get("taxAmount", 0)),
		"approval_limit": flt(data.get("approvalLimit", 0)),
	}
