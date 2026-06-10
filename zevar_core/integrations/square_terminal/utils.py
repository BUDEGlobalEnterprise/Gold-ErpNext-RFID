"""
Square Terminal Integration Utilities

Handles REST API communication with Square Terminal for card-present payments.
Cloud-to-cloud checkout flow with device code pairing.
"""

import hashlib
import hmac
import json

import frappe
from frappe import _
from frappe.utils import cint, flt

try:
	import requests
except ImportError:
	requests = None


def _get_settings():
	return frappe.get_single("Payment Gateway Settings")


def _get_base_url():
	settings = _get_settings()
	if settings.is_sandbox():
		return "https://connect.squareupsandbox.com/v2"
	return "https://connect.squareup.com/v2"


def _get_headers():
	settings = _get_settings()
	token = settings.get_square_access_token()
	return {
		"Square-Version": "2024-12-18",
		"Authorization": f"Bearer {token}",
		"Content-Type": "application/json",
	}


def _api_request(method, endpoint, data=None):
	if not requests:
		frappe.throw(_("requests library is required for Square integration."))
	url = f"{_get_base_url()}{endpoint}"
	try:
		resp = requests.request(method, url, headers=_get_headers(), json=data, timeout=30)
		result = resp.json()
		if resp.status_code >= 400:
			errors = result.get("errors", [])
			error_msg = errors[0].get("detail", str(result)) if errors else str(result)
			frappe.log_error(f"Square API Error: {error_msg}", "Square Terminal")
			return {"success": False, "error": error_msg, "status_code": resp.status_code}
		return {"success": True, "data": result}
	except Exception as e:
		frappe.log_error(f"Square API request failed: {e}", "Square Terminal")
		return {"success": False, "error": str(e)}


def create_device_code(name, location_id):
	data = {
		"idempotency_key": frappe.generate_hash(length=32),
		"device_code": {
			"product_type": "TERMINAL_API",
			"name": name,
			"location_id": location_id,
		},
	}
	return _api_request("POST", "/devices/codes", data)


def list_devices(location_id=None):
	params = {}
	if location_id:
		params["location_id"] = location_id
	return _api_request("GET", "/devices", params)


def create_checkout(device_id, amount_money, reference_id=None, note=None, tip_money=None):
	data = {
		"idempotency_key": frappe.generate_hash(length=32),
		"amount_money": amount_money,
		"device_options": {
			"device_id": device_id,
			"skip_receipt_screen": False,
			"collect_signature": False,
		},
	}
	if reference_id:
		data["reference_id"] = reference_id
	if note:
		data["note"] = note
	if tip_money:
		data["tip_money"] = tip_money
	return _api_request("POST", "/terminals/checkouts", data)


def get_checkout(checkout_id):
	return _api_request("GET", f"/terminals/checkouts/{checkout_id}")


def dismiss_checkout(checkout_id):
	return _api_request("POST", f"/terminals/checkouts/{checkout_id}/dismiss")


def create_refund(payment_id, amount_money, reason=None, idempotency_key=None):
	data = {
		"idempotency_key": idempotency_key or frappe.generate_hash(length=32),
		"payment_id": payment_id,
		"amount_money": amount_money,
	}
	if reason:
		data["reason"] = reason
	return _api_request("POST", "/refunds", data)


def verify_webhook_signature(payload, sig_header, notification_url=None):
	settings = _get_settings()
	sig_key = settings.get_square_webhook_signature()
	if not sig_key:
		frappe.log_error("Square webhook signature key not configured", "Square Terminal")
		return False
	try:
		# Square signs: notification_url + request body, HMAC-SHA256 with webhook sig key
		url = notification_url or ""
		combined = url + payload
		computed = hmac.new(sig_key.encode("utf-8"), combined.encode("utf-8"), hashlib.sha256).hexdigest()
		# Square sends signature in header — compare using constant-time digest
		return hmac.compare_digest(computed, sig_header)
	except Exception as e:
		frappe.log_error(f"Square webhook verification failed: {e}", "Square Terminal")
		return False
