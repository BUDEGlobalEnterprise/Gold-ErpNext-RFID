"""
Auto Stock Reduction Detection

Hooks into Sales Invoice on_submit to detect and log all stock reductions.
ERPNext handles actual stock via SLE — this module detects changes and creates
detailed POS Audit Log entries for every serial/item reduced.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime


def detect_stock_reduction(doc, method=None):
	if doc.doctype != "Sales Invoice":
		return

	if not doc.update_stock:
		return

	for item in doc.items:
		_detect_item_reduction(doc, item)


def _detect_item_reduction(invoice, item_row):
	serial_nos = []
	if item_row.serial_no:
		serial_nos = [s.strip() for s in item_row.serial_no.split("\n") if s.strip()]

	item_code = item_row.item_code
	qty = flt(item_row.qty)
	warehouse = item_row.warehouse

	if serial_nos:
		for sn in serial_nos:
			_log_serial_reduction(invoice, item_code, sn, warehouse)
	else:
		_log_bulk_reduction(invoice, item_code, qty, warehouse)


def _log_serial_reduction(invoice, item_code, serial_no, warehouse):
	item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code
	valuation = frappe.db.get_value("Serial No", serial_no, "valuation_rate") or 0
	sn_wh = frappe.db.get_value("Serial No", serial_no, "warehouse") or warehouse or "Unknown"

	details = {
		"invoice": invoice.name,
		"customer": invoice.customer,
		"item_code": item_code,
		"item_name": item_name,
		"serial_no": serial_no,
		"warehouse": sn_wh,
		"valuation_rate": flt(valuation, 2),
		"reduced_at": str(now_datetime()),
	}

	_log = frappe.new_doc("POS Audit Log")
	_log.user = invoice.owner or frappe.session.user
	_log.event_type = "stock_auto_reduced"
	_log.category = "Inventory"
	_log.severity = "Info"
	_log.reference_type = "Sales Invoice"
	_log.reference_document = invoice.name
	_log.details = frappe.as_json(details)
	_log.insert(ignore_permissions=True)


def _log_bulk_reduction(invoice, item_code, qty, warehouse):
	item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code
	valuation_rate = frappe.db.get_value("Item", item_code, "valuation_rate") or 0

	details = {
		"invoice": invoice.name,
		"customer": invoice.customer,
		"item_code": item_code,
		"item_name": item_name,
		"qty_reduced": qty,
		"warehouse": warehouse or "Not specified",
		"valuation_rate": flt(valuation_rate, 2),
		"total_value": flt(qty * valuation_rate, 2),
		"reduced_at": str(now_datetime()),
	}

	_log = frappe.new_doc("POS Audit Log")
	_log.user = invoice.owner or frappe.session.user
	_log.event_type = "stock_auto_reduced"
	_log.category = "Inventory"
	_log.severity = "Info"
	_log.reference_type = "Sales Invoice"
	_log.reference_document = invoice.name
	_log.details = frappe.as_json(details)
	_log.insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=False)
def get_recent_reductions(hours=24, limit=50):
	frappe.has_permission("POS Audit Log", ptype="read", throw=True)

	from frappe.utils import add_to_date

	since = add_to_date(now_datetime(), hours=-1 * int(hours))

	logs = frappe.get_all(
		"POS Audit Log",
		filters={
			"event_type": "stock_auto_reduced",
			"creation": [">=", since],
		},
		fields=["name", "user", "details", "reference_document", "creation"],
		order_by="creation desc",
		limit=int(limit),
	)

	results = []
	for log in logs:
		try:
			details = frappe.parse_json(log.details) if isinstance(log.details, str) else log.details
			results.append(
				{
					"log_id": log.name,
					"invoice": log.reference_document,
					"user": log.user,
					"item_code": details.get("item_code"),
					"item_name": details.get("item_name"),
					"serial_no": details.get("serial_no"),
					"qty_reduced": details.get("qty_reduced", 1),
					"warehouse": details.get("warehouse"),
					"valuation_rate": details.get("valuation_rate"),
					"total_value": details.get("total_value"),
					"reduced_at": details.get("reduced_at") or str(log.creation),
				}
			)
		except Exception:
			results.append({"log_id": log.name, "error": "Could not parse details"})

	return {"success": True, "count": len(results), "reductions": results}


@frappe.whitelist(allow_guest=False)
def ui_add_stock(item_code, warehouse, qty, valuation_rate=None, serial_no=None, reason=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.inventory_events import material_receipt

	qty = cint(qty)
	if qty <= 0:
		frappe.throw(_("Quantity must be greater than 0"))

	vr = flt(valuation_rate) if valuation_rate else None
	se = material_receipt(item_code, warehouse, qty=qty, serial_no=serial_no, valuation_rate=vr)

	_log = frappe.new_doc("POS Audit Log")
	_log.user = frappe.session.user
	_log.event_type = "stock_cli_adjustment"
	_log.category = "Inventory"
	_log.severity = "Info"
	_log.reference_type = "Stock Entry"
	_log.reference_document = se.name
	_log.details = frappe.as_json(
		{
			"action": "add_stock",
			"item_code": item_code,
			"warehouse": warehouse,
			"qty": qty,
			"serial_no": serial_no,
			"reason": reason or "UI stock addition",
			"stock_entry": se.name,
		}
	)
	_log.insert(ignore_permissions=True)

	return {"success": True, "stock_entry": se.name}


@frappe.whitelist(allow_guest=False)
def ui_remove_stock(serial_no, reason=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.inventory_events import material_issue

	sn = frappe.get_doc("Serial No", serial_no)
	if not sn.warehouse:
		frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))

	se = material_issue(sn.item_code, sn.warehouse, qty=1, serial_no=serial_no)

	_log = frappe.new_doc("POS Audit Log")
	_log.user = frappe.session.user
	_log.event_type = "stock_cli_adjustment"
	_log.category = "Inventory"
	_log.severity = "Info"
	_log.reference_type = "Stock Entry"
	_log.reference_document = se.name
	_log.details = frappe.as_json(
		{
			"action": "remove_stock",
			"serial_no": serial_no,
			"item_code": sn.item_code,
			"warehouse": sn.warehouse,
			"reason": reason or "UI stock removal",
			"stock_entry": se.name,
		}
	)
	_log.insert(ignore_permissions=True)

	return {"success": True, "stock_entry": se.name}


@frappe.whitelist(allow_guest=False)
def ui_move_stock(serial_no, target_warehouse):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	frappe.only_for("Sales Manager", "Store Manager", "System Manager")

	from zevar_core.services.inventory_events import transfer_serial

	sn = frappe.get_doc("Serial No", serial_no)
	if not sn.warehouse:
		frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))
	if sn.warehouse == target_warehouse:
		frappe.throw(_("Already in target warehouse"))

	se = transfer_serial(serial_no, sn.item_code, sn.warehouse, target_warehouse)

	_log = frappe.new_doc("POS Audit Log")
	_log.user = frappe.session.user
	_log.event_type = "stock_cli_adjustment"
	_log.category = "Inventory"
	_log.severity = "Info"
	_log.reference_type = "Stock Entry"
	_log.reference_document = se.name
	_log.details = frappe.as_json(
		{
			"action": "move_stock",
			"serial_no": serial_no,
			"item_code": sn.item_code,
			"from_warehouse": sn.warehouse,
			"to_warehouse": target_warehouse,
			"stock_entry": se.name,
		}
	)
	_log.insert(ignore_permissions=True)

	return {"success": True, "stock_entry": se.name}


@frappe.whitelist(allow_guest=False)
def ui_lookup_piece(query):
	frappe.has_permission("Serial No", ptype="read", throw=True)

	result = {"found": False, "query": query}

	sn = frappe.db.get_value(
		"Serial No",
		query,
		["name", "item_code", "item_name", "warehouse", "status", "valuation_rate"],
		as_dict=True,
	)
	if sn:
		wh_name = frappe.db.get_value("Warehouse", sn.warehouse, "warehouse_name") if sn.warehouse else "N/A"
		result = {
			"found": True,
			"type": "serial",
			"serial_no": sn.name,
			"item_code": sn.item_code,
			"item_name": sn.item_name,
			"warehouse": sn.warehouse,
			"warehouse_name": wh_name,
			"status": sn.status,
			"valuation_rate": flt(sn.valuation_rate, 2),
		}
	return result


@frappe.whitelist(allow_guest=False)
def ui_get_item_for_edit(item_code: str):
	frappe.has_permission("Item", ptype="read", throw=True)

	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} not found").format(item_code))

	item = frappe.get_doc("Item", item_code)

	gemstones = []
	child_field = None
	for fname in ["custom_gemstones", "gemstones"]:
		if hasattr(item, fname) and getattr(item, fname):
			child_field = fname
			break
	if child_field:
		for g in getattr(item, child_field):
			gemstones.append(
				{
					"gem_type": g.gem_type,
					"carat": flt(g.carat, 3),
					"count": cint(g.count),
					"cut": g.cut,
					"color": g.color,
					"clarity": g.clarity,
					"rate": flt(g.rate, 2),
				}
			)

	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"item_group": item.item_group,
		"description": item.description,
		"image": item.image,
		"standard_rate": flt(item.standard_rate, 2),
		"disabled": item.disabled,
		"custom_metal_type": item.get("custom_metal_type"),
		"custom_purity": item.get("custom_purity"),
		"custom_gross_weight_g": flt(item.get("custom_gross_weight_g", 0), 3),
		"custom_stone_weight_g": flt(item.get("custom_stone_weight_g", 0), 3),
		"custom_net_weight_g": flt(item.get("custom_net_weight_g", 0), 3),
		"custom_jewelry_type": item.get("custom_jewelry_type"),
		"custom_jewelry_subtype": item.get("custom_jewelry_subtype"),
		"custom_product_type": item.get("custom_product_type"),
		"custom_vendor": item.get("custom_vendor"),
		"custom_vendor_sku": item.get("custom_vendor_sku"),
		"custom_barcode": item.get("custom_barcode"),
		"custom_rfid_epc": item.get("custom_rfid_epc"),
		"custom_msrp": flt(item.get("custom_msrp", 0), 2),
		"custom_cost_price": flt(item.get("custom_cost_price", 0), 2),
		"custom_gender": item.get("custom_gender"),
		"custom_source": item.get("custom_source"),
		"custom_country_of_origin": item.get("custom_country_of_origin"),
		"custom_material_color": item.get("custom_material_color"),
		"custom_finish": item.get("custom_finish"),
		"custom_plating": item.get("custom_plating"),
		"custom_size": item.get("custom_size"),
		"custom_chain_type": item.get("custom_chain_type"),
		"custom_clasp_type": item.get("custom_clasp_type"),
		"custom_length_value": flt(item.get("custom_length_value", 0), 2),
		"custom_length_unit": item.get("custom_length_unit"),
		"custom_width_value": flt(item.get("custom_width_value", 0), 2),
		"custom_width_unit": item.get("custom_width_unit"),
		"gemstones": gemstones,
	}


@frappe.whitelist(allow_guest=False)
def ui_get_item_inventory(item_code: str):
	frappe.has_permission("Item", ptype="read", throw=True)

	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} not found").format(item_code))

	item = frappe.get_doc("Item", item_code)

	bins = frappe.get_all(
		"Bin",
		filters={"item_code": item_code, "actual_qty": [">", 0]},
		fields=["warehouse", "actual_qty", "valuation_rate", "stock_value"],
	)

	serials = frappe.get_all(
		"Serial No",
		filters={"item_code": item_code, "warehouse": ["is", "set"]},
		fields=["name", "warehouse", "status", "valuation_rate"],
		order_by="name",
	)

	from zevar_core.constants import STORE_LOCATIONS
	from zevar_core.services.inventory_events import _get_abbr

	abbr = _get_abbr()
	store_breakdown = {}
	for store_code, store_name in STORE_LOCATIONS.items():
		root = f"{store_code} - {abbr}"
		if not frappe.db.exists("Warehouse", root):
			continue
		wh_names = frappe.get_all(
			"Warehouse", filters={"parent_warehouse": root, "is_group": 0}, pluck="name"
		)
		store_qty = sum(
			flt(frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": wh}, "actual_qty") or 0)
			for wh in wh_names
		)
		if store_qty > 0:
			store_breakdown[store_code] = {"name": store_name, "qty": store_qty}

	reservations = frappe.get_all(
		"Stock Reservation",
		filters={"item_code": item_code, "status": "Active"},
		fields=["name", "serial_no", "customer", "hold_until", "deposit_amount"],
		limit=10,
	)

	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"item_group": item.item_group,
		"image": item.image,
		"disabled": item.disabled,
		"standard_rate": flt(item.standard_rate, 2),
		"valuation_rate": flt(item.valuation_rate, 2),
		"custom_metal_type": item.get("custom_metal_type"),
		"custom_purity": item.get("custom_purity"),
		"custom_gross_weight_g": flt(item.get("custom_gross_weight_g", 0), 3),
		"custom_stone_weight_g": flt(item.get("custom_stone_weight_g", 0), 3),
		"custom_net_weight_g": flt(item.get("custom_net_weight_g", 0), 3),
		"custom_jewelry_type": item.get("custom_jewelry_type"),
		"custom_vendor_sku": item.get("custom_vendor_sku"),
		"custom_vendor": item.get("custom_vendor"),
		"custom_barcode": item.get("custom_barcode"),
		"custom_msrp": flt(item.get("custom_msrp", 0), 2),
		"custom_cost_price": flt(item.get("custom_cost_price", 0), 2),
		"custom_gender": item.get("custom_gender"),
		"custom_source": item.get("custom_source"),
		"total_qty": sum(b.actual_qty for b in bins),
		"total_value": sum(flt(b.stock_value) for b in bins),
		"bins": bins,
		"serials": serials,
		"store_breakdown": store_breakdown,
		"reservations": reservations,
	}


@frappe.whitelist(allow_guest=False)
def ui_get_store_warehouses(store_code=None):
	frappe.has_permission("Warehouse", ptype="read", throw=True)

	from zevar_core.constants import STORE_LOCATIONS
	from zevar_core.services.inventory_events import _get_abbr

	abbr = _get_abbr()
	stores = (
		{store_code: STORE_LOCATIONS[store_code]}
		if store_code and store_code in STORE_LOCATIONS
		else STORE_LOCATIONS
	)

	result = {}
	for code, name in stores.items():
		root = f"{code} - {abbr}"
		if frappe.db.exists("Warehouse", root):
			whs = frappe.get_all(
				"Warehouse",
				filters={"parent_warehouse": root, "is_group": 0},
				fields=["name", "warehouse_name"],
			)
			result[code] = {"name": name, "warehouses": whs}

	return result
