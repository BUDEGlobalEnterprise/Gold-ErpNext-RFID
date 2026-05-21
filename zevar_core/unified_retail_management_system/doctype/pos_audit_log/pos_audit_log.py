# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class POSAuditLog(Document):
	"""POS Audit Log for tracking all POS-related events."""

	def before_insert(self) -> None:
		"""Set default values before insert."""
		if not self.timestamp:
			self.timestamp = now()

	def validate(self) -> None:
		"""Validate the audit log entry."""
		self._validate_event_type_category()

	def _validate_event_type_category(self) -> None:
		"""Ensure event type matches category."""
		event_category_map = {
			"Sales": [
				"invoice_created",
				"invoice_submitted",
				"invoice_cancelled",
				"invoice_voided",
				"invoice_returned",
			],
			"Payment": [
				"payment_received",
				"payment_refunded",
				"split_payment_processed",
				"finance_payment",
				"gift_card_used",
				"gift_card_issued",
			],
			"Discount": ["discount_applied", "large_discount_applied", "discount_override_approved"],
			"Session": [
				"session_opened",
				"session_closed",
				"cash_variance_detected",
				"blind_close_step1",
				"blind_close_sealed_final",
				"blind_close_finalized",
				"session_suspended",
				"session_resumed",
				"opening_count_verified",
			],
			"Security": [
				"login_success",
				"login_failed",
				"manager_override_requested",
				"manager_override_approved",
				"manager_override_rejected",
				"permission_denied",
			],
			"Layaway": ["layaway_created", "layaway_payment", "layaway_cancelled", "layaway_completed"],
			"Customer": ["customer_created", "customer_updated"],
			"Inventory": ["stock_adjusted", "low_stock_alert"],
		}

		if self.category:
			valid_events = event_category_map.get(self.category, [])
			if valid_events and self.event_type not in valid_events:
				frappe.msgprint(
					frappe._("Event type '{0}' is not typically in category '{1}'").format(
						self.event_type, self.category
					)
				)
