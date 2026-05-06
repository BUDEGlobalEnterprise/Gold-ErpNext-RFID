"""
Terminal Stock Management CLI for Zevar Jewelers

Provides admin/managers an easy way to view, adjust, and manage
stock directly from the terminal.

Usage:
    bench --site <site> zevar-stock status [--store STORE] [--item ITEM]
    bench --site <site> zevar-stock lookup <serial_no|barcode|item_code>
    bench --site <site> zevar-stock add <item_code> <warehouse> <qty>
    bench --site <site> zevar-stock remove <serial_no> [--reason REASON]
    bench --site <site> zevar-stock move <serial_no> <target_warehouse>
    bench --site <site> zevar-stock low [--threshold N]
    bench --site <site> zevar-stock reductions [--hours N]
    bench --site <site> zevar-stock recent [--limit N]
"""

from __future__ import annotations

import json
import sys

import click
import frappe
from frappe.commands import get_site, pass_context
from frappe.utils import cint, cstr, flt, now_datetime

from zevar_core.constants import INVENTORY_ZONES, SELLABLE_ZONES, STORE_LOCATIONS

STOCK_ROLES = ["Sales Manager", "Store Manager", "System Manager", "Administrator"]


def _check_role():
	user = frappe.session.user
	if user == "Administrator":
		return True
	roles = frappe.get_roles(user)
	if not any(r in roles for r in STOCK_ROLES):
		click.echo(click.style(f"Access denied. Required roles: {', '.join(STOCK_ROLES)}", fg="red"))
		return False
	return True


def _get_abbr():
	company = frappe.defaults.get_user_default("Company") or "Zevar Jewelers"
	return frappe.get_cached_value("Company", company, "abbr") or "Z"


def _get_company():
	return frappe.defaults.get_user_default("Company") or "Zevar Jewelers"


def _get_cost_center(company=None):
	if not company:
		company = _get_company()
	return frappe.get_cached_value("Company", company, "cost_center")


def _store_warehouses(store_code, abbr):
	root = f"{store_code} - {abbr}"
	if not frappe.db.exists("Warehouse", root):
		return {}
	children = frappe.get_all(
		"Warehouse",
		filters={"parent_warehouse": root, "is_group": 0},
		pluck="name",
	)
	return {
		wh: frappe.get_all(
			"Bin",
			filters={"warehouse": wh, "actual_qty": [">", 0]},
			fields=["item_code", "actual_qty", "valuation_rate"],
		)
		for wh in children
	}


def _print_table(headers, rows, col_widths=None):
	if not col_widths:
		col_widths = [max(len(str(r[i])) for r in [headers, *rows]) + 2 for i in range(len(headers))]
	header_line = "".join(str(h).ljust(w) for h, w in zip(headers, col_widths, strict=True))
	click.echo(click.style(header_line, bold=True))
	click.echo("-" * sum(col_widths))
	for row in rows:
		line = "".join(str(c).ljust(w) for c, w in zip(row, col_widths, strict=True))
		click.echo(line)


def _log_cli_action(action, details):
	log = frappe.new_doc("POS Audit Log")
	log.user = frappe.session.user
	log.event_type = "stock_cli_adjustment"
	log.category = "Inventory"
	log.severity = "Info"
	log.details = json.dumps({"action": action, **details}, default=str)
	log.insert(ignore_permissions=True)
	frappe.db.commit()


# ────────────────────────────────────────────────────────────────
# CLI Group
# ────────────────────────────────────────────────────────────────


@click.group("zevar-stock")
@click.option("--site", help="Site name")
@pass_context
def stock_cli(context, site=None):
	"""Zevar terminal stock management for admin/managers."""
	pass


# ────────────────────────────────────────────────────────────────
# status
# ────────────────────────────────────────────────────────────────


