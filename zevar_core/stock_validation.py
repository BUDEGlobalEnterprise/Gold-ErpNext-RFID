"""
Defensive validation for POS Sales Invoice stock quantities.

Prevents UOM conversion factor from inflating stock_qty on POS invoices,
which causes over-deduction of inventory (e.g. selling 1 unit deducts 16).
"""

import frappe
from frappe import _
from frappe.utils import flt


def validate_pos_stock_qty(doc, method=None):
	if not getattr(doc, "is_pos", 0) or not getattr(doc, "update_stock", 0):
		return

	for item in doc.items:
		# stock_qty should equal qty * conversion_factor.
		# For POS, we force conversion_factor=1, so stock_qty must equal qty.
		if flt(item.stock_qty) > flt(item.qty) * 1.01:
			item.uom = item.stock_uom
			item.conversion_factor = 1.0
			item.stock_qty = item.qty
			frappe.log_error(
				title=f"POS Stock Qty Auto-Fix: {doc.name}",
				message=(
					f"Item {item.item_code} had stock_qty={item.stock_qty} "
					f"which exceeded qty={item.qty}. "
					f"Reset to uom={item.stock_uom}, conversion_factor=1.0"
				),
			)
