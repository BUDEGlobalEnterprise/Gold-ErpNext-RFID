# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [
		{"fieldname": "item_code", "label": _("Item Code"), "fieldtype": "Link", "options": "Item", "width": 140},
		{"fieldname": "item_name", "label": _("Item Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "item_group", "label": _("Item Group"), "fieldtype": "Data", "width": 110},
		{"fieldname": "metal_type", "label": _("Metal"), "fieldtype": "Data", "width": 80},
		{"fieldname": "jewelry_type", "label": _("Type"), "fieldtype": "Data", "width": 90},
		{"fieldname": "warehouse", "label": _("Warehouse"), "fieldtype": "Link", "options": "Warehouse", "width": 130},
		{"fieldname": "actual_qty", "label": _("Qty"), "fieldtype": "Float", "width": 60},
		{"fieldname": "valuation_rate", "label": _("Valuation"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "total_value", "label": _("Total Value"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "days_on_hand", "label": _("Days on Hand"), "fieldtype": "Int", "width": 90},
		{"fieldname": "aging_bucket", "label": _("Aging Bucket"), "fieldtype": "Data", "width": 100},
	]


def get_data(filters):
	today_date = getdate(filters.get("as_of_date") or today())

	# Get items with stock, joined with first stock ledger entry date (receipt date)
	conditions = "WHERE b.actual_qty > 0 AND i.disabled = 0"
	values: dict = {}

	if filters.get("warehouse"):
		conditions += " AND b.warehouse = %(warehouse)s"
		values["warehouse"] = filters["warehouse"]
	if filters.get("item_group"):
		conditions += " AND i.item_group = %(item_group)s"
		values["item_group"] = filters["item_group"]
	if filters.get("metal_type"):
		conditions += " AND i.custom_metal_type = %(metal_type)s"
		values["metal_type"] = filters["metal_type"]

	max_age = filters.get("max_days")
	if max_age:
		conditions += " AND DATEDIFF(%(as_of_date)s, COALESCE(first_sle.first_date, i.creation)) <= %(max_days)s"
		values["as_of_date"] = today_date
		values["max_days"] = max_age

	rows = frappe.db.sql(
		f"""
		SELECT
			b.item_code,
			i.item_name,
			i.item_group,
			i.custom_metal_type AS metal_type,
			i.custom_jewelry_type AS jewelry_type,
			b.warehouse,
			b.actual_qty,
			b.valuation_rate,
			(b.actual_qty * b.valuation_rate) AS total_value,
			COALESCE(first_sle.first_date, DATE(i.creation)) AS first_stock_date
		FROM `tabBin` b
		JOIN `tabItem` i ON b.item_code = i.name
		LEFT JOIN (
			SELECT item_code, warehouse, MIN(posting_date) AS first_date
			FROM `tabStock Ledger Entry`
			WHERE actual_qty > 0 AND docstatus = 1
			GROUP BY item_code, warehouse
		) first_sle ON b.item_code = first_sle.item_code AND b.warehouse = first_sle.warehouse
		{conditions}
		ORDER BY total_value DESC
		""",
		values=values,
		as_dict=True,
	)

	result = []
	for row in rows:
		days = (today_date - getdate(row.first_stock_date)).days if row.first_stock_date else 0
		bucket = _get_bucket(days)

		result.append({
			"item_code": row.item_code,
			"item_name": row.item_name,
			"item_group": row.item_group,
			"metal_type": row.metal_type,
			"jewelry_type": row.jewelry_type,
			"warehouse": row.warehouse,
			"actual_qty": row.actual_qty,
			"valuation_rate": flt(row.valuation_rate),
			"total_value": flt(row.total_value),
			"days_on_hand": days,
			"aging_bucket": bucket,
		})

	return result


def _get_bucket(days):
	if days <= 30:
		return "0-30"
	elif days <= 60:
		return "31-60"
	elif days <= 90:
		return "61-90"
	elif days <= 120:
		return "91-120"
	elif days <= 180:
		return "121-180"
	elif days <= 365:
		return "181-365"
	else:
		return "365+"
