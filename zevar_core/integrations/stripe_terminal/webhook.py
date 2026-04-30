"""
Stripe Terminal Webhook Handler

Processes asynchronous webhook events from Stripe.
Validates signatures, reconciles payments, and updates invoice status.
"""

import frappe
from frappe import _
from frappe.utils import flt, now_datetime

from zevar_core.integrations.stripe_terminal import utils as stripe_utils


def handle_webhook(payload, sig_header):
	if not stripe_utils.verify_webhook_signature(payload, sig_header):
		frappe.log_error("Invalid Stripe webhook signature", "Stripe Webhook")
		return {"success": False, "error": "Invalid signature"}
	try:
		import json
		event = json.loads(payload)
	except Exception:
		frappe.log_error("Invalid Stripe webhook payload", "Stripe Webhook")
		return {"success": False, "error": "Invalid payload"}
	event_type = event.get("type")
	event_data = event.get("data", {}).get("object", {})
	handlers = {
		"payment_intent.succeeded": _handle_payment_succeeded,
		"payment_intent.canceled": _handle_payment_canceled,
		"payment_intent.payment_failed": _handle_payment_failed,
		"charge.refunded": _handle_charge_refunded,
	}
	handler = handlers.get(event_type)
	if handler:
		handler(event_data)
	else:
		frappe.logger().info(f"Unhandled Stripe event: {event_type}")
	return {"success": True}


def _handle_payment_succeeded(data):
	payment_intent_id = data.get("id")
	metadata = data.get("metadata", {})
	invoice_name = metadata.get("invoice_name")
	amount = flt(data.get("amount", 0)) / 100
	frappe.logger().info(f"Stripe payment succeeded: {payment_intent_id} for ${amount}")
	if invoice_name and frappe.db.exists("Sales Invoice", invoice_name):
		_update_invoice_payment(invoice_name, payment_intent_id, amount, "Card Present")
	_store_payment_token(data)
	from zevar_core.api.audit_log import log_event_safely
	log_event_safely(
		event_type="stripe_payment_succeeded",
		details={"payment_intent_id": payment_intent_id, "amount": amount, "invoice": invoice_name},
		reference_document=invoice_name or payment_intent_id,
	)


def _handle_payment_canceled(data):
	payment_intent_id = data.get("id")
	frappe.logger().info(f"Stripe payment canceled: {payment_intent_id}")
	from zevar_core.api.audit_log import log_event_safely
	log_event_safely(
		event_type="stripe_payment_canceled",
		details={"payment_intent_id": payment_intent_id},
	)


def _handle_payment_failed(data):
	payment_intent_id = data.get("id")
	metadata = data.get("metadata", {})
	invoice_name = metadata.get("invoice_name")
	frappe.logger().warning(f"Stripe payment failed: {payment_intent_id}")
	from zevar_core.api.audit_log import log_event_safely
	log_event_safely(
		event_type="stripe_payment_failed",
		details={"payment_intent_id": payment_intent_id, "invoice": invoice_name},
		reference_document=invoice_name or payment_intent_id,
	)


def _handle_charge_refunded(data):
	charge_id = data.get("id")
	refund_amount = flt(data.get("amount_refunded", 0)) / 100
	frappe.logger().info(f"Stripe charge refunded: {charge_id} for ${refund_amount}")
	from zevar_core.api.audit_log import log_event_safely
	log_event_safely(
		event_type="stripe_refund_processed",
		details={"charge_id": charge_id, "refund_amount": refund_amount},
	)


def _update_invoice_payment(invoice_name, payment_intent_id, amount, method):
	try:
		si = frappe.get_doc("Sales Invoice", invoice_name)
		has_card_payment = False
		for p in si.payments:
			if p.mode_of_payment in ("Credit Card", "Debit Card", "Apple Pay", "Google Pay"):
				has_card_payment = True
				break
		if not has_card_payment:
			si.append("payments", {"mode_of_payment": "Credit Card", "amount": amount, "reference_no": payment_intent_id})
			si.flags.ignore_validate_update_after_submit = True
			si.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.log_error(f"Failed to update invoice {invoice_name} with Stripe payment", "Stripe Webhook")


def _store_payment_token(data):
	try:
		charges = data.get("charges", {}).get("data", [])
		if not charges:
			return
		charge = charges[0]
		payment_method = charge.get("payment_method")
		pm_details = charge.get("payment_method_details", {}).get("card_present", {})
		if not payment_method:
			return
		metadata = data.get("metadata", {})
		invoice_name = metadata.get("invoice_name")
		customer = None
		if invoice_name and frappe.db.exists("Sales Invoice", invoice_name):
			customer = frappe.db.get_value("Sales Invoice", invoice_name, "customer")
		if not customer:
			return
		if not frappe.db.exists("Payment Token", {"token_id": payment_method}):
			token = frappe.new_doc("Payment Token")
			token.customer = customer
			token.provider = "Stripe"
			token.token_type = "Card"
			token.token_id = payment_method
			token.last_four = pm_details.get("last4", "")
			token.card_brand = pm_details.get("brand", "")
			token.label = f"{pm_details.get('brand', 'Card')} ending {pm_details.get('last4', '****')}"
			token.insert(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		frappe.log_error("Failed to store Stripe payment token", "Stripe Webhook")