@stock_cli.command("status")
@click.option("--store", default=None, help="Store code (e.g. NY-01, Miami-01). Default: all stores")
@click.option("--item", default=None, help="Filter by item code")
@click.option("--zone", default=None, help="Filter by zone (Showcase, Back Stock, Safe, etc.)")
@pass_context
def stock_status(context, store=None, item=None, zone=None):
	"""View stock levels across stores and zones."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		abbr = _get_abbr()
		stores = {store: STORE_LOCATIONS[store]} if store and store in STORE_LOCATIONS else STORE_LOCATIONS

		total_pieces = 0
		total_value = 0.0

		for store_code, store_name in stores.items():
			root = f"{store_code} - {abbr}"
			if not frappe.db.exists("Warehouse", root):
				click.echo(f"\n  Store {store_code} ({store_name}): No warehouse found")
				continue

			wh_filters = {"parent_warehouse": root, "is_group": 0}
			warehouses = frappe.get_all("Warehouse", filters=wh_filters, fields=["name", "warehouse_name"])

			if zone:
				warehouses = [w for w in warehouses if zone.lower() in (w.warehouse_name or "").lower()]

			click.echo(click.style(f"\n  {store_code} — {store_name}", bold=True, fg="cyan"))
			click.echo("  " + "=" * 70)

			for wh in warehouses:
				bin_filters = {"warehouse": wh.name, "actual_qty": [">", 0]}
				if item:
					bin_filters["item_code"] = item

				bins = frappe.get_all(
					"Bin",
					filters=bin_filters,
					fields=["item_code", "actual_qty", "valuation_rate", "stock_value"],
					order_by="item_code",
				)

				if not bins:
					continue

				zone_name = wh.warehouse_name or wh.name
				store_qty = sum(b.actual_qty for b in bins)
				store_val = sum(flt(b.stock_value) for b in bins)
				total_pieces += store_qty
				total_value += store_val

				click.echo(f"\n  {zone_name} ({store_qty} pcs, ${store_val:,.2f})")
				click.echo("  " + "-" * 70)

				headers = ["Item Code", "Item Name", "Qty", "Val. Rate", "Stock Value"]
				rows = []
				for b in bins:
					iname = frappe.db.get_value("Item", b.item_code, "item_name") or ""
					rows.append(
						[
							b.item_code,
							iname[:30],
							b.actual_qty,
							f"${flt(b.valuation_rate):,.2f}",
							f"${flt(b.stock_value):,.2f}",
						]
					)

				if item:
					rows = [r for r in rows if item.lower() in r[0].lower()]

				if rows:
					_print_table(headers, rows, [20, 32, 6, 14, 14])

		click.echo(
			click.style(f"\n  TOTAL: {total_pieces} pieces, ${total_value:,.2f} value", bold=True, fg="green")
		)

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# lookup
# ────────────────────────────────────────────────────────────────


@stock_cli.command("lookup")
@click.argument("query")
@click.option("--json-output", is_flag=True, default=False, help="Output as JSON")
@pass_context
def stock_lookup(context, query, json_output=False):
	"""Look up a piece by serial no, barcode, or item code."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		result = _do_lookup(query)

		if json_output:
			click.echo(json.dumps(result, indent=2, default=str))
			return

		if not result.get("found"):
			click.echo(click.style(f"Not found: {query}", fg="red"))
			return

		if result.get("type") == "serial":
			_print_serial(result)
		elif result.get("type") == "item":
			_print_item_stock(result)

	finally:
		frappe.destroy()


def _do_lookup(query):
	sn = frappe.db.get_value(
		"Serial No",
		query,
		["name", "item_code", "item_name", "warehouse", "status", "valuation_rate"],
		as_dict=True,
	)
	if sn:
		wh_name = frappe.db.get_value("Warehouse", sn.warehouse, "warehouse_name") if sn.warehouse else "N/A"
		reservations = frappe.get_all(
			"Stock Reservation",
			filters={"serial_no": query, "status": "Active"},
			fields=["customer", "hold_until", "deposit_amount"],
			limit=1,
		)
		return {
			"found": True,
			"type": "serial",
			"serial_no": sn.name,
			"item_code": sn.item_code,
			"item_name": sn.item_name,
			"warehouse": sn.warehouse,
			"warehouse_name": wh_name,
			"status": sn.status,
			"valuation_rate": flt(sn.valuation_rate, 2),
			"reserved": bool(reservations),
			"reservation": reservations[0] if reservations else None,
		}

	barcode_item = frappe.db.get_value("Item", {"custom_barcode": query}, "name")
	if barcode_item:
		query = barcode_item

	if frappe.db.exists("Item", query):
		item = frappe.get_doc("Item", query)
		bins = frappe.get_all(
			"Bin",
			filters={"item_code": item.name, "actual_qty": [">", 0]},
			fields=["warehouse", "actual_qty", "valuation_rate", "stock_value"],
		)
		total_qty = sum(b.actual_qty for b in bins)
		total_value = sum(flt(b.stock_value) for b in bins)
		serials = frappe.get_all(
			"Serial No",
			filters={"item_code": item.name, "warehouse": ["is", "set"]},
			fields=["name", "warehouse", "status", "valuation_rate"],
		)
		return {
			"found": True,
			"type": "item",
			"item_code": item.name,
			"item_name": item.item_name,
			"item_group": item.item_group,
			"standard_rate": flt(item.standard_rate, 2),
			"total_qty": total_qty,
			"total_value": total_value,
			"bins": bins,
			"serials": serials,
		}

	return {"found": False, "query": query}


