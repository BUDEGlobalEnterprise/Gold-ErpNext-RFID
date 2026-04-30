"""
American First Finance (AFF) Integration Utilities

Tokenized REST API for near-prime and subprime financing.
Location-based authentication with callback webhook support.
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


def _get_api_base():
	settings = _get_settings()
	if settings.is_sandbox():
		return "https://api-stg.americanfirstfinance.com/v2"
	return "https://api.americanfirstfinance.com/v2"


def _api_request(method, endpoint, data=None, token=None):
	if not requests:
		frappe.throw(_("requests library is required for AFF integration."))
	url = f"{_get_api_base()}{endpoint}"
	headers = {"Content-Type": "application/json", "Accept": "application/json"}
	if token:
		headers["Authorization"] = f"Bearer {token}"
	try:
		resp = requests.request(method, url, headers=headers, json=data, timeout=30)
		result = resp.json()
		if resp.status_code >= 400:
			error_msg = result.get("message", result.get("error", str(result)))
			return {"success": False, "error": error_msg}
		return {"success": True, "data": result}
	except Exception as e:
		frappe.log_error(f"AFF API error: {e}", "AFF Integration")
		return {"success": False, "error": str(e)}


def get_access_token(location_id):
	settings = _get_settings()
	data = {"locationId": location_id, "grant_type": "client_credentials"}
	return _api_request("POST", "/auth/token", data=data)


def submit_application(token, application_data):
	return _api_request("POST", "/applications", data=application_data, token=token)


def get_application_status(token, application_id):
	return _api_request("GET", f"/applications/{application_id}", token=token)


def get_contract(token, application_id):
	return _api_request("GET", f"/applications/{application_id}/contract", token=token)
