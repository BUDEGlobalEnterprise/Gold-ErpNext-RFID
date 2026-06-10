"""Jewelry BOM assembly and disassembly operations.

Handles:
- Building a finished jewelry piece from components (assembly)
- Breaking down a piece into components (disassembly)
- Cost rollup from component costs
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, now_datetime

from zevar_core.services.inventory_events import (
	material_issue,
	material_receipt,
	transfer_serial,
)


def assemble_from_bom(bom_name: str, parent_serial_no: str | None = None) -> dict:
	"""Assemble a finished piece from a Jewelry BOM.

	1. Issues all component items from their source warehouses
	2. Receipts the parent item into the target warehouse
	3. Links child serials to parent via parent_serial_no
	"""
	bom = frappe.get_doc("Jewelry BOM", bom_name)
	if not bom.is_active:
		frappe.throw(_("BOM {0} is not active").format(bom_name))

	parent_item = bom.parent_item_code
	if not frappe.db.exists("Item", parent_item):
		frappe.throw(_("Parent item {0} not found").format(parent_item))

	target_warehouse = _get_assembly_warehouse(bom)
	total_component_cost = 0.0
	consumed_serials = []

	for comp in bom.components:
		if not comp.component_item:
			continue
		qty = flt(comp.qty_per_build)
		if qty <= 0:
			continue

		source_wh = _get_component_warehouse(comp, bom)
		unit_cost = flt(frappe.db.get_value("Item", comp.component_item, "valuation_rate") or 0)
		total_component_cost += unit_cost * qty

		serial_no = None
		if comp.serial_required and qty == 1:
			serial_no = _pick_available_serial(comp.component_item, source_wh)
			if serial_no:
				consumed_serials.append(serial_no)

		material_issue(
			item_code=comp.component_item,
			from_warehouse=source_wh,
			qty=qty,
			serial_no=serial_no,
		)

	labor_cost = flt(bom.labor_minutes or 0) * flt(bom.labor_cost_per_minute or 0)
	overhead = total_component_cost * flt(bom.overhead_pct or 0) / 100
	total_cost = total_component_cost + labor_cost + overhead

	se = material_receipt(
		item_code=parent_item,
		to_warehouse=target_warehouse,
		qty=flt(bom.yield_qty or 1),
		serial_no=parent_serial_no,
		valuation_rate=total_cost,
	)

	# Link child serials to parent
	if parent_serial_no:
		for child_sn in consumed_serials:
			frappe.db.set_value("Serial No", child_sn, "custom_parent_serial_no", parent_serial_no)

	_log_bom_event("assembly", bom_name, se.name, parent_item, parent_serial_no, total_cost)

	return {
		"success": True,
		"stock_entry": se.name,
		"parent_item": parent_item,
		"parent_serial": parent_serial_no,
		"component_cost": flt(total_component_cost, 2),
		"labor_cost": flt(labor_cost, 2),
		"overhead": flt(overhead, 2),
		"total_cost": flt(total_cost, 2),
	}


def disassemble_to_components(
	parent_serial_no: str,
	bom_name: str,
	reason: str | None = None,
) -> dict:
	"""Disassemble a finished piece back into components.

	For metals: returns to scrap/recovery warehouse.
	For stones/gemstones: returns to loose stone inventory.
	"""
	bom = frappe.get_doc("Jewelry BOM", bom_name)
	sn = frappe.get_doc("Serial No", parent_serial_no)

	if not sn.warehouse:
		frappe.throw(_("Serial No {0} has no warehouse").format(parent_serial_no))

	# Issue the parent piece
	parent_se = material_issue(
		item_code=sn.item_code,
		from_warehouse=sn.warehouse,
		qty=1,
		serial_no=parent_serial_no,
	)

	recovered_components = []

	for comp in bom.components:
		if not comp.component_item:
			continue
		qty = flt(comp.qty_per_build)
		if qty <= 0:
			continue

		dest_wh = _get_disassembly_destination(comp)
		unit_cost = flt(frappe.db.get_value("Item", comp.component_item, "valuation_rate") or 0)

		se = material_receipt(
			item_code=comp.component_item,
			to_warehouse=dest_wh,
			qty=qty,
			valuation_rate=unit_cost,
		)

		recovered_components.append(
			{
				"item_code": comp.component_item,
				"qty": qty,
				"warehouse": dest_wh,
				"stock_entry": se.name,
			}
		)

	# Clear parent_serial_no on any child serials
	child_serials = frappe.get_all(
		"Serial No",
		filters={"custom_parent_serial_no": parent_serial_no},
		pluck="name",
	)
	for child_sn in child_serials:
		frappe.db.set_value("Serial No", child_sn, "custom_parent_serial_no", None)

	_log_bom_event("disassembly", bom_name, parent_se.name, sn.item_code, parent_serial_no, 0, reason)

	return {
		"success": True,
		"parent_stock_entry": parent_se.name,
		"recovered_components": recovered_components,
	}


def get_bom_cost_rollup(bom_name: str) -> dict:
	"""Calculate the full cost rollup for a BOM."""
	bom = frappe.get_doc("Jewelry BOM", bom_name)

	component_costs = []
	total = 0.0

	for comp in bom.components:
		if not comp.component_item:
			continue
		qty = flt(comp.qty_per_build)
		unit_cost = flt(frappe.db.get_value("Item", comp.component_item, "valuation_rate") or 0)
		line_cost = unit_cost * qty
		total += line_cost

		component_costs.append(
			{
				"component_type": comp.component_type,
				"item_code": comp.component_item,
				"qty": qty,
				"unit_cost": flt(unit_cost, 2),
				"line_cost": flt(line_cost, 2),
			}
		)

	labor_cost = flt(bom.labor_minutes or 0) * flt(bom.labor_cost_per_minute or 0)
	overhead = total * flt(bom.overhead_pct or 0) / 100

	return {
		"bom_name": bom.name,
		"parent_item": bom.parent_item_code,
		"component_costs": component_costs,
		"material_total": flt(total, 2),
		"labor_cost": flt(labor_cost, 2),
		"overhead": flt(overhead, 2),
		"grand_total": flt(total + labor_cost + overhead, 2),
	}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_assembly_warehouse(bom) -> str:
	parent_item = bom.parent_item_code
	default_wh = frappe.db.get_value("Item", parent_item, "default_warehouse")
	if default_wh:
		return default_wh
	store_wh = frappe.db.get_value("Store Location", {"is_active": 1}, "default_warehouse")
	if store_wh:
		return store_wh
	frappe.throw(_("No target warehouse found for assembly"))


def _get_component_warehouse(comp, bom) -> str:
	if comp.vendor:
		eb = frappe.db.get_value("External Bench Vendor", {"supplier": comp.vendor}, "warehouse")
		if eb:
			return eb
	return _get_assembly_warehouse(bom)


def _get_disassembly_destination(comp) -> str:
	if comp.component_type in ("Center Stone", "Melee"):
		gem_wh = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Loose Stone%"]}, "name")
		if gem_wh:
			return gem_wh
	if comp.component_type == "Setting":
		scrap_wh = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Scrap%"]}, "name")
		if scrap_wh:
			return scrap_wh
	store_wh = frappe.db.get_value("Store Location", {"is_active": 1}, "default_warehouse")
	if store_wh:
		return store_wh
	frappe.throw(_("No destination warehouse found for disassembly component"))


def _pick_available_serial(item_code: str, warehouse: str) -> str | None:
	return frappe.db.get_value(
		"Serial No",
		{"item_code": item_code, "warehouse": warehouse, "status": "Active"},
		"name",
		order_by="creation asc",
	)


def _log_bom_event(event_type, bom_name, stock_entry, item_code, serial_no, cost, reason=None):
	log = frappe.new_doc("POS Audit Log")
	log.user = frappe.session.user
	log.event_type = f"bom_{event_type}"
	log.category = "Inventory"
	log.reference_type = "Stock Entry"
	log.reference_document = stock_entry
	log.details = frappe.as_json(
		{
			"bom": bom_name,
			"item_code": item_code,
			"serial_no": serial_no or "",
			"cost": flt(cost, 2),
			"reason": reason or "",
		}
	)
	log.insert(ignore_permissions=True)
