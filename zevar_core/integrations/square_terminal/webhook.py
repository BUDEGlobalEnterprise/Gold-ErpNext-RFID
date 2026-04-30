"""
Square Terminal Webhook Handler

Processes asynchronous webhook events from Square Terminal.
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.square_terminal import utils as square_utils


def handle_webhook(payload, sig_header):
	if not square_utils.verify_webhook_signature(payload, sig_header):
		frappe.log_error("Invalid Square webhook signature", "Square Webhook")
		return {"success": False, "error": "Invalid signature"}
	try:
		import json
		event = json.loads(payload)
	except Exception:
		return {"success": False, "error": "Invalid payload"}
	event_type = event.get("type") or event.get("event_type")
	data = event.get("data", {}).get("object", {})
	handlers = {
		"terminal.checkout.updated": _handle_checkout_updated,
		"payment.updated": _handle_payment_updated,
		"payment.created": _handle_payment_created,
		"refund.updated": _handle_refund_updated,
	}
	handler = handlers.get(event_type)
	if handler:
		handler(data)
	else:
		frappe.logger().info(f"Unhandled Square event: {event_type}")
	return {"success": True}


def _handle_checkout_updated(data):
	checkout = data.get("checkout", data)
	status = checkout.get("status")
	reference_id = checkout.get("reference_id")
	if status == "COMPLETED" and reference_id:
		payment = checkout.get("payment", {}) or {}
		amount = flt(payment.get("amount_money", {}).get("amount", 0)) / 100
		payment_id = payment.get("id")
		if reference_id and frappe.db.exists("Sales Invoice", reference_id):
			_update_invoice_payment(reference_id, payment_id, amount)
		from zevar_core.api.audit_log import log_event_safely
		log_event_safely(
			event_type="square_checkout_completed",
			details={"checkout_id": checkout.get("id"), "payment_id": payment_id, "amount": amount},
			reference_document=reference_id,
		)


def _handle_payment_created(data):
	payment = data.get("payment", data)
	frappe.logger().info(f"Square payment created: {payment.get('id')}")


def _handle_payment_updated(data):
	payment = data.get("payment", data)
	status = payment.get("status")
	if status == "COMPLETED":
		frappe.logger().info(f"Square payment completed: {payment.get('id')}")


def _handle_refund_updated(data):
	refund = data.get("refund", data)
	frappe.logger().info(f"Square refund updated: {refund.get('id')} status={refund.get('status')}")


def _update_invoice_payment(invoice_name, payment_id, amount):
	try:
		si = frappe.get_doc("Sales Invoice", invoice_name)
		has_card_payment = any(
			p.mode_of_payment in ("Credit Card", "Debit Card", "Apple Pay", "Google Pay")
			for p in si.payments
		)
		if not has_card_payment:
			si.append("payments", {"mode_of_payment": "Credit Card", "amount": amount, "reference_no": payment_id})
			si.flags.ignore_validate_update_after_submit = True
			si.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.log_error(f"Failed to update invoice {invoice_name} with Square payment", "Square Webhook")
