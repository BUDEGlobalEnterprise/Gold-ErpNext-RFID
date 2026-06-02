"""External Bench Vendor management service.

Handles dispatching repairs to external bench vendors and tracking
return/receipt of completed work.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, now_datetime


def dispatch_to_bench(
	repair_order: str,
	vendor: str,
	estimated_days: int | None = None,
	notes: str | None = None,
) -> dict:
	"""Dispatch a repair order to an external bench vendor."""
	_validate_repair_dispatchable(repair_order)

	bench = frappe.db.get_value(
		"External Bench Vendor",
		{"supplier": vendor},
		["name", "warehouse", "default_turnaround_days", "specialty"],
		as_dict=True,
	)
	if not bench:
		frappe.throw(_("External Bench Vendor not configured for supplier {0}").format(vendor))

	turnaround = estimated_days or bench.default_turnaround_days or 14

	repair = frappe.get_doc("Repair Order", repair_order)
	repair.external_bench_vendor = vendor
	repair.external_bench_dispatched_at = now_datetime()
	repair.save(ignore_permissions=True)

	_log_bench_event("dispatched_to_bench", repair_order, vendor, bench.warehouse)

	return {
		"success": True,
		"repair_order": repair_order,
		"vendor": vendor,
		"bench_warehouse": bench.warehouse,
		"estimated_return": str(add_to_date(now_datetime(), days=turnaround)),
	}


def receive_from_bench(
	repair_order: str,
	invoice_ref: str | None = None,
	bench_cost: float | None = None,
) -> dict:
	"""Receive a repair back from external bench."""
	repair = frappe.get_doc("Repair Order", repair_order)
	if not repair.external_bench_vendor:
		frappe.throw(_("Repair Order {0} was not dispatched to an external bench").format(repair_order))

	repair.external_bench_received_at = now_datetime()
	if invoice_ref:
		repair.external_bench_invoice_ref = invoice_ref
	if bench_cost is not None:
		repair.external_bench_cost = flt(bench_cost)
	repair.save(ignore_permissions=True)

	_log_bench_event("received_from_bench", repair_order, repair.external_bench_vendor, None)

	return {
		"success": True,
		"repair_order": repair_order,
		"vendor": repair.external_bench_vendor,
		"received_at": str(now_datetime()),
	}


def get_bench_status(vendor: str) -> dict:
	"""Get all repairs currently at an external bench vendor."""
	repairs = frappe.get_all(
		"Repair Order",
		filters={
			"external_bench_vendor": vendor,
			"external_bench_received_at": ["is", "not set"],
			"status": ["not in", ["Completed", "Cancelled", "Delivered"]],
		},
		fields=["name", "customer", "status", "external_bench_dispatched_at", "external_bench_vendor"],
		order_by="external_bench_dispatched_at asc",
	)

	return {
		"vendor": vendor,
		"active_repairs": repairs,
		"count": len(repairs),
	}


def get_overdue_bench_repairs(days_threshold: int = 14) -> list[dict]:
	"""Get repairs that have been at external bench longer than threshold."""
	from frappe.utils import add_days

	cutoff = add_days(now_datetime(), -days_threshold)

	repairs = frappe.get_all(
		"Repair Order",
		filters={
			"external_bench_dispatched_at": ["<=", cutoff],
			"external_bench_received_at": ["is", "not set"],
			"status": ["not in", ["Completed", "Cancelled", "Delivered"]],
		},
		fields=[
			"name", "customer", "status",
			"external_bench_vendor", "external_bench_dispatched_at",
		],
		order_by="external_bench_dispatched_at asc",
	)

	return repairs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_repair_dispatchable(repair_order: str):
	status = frappe.db.get_value("Repair Order", repair_order, "status")
	if not status:
		frappe.throw(_("Repair Order {0} not found").format(repair_order))
	if status in ("Completed", "Cancelled", "Delivered"):
		frappe.throw(_("Cannot dispatch a {0} repair to bench").format(status))


def _log_bench_event(event_type, repair_order, vendor, warehouse):
	log = frappe.new_doc("POS Audit Log")
	log.user = frappe.session.user
	log.event_type = event_type
	log.category = "Repair"
	log.reference_type = "Repair Order"
	log.reference_document = repair_order
	log.details = frappe.as_json({
		"vendor": vendor,
		"warehouse": warehouse or "",
	})
	log.insert(ignore_permissions=True)