def _print_serial(data):
	click.echo(click.style("\n  Serial No Found", bold=True, fg="green"))
	click.echo("  " + "=" * 50)
	click.echo(f"  Serial No:      {data['serial_no']}")
	click.echo(f"  Item Code:      {data['item_code']}")
	click.echo(f"  Item Name:      {data['item_name']}")
	click.echo(f"  Warehouse:      {data['warehouse']}")
	click.echo(f"  Zone:           {data['warehouse_name']}")
	click.echo(f"  Status:         {data['status']}")
	click.echo(f"  Valuation:      ${data['valuation_rate']:,.2f}")
	if data.get("reserved"):
		res = data["reservation"]
		click.echo(click.style(f"  RESERVED for:   {res['customer']} until {res['hold_until']}", fg="yellow"))


def _print_item_stock(data):
	click.echo(click.style(f"\n  Item: {data['item_code']} — {data['item_name']}", bold=True, fg="green"))
	click.echo(f"  Group: {data['item_group']}  |  Rate: ${data['standard_rate']:,.2f}")
	click.echo(f"  Total: {data['total_qty']} pcs  |  Value: ${data['total_value']:,.2f}")
	click.echo("  " + "=" * 70)

	if data["bins"]:
		click.echo("\n  Stock by Warehouse:")
		headers = ["Warehouse", "Qty", "Value"]
		rows = [[b.warehouse, b.actual_qty, f"${flt(b.stock_value):,.2f}"] for b in data["bins"]]
		_print_table(headers, rows)

	if data["serials"]:
		click.echo(f"\n  Serial Numbers ({len(data['serials'])}):")
		headers = ["Serial No", "Warehouse", "Status", "Valuation"]
		rows = [
			[s.name, s.warehouse or "N/A", s.status, f"${flt(s.valuation_rate):,.2f}"]
			for s in data["serials"][:20]
		]
		_print_table(headers, rows)
		if len(data["serials"]) > 20:
			click.echo(f"  ... and {len(data['serials']) - 20} more")


# ────────────────────────────────────────────────────────────────
# add (Material Receipt)
# ────────────────────────────────────────────────────────────────


