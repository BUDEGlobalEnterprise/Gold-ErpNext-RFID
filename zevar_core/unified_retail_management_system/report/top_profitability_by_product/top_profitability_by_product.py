# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": frappe._("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{"fieldname": "item_name", "label": frappe._("Item Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "jewelry_type", "label": frappe._("Jewelry Type"), "fieldtype": "Data", "width": 130},
		{"fieldname": "metal_type", "label": frappe._("Metal Type"), "fieldtype": "Data", "width": 120},
		{"fieldname": "units_sold", "label": frappe._("Units Sold"), "fieldtype": "Int", "width": 100},
		{"fieldname": "revenue", "label": frappe._("Revenue ($)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "cogs", "label": frappe._("COGS ($)"), "fieldtype": "Currency", "width": 120},
		{
			"fieldname": "gross_profit",
			"label": frappe._("Gross Profit ($)"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{"fieldname": "margin", "label": frappe._("Margin (%)"), "fieldtype": "Percent", "width": 100},
	]


def get_data(filters):
	conditions = ""
	values = {}

	if filters and filters.get("from_date"):
		conditions += " AND scb.posting_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]

	if filters and filters.get("to_date"):
		conditions += " AND scb.posting_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	if filters and filters.get("jewelry_type"):
		conditions += " AND i.custom_jewelry_type = %(jewelry_type)s"
		values["jewelry_type"] = filters["jewelry_type"]

	limit = 20
	if filters and filters.get("limit"):
		limit = int(filters["limit"])
	values["limit"] = limit

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	# Phase 0: profitability comes straight from the SCB's gross_profit (the one
	# true margin), allocated to each item by its revenue share of the invoice -
	# not recomputed from the inflated stock-ledger valuation_rate.
	# SCB is a non-submittable (draft-only) doctype, so docstatus is 0 (cancelled
	# invoices' rows are deleted on_cancel); the active-invoice guard is si.docstatus=1.
	data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			sii.item_code,
			sii.item_name,
			i.custom_jewelry_type AS jewelry_type,
			i.custom_metal_type AS metal_type,
			SUM(sii.qty) AS units_sold,
			SUM(sii.amount) AS revenue,
			SUM(
				CASE WHEN si.base_net_total > 0
				     THEN scb.gross_profit * (sii.amount / si.base_net_total)
				     ELSE 0 END
			) AS gross_profit
		FROM `tabSale Cost Breakdown` scb
		INNER JOIN `tabSales Invoice` si ON si.name = scb.sales_invoice
		INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		INNER JOIN `tabItem` i ON i.name = sii.item_code
		WHERE si.docstatus = 1 AND scb.docstatus < 2 {conditions}
		GROUP BY sii.item_code
		ORDER BY gross_profit DESC
		LIMIT %(limit)s
		""",
		values=values,
		as_dict=True,
	)

	for row in data:
		revenue = flt(row.get("revenue", 0))
		gross_profit = flt(row.get("gross_profit", 0))
		row["cogs"] = revenue - gross_profit
		row["margin"] = flt((gross_profit / revenue) * 100) if revenue > 0 else 0

	return data
