"""
Acima Integration Utilities

Enterprise REST API for high-ticket leasing up to $5,000.
Features 90-day early purchase option.
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


def _api_request(method, endpoint, data=None, token=None):
	if not requests:
		frappe.throw(_("requests library is required for Acima integration."))
	settings = _get_settings()
	if settings.is_sandbox():
		base_url = "https://api-stg.acima.com/v1"
	else:
		base_url = "https://api.acima.com/v1"
	url = f"{base_url}{endpoint}"
	headers = {"Content-Type": "application/json", "Accept": "application/json"}
	if token:
		headers["Authorization"] = f"Bearer {token}"
	try:
		resp = requests.request(method, url, headers=headers, json=data, timeout=30)
		result = resp.json()
		if resp.status_code >= 400:
			error_msg = result.get("message", str(result))
			return {"success": False, "error": error_msg}
		return {"success": True, "data": result}
	except Exception as e:
		frappe.log_error(f"Acima API error: {e}", "Acima")
		return {"success": False, "error": str(e)}


def submit_application(token, application_data):
	return _api_request("POST", "/applications", data=application_data, token=token)


def get_application(token, application_id):
	return _api_request("GET", f"/applications/{application_id}", token=token)


def sync_cart(token, application_id, cart_data):
	return _api_request("POST", f"/applications/{application_id}/cart", data=cart_data, token=token)


def confirm_delivery(token, application_id, delivery_data):
	return _api_request("POST", f"/applications/{application_id}/delivery", data=delivery_data, token=token)
