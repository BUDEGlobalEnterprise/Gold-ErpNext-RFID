# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from frappe.utils import flt


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
		{
			"fieldname": "item_group",
			"label": _("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 120,
		},
		{"fieldname": "metal_type", "label": _("Metal"), "fieldtype": "Data", "width": 90},
		{"fieldname": "purity", "label": _("Purity"), "fieldtype": "Data", "width": 70},
		{"fieldname": "jewelry_type", "label": _("Jewelry Type"), "fieldtype": "Data", "width": 100},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 130,
		},
		{"fieldname": "actual_qty", "label": _("Qty"), "fieldtype": "Float", "width": 70},
		{"fieldname": "cost_price", "label": _("Cost Price"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "retail_price", "label": _("Retail Price"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "total_cost", "label": _("Total Cost"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "total_retail", "label": _("Total Retail"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "markup_pct", "label": _("Markup %"), "fieldtype": "Percent", "width": 80},
	]


def get_data(filters):
	Bin = DocType("Bin")
	Item = DocType("Item")

	query = (
		frappe.qb.from_(Bin)
		.left_join(Item)
		.on(Bin.item_code == Item.name)
		.select(
			Bin.item_code,
			Item.item_name,
			Item.item_group,
			Item.custom_metal_type.as_("metal_type"),
			Item.custom_purity.as_("purity"),
			Item.custom_jewelry_type.as_("jewelry_type"),
			Bin.warehouse,
			Bin.actual_qty,
			Bin.valuation_rate.as_("cost_price"),
			Item.standard_rate.as_("retail_price"),
		)
		.where(Bin.actual_qty > 0)
		.where(Item.disabled == 0)
	)

	if filters.get("warehouse"):
		query = query.where(Bin.warehouse == filters["warehouse"])
	if filters.get("item_group"):
		query = query.where(Item.item_group == filters["item_group"])
	if filters.get("metal_type"):
		query = query.where(Item.custom_metal_type == filters["metal_type"])
	if filters.get("jewelry_type"):
		query = query.where(Item.custom_jewelry_type == filters["jewelry_type"])

	query = query.orderby(Bin.valuation_rate, order=frappe.qb.desc)

	rows = frappe.db.sql(query.get_sql(), as_dict=True)

	result = []
	totals = {"total_cost": 0, "total_retail": 0}

	for row in rows:
		cost = flt(row.cost_price) or 0
		retail = flt(row.retail_price) or 0
		total_cost = flt(row.actual_qty) * cost
		total_retail = flt(row.actual_qty) * retail
		markup = ((retail - cost) / cost * 100) if cost > 0 else 0

		result.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"item_group": row.item_group,
				"metal_type": row.metal_type,
				"purity": row.purity,
				"jewelry_type": row.jewelry_type,
				"warehouse": row.warehouse,
				"actual_qty": row.actual_qty,
				"cost_price": cost,
				"retail_price": retail,
				"total_cost": total_cost,
				"total_retail": total_retail,
				"markup_pct": markup,
			}
		)
		totals["total_cost"] += total_cost
		totals["total_retail"] += total_retail

	# Summary totals row
	if len(result) > 0:
		result.append(
			{
				"item_code": None,
				"item_name": _("** TOTAL **"),
				"total_cost": totals["total_cost"],
				"total_retail": totals["total_retail"],
				"markup_pct": ((totals["total_retail"] - totals["total_cost"]) / totals["total_cost"] * 100)
				if totals["total_cost"] > 0
				else 0,
			}
		)

	return result
