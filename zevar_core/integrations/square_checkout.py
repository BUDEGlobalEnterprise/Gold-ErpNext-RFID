import frappe
from frappe import _
from urllib.parse import urlencode

@frappe.whitelist(allow_guest=True)
def create_checkout_session(**kwargs):
	try:
		# Extract data passed from Frappe Payments
		payment_request_name = kwargs.get("reference_docname")
		payment_request = frappe.get_doc("Payment Request", payment_request_name)
		
		# Get Square Settings
		square_settings = frappe.get_doc("Square Settings", payment_request.payment_gateway_account)
		
		from square.client import Client
		import uuid
		
		client = Client(
			access_token=square_settings.get_password("access_token"),
			environment="sandbox" if square_settings.environment == "Sandbox" else "production"
		)
		
		amount = int(payment_request.grand_total * 100)  # Square takes amount in cents
		currency = payment_request.currency
		
		body = {
			"idempotency_key": str(uuid.uuid4()),
			"order": {
				"location_id": square_settings.location_id,
				"line_items": [
					{
						"name": payment_request.reason,
						"quantity": "1",
						"base_price_money": {
							"amount": amount,
							"currency": currency
						}
					}
				]
			},
			"checkout_options": {
				"redirect_url": frappe.utils.get_url(f"/api/method/zevar_core.integrations.square_checkout.handle_redirect?payment_request={payment_request_name}")
			}
		}
		
		result = client.checkout.create_payment_link(body)
		
		if result.is_success():
			url = result.body["payment_link"]["url"]
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = url
		else:
			frappe.throw(_("Square Checkout Error: {0}").format(result.errors))
			
	except Exception as e:
		frappe.log_error("Square Checkout Error", str(e))
		frappe.throw(_("There was an error creating the Square checkout session. Please contact support."))

@frappe.whitelist(allow_guest=True)
def handle_redirect(**kwargs):
	# Square redirects here after payment is complete.
	payment_request_name = kwargs.get("payment_request")
	if payment_request_name:
		payment_request = frappe.get_doc("Payment Request", payment_request_name)
		# NOTE: You should ideally verify the payment status using Square API or rely on Square Webhooks
		# For simplicity, we just redirect to the success page.
		redirect_url = f"/payment-success?doctype=Payment%20Request&docname={payment_request_name}"
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = redirect_url
	else:
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/payment-failed"