@stock_cli.command("add")
@click.argument("item_code")
@click.argument("warehouse")
@click.argument("qty", type=int, default=1)
@click.option("--valuation-rate", type=float, default=None, help="Valuation rate per unit")
@click.option("--serial-no", default=None, help="Serial number (for qty=1)")
@click.option("--reason", default="CLI stock addition", help="Reason for addition")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without creating")
@pass_context
def stock_add(context, item_code, warehouse, qty, valuation_rate, serial_no, reason, dry_run):
	"""Add stock to a warehouse (Material Receipt)."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		if not frappe.db.exists("Item", item_code):
			click.echo(click.style(f"Item not found: {item_code}", fg="red"))
			return

		if not frappe.db.exists("Warehouse", warehouse):
			click.echo(click.style(f"Warehouse not found: {warehouse}", fg="red"))
			return

		item_name = frappe.db.get_value("Item", item_code, "item_name")
		wh_name = frappe.db.get_value("Warehouse", warehouse, "warehouse_name")

		click.echo(f"\n  Adding {qty} x {item_code} ({item_name}) to {warehouse} ({wh_name})")
		if valuation_rate:
			click.echo(f"  Valuation rate: ${valuation_rate:,.2f}")
		if serial_no:
			click.echo(f"  Serial No: {serial_no}")

		if dry_run:
			click.echo(click.style("\n  [DRY RUN] No stock entry created.", fg="yellow"))
			return

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Receipt"
		se.company = _get_company()
		se.cost_center = _get_cost_center()
		se.remarks = reason

		row = {
			"item_code": item_code,
			"qty": qty,
			"t_warehouse": warehouse,
			"cost_center": se.cost_center,
		}
		if valuation_rate:
			row["basic_rate"] = valuation_rate
		if serial_no:
			row["serial_no"] = serial_no

		se.append("items", row)
		se.insert(ignore_permissions=True)
		se.submit()

		_log_cli_action(
			"add_stock",
			{
				"item_code": item_code,
				"warehouse": warehouse,
				"qty": qty,
				"serial_no": serial_no,
				"stock_entry": se.name,
			},
		)

		click.echo(click.style(f"\n  Stock Entry created: {se.name}", fg="green"))
		click.echo(f"  Added {qty} pcs of {item_code} to {warehouse}")

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# remove (Material Issue)
# ────────────────────────────────────────────────────────────────


@stock_cli.command("remove")
@click.argument("serial_no")
@click.option("--reason", default="CLI stock removal", help="Reason for removal")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without creating")
@pass_context
def stock_remove(context, serial_no, reason, dry_run):
	"""Remove a piece from stock by serial number (Material Issue)."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		if not frappe.db.exists("Serial No", serial_no):
			click.echo(click.style(f"Serial No not found: {serial_no}", fg="red"))
			return

		sn = frappe.get_doc("Serial No", serial_no)
		if not sn.warehouse:
			click.echo(click.style(f"Serial No {serial_no} has no warehouse (already issued).", fg="red"))
			return

		click.echo(f"\n  Removing {serial_no} ({sn.item_code} - {sn.item_name}) from {sn.warehouse}")

		if dry_run:
			click.echo(click.style("\n  [DRY RUN] No stock entry created.", fg="yellow"))
			return

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.company = _get_company()
		se.cost_center = _get_cost_center()
		se.remarks = reason

		se.append(
			"items",
			{
				"item_code": sn.item_code,
				"qty": 1,
				"s_warehouse": sn.warehouse,
				"serial_no": serial_no,
				"cost_center": se.cost_center,
			},
		)
		se.insert(ignore_permissions=True)
		se.submit()

		_log_cli_action(
			"remove_stock",
			{
				"serial_no": serial_no,
				"item_code": sn.item_code,
				"warehouse": sn.warehouse,
				"reason": reason,
				"stock_entry": se.name,
			},
		)

		click.echo(click.style(f"\n  Stock Entry created: {se.name}", fg="green"))
		click.echo(f"  Removed {serial_no} from {sn.warehouse}")

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# move (Material Transfer)
# ────────────────────────────────────────────────────────────────


