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
		"metal_type": "",
		"weight_grams": 0,
	}
	tag_text = hw_utils.generate_escpos_tag(tag_data)
	barcode_cmd = hw_utils.generate_barcode_commands(item_code)
	return {
		"tag_text": tag_text,
		"barcode_commands_hex": barcode_cmd.hex(),
		"print_payload": hw_utils.format_print_payload(tag_text, printer_type="tag"),
	}
