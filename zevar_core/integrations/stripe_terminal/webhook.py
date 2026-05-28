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
		"checkout.session.completed": _handle_checkout_session_completed,
		"checkout.session.expired": _handle_checkout_session_expired,
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


def _handle_checkout_session_completed(data):
	"""Handle Stripe Checkout Session completion (online repair payments)."""
	session_id = data.get("id")
	metadata = data.get("metadata", {})
	repair_order = metadata.get("repair_order")
	amount_total = flt(data.get("amount_total", 0)) / 100
	customer_email = data.get("customer_email", "")
	payment_intent = data.get("payment_intent", "")
	payment_status = data.get("payment_status", "")

	frappe.logger().info(
		f"Stripe Checkout completed: {session_id} for ${amount_total} "
		f"(repair: {repair_order}, status: {payment_status})"
	)

	# Only process if payment was actually collected
	if payment_status != "paid":
		frappe.logger().warning(
			f"Checkout {session_id} completed but payment_status={payment_status}, skipping"
		)
		return

	if repair_order and frappe.db.exists("Repair Order", repair_order):
		_reconcile_repair_payment(repair_order, session_id, payment_intent, amount_total, customer_email)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="stripe_checkout_completed",
		details={
			"session_id": session_id,
			"repair_order": repair_order,
			"amount": amount_total,
			"payment_intent": payment_intent,
			"customer_email": customer_email,
		},
		reference_document=repair_order or session_id,
	)


def _handle_checkout_session_expired(data):
	"""Handle Stripe Checkout Session expiry."""
	session_id = data.get("id")
	metadata = data.get("metadata", {})
	repair_order = metadata.get("repair_order")

	frappe.logger().warning(f"Stripe Checkout expired: {session_id} (repair: {repair_order})")

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="stripe_checkout_expired",
		details={"session_id": session_id, "repair_order": repair_order},
		reference_document=repair_order or session_id,
	)


def _reconcile_repair_payment(repair_order, session_id, payment_intent, amount, customer_email):
	"""Update a Repair Order with the payment received from Stripe Checkout."""
	try:
		doc = frappe.get_doc("Repair Order", repair_order)

		# Update deposit / payment status
		current_deposit = flt(doc.deposit_amount or 0)
		doc.deposit_amount = current_deposit + amount
		total_cost = flt(doc.total_cost or 0)
		if total_cost > 0 and doc.deposit_amount >= total_cost:
			doc.payment_status = "Fully Paid"
		else:
			doc.payment_status = "Partially Paid"

		# Recalculate balance
		doc.balance_due = max(0, total_cost - doc.deposit_amount)

		doc.flags.ignore_validate_update_after_submit = True
		doc.save(ignore_permissions=True)

		# Log communication on the repair
		try:
			doc._log_communication(
				"System",
				"Incoming",
				(
					f"Online payment of ${amount:.2f} received via Stripe Checkout\n"
					f"Session: {session_id}\n"
					f"Payment Intent: {payment_intent}\n"
					f"Customer Email: {customer_email}"
				),
				"System",
				"Payment Received",
			)
		except Exception:
			pass  # Communication logging is best-effort

		# Broadcast to live monitor
		try:
			from zevar_core.api.live_monitor import publish_repair_event

			publish_repair_event(
				"payment_received",
				{
					"repair": doc.name,
					"customer": doc.customer_name,
					"amount": amount,
					"method": "Stripe Checkout",
					"warehouse": doc.warehouse,
				},
			)
		except Exception:
			pass  # Live monitor broadcast is best-effort

		frappe.db.commit()

	except Exception:
		frappe.log_error(
			f"Failed to reconcile repair payment for {repair_order} (session: {session_id})",
			"Stripe Webhook",
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
			si.append(
				"payments",
				{"mode_of_payment": "Credit Card", "amount": amount, "reference_no": payment_intent_id},
			)
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
