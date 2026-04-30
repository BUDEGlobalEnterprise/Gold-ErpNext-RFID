"""
Financing Waterfall Orchestrator

Implements the prime-to-subprime financing cascade:
Synchrony -> AFF -> Progressive -> Snap -> Acima

When a customer's application is denied by one provider,
the system automatically cascades to the next, reusing PII
to prevent re-keying and cart abandonment.
"""

import frappe
from frappe import _, flt

from zevar_core.services.financing_service import WATERFALL_PROVIDERS, FinancingWaterfallManager


@frappe.whitelist(methods=["POST"])
def start_financing_waterfall(**kwargs):
	"""
	Starts the financing waterfall process.
	Can be run synchronously or asynchronously.
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	# Validate and sanitize input
	required_fields = ["customer", "first_name", "last_name", "requested_amount"]
	for field in required_fields:
		if not kwargs.get(field):
			frappe.throw(_("{0} is required").format(_(field.replace("_", " ").title())))

	# Structure data for internal processing
	app_data = {
		"customer": kwargs.get("customer"),
		"first_name": kwargs.get("first_name"),
		"last_name": kwargs.get("last_name"),
		"email": kwargs.get("email"),
		"phone": kwargs.get("phone"),
		"monthly_income": flt(kwargs.get("monthly_income")),
		"requested_amount": flt(kwargs.get("requested_amount")),
		"ssn_last4": str(kwargs.get("ssn_last4") or "")[-4:],
		"address_line1": kwargs.get("address_line1"),
		"city": kwargs.get("city"),
		"state": kwargs.get("state"),
		"zip_code": kwargs.get("zip_code"),
		"pay_frequency": kwargs.get("pay_frequency"),
		"bank_routing": kwargs.get("bank_routing"),
		"bank_account": kwargs.get("bank_account"),
	}

	if kwargs.get("async_mode"):
		frappe.enqueue(
			"zevar_core.services.financing_service.run_waterfall_async",
			app_data=app_data,
			user_email=frappe.session.user,
			queue="long",
			at_front=True,
		)
		return {
			"status": "queued",
			"message": _("Financing waterfall started in background. You will be notified once complete."),
		}

	# Synchronous execution
	manager = FinancingWaterfallManager(app_data)
	return manager.run()


@frappe.whitelist()
def get_waterfall_status():
	settings = frappe.get_single("Payment Gateway Settings")
	waterfall = settings.get_financing_waterfall()
	available = []
	for provider_name in waterfall:
		config = WATERFALL_PROVIDERS.get(provider_name)
		if config and settings.get(config["enabled_field"]):
			available.append(provider_name)
	return {
		"waterfall_order": waterfall,
		"available_providers": available,
	}
