"""
Snap Finance Integration Utilities

Platform API for deep subprime leasing.
Supports 1-step and 3-step application approaches with JS SDK integration.
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
		frappe.throw(_("requests library is required for Snap Finance integration."))
	settings = _get_settings()
	if settings.is_sandbox():
		base_url = "https://api-stg.snapfinance.com"
	else:
		base_url = "https://api.snapfinance.com"
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
		frappe.log_error(f"Snap Finance API error: {e}", "Snap Finance")
		return {"success": False, "error": str(e)}


def create_application(token, application_data):
	return _api_request("POST", "/platform/v1/applications", data=application_data, token=token)


def get_application(token, application_id):
	return _api_request("GET", f"/platform/v1/applications/{application_id}", token=token)


def update_application(token, application_id, data):
	return _api_request("PUT", f"/platform/v1/applications/{application_id}", data=data, token=token)
