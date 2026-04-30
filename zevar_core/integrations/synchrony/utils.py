"""
Synchrony Financial Integration Utilities

Handles API communication with Synchrony for prime credit applications
and credit authorizations (Apply API + Credit Authorizations API).
"""

import hashlib
import json
import time

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


def _api_request(method, endpoint, data=None, headers=None):
	if not requests:
		frappe.throw(_("requests library is required for Synchrony integration."))
	url = endpoint
	req_headers = headers or _get_headers()
	try:
		resp = requests.request(method, url, headers=req_headers, json=data, timeout=30)
		result = resp.json()
		if resp.status_code >= 400:
			error_msg = result.get("errorMessage", result.get("error", str(result)))
			frappe.log_error(f"Synchrony API Error: {error_msg}", "Synchrony")
			return {"success": False, "error": error_msg, "status_code": resp.status_code}
		return {"success": True, "data": result}
	except Exception as e:
		frappe.log_error(f"Synchrony API request failed: {e}", "Synchrony")
		return {"success": False, "error": str(e)}


def submit_credit_application(applicant_data):
	settings = _get_settings()
	if settings.is_sandbox():
		url = "https://api.stg.syf.com/v1/apply/retail"
	else:
		url = "https://api.syf.com/v1/apply/retail"
	return _api_request("POST", url, data=applicant_data)


def authorize_purchase(account_token, amount, promo_code=None, merchant_ref=None):
	settings = _get_settings()
	if settings.is_sandbox():
		url = "https://api.stg.syf.com/v1/credit/authorizations"
	else:
		url = "https://api.syf.com/v1/credit/authorizations"
	data = {
		"accountToken": account_token,
		"transactionAmount": flt(amount),
		"transactionType": "PURCHASE",
	}
	if promo_code:
		data["promoCode"] = promo_code
	if merchant_ref:
		data["merchantReferenceNumber"] = merchant_ref
	return _api_request("POST", url, data=data)


def preauthorize(account_token, amount, promo_code=None):
	return authorize_purchase(account_token, amount, promo_code=promo_code)


def completion(auth_reference, final_amount):
	settings = _get_settings()
	if settings.is_sandbox():
		url = f"https://api.stg.syf.com/v1/credit/authorizations/{auth_reference}/completion"
	else:
		url = f"https://api.syf.com/v1/credit/authorizations/{auth_reference}/completion"
	data = {"completionAmount": flt(final_amount)}
	return _api_request("POST", url, data=data)


def process_refund(account_token, amount, original_auth_reference=None):
	settings = _get_settings()
	if settings.is_sandbox():
		url = "https://api.stg.syf.com/v1/credit/refunds"
	else:
		url = "https://api.syf.com/v1/credit/refunds"
	data = {
		"accountToken": account_token,
		"refundAmount": flt(amount),
	}
	if original_auth_reference:
		data["originalAuthorizationReference"] = original_auth_reference
	return _api_request("POST", url, data=data)


def reverse_authorization(auth_reference):
	settings = _get_settings()
	if settings.is_sandbox():
		url = f"https://api.stg.syf.com/v1/credit/authorizations/{auth_reference}/reversal"
	else:
		url = f"https://api.syf.com/v1/credit/authorizations/{auth_reference}/reversal"
	return _api_request("POST", url, data={})


def get_promo_codes():
	settings = _get_settings()
	if settings.is_sandbox():
		url = "https://api.stg.syf.com/v1/promos"
	else:
		url = "https://api.syf.com/v1/promos"
	return _api_request("GET", url)
