
import frappe
from frappe import _
from frappe.utils import flt

WATERFALL_PROVIDERS = {
	"Synchrony": {
		"module": "zevar_core.integrations.synchrony.api",
		"submit_method": "submit_application",
		"enabled_field": "synchrony_enabled",
	},
	"AFF": {
		"module": "zevar_core.integrations.aff.api",
		"submit_method": "submit_aff_application",
		"enabled_field": "aff_enabled",
	},
	"Progressive": {
		"module": "zevar_core.integrations.progressive.api",
		"submit_method": "submit_progressive_application",
		"enabled_field": "progressive_enabled",
	},
	"Snap": {
		"module": "zevar_core.integrations.snap.api",
		"submit_method": "submit_snap_application",
		"enabled_field": "snap_enabled",
	},
	"Acima": {
		"module": "zevar_core.integrations.acima.api",
		"submit_method": "submit_acima_application",
		"enabled_field": "acima_enabled",
	},
}

class FinancingWaterfallManager:
	def __init__(self, app_data):
		self.app_data = app_data
		self.results = []
		self.settings = frappe.get_single("Payment Gateway Settings")
		self.waterfall_order = self.settings.get_financing_waterfall()

	def run(self):
		for attempt, provider_name in enumerate(self.waterfall_order, 1):
			provider_config = WATERFALL_PROVIDERS.get(provider_name)
			if not provider_config:
				continue

			if not self.settings.get(provider_config["enabled_field"]):
				self.results.append({
					"provider": provider_name,
					"attempt": attempt,
					"status": "skipped",
					"reason": "Provider not enabled",
				})
				continue

			try:
				result = self._submit_to_provider(provider_name, provider_config, attempt)
				self.results.append(result)

				if result.get("status") == "approved":
					return self._complete("approved")

				if result.get("status") == "pending":
					return self._complete("pending")

			except Exception as e:
				error_msg = self._sanitize_error(str(e))
				self.results.append({
					"provider": provider_name,
					"attempt": attempt,
					"status": "error",
					"error": error_msg,
				})
				frappe.log_error(
					f"Waterfall error with {provider_name}: {error_msg}", 
					"Financing Waterfall",
					reference_doctype="Customer",
					reference_name=self.app_data.get("customer")
				)

		return self._complete("all_denied")

	def _submit_to_provider(self, provider_name, provider_config, attempt):
		# Include all relevant PII
		params = self.app_data.copy()
		
		module = frappe.get_module(provider_config["module"])
		method = getattr(module, provider_config["submit_method"])
		
		result = method(**params)
		
		decision = result.get("decision", result.get("status", "")).lower()
		is_approved = result.get("success") and decision in ("approved", "accepted", "approved_with_conditions")
		is_pending = not is_approved and decision in ("pending", "under_review", "wait")

		status = "denied"
		if is_approved:
			status = "approved"
		elif is_pending:
			status = "pending"

		return {
			"provider": provider_name,
			"attempt": attempt,
			"status": status,
			"application_id": result.get("application_id"),
			"approval_amount": flt(result.get("approval_amount") or result.get("credit_limit") or result.get("financed_amount") or result.get("approval_limit") or 0),
			"initial_payment": flt(result.get("initial_payment", 0)),
			"error": result.get("error"),
			"checkout_url": result.get("checkout_url"),
		}

	def _sanitize_error(self, error_msg):
		# Redact sensitive info from error messages
		for key in ("bank_account", "bank_routing", "ssn_last4"):
			val = self.app_data.get(key)
			if val and len(str(val)) > 4:
				error_msg = error_msg.replace(str(val), "********")
		return error_msg

	def _complete(self, status):
		return {
			"waterfall_complete": True,
			"status": status,
			"message": self._get_status_message(status),
			"waterfall_results": self.results,
		}

	def _get_status_message(self, status):
		messages = {
			"approved": _("Financing application approved!"),
			"pending": _("Application is pending review. Please wait for provider notification."),
			"all_denied": _("All financing providers denied the application."),
		}
		return messages.get(status, "")

def run_waterfall_async(app_data, user_email):
	# Set user context for background job
	frappe.set_user(user_email)
	manager = FinancingWaterfallManager(app_data)
	result = manager.run()
	
	# Notify user via Socket.io or Email if needed
	frappe.publish_realtime(
		"financing_waterfall_complete", 
		result, 
		user=user_email
	)
	return result
