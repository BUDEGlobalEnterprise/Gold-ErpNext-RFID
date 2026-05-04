# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "repair_order",
			"label": _("Repair Order"),
			"fieldtype": "Link",
			"options": "Repair Order",
			"width": 140,
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{
			"fieldname": "received_date",
			"label": _("Received Date"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "metal_type",
			"label": _("Metal Type"),
			"fieldtype": "Link",
			"options": "Zevar Metal",
			"width": 120,
		},
		{
			"fieldname": "purity",
			"label": _("Purity"),
			"fieldtype": "Link",
			"options": "Zevar Purity",
			"width": 100,
		},
		{
			"fieldname": "metal_weight_in",
			"label": _("Weight In (g)"),
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"fieldname": "metal_weight_out",
			"label": _("Weight Out (g)"),
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"fieldname": "metal_scrap",
			"label": _("Scrap (g)"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "net_difference",
			"label": _("Net Diff (g)"),
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"fieldname": "stone_weight",
			"label": _("Stone Wt (ct)"),
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"fieldname": "gemstone_details",
			"label": _("Gemstones"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "warehouse",
			"label": _("Store"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 130,
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)
	values = get_values(filters)

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			ro.name as repair_order,
			ro.customer,
			DATE(ro.received_date) as received_date,
			ro.status,
			ro.metal_type,
			ro.purity,
			ro.metal_weight_in,
			ro.metal_weight_out,
			ro.metal_scrap,
			ro.metal_weight_difference,
			ro.stone_weight,
			ro.warehouse
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			AND (ro.metal_weight_in > 0 OR ro.metal_weight_out > 0 OR ro.stone_weight > 0)
			{conditions}
		ORDER BY ro.received_date DESC
		""",
		values=values,
		as_dict=True,
	)

	data = []
	for row in rows:
		row.net_difference = flt(row.metal_weight_difference)

		# Get gemstone details
		row.gemstone_details = get_gemstone_summary(row.repair_order)

		# Format metal info
		if row.metal_type:
			metal_info = f"{row.metal_type}"
			if row.purity:
				metal_info += f" ({row.purity})"
			row.metal_type = metal_info

		data.append(row)

	return data


def get_gemstone_summary(repair_order):
	"""Get summary of gemstones for this repair order"""
	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	gemstones = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			gem.gemstone_type,
			gem.quantity,
			gem.carat_weight
		FROM `tabRepair Gemstone` gem
		WHERE gem.parent = %s
		ORDER BY gem.idx
		""",
		values=(repair_order,),
		as_dict=True,
	)

	if not gemstones:
		return ""

	parts = []
	for gem in gemstones:
		if gem.quantity:
			parts.append(f"{gem.gemstone_type}: {gem.quantity} x {flt(gem.carat_weight, 2)}ct")
		else:
			parts.append(f"{gem.gemstone_type}: {flt(gem.carat_weight, 2)}ct")

	return "; ".join(parts) if parts else ""


def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " AND ro.received_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND ro.received_date <= %(to_date)s"

	if filters.get("warehouse"):
		conditions += " AND ro.warehouse = %(warehouse)s"

	if filters.get("customer"):
		conditions += " AND ro.customer = %(customer)s"

	if filters.get("metal_type"):
		conditions += " AND ro.metal_type = %(metal_type)s"

	if filters.get("status"):
		conditions += " AND ro.status = %(status)s"

	if filters.get("has_discrepancy"):
		# Show only repairs with metal weight differences
		conditions += " AND ABS(ro.metal_weight_difference) > 0.01"

	return conditions


def get_values(filters):
	values = {}
	if filters.get("from_date"):
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		values["to_date"] = filters["to_date"]
	if filters.get("warehouse"):
		values["warehouse"] = filters["warehouse"]
	if filters.get("customer"):
		values["customer"] = filters["customer"]
	if filters.get("metal_type"):
		values["metal_type"] = filters["metal_type"]
	if filters.get("status"):
		values["status"] = filters["status"]
	return values
