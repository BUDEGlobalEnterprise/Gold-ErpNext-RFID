"""
Progressive Leasing Integration Utilities

Commerce API for lease-to-own financing.
Multi-step: Application -> Cart -> Pricing -> Contract -> Delivery Confirmation.
"""

import frappe
from frappe import _
from frappe.utils import flt

try:
	import requests
except ImportError:
	requests = None


def _get_settings():
	return frappe.get_single("Payment Gateway Settings")


def _get_headers():
	return {
		"Content-Type": "application/json",
		"Accept": "application/json",
	}


def _api_request(method, endpoint, data=None):
	if not requests:
		frappe.throw(_("requests library is required for Progressive integration."))
	settings = _get_settings()
	if settings.is_sandbox():
		base_url = "https://api-stg.progleasing.com"
	else:
		base_url = "https://api.progleasing.com"
	url = f"{base_url}{endpoint}"
	try:
		resp = requests.request(method, url, headers=_get_headers(), json=data, timeout=30)
		result = resp.json()
		if resp.status_code >= 400:
			error_msg = result.get("message", str(result))
			return {"success": False, "error": error_msg}
		return {"success": True, "data": result}
	except Exception as e:
		frappe.log_error(f"Progressive API error: {e}", "Progressive")
		return {"success": False, "error": str(e)}


def submit_application(app_data):
	return _api_request("POST", "/api/v1/application", data=app_data)


def add_cart_items(application_id, cart_items):
	return _api_request("POST", f"/api/v1/application/{application_id}/cart", data=cart_items)


def get_pricing(application_id):
	return _api_request("GET", f"/api/v1/application/{application_id}/cart/pricing")


def get_contract(application_id):
	return _api_request("GET", f"/api/v1/application/{application_id}/contract")


def confirm_delivery(delivery_data):
	return _api_request("POST", "/api/v1/delivery/confirm", data=delivery_data)
