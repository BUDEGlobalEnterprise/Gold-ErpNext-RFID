"""Repair Parts Consumption service.

Tracks parts/materials consumed during jewelry repairs with full
stock audit trail via Stock Entry (Material Issue).
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, now_datetime


def consume_part(
	repair_order: str,
	component_item: str,
	qty: float,
	source_warehouse: str,
	unit_cost: float | None = None,
	serial_no: str | None = None,
	notes: str | None = None,
) -> dict:
	"""Issue a part from warehouse for a repair order."""
	_validate_repair_open(repair_order)
	_validate_stock_available(component_item, source_warehouse, qty, serial_no)

	if not unit_cost:
		unit_cost = flt(frappe.db.get_value("Item", component_item, "valuation_rate") or 0)

	from zevar_core.services.inventory_events import material_issue

	se = material_issue(
		item_code=component_item,
		from_warehouse=source_warehouse,
		qty=qty,
		serial_no=serial_no,
	)

	# Add to repair order parts_consumed table
	repair = frappe.get_doc("Repair Order", repair_order)
	repair.append(
		"parts_consumed",
		{
			"component_item": component_item,
			"component_item_name": frappe.db.get_value("Item", component_item, "item_name"),
			"qty": qty,
			"uom": frappe.db.get_value("Item", component_item, "stock_uom") or "Nos",
			"unit_cost": unit_cost,
			"source_warehouse": source_warehouse,
			"serial_no": serial_no or "",
			"consumed_at": now_datetime(),
			"consumed_by": frappe.session.user,
			"notes": notes or "",
		},
	)
	repair.save(ignore_permissions=True)

	_log_parts_event("part_consumed", repair_order, component_item, qty, se.name)

	return {
		"success": True,
		"stock_entry": se.name,
		"repair_order": repair_order,
		"component_item": component_item,
		"qty": qty,
		"cost": flt(qty * unit_cost, 2),
	}


def return_unused_part(
	repair_order: str,
	component_item: str,
	qty: float,
	to_warehouse: str,
	serial_no: str | None = None,
) -> dict:
	"""Return an unused part back to warehouse from a repair."""
	from zevar_core.services.inventory_events import material_receipt

	se = material_receipt(
		item_code=component_item,
		to_warehouse=to_warehouse,
		qty=qty,
		serial_no=serial_no,
	)

	_log_parts_event("part_returned", repair_order, component_item, qty, se.name)

	return {
		"success": True,
		"stock_entry": se.name,
		"repair_order": repair_order,
	}


def get_parts_summary(repair_order: str) -> dict:
	"""Get consumed parts summary for a repair order."""
	repair = frappe.get_doc("Repair Order", repair_order)
	parts = []
	total_cost = 0.0

	for row in repair.parts_consumed:
		line_cost = flt(row.qty) * flt(row.unit_cost)
		total_cost += line_cost
		parts.append(
			{
				"component_item": row.component_item,
				"component_item_name": row.component_item_name,
				"qty": row.qty,
				"uom": row.uom,
				"unit_cost": flt(row.unit_cost, 2),
				"line_cost": flt(line_cost, 2),
				"source_warehouse": row.source_warehouse,
				"serial_no": row.serial_no,
				"consumed_at": str(row.consumed_at) if row.consumed_at else "",
				"consumed_by": row.consumed_by,
			}
		)

	return {
		"repair_order": repair_order,
		"parts": parts,
		"total_parts_cost": flt(total_cost, 2),
		"parts_count": len(parts),
	}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_repair_open(repair_order: str):
	status = frappe.db.get_value("Repair Order", repair_order, "status")
	if not status:
		frappe.throw(_("Repair Order {0} not found").format(repair_order))
	if status in ("Completed", "Cancelled", "Delivered"):
		frappe.throw(_("Cannot consume parts for a {0} repair").format(status))


def _validate_stock_available(item_code: str, warehouse: str, qty: float, serial_no: str | None = None):
	if serial_no:
		sn_wh = frappe.db.get_value("Serial No", serial_no, "warehouse")
		if sn_wh != warehouse:
			frappe.throw(_("Serial No {0} is not in warehouse {1}").format(serial_no, warehouse))
	else:
		actual_qty = flt(
			frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
		)
		if actual_qty < qty:
			frappe.throw(
				_("Insufficient stock: {0} available, {1} needed in {2}").format(actual_qty, qty, warehouse)
			)


def _log_parts_event(event_type, repair_order, item_code, qty, stock_entry):
	log = frappe.new_doc("POS Audit Log")
	log.user = frappe.session.user
	log.event_type = event_type
	log.category = "Repair"
	log.reference_type = "Repair Order"
	log.reference_document = repair_order
	log.details = frappe.as_json(
		{
			"item_code": item_code,
			"qty": qty,
			"stock_entry": stock_entry,
		}
	)
	log.insert(ignore_permissions=True)
