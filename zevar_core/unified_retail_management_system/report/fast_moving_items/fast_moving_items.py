# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt


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
		{"fieldname": "jewelry_type", "label": _("Type"), "fieldtype": "Data", "width": 90},
		{"fieldname": "qty_sold", "label": _("Qty Sold"), "fieldtype": "Float", "width": 80},
		{"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "avg_rate", "label": _("Avg Rate"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "current_stock", "label": _("Current Stock"), "fieldtype": "Float", "width": 90},
		{"fieldname": "days_of_supply", "label": _("Days of Supply"), "fieldtype": "Float", "width": 100},
	]


def get_data(filters):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	days_in_period = max(1, (flt(to_date) - flt(from_date)) if from_date and to_date else 30)

	query = """
		SELECT
			sii.item_code,
			sii.item_name,
			i.custom_metal_type AS metal_type,
			i.custom_jewelry_type AS jewelry_type,
			SUM(sii.qty) AS qty_sold,
			SUM(sii.base_amount) AS revenue,
			AVG(sii.base_rate) AS avg_rate
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		LEFT JOIN `tabItem` i ON sii.item_code = i.name
		WHERE si.docstatus = 1
		  AND si.is_pos = 1
	"""
	values: dict = {}

	if from_date:
		query += " AND si.posting_date >= %(from_date)s"
		values["from_date"] = from_date
	if to_date:
		query += " AND si.posting_date <= %(to_date)s"
		values["to_date"] = to_date
	if filters.get("warehouse"):
		query += " AND sii.warehouse = %(warehouse)s"
		values["warehouse"] = filters["warehouse"]
	if filters.get("jewelry_type"):
		query += " AND i.custom_jewelry_type = %(jewelry_type)s"
		values["jewelry_type"] = filters["jewelry_type"]

	query += " GROUP BY sii.item_code, sii.item_name, i.custom_metal_type, i.custom_jewelry_type"
	query += " ORDER BY revenue DESC"

	limit = cint(filters.get("limit") or 50)
	values["lim"] = limit
	query += " LIMIT %(lim)s"

	rows = frappe.db.sql(query, values=values, as_dict=True)

	result = []
	for row in rows:
		# Get current stock
		stock = frappe.db.get_value("Bin", {"item_code": row.item_code}, "SUM(actual_qty)") or 0
		daily_velocity = flt(row.qty_sold) / days_in_period
		dos = (flt(stock) / daily_velocity) if daily_velocity > 0 else 999

		result.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"metal_type": row.metal_type,
				"jewelry_type": row.jewelry_type,
				"qty_sold": flt(row.qty_sold),
				"revenue": flt(row.revenue),
				"avg_rate": flt(row.avg_rate),
				"current_stock": flt(stock),
				"days_of_supply": round(dos, 1),
			}
		)

	return result
