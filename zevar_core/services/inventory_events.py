"""Factored helpers for the 20 inventory stock event types.

Every function creates a proper ERPNext stock document (Stock Entry / Delivery Note /
Purchase Receipt / Purchase Return) so the stock ledger stays the single source of truth.
No function mutates tabBin directly.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, now_datetime


def _get_company():
	return frappe.defaults.get_user_default("company") or "Zevar Jewelers"


def _get_abbr():
	company = _get_company()
	return frappe.get_cached_value("Company", company, "abbr") or "Z"


def _get_cost_center(company=None):
	if not company:
		company = _get_company()
	cc = frappe.get_cached_value("Company", company, "cost_center")
	return cc


def _log_inventory_event(event_type, reference_type, reference_name, details):
	log = frappe.new_doc("POS Audit Log")
	log.user = frappe.session.user or "Administrator"
	log.event_type = event_type
	log.category = "Inventory"
	log.reference_type = reference_type
	log.reference_document = reference_name
	log.details = details
	log.insert(ignore_permissions=True)


def _update_serial_last_seen(serial_no):
	frappe.db.set_value(
		"Serial No",
		serial_no,
		{
			"custom_last_seen_at": now_datetime(),
			"custom_last_seen_by": frappe.session.user,
		},
		update_modified=False,
	)


def _get_store_warehouse(serial_no):
	wh = frappe.db.get_value("Serial No", serial_no, "warehouse")
	if not wh:
		return None, None
	parent = frappe.db.get_value("Warehouse", wh, "parent_warehouse")
	return wh, parent


def _get_zone_warehouse(store_parent_wh, zone_name, store_code=None):
	abbr = _get_abbr()
	if store_code:
		return f"{zone_name} {store_code} - {abbr}"
	if store_parent_wh:
		parts = store_parent_wh.split(" - ")
		code = parts[0].strip() if parts else "NYC"
		return f"{zone_name} {code} - {abbr}"
	return None


def transfer_serial(
	serial_no, item_code, from_warehouse, to_warehouse, reference_doctype=None, reference_name=None, qty=1
):
	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Transfer"
	se.company = _get_company()
	se.cost_center = _get_cost_center(se.company)

	if reference_doctype and reference_name:
		se.append(
			"additional_costs",
			{
				"description": f"Ref: {reference_doctype} {reference_name}",
				"amount": 0,
			},
		)

	row = {
		"item_code": item_code,
		"qty": qty,
		"s_warehouse": from_warehouse,
		"t_warehouse": to_warehouse,
		"cost_center": se.cost_center,
	}
	if serial_no:
		row["serial_no"] = serial_no

	se.append("items", row)

	se.insert(ignore_permissions=True)
	se.submit()

	_update_serial_last_seen(serial_no)
	return se


def _get_or_create_sbb(serial_no, item_code, warehouse):
	if not serial_no:
		return None

	existing = frappe.db.get_value(
		"Serial and Batch Bundle",
		{"item_code": item_code, "warehouse": warehouse, "docstatus": 1},
		"name",
	)
	if existing:
		return existing
	return None


def material_receipt(
	item_code,
	to_warehouse,
	qty=1,
	serial_no=None,
	valuation_rate=None,
	reference_doctype=None,
	reference_name=None,
):
	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Receipt"
	se.company = _get_company()
	se.cost_center = _get_cost_center(se.company)

	row = {
		"item_code": item_code,
		"qty": qty,
		"t_warehouse": to_warehouse,
		"cost_center": se.cost_center,
	}
	if valuation_rate:
		row["basic_rate"] = valuation_rate
	if serial_no:
		row["serial_no"] = serial_no

	se.append("items", row)
	se.insert(ignore_permissions=True)
	se.submit()

	if serial_no:
		_update_serial_last_seen(serial_no)
	return se


def material_issue(
	item_code, from_warehouse, qty=1, serial_no=None, reference_doctype=None, reference_name=None
):
	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Issue"
	se.company = _get_company()
	se.cost_center = _get_cost_center(se.company)

	row = {
		"item_code": item_code,
		"qty": qty,
		"s_warehouse": from_warehouse,
		"cost_center": se.cost_center,
	}
	if serial_no:
		row["serial_no"] = serial_no

	se.append("items", row)
	se.insert(ignore_permissions=True)
	se.submit()

	if serial_no:
		_update_serial_last_seen(serial_no)
	return se


def move_to_showcase(serial_no, item_code, from_warehouse, showcase_warehouse):
	se = transfer_serial(serial_no, item_code, from_warehouse, showcase_warehouse)
	_log_inventory_event(
		"move_to_showcase",
		"Serial No",
		serial_no,
		f"Moved {serial_no} from {from_warehouse} to {showcase_warehouse}",
	)
	return se


def create_sale_stock_issue(serial_no, item_code, warehouse):
	se = material_issue(item_code, warehouse, qty=1, serial_no=serial_no)
	_update_serial_last_seen(serial_no)
	return se


def return_to_quarantine(serial_no, item_code, to_warehouse):
	sn_doc = frappe.get_doc("Serial No", serial_no)
	from_wh = sn_doc.warehouse
	if not from_wh:
		frappe.throw(_("Serial No {0} has no warehouse").format(serial_no))
	se = transfer_serial(serial_no, item_code, from_wh, to_warehouse)
	_update_serial_last_seen(serial_no)
	return se


def dispatch_inter_store_transfer(serial_nos, item_codes, source_back_stock, transit_out_wh):
	entries = []
	for sn, ic in zip(serial_nos, item_codes, strict=False):
		se = transfer_serial(sn, ic, source_back_stock, transit_out_wh)
		entries.append(se.name)
	_log_inventory_event(
		"transfer_dispatched",
		"Stock Entry",
		",".join(entries),
		f"Dispatched {len(serial_nos)} pieces from {source_back_stock} to {transit_out_wh}",
	)
	return entries


def receive_inter_store_transfer(serial_nos, item_codes, transit_out_wh, dest_back_stock):
	entries = []
	for sn, ic in zip(serial_nos, item_codes, strict=False):
		se = transfer_serial(sn, ic, transit_out_wh, dest_back_stock)
		entries.append(se.name)
	_update_serial_last_seen(serial_nos[-1] if serial_nos else None)
	_log_inventory_event(
		"transfer_received",
		"Stock Entry",
		",".join(entries),
		f"Received {len(serial_nos)} pieces at {dest_back_stock}",
	)
	return entries


def damage_write_off(serial_no, item_code, warehouse, shrinkage_wh, reason=None):
	se = transfer_serial(serial_no, item_code, warehouse, shrinkage_wh)
	_log_inventory_event(
		"damage_written_off",
		"Stock Entry",
		se.name,
		f"Damaged: {serial_no} moved to {shrinkage_wh}. Reason: {reason or 'N/A'}",
	)
	return se


def gift_out(serial_no, item_code, warehouse, reason=None):
	se = material_issue(item_code, warehouse, qty=1, serial_no=serial_no)
	_log_inventory_event(
		"gift_out",
		"Stock Entry",
		se.name,
		f"Gifted out {serial_no}. Reason: {reason or 'N/A'}",
	)
	return se


def trade_in_accept(item_code, to_warehouse, valuation_rate, serial_no=None):
	se = material_receipt(
		item_code,
		to_warehouse,
		qty=1,
		serial_no=serial_no,
		valuation_rate=valuation_rate,
	)
	_log_inventory_event(
		"trade_in_accepted",
		"Stock Entry",
		se.name,
		f"Trade-in accepted: {serial_no or item_code} valued at ${valuation_rate}",
	)
	return se


def consign_out(serial_nos, item_codes, from_warehouse, consignment_wh, event_name):
	entries = []
	for sn, ic in zip(serial_nos, item_codes, strict=False):
		se = transfer_serial(sn, ic, from_warehouse, consignment_wh)
		entries.append(se.name)
	_log_inventory_event(
		"consignment_out",
		"Stock Entry",
		",".join(entries),
		f"Consigned {len(serial_nos)} pieces for event '{event_name}'",
	)
	return entries


def consign_in(serial_nos, item_codes, consignment_wh, back_stock_wh, event_name):
	entries = []
	for sn, ic in zip(serial_nos, item_codes, strict=False):
		se = transfer_serial(sn, ic, consignment_wh, back_stock_wh)
		entries.append(se.name)
	_log_inventory_event(
		"consignment_back",
		"Stock Entry",
		",".join(entries),
		f"Consign-in {len(serial_nos)} pieces from event '{event_name}'",
	)
	return entries


def recover_found_piece(serial_no, item_code, to_warehouse, original_shrinkage_ref=None):
	se = material_receipt(item_code, to_warehouse, qty=1, serial_no=serial_no)
	_update_serial_last_seen(serial_no)
	_log_inventory_event(
		"piece_recovered",
		"Stock Entry",
		se.name,
		f"Recovered {serial_no}. Original shrinkage ref: {original_shrinkage_ref or 'N/A'}",
	)
	return se


def vendor_return(serial_no, item_code, warehouse, reason=None):
	se = material_issue(item_code, warehouse, qty=1, serial_no=serial_no)
	_log_inventory_event(
		"vendor_return",
		"Stock Entry",
		se.name,
		f"Vendor return: {serial_no}. Reason: {reason or 'N/A'}",
	)
	return se


def repair_in(item_code, to_warehouse, serial_no=None):
	se = material_receipt(item_code, to_warehouse, qty=1, serial_no=serial_no)
	if serial_no:
		frappe.db.set_value("Serial No", serial_no, "custom_is_customer_owned", 1)
		_update_serial_last_seen(serial_no)
	_log_inventory_event(
		"repair_in",
		"Stock Entry",
		se.name,
		f"Repair-in: {serial_no or item_code}",
	)
	return se


def repair_out(serial_no, item_code, from_warehouse):
	se = material_issue(item_code, from_warehouse, qty=1, serial_no=serial_no)
	if serial_no:
		frappe.db.set_value("Serial No", serial_no, "custom_is_customer_owned", 0)
		_update_serial_last_seen(serial_no)
	_log_inventory_event(
		"repair_out",
		"Stock Entry",
		se.name,
		f"Repair-out: {serial_no}",
	)
	return se
