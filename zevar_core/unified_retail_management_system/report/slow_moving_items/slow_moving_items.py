# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, today


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{"fieldname": "item_name", "label": _("Item Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "metal_type", "label": _("Metal"), "fieldtype": "Data", "width": 80},
		{"fieldname": "purity", "label": _("Purity"), "fieldtype": "Data", "width": 70},
		{"fieldname": "jewelry_type", "label": _("Type"), "fieldtype": "Data", "width": 90},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 130,
		},
		{"fieldname": "actual_qty", "label": _("Stock Qty"), "fieldtype": "Float", "width": 80},
		{"fieldname": "valuation_rate", "label": _("Cost"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "total_value", "label": _("Total Value"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "days_on_hand", "label": _("Days on Hand"), "fieldtype": "Int", "width": 90},
		{"fieldname": "last_sold_date", "label": _("Last Sold"), "fieldtype": "Date", "width": 100},
		{"fieldname": "days_since_sale", "label": _("Days Since Sale"), "fieldtype": "Int", "width": 100},
		{"fieldname": "holding_cost", "label": _("Est. Holding Cost"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	today_date = getdate(filters.get("as_of_date") or today())
	min_days = cint(filters.get("min_days") or 90)

	values: dict = {
		"as_of_date": today_date,
		"min_days": min_days,
	}

	conditions = ""
	if filters.get("warehouse"):
		conditions += " AND b.warehouse = %(warehouse)s"
		values["warehouse"] = filters["warehouse"]
	if filters.get("item_group"):
		conditions += " AND i.item_group = %(item_group)s"
		values["item_group"] = filters["item_group"]

	# Items in stock with no sale in the last N days, or never sold
	rows = frappe.db.sql(
		f"""
		SELECT
			b.item_code,
			i.item_name,
			i.custom_metal_type AS metal_type,
			i.custom_purity AS purity,
			i.custom_jewelry_type AS jewelry_type,
			b.warehouse,
			b.actual_qty,
			b.valuation_rate,
			(b.actual_qty * b.valuation_rate) AS total_value,
			COALESCE(first_sle.first_date, DATE(i.creation)) AS first_stock_date,
			last_sale.last_sold AS last_sold_date
		FROM `tabBin` b
		JOIN `tabItem` i ON b.item_code = i.name
		LEFT JOIN (
			SELECT item_code, warehouse, MIN(posting_date) AS first_date
			FROM `tabStock Ledger Entry`
			WHERE actual_qty > 0 AND docstatus = 1
			GROUP BY item_code, warehouse
		) first_sle ON b.item_code = first_sle.item_code AND b.warehouse = first_sle.warehouse
		LEFT JOIN (
			SELECT sii.item_code, MAX(si.posting_date) AS last_sold
			FROM `tabSales Invoice Item` sii
			JOIN `tabSales Invoice` si ON sii.parent = si.name
			WHERE si.docstatus = 1 AND si.is_pos = 1
			GROUP BY sii.item_code
		) last_sale ON b.item_code = last_sale.item_code
		WHERE b.actual_qty > 0
		  AND i.disabled = 0
		  AND (
		    last_sale.last_sold IS NULL
		    OR DATEDIFF(%(as_of_date)s, last_sale.last_sold) >= %(min_days)s
		  )
		  {conditions}
		ORDER BY total_value DESC
		""",
		values=values,
		as_dict=True,
	)

	result = []
	# Assume 8% annual carrying cost (industry standard)
	annual_carrying_rate = 0.08

	for row in rows:
		days_on_hand = (today_date - getdate(row.first_stock_date)).days if row.first_stock_date else 0
		days_since_sale = (
			(today_date - getdate(row.last_sold_date)).days if row.last_sold_date else days_on_hand
		)
		holding_cost = flt(row.total_value) * annual_carrying_rate * (days_on_hand / 365)

		result.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"metal_type": row.metal_type,
				"purity": row.purity,
				"jewelry_type": row.jewelry_type,
				"warehouse": row.warehouse,
				"actual_qty": flt(row.actual_qty),
				"valuation_rate": flt(row.valuation_rate),
				"total_value": flt(row.total_value),
				"days_on_hand": days_on_hand,
				"last_sold_date": row.last_sold_date,
				"days_since_sale": days_since_sale,
				"holding_cost": round(holding_cost, 2),
			}
		)

	return result
