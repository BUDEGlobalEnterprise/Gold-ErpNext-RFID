"""
Square Terminal API Endpoints

Whitelisted API methods for the POS frontend to interact with Square Terminal.
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.square_terminal import utils as square_utils


@frappe.whitelist()
def pair_device(device_name, location_id=None):
	frappe.only_for(["System Manager", "Sales Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.square_enabled:
		frappe.throw(_("Square Terminal is not enabled."))
	result = square_utils.create_device_code(device_name, location_id)
	if not result.get("success"):
		frappe.throw(_("Failed to create device code: {0}").format(result.get("error")))
	code_data = result["data"].get("device_code", {})
	return {
		"device_code": code_data.get("code"),
		"device_id": code_data.get("device_id"),
		"status": code_data.get("status"),
		"pair_by": code_data.get("pair_by"),
	}


@frappe.whitelist()
def get_devices():
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	result = square_utils.list_devices()
	if not result.get("success"):
		return {"devices": []}
	devices = result["data"].get("devices", [])
	return {
		"devices": [
			{
				"id": d.get("id"),
				"name": d.get("name"),
				"type": d.get("type"),
				"status": d.get("status"),
				"location_id": d.get("location_id"),
			}
			for d in devices
		]
	}


@frappe.whitelist()
def create_terminal_checkout(device_id, amount, currency="USD", invoice_name=None, note=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.square_enabled:
		frappe.throw(_("Square Terminal is not enabled."))
	if flt(amount) <= 0:
		frappe.throw(_("Amount must be greater than zero."))
	amount_money = {"amount": int(flt(amount) * 100), "currency": currency}
	result = square_utils.create_checkout(
		device_id=device_id,
		amount_money=amount_money,
		reference_id=invoice_name or frappe.generate_hash(length=12),
		note=note or f"POS Transaction - {invoice_name or 'Direct'}",
	)
	if not result.get("success"):
		frappe.throw(_("Failed to create checkout: {0}").format(result.get("error")))
	checkout = result["data"].get("checkout", {})
	return {
		"checkout_id": checkout.get("id"),
		"reference_id": checkout.get("reference_id"),
		"status": checkout.get("status"),
		"amount": flt(amount),
		"device_id": checkout.get("device_options", {}).get("device_id"),
		"created_at": checkout.get("created_at"),
	}


@frappe.whitelist()
def get_checkout_status(checkout_id):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	result = square_utils.get_checkout(checkout_id)
	if not result.get("success"):
		frappe.throw(_("Failed to get checkout: {0}").format(result.get("error")))
	checkout = result["data"].get("checkout", {})
	payment = checkout.get("payment", {}) or {}
	return {
		"checkout_id": checkout.get("id"),
		"status": checkout.get("status"),
		"payment_id": payment.get("id"),
		"amount": flt(payment.get("amount_money", {}).get("amount", 0)) / 100,
		"card_brand": payment.get("card_details", {}).get("card", {}).get("card_brand"),
		"last_4": payment.get("card_details", {}).get("card", {}).get("last_4"),
		"receipt_url": payment.get("receipt_url"),
		"receipt_number": payment.get("receipt_number"),
	}


@frappe.whitelist(methods=["POST"])
def refund_square_payment(payment_id, amount, currency="USD", reason=None):
	frappe.only_for(["Sales Manager", "System Manager"])
	if flt(amount) <= 0:
		frappe.throw(_("Refund amount must be greater than zero."))
	amount_money = {"amount": int(flt(amount) * 100), "currency": currency}
	result = square_utils.create_refund(payment_id, amount_money, reason=reason)
	if not result.get("success"):
		frappe.throw(_("Failed to process refund: {0}").format(result.get("error")))
	refund = result["data"].get("refund", {})
	return {
		"success": True,
		"refund_id": refund.get("id"),
		"status": refund.get("status"),
		"amount": flt(refund.get("amount_money", {}).get("amount", 0)) / 100,
	}
