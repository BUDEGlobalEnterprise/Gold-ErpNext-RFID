"""
Diagnostic script: Find items with UOM conversion issues that cause
inventory over-deduction on POS sales.

Run: bench --site <site> execute zevar_core.diagnose_uom.run
"""

import frappe
from frappe.utils import flt


def run():
	print("\n=== UOM Conversion Diagnostic ===\n")

	# 1. Items where sales_uom != stock_uom
	mismatched = frappe.get_all(
		"Item",
		filters={
			"is_stock_item": 1,
			"disabled": 0,
			"sales_uom": ["is", "set"],
		},
		fields=["name", "item_name", "stock_uom", "sales_uom"],
	)

	if mismatched:
		print(f"Items with sales_uom != stock_uom ({len(mismatched)} found):")
		for item in mismatched:
			if item.sales_uom != item.stock_uom:
				cf = (
					frappe.db.get_value(
						"UOM Conversion Detail",
						{"parent": item.name, "uom": item.sales_uom},
						"conversion_factor",
					)
					or 1.0
				)
				print(f"  {item.name}: stock_uom={item.stock_uom}, sales_uom={item.sales_uom}, cf={cf}")
	else:
		print("No items with sales_uom set.")

	# 2. Items with non-1 UOM conversion factors
	print("\nItems with UOM Conversion Details (non-1 conversion factor):")
	conversions = frappe.get_all(
		"UOM Conversion Detail",
		filters={"conversion_factor": ["!=", 1]},
		fields=["parent", "uom", "conversion_factor"],
	)
	for conv in conversions:
		item_name = frappe.db.get_value("Item", conv.parent, "item_name")
		print(f"  {conv.parent} ({item_name}): 1 {conv.uom} = {conv.conversion_factor} stock units")

	# 3. Recent POS invoices where stock_qty != qty
	print("\nRecent POS Invoices with stock_qty != qty (last 30 days):")
	from frappe.utils import add_days, today

	since = add_days(today(), -30)
	suspect_invoices = frappe.db.sql(
		"""
		SELECT si.name, sii.item_code, sii.qty, sii.stock_qty, sii.uom, sii.conversion_factor
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON si.name = sii.parent
		WHERE si.is_pos = 1
		  AND si.update_stock = 1
		  AND si.docstatus = 1
		  AND si.creation >= %s
		  AND ABS(sii.stock_qty - sii.qty) > 0.01
		ORDER BY si.creation DESC
		LIMIT 20
	""",
		(since,),
		as_dict=True,
	)

	if suspect_invoices:
		for inv in suspect_invoices:
			print(
				f"  {inv.name}: {inv.item_code} qty={inv.qty} stock_qty={inv.stock_qty} "
				f"(uom={inv.uom}, cf={inv.conversion_factor})"
			)
	else:
		print("  None found.")

	print("\n=== Diagnostic Complete ===\n")
