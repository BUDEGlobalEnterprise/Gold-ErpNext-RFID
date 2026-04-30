# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

from zevar_core.services.inventory_audit_utils import _log_audit_event, _reconcile_audit


class CaseAuditSession(Document):
	def before_submit(self):
		if not self.completed_at:
			self.completed_at = now_datetime()

		missing_items, missing_count, total_value_scanned, total_value_discrepancy, has_unexpected = (
			_reconcile_audit(self)
		)

		self.total_value_scanned = total_value_scanned
		self.total_value_discrepancy = total_value_discrepancy

		# Compute variance dollar total (value of missing pieces)
		variance_dollar = 0.0
		if missing_items:
			item_codes = [m["item_code"] for m in missing_items]
			rates = {}
			if item_codes:
				for itm in frappe.get_all(
					"Item",
					filters={"name": ["in", item_codes]},
					fields=["name", "standard_rate", "valuation_rate"],
				):
					rates[itm.name] = flt(itm.standard_rate) or flt(itm.valuation_rate)
			for m in missing_items:
				variance_dollar += flt(m.get("qty", 1)) * rates.get(m["item_code"], 0)
		self.variance_dollar_total = variance_dollar

		# Check variance thresholds from Audit Policy
		policy = _get_audit_policy()
		threshold_dollars = flt(policy.get("variance_threshold_dollars", 500))
		threshold_pieces = int(policy.get("variance_pieces_hard_stop", 3))

		above_dollar_threshold = variance_dollar >= threshold_dollars
		above_pieces_threshold = missing_count > threshold_pieces

		if missing_items or has_unexpected:
			if above_dollar_threshold or above_pieces_threshold:
				self.status = "Pending Manager Review"
				self.freeze_reason = _build_freeze_reason(
					missing_count, variance_dollar, threshold_dollars, threshold_pieces
				)
			else:
				self.status = "Discrepancy"
		else:
			self.status = "Reconciled"

		self._missing_items = missing_items
		self._has_unexpected = has_unexpected
		self._above_threshold = above_dollar_threshold or above_pieces_threshold

	def on_submit(self):
		missing_items = getattr(self, "_missing_items", [])
		has_unexpected = getattr(self, "_has_unexpected", False)
		above_threshold = getattr(self, "_above_threshold", False)

		if above_threshold:
			# Freeze store: disable reservations and transfers
			_freeze_store(self.store_location, self.freeze_reason)
			_log_audit_event(
				"store_frozen",
				"Inventory",
				self.name,
				f"Store {self.store_location} frozen due to audit variance: {self.freeze_reason}",
			)
			# Notify managers
			frappe.enqueue(
				"zevar_core.services.inventory_audit_utils.notify_variance_escalation",
				session=self.name,
				store_location=self.store_location,
				missing_items_json=json.dumps(missing_items),
				freeze_reason=self.freeze_reason,
				queue="short",
				now=frappe.flags.in_test,
			)

		if missing_items and not above_threshold:
			# Below threshold: auto-create shrinkage entry
			policy = _get_audit_policy()
			if policy.get("auto_create_shrinkage_entry"):
				frappe.enqueue(
					"zevar_core.services.inventory_audit_utils.process_shrinkage_async",
					session=self.name,
					missing_items_json=json.dumps(missing_items),
					store_location=self.store_location,
					queue="long",
					now=frappe.flags.in_test,
				)
				# Update status to reflect auto-shrinkage
				self.db_set("status", "Reconciled with Shrinkage")

			frappe.enqueue(
				"zevar_core.services.inventory_audit_utils.notify_shrinkage_async",
				session=self.name,
				missing_items_json=json.dumps(missing_items),
				display_case=self.display_case or self.store_location,
				queue="short",
				now=frappe.flags.in_test,
			)

			_log_audit_event(
				"shrinkage_detected",
				"Inventory",
				self.name,
				f"Audit {self.name} finalized with discrepancies. Missing: {len(missing_items)}. Stock Entry processing in background.",
			)
		elif missing_items and above_threshold:
			# Above threshold: still process shrinkage but store is frozen
			policy = _get_audit_policy()
			if policy.get("auto_create_shrinkage_entry"):
				frappe.enqueue(
					"zevar_core.services.inventory_audit_utils.process_shrinkage_async",
					session=self.name,
					missing_items_json=json.dumps(missing_items),
					store_location=self.store_location,
					queue="long",
					now=frappe.flags.in_test,
				)
		else:
			_log_audit_event(
				"audit_reconciled", "Inventory", self.name, f"Audit {self.name} reconciled perfectly."
			)

		# Handle unexpected items: move to quarantine
		if has_unexpected:
			frappe.enqueue(
				"zevar_core.services.inventory_audit_utils.quarantine_unexpected_items",
				session=self.name,
				store_location=self.store_location,
				queue="long",
				now=frappe.flags.in_test,
			)

		# Update linked Audit Plan
		if self.audit_plan:
			frappe.db.set_value(
				"Audit Plan",
				self.audit_plan,
				{
					"status": "Completed",
					"completed_at": now_datetime(),
					"audit_session": self.name,
				},
			)


