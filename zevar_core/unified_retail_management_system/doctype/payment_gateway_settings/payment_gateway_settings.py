import frappe
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password


class PaymentGatewaySettings(Document):
	def validate(self):
		self._validate_gateway_config()
		self._validate_financing_config()

	def _validate_gateway_config(self):
		if self.stripe_enabled and not self.stripe_api_key:
			frappe.throw(frappe._("Stripe Secret Key is required when Stripe Terminal is enabled."))
		if self.square_enabled and not self.square_access_token:
			frappe.throw(frappe._("Square Access Token is required when Square Terminal is enabled."))

	def _validate_financing_config(self):
		if not self.financing_waterfall_order:
			return
		try:
			frappe.parse_json(self.financing_waterfall_order)
		except Exception:
			frappe.throw(frappe._("Financing Waterfall Order must be a valid JSON array."))

	def get_stripe_secret_key(self):
		return get_decrypted_password("Payment Gateway Settings", "Payment Gateway Settings", "stripe_api_key")

	def get_stripe_publishable_key(self):
		return self.stripe_publishable_key or ""

	def get_stripe_webhook_secret(self):
		return get_decrypted_password("Payment Gateway Settings", "Payment Gateway Settings", "stripe_webhook_secret")

	def get_square_access_token(self):
		return get_decrypted_password("Payment Gateway Settings", "Payment Gateway Settings", "square_access_token")

	def get_square_webhook_signature(self):
		return get_decrypted_password("Payment Gateway Settings", "Payment Gateway Settings", "square_webhook_signature_key")

	def get_financing_waterfall(self):
		if not self.financing_waterfall_order:
			return ["Synchrony", "AFF", "Progressive", "Snap", "Acima"]
		try:
			return frappe.parse_json(self.financing_waterfall_order)
		except Exception:
			return ["Synchrony", "AFF", "Progressive", "Snap", "Acima"]

	def is_sandbox(self):
		return bool(self.sandbox_mode)
