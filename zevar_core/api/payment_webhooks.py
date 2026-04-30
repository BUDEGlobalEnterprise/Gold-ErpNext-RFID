"""
Payment Gateway Webhook Endpoints

Central webhook handler that routes events to the correct provider.
Called via www/ endpoint or API method.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True, methods=["POST"])
def stripe_webhook():
	import json
	payload = frappe.request.get_data(as_text=True)
	sig_header = frappe.get_request_header("Stripe-Signature", "")
	from zevar_core.integrations.stripe_terminal.webhook import handle_webhook
	result = handle_webhook(payload, sig_header)
	return result


@frappe.whitelist(allow_guest=True, methods=["POST"])
def square_webhook():
	import json
	payload = frappe.request.get_data(as_text=True)
	sig_header = frappe.get_request_header("X-Square-Signature", "")
	from zevar_core.integrations.square_terminal.webhook import handle_webhook
	result = handle_webhook(payload, sig_header)
	return result


def verify_webhook_token(provider):
	settings = frappe.get_single("Payment Gateway Settings")
	secret_field = f"{provider.lower()}_webhook_secret"
	expected = settings.get(secret_field)

	if not expected:
		# If no secret is configured, we assume it's not yet secured in settings
		return

	received = frappe.get_request_header("X-Zevar-Webhook-Secret") or frappe.get_request_header("Authorization")
	if received and received.startswith("Bearer "):
		received = received[7:]

	if received != expected:
		frappe.throw(_("Invalid webhook secret for {0}").format(provider), frappe.PermissionError)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def aff_callback():
	verify_webhook_token("AFF")
	import json
	payload = frappe.request.get_data(as_text=True)
	try:
		data = json.loads(payload)
	except Exception:
		return {"success": False}
	event_type = data.get("eventType")
	application_id = data.get("applicationId")
	app_status = data.get("appStatus")
	if application_id and frappe.db.exists("Financing Application", {"application_id": application_id}):
		app_name = frappe.db.get_value("Financing Application", {"application_id": application_id}, "name")
		doc = frappe.get_doc("Financing Application", app_name)
		if app_status == "APPROVED":
			doc.status = "Approved"
			doc.approved_amount = data.get("financedAmount", 0)
		elif app_status == "DENIED":
			doc.status = "Denied"
			doc.denial_reason = data.get("denialReason", "")
		doc.provider_response = frappe.as_json(data)
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	from zevar_core.api.audit_log import log_event_safely
	log_event_safely(
		event_type="aff_callback",
		details={"application_id": application_id, "status": app_status, "event_type": event_type},
	)
	return {"success": True}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def snap_callback():
	verify_webhook_token("Snap")
	import json
	payload = frappe.request.get_data(as_text=True)
	try:
		data = json.loads(payload)
	except Exception:
		return {"success": False}
	application_id = data.get("applicationId")
	state = data.get("state")
	if application_id and frappe.db.exists("Financing Application", {"application_id": application_id}):
		app_name = frappe.db.get_value("Financing Application", {"application_id": application_id}, "name")
		doc = frappe.get_doc("Financing Application", app_name)
		if state in ("APPROVED", "SIGNED"):
			doc.status = "Approved"
			doc.approved_amount = data.get("totalAmount", 0)
		elif state in ("DENIED", "CANCELLED"):
			doc.status = "Denied"
			doc.denial_reason = data.get("reason", "")
		doc.provider_response = frappe.as_json(data)
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	return {"success": True}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def zelle_webhook():
	verify_webhook_token("Zelle")
	import json
	payload = frappe.request.get_data(as_text=True)
	try:
		data = json.loads(payload)
	except Exception:
		return {"success": False}
	amount = data.get("amount", 0)
	sender = data.get("sender", {})
	reference = data.get("reference", "")

	# Sanitize sender details for logging
	safe_sender = {}
	if isinstance(sender, dict):
		for k, v in sender.items():
			if k in ("account_number", "routing_number", "email", "phone"):
				safe_sender[k] = "********"
			else:
				safe_sender[k] = v
	else:
		safe_sender = "********"

	frappe.logger().info(f"Zelle payment received: ${amount} from {safe_sender}")
	from zevar_core.api.audit_log import log_event_safely
	log_event_safely(
		event_type="zelle_payment_received",
		details={"amount": amount, "sender": safe_sender, "reference": reference},
	)
	return {"success": True}