@stock_cli.command("move")
@click.argument("serial_no")
@click.argument("target_warehouse")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without creating")
@pass_context
def stock_move(context, serial_no, target_warehouse, dry_run):
	"""Move a piece between warehouses/zones."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		if not frappe.db.exists("Serial No", serial_no):
			click.echo(click.style(f"Serial No not found: {serial_no}", fg="red"))
			return

		if not frappe.db.exists("Warehouse", target_warehouse):
			click.echo(click.style(f"Target warehouse not found: {target_warehouse}", fg="red"))
			return

		sn = frappe.get_doc("Serial No", serial_no)
		if not sn.warehouse:
			click.echo(click.style(f"Serial No {serial_no} has no warehouse.", fg="red"))
			return

		if sn.warehouse == target_warehouse:
			click.echo(click.style(f"Already in {target_warehouse}.", fg="yellow"))
			return

		src_name = frappe.db.get_value("Warehouse", sn.warehouse, "warehouse_name") or sn.warehouse
		tgt_name = frappe.db.get_value("Warehouse", target_warehouse, "warehouse_name") or target_warehouse

		click.echo(f"\n  Moving {serial_no} ({sn.item_code})")
		click.echo(f"  From: {sn.warehouse} ({src_name})")
		click.echo(f"  To:   {target_warehouse} ({tgt_name})")

		if dry_run:
			click.echo(click.style("\n  [DRY RUN] No stock entry created.", fg="yellow"))
			return

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		se.company = _get_company()
		se.cost_center = _get_cost_center()

		se.append(
			"items",
			{
				"item_code": sn.item_code,
				"qty": 1,
				"s_warehouse": sn.warehouse,
				"t_warehouse": target_warehouse,
				"serial_no": serial_no,
				"cost_center": se.cost_center,
			},
		)
		se.insert(ignore_permissions=True)
		se.submit()

		_log_cli_action(
			"move_stock",
			{
				"serial_no": serial_no,
				"item_code": sn.item_code,
				"from_warehouse": sn.warehouse,
				"to_warehouse": target_warehouse,
				"stock_entry": se.name,
			},
		)

		click.echo(click.style(f"\n  Stock Entry created: {se.name}", fg="green"))

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# low
# ────────────────────────────────────────────────────────────────


@stock_cli.command("low")
@click.option("--threshold", type=int, default=2, help="Low stock threshold (total qty across stores)")
@click.option("--store", default=None, help="Filter by store code")
@click.option("--json-output", is_flag=True, default=False, help="Output as JSON")
@pass_context
def stock_low(context, threshold, store, json_output):
	"""List items below stock threshold."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		abbr = _get_abbr()
		stores = {store: STORE_LOCATIONS[store]} if store and store in STORE_LOCATIONS else STORE_LOCATIONS

		items = frappe.get_all(
			"Item",
			filters={"is_stock_item": 1, "disabled": 0},
			fields=["name", "item_name", "item_group", "standard_rate"],
		)

		low_items = []
		for item in items:
			total_qty = 0
			store_qtys = {}
			for store_code in stores:
				wh_names = frappe.get_all(
					"Warehouse",
					filters={"parent_warehouse": f"{store_code} - {abbr}"},
					pluck="name",
				)
				qty = 0
				for wh in wh_names or []:
					bin_qty = frappe.db.get_value(
						"Bin", {"item_code": item.name, "warehouse": wh}, "actual_qty"
					)
					qty += flt(bin_qty)
				store_qtys[store_code] = qty
				total_qty += qty

			if total_qty <= threshold:
				low_items.append(
					{
						"item_code": item.name,
						"item_name": item.item_name,
						"item_group": item.item_group,
						"total_qty": total_qty,
						"store_qtys": store_qtys,
						"standard_rate": flt(item.standard_rate, 2),
					}
				)

		if json_output:
			click.echo(json.dumps(low_items, indent=2, default=str))
			return

		if not low_items:
			click.echo(click.style("\n  No items below threshold.", fg="green"))
			return

		click.echo(click.style(f"\n  Low Stock Items (threshold: {threshold})", bold=True, fg="yellow"))
		click.echo("  " + "=" * 90)

		headers = ["Item Code", "Item Name", "Total"]
		for sc in stores:
			headers.append(sc)
		headers.append("Rate")

		rows = []
		for li in low_items:
			row = [li["item_code"], li["item_name"][:25], li["total_qty"]]
			for sc in stores:
				row.append(li["store_qtys"].get(sc, 0))
			row.append(f"${li['standard_rate']:,.2f}")
			rows.append(row)

		rows.sort(key=lambda r: r[2])
		_print_table(headers, rows)
		click.echo(f"\n  Total low-stock items: {len(low_items)}")

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# reductions
# ────────────────────────────────────────────────────────────────


