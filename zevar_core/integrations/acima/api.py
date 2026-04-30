"""
Acima API Endpoints
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.acima import utils as acima_utils


@frappe.whitelist(methods=["POST"])
def submit_acima_application(
	customer,
	first_name,
	last_name,
	email,
	phone,
	requested_amount=None,
	monthly_income=None,
):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.acima_enabled:
		frappe.throw(_("Acima is not enabled."))
	application_data = {
		"firstName": first_name,
		"lastName": last_name,
		"email": email,
		"phone": phone,
	}
	if requested_amount:
		application_data["requestedAmount"] = flt(requested_amount)
	if monthly_income:
		application_data["monthlyIncome"] = flt(monthly_income)
	token = frappe.generate_hash(length=32)
	result = acima_utils.submit_application(token, application_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	data = result["data"]
	return {
		"success": True,
		"application_id": data.get("applicationId"),
		"status": data.get("status"),
		"approval_amount": flt(data.get("approvalAmount", 0)),
		"initial_payment": flt(data.get("initialPayment", 0)),
		"early_purchase_option": data.get("hasEarlyPurchaseOption", False),
		"early_purchase_fee": flt(data.get("earlyPurchaseFee", 25)),
	}


@frappe.whitelist(methods=["POST"])
def sync_acima_cart(application_id, items):
	frappe.only_for(["Sales User", "Sales Manager"])
	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	cart_data = {
		"items": [
			{
				"sku": item.get("item_code", ""),
				"description": item.get("item_name", ""),
				"quantity": item.get("qty", 1),
				"price": flt(item.get("rate", 0)),
			}
			for item in items_list
		]
	}
	token = frappe.generate_hash(length=32)
	result = acima_utils.sync_cart(token, application_id, cart_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	return {
		"success": True,
		"cart_total": flt(result["data"].get("cartTotal", 0)),
		"lease_amount": flt(result["data"].get("leaseAmount", 0)),
		"initial_payment": flt(result["data"].get("initialPayment", 0)),
	}


@frappe.whitelist(methods=["POST"])
def confirm_acima_delivery(application_id, invoice_name):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	token = frappe.generate_hash(length=32)
	delivery_data = {"invoiceNumber": invoice_name}
	result = acima_utils.confirm_delivery(token, application_id, delivery_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	if frappe.db.exists("Financing Application", {"application_id": application_id}):
		app_name = frappe.db.get_value("Financing Application", {"application_id": application_id}, "name")
		doc = frappe.get_doc("Financing Application", app_name)
		doc.delivery_confirmed = 1
		doc.delivery_date = frappe.utils.now_datetime()
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	return {"success": True, "funding_status": result["data"].get("fundingStatus")}
