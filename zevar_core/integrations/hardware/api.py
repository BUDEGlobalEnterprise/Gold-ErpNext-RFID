"""
Hardware API Endpoints - Printer & Scanner
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.integrations.hardware import utils as hw_utils


@frappe.whitelist()
def generate_receipt_content(invoice_name):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	if not frappe.db.exists("Sales Invoice", invoice_name):
		frappe.throw(_("Invoice {0} not found.").format(invoice_name))
	si = frappe.get_doc("Sales Invoice", invoice_name)

	warehouse = si.items[0].warehouse if si.items else None
	store_info = {}
	if warehouse:
		store_loc = frappe.get_all(
			"Store Location",
			filters={"default_warehouse": warehouse},
			fields=["store_name", "store_address", "county"],
			limit=1,
		)
		store_info = store_loc[0] if store_loc else {}

	# Collect salesperson info from the splits table
	salespersons = []
	associate_name = ""
	if hasattr(si, "custom_salesperson_splits") and si.custom_salesperson_splits:
		for row in si.custom_salesperson_splits:
			if row.employee:
				emp_name = frappe.get_cached_value("Employee", row.employee, "employee_name") or row.employee
				salespersons.append(
					{
						"employee": row.employee,
						"name": emp_name,
						"split": flt(row.split_percent),
					}
				)
		if salespersons:
			associate_name = salespersons[0]["name"]
	elif si.get("custom_salesperson_1"):
		associate_name = frappe.get_cached_value("Employee", si.custom_salesperson_1, "employee_name") or ""

	invoice_data = {
		"invoice_name": si.name,
		"date": str(si.posting_date),
		"customer": si.customer_name or si.customer,
		"associate": associate_name,
		"salespersons": salespersons,
		"store_address": store_info.get("store_address", ""),
		"store_phone": "",
		"items": [
			{
				"item_name": item.item_name,
				"item_code": item.item_code,
				"qty": flt(item.qty),
				"rate": flt(item.rate),
				"amount": flt(item.amount),
			}
			for item in si.items
		],
		"subtotal": flt(si.total),
		"discount": flt(si.discount_amount or 0),
		"tax": flt(si.total_taxes_and_charges or 0),
		"grand_total": flt(si.grand_total),
		"payments": [
			{
				"mode_of_payment": p.mode_of_payment,
				"amount": flt(p.amount),
				"reference_no": getattr(p, "reference_no", ""),
			}
			for p in si.payments
		],
	}
	receipt_text = hw_utils.generate_escpos_receipt(invoice_data)
	return hw_utils.format_print_payload(receipt_text)


@frappe.whitelist()
def generate_tag_content(item_code):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} not found.").format(item_code))
	item = frappe.get_doc("Item", item_code)
	tag_data = {
		"item_code": item.item_code,
		"item_name": item.item_name,
		"standard_rate": flt(item.standard_rate or 0),
		"rate": flt(item.standard_rate or 0),
		"metal_type": getattr(item, "custom_metal_type", "") or "",
		"weight_grams": flt(getattr(item, "custom_gross_weight_g", 0) or 0),
	}
	tag_text = hw_utils.generate_escpos_tag(tag_data)
	barcode_cmd = hw_utils.generate_barcode_commands(item_code)
	return {
		"tag_text": tag_text,
		"barcode_commands_hex": barcode_cmd.hex(),
		"print_payload": hw_utils.format_print_payload(tag_text, printer_type="tag"),
		"tag_data": tag_data,
	}


@frappe.whitelist()
def generate_zpl_tag(item_code):
	"""Generate ZPL commands for jewelry tag printing on Zebra printers."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	if not frappe.db.exists("Item", item_code):
		frappe.throw(_("Item {0} not found.").format(item_code))
	item = frappe.get_doc("Item", item_code)
	tag_data = {
		"item_code": item.item_code,
		"item_name": item.item_name,
		"rate": flt(item.standard_rate or 0),
		"metal_type": getattr(item, "custom_metal_type", "") or "",
		"weight_grams": flt(getattr(item, "custom_gross_weight_g", 0) or 0),
	}
	zpl = _generate_zpl(tag_data)
	return {"success": True, "zpl": zpl, "tag_data": tag_data}


@frappe.whitelist()
def generate_zpl_tags_batch(item_codes):
	"""Generate ZPL for multiple tags (batch printing for received shipments)."""
	import json

	if isinstance(item_codes, str):
		item_codes = json.loads(item_codes)
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	zpl_batch = []
	for code in item_codes:
		if not frappe.db.exists("Item", code):
			continue
		item = frappe.get_doc("Item", code)
		tag_data = {
			"item_code": item.item_code,
			"item_name": item.item_name,
			"rate": flt(item.standard_rate or 0),
			"metal_type": getattr(item, "custom_metal_type", "") or "",
			"weight_grams": flt(getattr(item, "custom_gross_weight_g", 0) or 0),
		}
		zpl_batch.append(_generate_zpl(tag_data))
	return {"success": True, "count": len(zpl_batch), "zpl": "\n".join(zpl_batch)}


@frappe.whitelist()
def open_cash_drawer():
	"""Trigger cash drawer kick-out signal via the hardware bridge."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "POS User"])
	return {"success": True, "action": "cash_drawer"}


def _generate_zpl(data):
	"""Generate ZPL II commands for a 50mm x 25mm jewelry tag."""
	item_code = data.get("item_code", "")
	item_name = data.get("item_name", "")[:28]
	price = data.get("rate", 0)
	metal = data.get("metal_type", "")
	weight = data.get("weight_grams", 0)
	price_str = f"${price:.2f}" if price else ""
	desc = f"{metal} {weight}g" if metal else item_name
	zpl = "^XA\n"
	zpl += "^PW400\n"
	zpl += "^LL200\n"
	zpl += "^FO20,10^A0N,25,25^FDZEVAR^FS\n"
	zpl += "^FO20,40^A0N,18,18^FD{}^FS\n".format(desc)
	zpl += "^FO20,65^A0N,18,18^FD{}^FS\n".format(item_name)
	zpl += "^FO20,90^A0N,30,30^FD{}^FS\n".format(price_str)
	zpl += "^FO20,130^BY2^BCN,40,Y,N,N^FD{}^FS\n".format(item_code)
	zpl += "^XZ\n"
	return zpl