@stock_cli.command("reductions")
@click.option("--hours", type=int, default=24, help="Look back hours")
@click.option("--limit", type=int, default=50, help="Max results")
@pass_context
def stock_reductions(context, hours, limit):
	"""View recent auto-detected stock reductions from sales."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		from frappe.utils import add_to_date

		since = add_to_date(now_datetime(), hours=-1 * hours)
		logs = frappe.get_all(
			"POS Audit Log",
			filters={"event_type": "stock_auto_reduced", "creation": [">=", since]},
			fields=["name", "user", "details", "reference_document", "creation"],
			order_by="creation desc",
			limit=limit,
		)

		if not logs:
			click.echo(click.style(f"\n  No stock reductions in the last {hours} hours.", fg="green"))
			return

		click.echo(click.style(f"\n  Stock Reductions (last {hours}h)", bold=True, fg="yellow"))
		click.echo("  " + "=" * 90)

		headers = ["Time", "Invoice", "Item", "Serial No", "Qty", "Warehouse", "Value"]
		rows = []
		total_value = 0

		for log in logs:
			try:
				d = frappe.parse_json(log.details) if isinstance(log.details, str) else log.details
				val = flt(d.get("valuation_rate", 0)) * flt(d.get("qty_reduced", 1))
				total_value += val
				rows.append(
					[
						str(log.creation)[:16],
						log.reference_document or "",
						d.get("item_code", ""),
						d.get("serial_no", "-"),
						d.get("qty_reduced", 1),
						(d.get("warehouse") or "")[:25],
						f"${val:,.2f}",
					]
				)
			except Exception:
				rows.append([str(log.creation)[:16], log.reference_document or "", "?", "?", "?", "?", "?"])

		_print_table(headers, rows)
		click.echo(
			click.style(f"\n  Total reductions: {len(logs)}  |  Total value: ${total_value:,.2f}", bold=True)
		)

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# recent
# ────────────────────────────────────────────────────────────────


@stock_cli.command("recent")
@click.option("--limit", type=int, default=20, help="Number of recent movements")
@pass_context
def stock_recent(context, limit):
	"""View recent stock movements across all stores."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		sles = frappe.get_all(
			"Stock Ledger Entry",
			filters={"is_cancelled": 0},
			fields=[
				"posting_date",
				"posting_time",
				"item_code",
				"warehouse",
				"actual_qty",
				"qty_after_transaction",
				"voucher_type",
				"voucher_no",
				"valuation_rate",
			],
			order_by="posting_date desc, posting_time desc, creation desc",
			limit=limit,
		)

		if not sles:
			click.echo("\n  No stock movements found.")
			return

		click.echo(click.style(f"\n  Recent Stock Movements (last {limit})", bold=True, fg="cyan"))
		click.echo("  " + "=" * 110)

		headers = ["Date", "Item", "Warehouse", "Qty", "After", "Type", "Voucher"]
		rows = []
		for sle in sles:
			qty = flt(sle.actual_qty)
			color_qty = "+" if qty > 0 else ""
			rows.append(
				[
					f"{sle.posting_date} {sle.posting_time}"[:16],
					sle.item_code,
					(sle.warehouse or "")[:30],
					f"{color_qty}{qty}",
					sle.qty_after_transaction,
					(sle.voucher_type or "")[:15],
					sle.voucher_no or "",
				]
			)

		_print_table(headers, rows)

	finally:
		frappe.destroy()


# ────────────────────────────────────────────────────────────────
# zones (list available zones for a store)
# ────────────────────────────────────────────────────────────────


@stock_cli.command("zones")
@click.option("--store", default=None, help="Store code to list zones for")
@pass_context
def stock_zones(context, store):
	"""List available inventory zones and their warehouses."""
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()

	try:
		if not _check_role():
			return

		abbr = _get_abbr()
		stores = {store: STORE_LOCATIONS[store]} if store and store in STORE_LOCATIONS else STORE_LOCATIONS

		click.echo(click.style("\n  Inventory Zones", bold=True, fg="cyan"))
		click.echo("  " + "=" * 70)

		for store_code, store_name in stores.items():
			click.echo(f"\n  {store_code} — {store_name}")
			root = f"{store_code} - {abbr}"
			if not frappe.db.exists("Warehouse", root):
				click.echo("    No warehouse root found")
				continue

			warehouses = frappe.get_all(
				"Warehouse",
				filters={"parent_warehouse": root, "is_group": 0},
				fields=["name", "warehouse_name"],
			)

			for wh in warehouses:
				bin_count = (
					frappe.db.sql(
						"SELECT SUM(actual_qty) FROM tabBin WHERE warehouse=%s AND actual_qty > 0",
						wh.name,
					)[0][0]
					or 0
				)
				sellable = any(z.lower() in (wh.warehouse_name or "").lower() for z in SELLABLE_ZONES)
				sellable_tag = click.style(" [SELLABLE]", fg="green") if sellable else ""
				click.echo(f"    {wh.name}{sellable_tag}  ({int(bin_count)} pcs)")

	finally:
		frappe.destroy()


commands = [stock_cli]