def _get_audit_policy():
	"""Get audit policy settings as dict. Returns defaults if no policy exists."""
	if frappe.db.exists("DocType", "Audit Policy"):
		try:
			doc = frappe.get_single("Audit Policy")
			return {
				"enable_audit_schedule": doc.enable_audit_schedule,
				"showcase_cadence_days": doc.showcase_cadence_days or 7,
				"backstock_cadence_days": doc.backstock_cadence_days or 30,
				"full_store_cadence_days": doc.full_store_cadence_days or 90,
				"daily_spot_case": doc.daily_spot_case,
				"variance_threshold_dollars": doc.variance_threshold_dollars or 500,
				"variance_pieces_hard_stop": doc.variance_pieces_hard_stop or 3,
				"auto_create_shrinkage_entry": doc.auto_create_shrinkage_entry,
				"require_two_person_rule": doc.require_two_person_rule,
			}
		except Exception:
			pass
	return {
		"enable_audit_schedule": 1,
		"showcase_cadence_days": 7,
		"backstock_cadence_days": 30,
		"full_store_cadence_days": 90,
		"variance_threshold_dollars": 500,
		"variance_pieces_hard_stop": 3,
		"auto_create_shrinkage_entry": 1,
		"require_two_person_rule": 1,
	}


def _build_freeze_reason(missing_count, variance_dollar, threshold_dollars, threshold_pieces):
	reasons = []
	if variance_dollar >= threshold_dollars:
		reasons.append(f"variance ${variance_dollar:.2f} >= ${threshold_dollars:.2f} threshold")
	if missing_count > threshold_pieces:
		reasons.append(f"{missing_count} missing pieces > {threshold_pieces} piece limit")
	return "; ".join(reasons)


def _freeze_store(store_location, reason):
	"""Freeze a store by setting a flag that blocks reservations and transfers."""
	# Use a simple cache flag; checked by reserve_for_customer and create_inter_store_transfer
	frappe.cache().set_value(f"zevar:store_frozen:{store_location}", reason)
	_log_audit_event(
		"store_frozen",
		"Inventory",
		store_location,
		f"Store {store_location} frozen: {reason}",
	)


def unfreeze_store(store_location, unfrozen_by):
	"""Unfreeze a store after manager approval."""
	frappe.cache().delete_key(f"zevar:store_frozen:{store_location}")
	_log_audit_event(
		"store_unfrozen",
		"Inventory",
		store_location,
		f"Store {store_location} unfrozen by {unfrozen_by}",
	)


def is_store_frozen(store_location):
	"""Check if a store is currently frozen due to audit variance."""
	return frappe.cache().get_value(f"zevar:store_frozen:{store_location}")
