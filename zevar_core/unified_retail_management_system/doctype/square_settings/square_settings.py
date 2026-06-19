# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import call_hook_method, get_url
from urllib.parse import urlencode

class SquareSettings(Document):
	def validate(self):
		if not self.gateway_name:
			self.gateway_name = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "name") or "Square"

	def on_update(self):
		self.create_payment_gateway()

	def create_payment_gateway(self):
		gateway_name = f"Square-{self.gateway_name}"
		if not frappe.db.exists("Payment Gateway", gateway_name):
			gateway = frappe.new_doc("Payment Gateway")
			gateway.gateway = gateway_name
			gateway.gateway_settings = "Square Settings"
			gateway.gateway_controller = self.name
			gateway.insert(ignore_permissions=True)
		call_hook_method("payment_gateway_enabled", gateway=gateway_name)

	def validate_transaction_currency(self, currency):
		if currency not in ("USD", "CAD", "AUD", "GBP", "JPY", "EUR"):
			frappe.throw(_("Square does not support transactions in currency '{0}'").format(currency))

	def get_payment_url(self, **kwargs):
		# Will be used by Frappe to redirect to Square checkout page
		return get_url(f"/api/method/zevar_core.integrations.square_checkout.create_checkout_session?{urlencode(kwargs)}")
