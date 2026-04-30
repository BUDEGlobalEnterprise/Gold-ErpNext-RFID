"""
Stripe Terminal Integration Utilities

Handles API communication with Stripe Terminal for card-present payments.
Supports connection tokens, PaymentIntents, and device management.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint

import hashlib
import hmac
import json
import time

try:
	import requests
except ImportError:
	requests = None

STRIPE_API_BASE = "https://api.stripe.com/v1"


def _get_settings():
	return frappe.get_single("Payment Gateway Settings")


def _get_headers():
	settings = _get_settings()
	secret_key = settings.get_stripe_secret_key()
	return {
		"Authorization": f"Bearer {secret_key}",
		"Content-Type": "application/x-www-form-urlencoded",
		"Stripe-Version": "2024-12-18.acacia",
	}


def _api_request(method, endpoint, data=None):
	if not requests:
		frappe.throw(_("requests library is required for Stripe integration."))
	url = f"{STRIPE_API_BASE}{endpoint}"
	try:
		resp = requests.request(method, url, headers=_get_headers(), data=data, timeout=30)
		result = resp.json()
		if resp.status_code >= 400:
			error_msg = result.get("error", {}).get("message", str(result))
			frappe.log_error(f"Stripe API Error: {error_msg}", "Stripe Terminal")
			return {"success": False, "error": error_msg, "status_code": resp.status_code}
		return {"success": True, "data": result}
	except Exception as e:
		frappe.log_error(f"Stripe API request failed: {e}", "Stripe Terminal")
		return {"success": False, "error": str(e)}


def create_connection_token():
	result = _api_request("POST", "/terminal/connection_tokens")
	return result


def create_payment_intent(amount, currency="usd", description=None, metadata=None):
	data = {
		"amount": cint(flt(amount) * 100),
		"currency": currency,
		"payment_method_types[]": "card_present",
		"capture_method": "automatic",
	}
	if description:
		data["description"] = description
	if metadata:
		for k, v in metadata.items():
			data[f"metadata[{k}]"] = str(v)
	return _api_request("POST", "/payment_intents", data)


def capture_payment_intent(payment_intent_id):
	return _api_request("POST", f"/payment_intents/{payment_intent_id}/capture")


def cancel_payment_intent(payment_intent_id):
	return _api_request("POST", f"/payment_intents/{payment_intent_id}/cancel")


def retrieve_payment_intent(payment_intent_id):
	return _api_request("GET", f"/payment_intents/{payment_intent_id}")


def create_refund(payment_intent_id, amount=None, reason=None):
	data = {"payment_intent": payment_intent_id}
	if amount:
		data["amount"] = cint(flt(amount) * 100)
	if reason:
		data["reason"] = reason
	return _api_request("POST", "/refunds", data)


def list_terminals(limit=10):
	settings = _get_settings()
	data = {"limit": limit}
	if settings.stripe_terminal_location:
		data["location"] = settings.stripe_terminal_location
	return _api_request("GET", "/terminal/readers", data)


def simulate_payment(payment_intent_id):
	settings = _get_settings()
	if not settings.is_sandbox():
		return {"success": False, "error": "Simulation only available in sandbox mode"}
	data = {"payment_intent": payment_intent_id}
	return _api_request("POST", "/terminal/readers/rdr_123/test_helpers/present_payment_method", data)


def verify_webhook_signature(payload, sig_header):
	settings = _get_settings()
	webhook_secret = settings.get_stripe_webhook_secret()
	if not webhook_secret:
		frappe.log_error("Stripe webhook secret not configured", "Stripe Terminal")
		return False
	try:
		timestamp, signature = sig_header.split(",")
		timestamp = timestamp.split("=")[1]
		expected_sig = signature.split("=")[1]
		signed_payload = f"{timestamp}.{payload}"
		computed_sig = hmac.new(
			webhook_secret.encode("utf-8"),
			signed_payload.encode("utf-8"),
			hashlib.sha256,
		).hexdigest()
		return hmac.compare_digest(computed_sig, expected_sig)
	except Exception as e:
		frappe.log_error(f"Stripe webhook verification failed: {e}", "Stripe Terminal")
		return False
