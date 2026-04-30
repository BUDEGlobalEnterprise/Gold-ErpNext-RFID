"""
Zelle Integration Utilities

QR code generation for merchant alias + amount,
polling for payment confirmation via banking API middleware.
"""

import hashlib
import json

import frappe
from frappe import _
from frappe.utils import flt

try:
	import base64
	import io

	import qrcode

	HAS_QRCODE = True
except ImportError:
	HAS_QRCODE = False

try:
	import requests
except ImportError:
	requests = None


def _get_settings():
	return frappe.get_single("Payment Gateway Settings")


def generate_qr_code(amount, invoice_reference=None):
	settings = _get_settings()
	merchant_alias = settings.zelle_merchant_alias
	if not merchant_alias:
		frappe.throw(_("Zelle merchant alias is not configured."))
	qr_data = {
		"merchant_alias": merchant_alias,
		"amount": flt(amount),
		"currency": "USD",
		"reference": invoice_reference or frappe.generate_hash(length=8),
	}
	if not HAS_QRCODE:
		frappe.throw(_("qrcode library is required. Install with: pip install qrcode[pil]"))
	qr_string = json.dumps(qr_data)
	qr = qrcode.QRCode(version=1, box_size=10, border=5)
	qr.add_data(qr_string)
	qr.make(fit=True)
	img = qr.make_image(fill_color="black", back_color="white")
	buffer = io.BytesIO()
	img.save(buffer, format="PNG")
	qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
	return {
		"qr_code_base64": qr_base64,
		"qr_data": qr_data,
		"merchant_alias": merchant_alias,
		"reference": qr_data["reference"],
	}


def check_payment_received(amount, reference=None):
	settings = _get_settings()
	provider = settings.zelle_banking_provider
	if not provider:
		return {"received": False, "message": "No banking provider configured"}
	if provider == "Versori":
		return _check_versori(amount, reference)
	return {"received": False, "message": f"Provider {provider} not implemented"}


def _check_versori(amount, reference):
	return {"received": False, "message": "Poll Versori API for payment matching"}
