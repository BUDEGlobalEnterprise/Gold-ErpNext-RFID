"""Inventory management API — 14 endpoints for the unified inventory workflow.

Every endpoint uses @frappe.whitelist(allow_guest=False), validates permissions,
validates/casts kwargs, and writes a POS Audit Log row.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import add_to_date, cint, cstr, flt, now_datetime

from zevar_core.constants import (
	DEFAULT_RESERVATION_HOURS,
	INVENTORY_ZONES,
	REORDER_SAFETY_DAYS,
	SELLABLE_ZONES,
	STORE_LOCATIONS,
)
from zevar_core.services.inventory_events import (
	_get_abbr,
	_get_company,
	_get_cost_center,
	_get_store_warehouse,
	_get_zone_warehouse,
	_log_inventory_event,
	consign_in,
	consign_out,
	damage_write_off,
	dispatch_inter_store_transfer,
	gift_out,
	material_issue,
	material_receipt,
	move_to_showcase,
	receive_inter_store_transfer,
	recover_found_piece,
	repair_in,
	repair_out,
	return_to_quarantine,
	trade_in_accept,
	transfer_serial,
	vendor_return,
)


def _validate_kwargs(kwargs, required_fields):
	for field in required_fields:
		if not kwargs.get(field):
			frappe.throw(_("{0} is required").format(field))


def _get_store_code_from_warehouse(wh):
	parent = frappe.db.get_value("Warehouse", wh, "parent_warehouse")
	if not parent:
		parts = wh.split(" - ")
		return parts[0].strip() if parts else None
	parts = parent.split(" - ")
	return parts[0].strip() if parts else None


# ─── 1. bulk_push_to_stores ────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def bulk_push_to_stores(item_code=None, allocation=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["item_code", "allocation"])

	if isinstance(allocation, str):
		allocation = json.loads(allocation)

	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} does not exist").format(item_code))

	abbr = _get_abbr()
	company = _get_company()
	cost_center = _get_cost_center(company)
	results = []

	for alloc in allocation:
		store_code = cstr(alloc.get("store_code"))
		qty = cint(alloc.get("qty", 0))
		if qty <= 0:
			continue

		back_stock_wh = f"Back Stock {store_code} - {abbr}"
		if not frappe.db.exists("Warehouse", back_stock_wh):
			frappe.throw(_("Warehouse {0} not found. Run warehouse seed patch.").format(back_stock_wh))

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Receipt"
		se.company = company
		se.cost_center = cost_center

		for _i in range(qty):
			se.append(
				"items",
				{
					"item_code": item_code,
					"qty": 1,
					"t_warehouse": back_stock_wh,
					"cost_center": cost_center,
				},
			)

		se.insert(ignore_permissions=True)
		se.submit()
		results.append({"store": store_code, "stock_entry": se.name, "qty": qty})

	_log_inventory_event(
		"bulk_push_completed",
		"Item",
		item_code,
		f"Pushed {sum(a.get('qty', 0) for a in allocation)} pieces across {len(results)} stores",
	)
	return {"success": True, "results": results}


# ─── 2. reserve_for_customer ────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def reserve_for_customer(serial_no=None, customer=None, hold_until=None, deposit_amount=0):
	frappe.has_permission("Stock Reservation", ptype="create", throw=True)
	_validate_kwargs(locals(), ["serial_no", "customer"])

	if not hold_until:
		hold_until = add_to_date(now_datetime(), hours=DEFAULT_RESERVATION_HOURS)

	reservation = frappe.new_doc("Stock Reservation")
	reservation.customer = customer
	reservation.serial_no = serial_no
	reservation.hold_until = hold_until
	reservation.deposit_amount = flt(deposit_amount)
	reservation.insert(ignore_permissions=True)
	reservation.submit()

	return {
		"success": True,
		"reservation": reservation.name,
		"stock_entry": reservation.stock_entry_ref,
	}


# ─── 3. release_reservation ─────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def release_reservation(reservation_name=None):
	frappe.has_permission("Stock Reservation", ptype="cancel", throw=True)
	_validate_kwargs(locals(), ["reservation_name"])

	res = frappe.get_doc("Stock Reservation", reservation_name)
	if res.status != "Active":
		frappe.throw(_("Reservation is not active"))
	res.cancel()
	return {"success": True, "status": "Cancelled"}


# ─── 4. create_inter_store_transfer ──────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def create_inter_store_transfer(items=None, source=None, destination=None, carrier_ref=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["items", "source", "destination"])

	if isinstance(items, str):
		items = json.loads(items)

	if not items:
		frappe.throw(_("No items to transfer"))

	abbr = _get_abbr()
	source_code = _get_store_code_from_warehouse(source)
	dest_code = _get_store_code_from_warehouse(destination)
	if not source_code or not dest_code:
		frappe.throw(_("Could not determine store codes from warehouses"))

	transit_out_wh = f"Transit Out {source_code} - {abbr}"
	if not frappe.db.exists("Warehouse", transit_out_wh):
		frappe.throw(_("Transit Out warehouse not found for {0}").format(source_code))

	serial_nos = []
	item_codes = []
	for item in items:
		sn = cstr(item.get("serial_no"))
		ic = cstr(item.get("item_code"))
		if not sn:
			sn = frappe.db.get_value("Serial No", {"item_code": ic, "warehouse": source}, "name")
		if sn:
			serial_nos.append(sn)
			item_codes.append(ic or frappe.db.get_value("Serial No", sn, "item_code"))

	if not serial_nos:
		frappe.throw(_("No valid serial numbers found for transfer"))

	entries = dispatch_inter_store_transfer(serial_nos, item_codes, source, transit_out_wh)
	return {
		"success": True,
		"stock_entries": entries,
		"transit_warehouse": transit_out_wh,
		"destination": destination,
		"pieces_dispatched": len(serial_nos),
	}


# ─── 5. receive_inter_store_transfer ─────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def do_receive_inter_store_transfer(transfer_name=None, scanned_serials=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["scanned_serials"])

	if isinstance(scanned_serials, str):
		scanned_serials = json.loads(scanned_serials)

	abbr = _get_abbr()
	dest_back_stock = None

	if transfer_name:
		sle = frappe.get_all(
			"Stock Ledger Entry",
			filters={"voucher_no": transfer_name, "actual_qty": [">", 0]},
			fields=["warehouse"],
			limit=1,
		)
		if sle:
			dest_code = _get_store_code_from_warehouse(sle[0].warehouse)
			if dest_code:
				dest_back_stock = f"Back Stock {dest_code} - {abbr}"

	if not dest_back_stock:
		frappe.throw(_("Could not determine destination back stock warehouse"))

	serial_nos = []
	item_codes = []
	for sn in scanned_serials:
		sn = cstr(sn)
		if not frappe.db.exists("Serial No", sn):
			continue
		ic = frappe.db.get_value("Serial No", sn, "item_code")
		wh = frappe.db.get_value("Serial No", sn, "warehouse")
		if ic and wh:
			serial_nos.append(sn)
			item_codes.append(ic)

	if not serial_nos:
		frappe.throw(_("No valid serial numbers scanned"))

	transit_out_wh = frappe.db.get_value("Serial No", serial_nos[0], "warehouse")
	entries = receive_inter_store_transfer(serial_nos, item_codes, transit_out_wh, dest_back_stock)

	variance = len(scanned_serials) - len(serial_nos)
	return {
		"success": True,
		"stock_entries": entries,
		"received": len(serial_nos),
		"expected": len(scanned_serials),
		"variance": variance,
	}


# ─── 6. damage_write_off ────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def do_damage_write_off(serial_no=None, reason=None, evidence_file=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["serial_no"])

	sn = frappe.get_doc("Serial No", serial_no)
	if not sn.warehouse:
		frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))

	store_code = _get_store_code_from_warehouse(sn.warehouse)
	abbr = _get_abbr()
	shrinkage_wh = f"Shrinkage {store_code} - {abbr}" if store_code else None
	if not shrinkage_wh or not frappe.db.exists("Warehouse", shrinkage_wh):
		shrinkage_wh = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Shrinkage%"]}, "name")
	if not shrinkage_wh:
		frappe.throw(_("No Shrinkage warehouse found"))

	se = damage_write_off(serial_no, sn.item_code, sn.warehouse, shrinkage_wh, reason)
	return {"success": True, "stock_entry": se.name}


# ─── 7. gift_out ─────────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def do_gift_out(serial_no=None, reason=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["serial_no"])

	sn = frappe.get_doc("Serial No", serial_no)
	if not sn.warehouse:
		frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))

	se = gift_out(serial_no, sn.item_code, sn.warehouse, reason)
	return {"success": True, "stock_entry": se.name}


# ─── 8. consign_out ─────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def do_consign_out(items=None, event_name=None, return_by=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["items", "event_name"])

	if isinstance(items, str):
		items = json.loads(items)

	abbr = _get_abbr()
	first_sn = items[0].get("serial_no") if items else None
	if not first_sn:
		frappe.throw(_("No serial numbers provided"))

	sn_doc = frappe.get_doc("Serial No", first_sn)
	store_code = _get_store_code_from_warehouse(sn_doc.warehouse)
	back_stock_wh = f"Back Stock {store_code} - {abbr}" if store_code else sn_doc.warehouse
	consignment_wh = f"Consignment - {event_name} - {abbr}"

	if not frappe.db.exists("Warehouse", consignment_wh):
		parent_wh = frappe.db.get_value("Warehouse", back_stock_wh, "parent_warehouse")
		frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": f"Consignment - {event_name}",
				"parent_warehouse": parent_wh,
				"company": _get_company(),
				"is_group": 0,
			}
		).insert(ignore_permissions=True)

	serial_nos = [cstr(i.get("serial_no")) for i in items]
	item_codes = [
		frappe.db.get_value("Serial No", sn, "item_code") or cstr(i.get("item_code"))
		for sn, i in zip(serial_nos, items, strict=False)
	]

	entries = consign_out(serial_nos, item_codes, back_stock_wh, consignment_wh, event_name)
	return {"success": True, "stock_entries": entries, "consignment_warehouse": consignment_wh}


# ─── 9. consign_in ──────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def do_consign_in(event_name=None, scanned_serials=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["event_name", "scanned_serials"])

	if isinstance(scanned_serials, str):
		scanned_serials = json.loads(scanned_serials)

	abbr = _get_abbr()
	consignment_wh = f"Consignment - {event_name} - {abbr}"
	if not frappe.db.exists("Warehouse", consignment_wh):
		frappe.throw(_("Consignment warehouse not found for event {0}").format(event_name))

	parent_wh = frappe.db.get_value("Warehouse", consignment_wh, "parent_warehouse")
	parts = parent_wh.split(" - ") if parent_wh else []
	store_code = parts[0].strip() if parts else "NY-01"
	back_stock_wh = f"Back Stock {store_code} - {abbr}"

	serial_nos = [cstr(sn) for sn in scanned_serials]
	item_codes = [frappe.db.get_value("Serial No", sn, "item_code") or "" for sn in serial_nos]

	entries = consign_in(serial_nos, item_codes, consignment_wh, back_stock_wh, event_name)
	return {"success": True, "stock_entries": entries, "returned": len(serial_nos)}


# ─── 10. recover_found_piece ────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def do_recover_found_piece(serial_no=None, original_shrinkage_ref=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	frappe.only_for("Store Manager", "System Manager")
	_validate_kwargs(locals(), ["serial_no"])

	ic = frappe.db.get_value("Serial No", serial_no, "item_code")
	if not ic:
		frappe.throw(_("Serial No {0} not found").format(serial_no))

	abbr = _get_abbr()
	showcase_wh = None
	sn_wh = frappe.db.get_value("Serial No", serial_no, "warehouse")
	if sn_wh:
		store_code = _get_store_code_from_warehouse(sn_wh)
		if store_code:
			showcase_wh = f"Showcase {store_code} - {abbr}"

	if not showcase_wh or not frappe.db.exists("Warehouse", showcase_wh):
		showcase_wh = frappe.db.get_value("Serial No", serial_no, "warehouse")

	se = recover_found_piece(serial_no, ic, showcase_wh, original_shrinkage_ref)
	return {"success": True, "stock_entry": se.name}


# ─── 11. get_piece_lifecycle ────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_piece_lifecycle(serial_no=None):
	frappe.has_permission("Serial No", ptype="read", throw=True)
	_validate_kwargs(locals(), ["serial_no"])

	sn = frappe.get_doc("Serial No", serial_no)
	sn_info = {
		"serial_no": serial_no,
		"item_code": sn.item_code,
		"item_name": sn.item_name,
		"warehouse": sn.warehouse,
		"status": sn.status,
		"reserved_for": sn.get("custom_reserved_for_customer"),
		"reserved_until": sn.get("custom_reserved_until"),
		"last_seen_at": sn.get("custom_last_seen_at"),
		"last_seen_by": sn.get("custom_last_seen_by"),
	}

	sles = frappe.get_all(
		"Stock Ledger Entry",
		filters={"serial_no": ["like", f"%{serial_no}%"], "item_code": sn.item_code},
		fields=[
			"name",
			"posting_date",
			"posting_time",
			"voucher_type",
			"voucher_no",
			"warehouse",
			"actual_qty",
			"qty_after_transaction",
			"incoming_rate",
			"valuation_rate",
		],
		order_by="posting_date desc, posting_time desc, creation desc",
		limit=200,
	)

	events = []
	for sle in sles:
		event_label = _classify_sle_event(sle)
		events.append(
			{
				"date": f"{sle.posting_date} {sle.posting_time}",
				"type": event_label,
				"voucher_type": sle.voucher_type,
				"voucher_no": sle.voucher_no,
				"warehouse": sle.warehouse,
				"qty_change": sle.actual_qty,
				"balance": sle.qty_after_transaction,
			}
		)

	sn_info["events"] = events
	return sn_info


def _classify_sle_event(sle):
	vt = sle.voucher_type or ""
	qty = flt(sle.actual_qty)
	if "Sales Invoice" in vt or "Delivery Note" in vt:
		return "Sale" if qty < 0 else "Return"
	if "Purchase Receipt" in vt:
		return "Received from Vendor"
	if "Purchase Return" in vt or "Purchase Invoice" in vt:
		return "Vendor Return" if qty < 0 else "Received"
	if "Stock Entry" in vt:
		if qty > 0 and "Receipt" in (sle.voucher_no or ""):
			return "New Item Received"
		if qty < 0 and "Issue" in (sle.voucher_no or ""):
			return "Issue"
		if qty > 0:
			return "Transfer In"
		return "Transfer Out"
	if "Credit Note" in vt:
		return "Return/Refund"
	return "Stock Movement"


# ─── 12. get_store_stock_matrix ─────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_store_stock_matrix(filters=None):
	frappe.has_permission("Bin", ptype="read", throw=True)

	if isinstance(filters, str):
		filters = json.loads(filters)

	abbr = _get_abbr()
	matrix = {}

	for store_code in STORE_LOCATIONS:
		back_stock = f"Back Stock {store_code} - {abbr}"
		showcase = f"Showcase {store_code} - {abbr}"
		warehouses = [back_stock, showcase]

		wh_names = frappe.get_all(
			"Warehouse",
			filters={"parent_warehouse": ["in", [f"{store_code} - {abbr}"]]},
			pluck="name",
		)
		warehouses = wh_names or warehouses

		for wh in warehouses:
			bins = frappe.get_all(
				"Bin",
				filters={"warehouse": wh, "actual_qty": [">", 0]},
				fields=["item_code", "actual_qty", "warehouse"],
			)
			for b in bins:
				if b.item_code not in matrix:
					matrix[b.item_code] = {
						"item_code": b.item_code,
						"item_name": frappe.db.get_value("Item", b.item_code, "item_name"),
						"total_qty": 0,
						"stores": {},
					}
				matrix[b.item_code]["stores"][store_code] = {
					"qty": matrix[b.item_code]["stores"].get(store_code, {}).get("qty", 0) + b.actual_qty,
					"warehouse": wh,
				}
				matrix[b.item_code]["total_qty"] += b.actual_qty

	items = list(matrix.values())
	if filters and filters.get("search"):
		q = filters["search"].lower()
		items = [i for i in items if q in i["item_code"].lower() or q in (i["item_name"] or "").lower()]

	return {"success": True, "items": items, "stores": list(STORE_LOCATIONS.keys())}


# ─── 13. get_low_stock ──────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_low_stock(store=None, threshold_strategy="velocity"):
	frappe.has_permission("Bin", ptype="read", throw=True)

	abbr = _get_abbr()
	low_items = []

	items = frappe.get_all(
		"Item",
		filters={"is_stock_item": 1, "disabled": 0, "custom_is_bulk_sku": 0},
		fields=["name", "item_name", "item_group", "standard_rate"],
	)

	for item in items:
		total_qty = 0
		store_qtys = {}

		for store_code in STORE_LOCATIONS:
			wh_names = frappe.get_all(
				"Warehouse",
				filters={"parent_warehouse": f"{store_code} - {abbr}"},
				pluck="name",
			)
			qty = 0
			for wh in wh_names or []:
				bin_qty = frappe.db.get_value("Bin", {"item_code": item.name, "warehouse": wh}, "actual_qty")
				qty += flt(bin_qty)
			store_qtys[store_code] = qty
			total_qty += qty

		if total_qty <= 2:
			low_items.append(
				{
					"item_code": item.name,
					"item_name": item.item_name,
					"item_group": item.item_group,
					"total_qty": total_qty,
					"store_qtys": store_qtys,
					"standard_rate": item.standard_rate,
				}
			)

	return {"success": True, "items": low_items}


# ─── 14. move_piece ─────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def move_piece(serial_no=None, target_warehouse=None):
	frappe.has_permission("Stock Entry", ptype="create", throw=True)
	_validate_kwargs(locals(), ["serial_no", "target_warehouse"])

	sn = frappe.get_doc("Serial No", serial_no)
	if not sn.warehouse:
		frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))

	se = move_to_showcase(serial_no, sn.item_code, sn.warehouse, target_warehouse)
	return {"success": True, "stock_entry": se.name}


# ─── Sales Invoice validation hook ──────────────────────────────────────────


def validate_serial_sellable_zones(doc, method=None):
	for item in doc.items:
		if not item.serial_no:
			continue
		for sn in item.serial_no.split("\n"):
			sn = sn.strip()
			if not sn:
				continue
			sn_wh = frappe.db.get_value("Serial No", sn, "warehouse")
			if not sn_wh:
				continue
			wh_name = frappe.db.get_value("Warehouse", sn_wh, "warehouse_name") or ""
			is_sellable = any(zone.lower() in wh_name.lower() for zone in SELLABLE_ZONES)
			if not is_sellable:
				frappe.throw(
					_("Serial No {0} is in {1} which is not a sellable zone. Cannot sell.").format(sn, sn_wh)
				)
