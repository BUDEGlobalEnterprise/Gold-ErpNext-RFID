"""
American First Finance API Endpoints
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.aff import utils as aff_utils


def _get_location_token():
	settings = frappe.get_single("Payment Gateway Settings")
	location_id = frappe.db.get_value("Store Location", {"is_active": 1}, "store_code") or "default"
	result = aff_utils.get_access_token(location_id)
	if not result.get("success"):
		frappe.throw(_("Failed to authenticate with AFF: {0}").format(result.get("error")))
	return result["data"].get("access_token")


@frappe.whitelist(methods=["POST"])
def submit_aff_application(
	customer,
	first_name,
	last_name,
	email,
	phone,
	monthly_income=None,
	requested_amount=None,
	address_line1=None,
	city=None,
	state=None,
	zip_code=None,
):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.aff_enabled:
		frappe.throw(_("American First Finance is not enabled."))
	token = _get_location_token()
	application_data = {
		"firstName": first_name,
		"lastName": last_name,
		"email": email,
		"phone": phone,
	}
	if monthly_income:
		application_data["monthlyIncome"] = flt(monthly_income)
	if requested_amount:
		application_data["customerRequestedAmount"] = flt(requested_amount)
	if address_line1:
		application_data["address"] = {
			"line1": address_line1,
			"city": city,
			"state": state,
			"zipCode": zip_code,
		}
	result = aff_utils.submit_application(token, application_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error"), "status": "error"}
	data = result["data"]
	app_status = data.get("appStatus", "PENDING")
	return {
		"success": True,
		"application_id": data.get("applicationId"),
		"status": app_status,
		"financed_amount": flt(data.get("financedAmount", 0)),
		"stipulations": data.get("stipulations", []),
		"checkout_url": data.get("checkoutUrl"),
	}


@frappe.whitelist()
def get_application_status(application_id):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	token = _get_location_token()
	result = aff_utils.get_application_status(token, application_id)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	data = result["data"]
	return {
		"success": True,
		"status": data.get("appStatus"),
		"financed_amount": flt(data.get("financedAmount", 0)),
		"stipulations": data.get("stipulations", []),
	}
