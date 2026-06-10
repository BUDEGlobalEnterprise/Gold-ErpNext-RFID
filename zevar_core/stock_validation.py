"""
Defensive validation for POS Sales Invoice stock quantities.

Two-layer protection:
1. validate hook: catches inflated stock_qty early in the validation chain
2. before_submit hook: last-resort reset right before SLE creation

The ERPNext stock deduction uses stock_qty (= qty x conversion_factor).
If conversion_factor != 1.0, the deduction is multiplied, causing the
15 → -1 bug (selling 1 unit deducts 16).
"""

import frappe
from frappe import _
from frappe.utils import flt


def validate_pos_stock_qty(doc, method=None):
	if not getattr(doc, "is_pos", 0) or not getattr(doc, "update_stock", 0):
		return

	for item in doc.items:
		if flt(item.conversion_factor) != 1.0 or flt(item.stock_qty) != flt(item.qty):
			original_cf = item.conversion_factor
			original_sq = item.stock_qty
			item.uom = item.stock_uom
			item.conversion_factor = 1.0
			item.stock_qty = item.qty
			frappe.log_error(
				title=f"POS Stock Validate Fix: {doc.name}",
				message=(
					f"Item {item.item_code} had conversion_factor={original_cf}, "
					f"stock_qty={original_sq}, qty={item.qty}. "
					f"Reset to uom={item.stock_uom}, cf=1.0, stock_qty={item.qty}"
				),
			)


def force_pos_stock_qty_before_submit(doc, method=None):
	"""Last-resort hook: runs in before_submit, AFTER all validate hooks
	and AFTER ERPNext's own recalculation. This ensures conversion_factor=1.0
	and stock_qty=qty right before SLEs are created during on_submit."""

	if not getattr(doc, "is_pos", 0) or not getattr(doc, "update_stock", 0):
		return

	for item in doc.items:
		if flt(item.conversion_factor) != 1.0 or flt(item.stock_qty) != flt(item.qty):
			item.uom = item.stock_uom
			item.conversion_factor = 1.0
			item.stock_qty = flt(item.qty)
			frappe.log_error(
				title=f"POS Stock Before-Submit Fix: {doc.name}",
				message=(
					f"Item {item.item_code}: conversion_factor was {item.conversion_factor}, "
					f"stock_qty was {item.stock_qty}. "
					f"Force-reset to cf=1.0, stock_qty={item.qty}"
				),
			)
