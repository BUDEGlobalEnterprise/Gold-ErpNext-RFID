"""
Hardware Bridging Utilities

ESC/POS encoding and WebSocket-based printing for thermal printers
(Citizen CL-S621) from web applications. Barcode scanner integration
via keyboard wedge emulation.
"""

import frappe
from frappe import _
from frappe.utils import cstr

import json


def generate_escpos_receipt(invoice_data, settings=None):
	lines = []
	lines.append(_esc_center("ZEVAR JEWELERS"))
	lines.append(_esc_center("=" * 32))
	if invoice_data.get("store_address"):
		lines.append(_esc_center(invoice_data["store_address"]))
	if invoice_data.get("store_phone"):
		lines.append(_esc_center(invoice_data["store_phone"]))
	lines.append(_esc_center("-" * 32))
	lines.append(f"Date: {invoice_data.get('date', '')}")
	lines.append(f"Invoice: {invoice_data.get('invoice_name', '')}")
	lines.append(f"Associate: {invoice_data.get('associate', '')}")
	if invoice_data.get("customer"):
		lines.append(f"Customer: {invoice_data['customer']}")
	lines.append(_esc_center("-" * 32))
	items = invoice_data.get("items", [])
	for item in items:
		name = item.get("item_name", "")[:20]
		qty = item.get("qty", 1)
		rate = item.get("rate", 0)
		amount = item.get("amount", qty * rate)
		lines.append(f"{name}")
		lines.append(f"  {qty} x ${rate:.2f}        ${amount:.2f}")
	lines.append(_esc_center("-" * 32))
	lines.append(f"{'Subtotal:':<22}${invoice_data.get('subtotal', 0):.2f}")
	if invoice_data.get("discount", 0) > 0:
		lines.append(f"{'Discount:':<22}-${invoice_data['discount']:.2f}")
	if invoice_data.get("tax", 0) > 0:
		lines.append(f"{'Tax:':<22}${invoice_data['tax']:.2f}")
	lines.append(_esc_center("=" * 32))
	lines.append(_esc_bold(f"{'TOTAL:':<22}${invoice_data.get('grand_total', 0):.2f}"))
	lines.append("")
	payments = invoice_data.get("payments", [])
	if payments:
		lines.append("Payment:")
		for p in payments:
			mode = p.get("mode_of_payment", "")
			amt = p.get("amount", 0)
			ref = p.get("reference_no", "")
			pay_line = f"  {mode:<18}${amt:.2f}"
			if ref:
				pay_line += f"\n  Ref: {ref}"
			lines.append(pay_line)
		lines.append("")
	lines.append(_esc_center("Thank you for shopping"))
	lines.append(_esc_center("with Zevar Jewelers!"))
	lines.append("")
	lines.append("")
	lines.append("")
	return "\n".join(lines)


def generate_escpos_tag(tag_data):
	lines = []
	sku = tag_data.get("item_code", "")
	name = tag_data.get("item_name", "")[:24]
	retail_price = tag_data.get("standard_rate", 0)
	selling_price = tag_data.get("rate", 0)
	metal = tag_data.get("metal_type", "")
	weight = tag_data.get("weight_grams", 0)
	lines.append(_esc_center("ZEVAR"))
	lines.append(_esc_center("-" * 20))
	lines.append(f"{name}")
	if metal:
		lines.append(f"{metal} {weight}g" if weight else metal)
	lines.append(f"SKU: {sku}")
	lines.append("")
	if retail_price and retail_price != selling_price:
		lines.append(f"Retail: ${retail_price:.2f}")
		lines.append(_esc_bold(f"Price: ${selling_price:.2f}"))
	else:
		lines.append(_esc_bold(f"${selling_price:.2f}"))
	lines.append("")
	lines.append("")
	return "\n".join(lines)


def generate_barcode_commands(data, barcode_type="CODE39", width=2, height=100):
	commands = []
	# GS w n - Set barcode width
	commands.append(b"\x1Dw" + bytes([width]))
	# GS h n - Set barcode height
	commands.append(b"\x1Dh" + bytes([height]))
	
	barcode_map = {
		"CODE39": 69,
		"EAN13": 67,
		"CODE128": 73,
	}
	barcode_num = barcode_map.get(barcode_type, 69)
	data_bytes = data.encode("ascii")
	data_len = len(data_bytes)
	
	# GS k m n d1...dn - Print barcode (Function B)
	commands.append(b"\x1Dk" + bytes([barcode_num, data_len]) + data_bytes)
	
	return b"".join(commands)


def _esc_center(text):
	return f"\x1B\x61\x01{text}"


def _esc_bold(text):
	return f"\x1B\x45\x01{text}\x1B\x45\x00"


def format_print_payload(content, printer_type="receipt"):
	return {
		"type": printer_type,
		"content": content,
		"cut": True,
		"encoding": "ESC/POS",
	}
