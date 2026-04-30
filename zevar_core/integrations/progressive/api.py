"""
Progressive Leasing API Endpoints
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.progressive import utils as prog_utils


@frappe.whitelist(methods=["POST"])
def submit_progressive_application(
	customer,
	first_name,
	last_name,
	email,
	phone,
	monthly_income=None,
	pay_frequency=None,
	bank_routing=None,
	bank_account=None,
	requested_amount=None,
):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.progressive_enabled:
		frappe.throw(_("Progressive Leasing is not enabled."))
	app_data = {
		"firstName": first_name,
		"lastName": last_name,
		"emailAddress": email,
		"mobilePhone": phone,
	}
	if monthly_income:
		app_data["monthlyIncome"] = flt(monthly_income)
	if pay_frequency:
		app_data["payFrequency"] = pay_frequency
	if bank_routing:
		app_data["bankRoutingNumber"] = bank_routing
	if bank_account:
		app_data["bankAccountNumber"] = bank_account
	result = prog_utils.submit_application(app_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	data = result["data"]
	return {
		"success": True,
		"application_id": data.get("applicationId"),
		"status": data.get("status"),
		"approval_amount": flt(data.get("approvedLeaseAmount", 0)),
		"initial_payment": flt(data.get("initialPayment", 0)),
	}


@frappe.whitelist(methods=["POST"])
def add_cart_to_application(application_id, items):
	frappe.only_for(["Sales User", "Sales Manager"])
	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	cart_items = {"items": []}
	for item in items_list:
		cart_items["items"].append({
			"sku": item.get("item_code", ""),
			"description": item.get("item_name", ""),
			"quantity": item.get("qty", 1),
			"price": flt(item.get("rate", 0)),
			"serialNumber": item.get("serial_number", ""),
		})
	result = prog_utils.add_cart_items(application_id, cart_items)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	return {"success": True, "cart_total": result["data"].get("cartTotal")}


@frappe.whitelist()
def get_lease_pricing(application_id):
	frappe.only_for(["Sales User", "Sales Manager"])
	result = prog_utils.get_pricing(application_id)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	data = result["data"]
	return {
		"success": True,
		"cash_price": flt(data.get("cashPrice", 0)),
		"total_lease_cost": flt(data.get("totalLeaseCost", 0)),
		"initial_payment": flt(data.get("initialPayment", 0)),
		"monthly_payment": flt(data.get("monthlyPayment", 0)),
		"term_months": data.get("leaseTermMonths", 0),
		"disclosures": data.get("disclosures", {}),
	}


@frappe.whitelist()
def get_lease_contract(application_id):
	frappe.only_for(["Sales User", "Sales Manager"])
	result = prog_utils.get_contract(application_id)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	return {
		"success": True,
		"contract_url": result["data"].get("contractUrl"),
		"contract_html": result["data"].get("contractHtml"),
	}


@frappe.whitelist(methods=["POST"])
def confirm_delivery(application_id, invoice_name, delivery_date=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	delivery_data = {
		"applicationId": application_id,
		"invoiceNumber": invoice_name,
	}
	if delivery_date:
		delivery_data["deliveryDate"] = delivery_date
	result = prog_utils.confirm_delivery(delivery_data)
	if not result.get("success"):
		return {"success": False, "error": result.get("error")}
	if frappe.db.exists("Financing Application", {"application_id": application_id}):
		app_name = frappe.db.get_value("Financing Application", {"application_id": application_id}, "name")
		doc = frappe.get_doc("Financing Application", app_name)
		doc.delivery_confirmed = 1
		doc.delivery_date = delivery_date or frappe.utils.now_datetime()
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	return {"success": True, "funding_status": result["data"].get("fundingStatus")}
