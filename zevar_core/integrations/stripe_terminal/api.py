"""
Stripe Terminal API Endpoints

Whitelisted API methods for the POS frontend to interact with Stripe Terminal.
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.stripe_terminal import utils as stripe_utils


@frappe.whitelist()
def get_connection_token():
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.stripe_enabled:
		frappe.throw(_("Stripe Terminal is not enabled."))
	result = stripe_utils.create_connection_token()
	if not result.get("success"):
		frappe.throw(_("Failed to create connection token: {0}").format(result.get("error")))
	return {"secret": result["data"].get("secret")}


@frappe.whitelist()
def create_terminal_payment(amount, currency="usd", invoice_name=None, description=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.stripe_enabled:
		frappe.throw(_("Stripe Terminal is not enabled."))
	if flt(amount) <= 0:
		frappe.throw(_("Amount must be greater than zero."))
	metadata = {}
	if invoice_name:
		metadata["invoice_name"] = invoice_name
		metadata["pos_station"] = frappe.session.user
	result = stripe_utils.create_payment_intent(
		amount=flt(amount),
		currency=currency,
		description=description or f"POS Transaction - {invoice_name or 'Direct'}",
		metadata=metadata,
	)
	if not result.get("success"):
		frappe.throw(_("Failed to create payment: {0}").format(result.get("error")))
	return {
		"client_secret": result["data"].get("client_secret"),
		"payment_intent_id": result["data"].get("id"),
		"amount": flt(amount),
		"status": result["data"].get("status"),
	}


@frappe.whitelist()
def get_payment_status(payment_intent_id):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	result = stripe_utils.retrieve_payment_intent(payment_intent_id)
	if not result.get("success"):
		frappe.throw(_("Failed to retrieve payment: {0}").format(result.get("error")))
	data = result["data"]
	return {
		"id": data.get("id"),
		"status": data.get("status"),
		"amount": flt(data.get("amount", 0)) / 100,
		"charges": [
			{
				"id": ch.get("id"),
				"amount": flt(ch.get("amount", 0)) / 100,
				"payment_method_details": ch.get("payment_method_details", {}),
				"receipt_url": ch.get("receipt_url"),
			}
			for ch in data.get("charges", {}).get("data", [])
		],
	}


@frappe.whitelist(methods=["POST"])
def cancel_terminal_payment(payment_intent_id):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	result = stripe_utils.cancel_payment_intent(payment_intent_id)
	if not result.get("success"):
		frappe.throw(_("Failed to cancel payment: {0}").format(result.get("error")))
	return {"success": True, "status": result["data"].get("status")}


@frappe.whitelist()
def list_terminal_devices():
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	result = stripe_utils.list_terminals()
	if not result.get("success"):
		return {"devices": []}
	devices = result["data"].get("data", [])
	return {
		"devices": [
			{
				"id": d.get("id"),
				"label": d.get("label"),
				"device_type": d.get("device_type"),
				"status": d.get("status"),
				"location": d.get("location"),
				"is_online": d.get("status") == "online",
			}
			for d in devices
		]
	}


@frappe.whitelist(methods=["POST"])
def refund_stripe_payment(payment_intent_id, amount=None, reason="requested_by_customer"):
	frappe.only_for(["Sales Manager", "System Manager"])
	result = stripe_utils.create_refund(payment_intent_id, amount=amount, reason=reason)
	if not result.get("success"):
		frappe.throw(_("Failed to process refund: {0}").format(result.get("error")))
	return {
		"success": True,
		"refund_id": result["data"].get("id"),
		"amount": flt(result["data"].get("amount", 0)) / 100,
		"status": result["data"].get("status"),
	}
