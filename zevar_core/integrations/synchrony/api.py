"""
Synchrony Financial API Endpoints

Whitelisted API methods for the POS frontend to submit credit applications,
authorize purchases, and manage Synchrony financing.
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.synchrony import utils as sync_utils


@frappe.whitelist(methods=["POST"])
def submit_application(
	customer,
	first_name,
	last_name,
	address_line1,
	city,
	state,
	zip_code,
	phone=None,
	email=None,
	ssn_last4=None,
	annual_income=None,
	requested_amount=None,
):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.synchrony_enabled:
		frappe.throw(_("Synchrony Financial is not enabled."))

	applicant_data = {
		"firstName": first_name,
		"lastName": last_name,
		"addressLine1": address_line1,
		"city": city,
		"state": state,
		"zipCode": zip_code,
	}
	if phone:
		applicant_data["phone"] = phone
	if email:
		applicant_data["email"] = email
	if ssn_last4:
		applicant_data["last4SSN"] = ssn_last4
	if annual_income:
		applicant_data["annualIncome"] = flt(annual_income)
	if requested_amount:
		applicant_data["requestedCreditLimit"] = flt(requested_amount)

	result = sync_utils.submit_credit_application(applicant_data)
	if not result.get("success"):
		_log_financing_application(customer, "Synchrony", "Denied", requested_amount, result.get("error"))
		return {"success": False, "error": result.get("error"), "status": "denied"}

	data = result["data"]
	decision = data.get("decision", "DENIED")
	app_id = data.get("applicationId", "")

	status = "Approved" if decision == "APPROVED" else "Denied"
	_log_financing_application(
		customer,
		"Synchrony",
		status,
		requested_amount,
		provider_response=data,
		application_id=app_id,
		approved_amount=data.get("approvedCreditLimit"),
	)
	return {
		"success": decision == "APPROVED",
		"decision": decision,
		"application_id": app_id,
		"credit_limit": flt(data.get("approvedCreditLimit", 0)),
		"account_token": data.get("accountToken", ""),
		"promo_codes": data.get("availablePromoCodes", []),
	}


@frappe.whitelist()
def authorize_payment(customer, account_token, amount, promo_code=None, invoice_name=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.synchrony_enabled:
		frappe.throw(_("Synchrony Financial is not enabled."))
	if flt(amount) <= 0:
		frappe.throw(_("Amount must be greater than zero."))
	result = sync_utils.authorize_purchase(
		account_token=account_token,
		amount=flt(amount),
		promo_code=promo_code,
		merchant_ref=invoice_name,
	)
	if not result.get("success"):
		frappe.throw(_("Synchrony authorization failed: {0}").format(result.get("error")))
	data = result["data"]
	return {
		"success": True,
		"auth_reference": data.get("authorizationReference"),
		"auth_code": data.get("authorizationCode"),
		"amount": flt(data.get("authorizedAmount", amount)),
		"status": data.get("status"),
	}


@frappe.whitelist()
def get_promotions():
	frappe.only_for(["Sales User", "Sales Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.synchrony_enabled:
		return {"promotions": []}
	result = sync_utils.get_promo_codes()
	if not result.get("success"):
		return {"promotions": []}
	return {"promotions": result["data"].get("promotions", [])}


@frappe.whitelist(methods=["POST"])
def refund_synchrony(account_token, amount, original_auth_reference=None):
	frappe.only_for(["Sales Manager", "System Manager"])
	result = sync_utils.process_refund(account_token, flt(amount), original_auth_reference)
	if not result.get("success"):
		frappe.throw(_("Synchrony refund failed: {0}").format(result.get("error")))
	return {
		"success": True,
		"refund_reference": result["data"].get("refundReference"),
		"amount": flt(result["data"].get("refundAmount", 0)),
	}


def _log_financing_application(customer, provider, status, amount, error=None, **kwargs):
	try:
		app = frappe.new_doc("Financing Application")
		app.customer = customer
		app.provider = provider
		app.status = status
		app.requested_amount = flt(amount) if amount else 0
		if error:
			app.denial_reason = str(error)[:500]
		if kwargs.get("application_id"):
			app.application_id = kwargs["application_id"]
		if kwargs.get("approved_amount"):
			app.approved_amount = flt(kwargs["approved_amount"])
		if kwargs.get("provider_response"):
			app.provider_response = frappe.as_json(kwargs["provider_response"])
		app.created_by_associate = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
		app.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.log_error("Failed to log financing application", "Synchrony")
