# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, getdate, time_diff_in_hours


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
			"width": 160,
		},
		{
			"fieldname": "received_date",
			"label": _("Received Date"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "delivered_date",
			"label": _("Delivered Date"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "turnaround_days",
			"label": _("Turnaround (Days)"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "repair_type",
			"label": _("Repair Type"),
			"fieldtype": "Link",
			"options": "Repair Type",
			"width": 150,
		},
		{
			"fieldname": "item_type",
			"label": _("Item Type"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "item_description",
			"label": _("Description"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "total_cost",
			"label": _("Total Cost"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "payment_status",
			"label": _("Payment Status"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "warehouse",
			"label": _("Store"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 130,
		},
		{
			"fieldname": "is_warranty_repair",
			"label": _("Warranty"),
			"fieldtype": "Check",
			"width": 80,
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)
	values = get_values(filters)

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(
		f"""
		SELECT
			ro.name as repair_order,
			ro.customer,
			DATE(ro.received_date) as received_date,
			DATE(ro.delivered_date) as delivered_date,
			ro.repair_type,
			ro.item_type,
			ro.item_description,
			ro.total_cost,
			ro.payment_status,
			ro.status,
			ro.warehouse,
			ro.is_warranty_repair
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			{conditions}
		ORDER BY ro.received_date DESC
		""",
		values=values,
		as_dict=True,
	)

	data = []
	for row in rows:
		# Calculate turnaround for delivered repairs
		if row.delivered_date and row.received_date:
			hours = time_diff_in_hours(get_datetime(row.delivered_date), get_datetime(row.received_date))
			row.turnaround_days = flt(hours / 24, 1)
		else:
			row.turnaround_days = None

		# Format warranty indicator
		if row.is_warranty_repair:
			row.is_warranty_repair = 1
		else:
			row.is_warranty_repair = 0

		data.append(row)

	return data


def get_conditions(filters):
	conditions = ""

	# Customer is usually required for this report
	if filters.get("customer"):
		conditions += " AND ro.customer = %(customer)s"

	if filters.get("from_date"):
		conditions += " AND ro.received_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND ro.received_date <= %(to_date)s"

	if filters.get("warehouse"):
		conditions += " AND ro.warehouse = %(warehouse)s"

	if filters.get("repair_type"):
		conditions += " AND ro.repair_type = %(repair_type)s"

	if filters.get("status"):
		conditions += " AND ro.status = %(status)s"

	if filters.get("item_type"):
		conditions += " AND ro.item_type = %(item_type)s"

	if filters.get("include_warranty_only"):
		conditions += " AND ro.is_warranty_repair = 1"

	return conditions


def get_values(filters):
	values = {}
	if filters.get("customer"):
		values["customer"] = filters["customer"]
	if filters.get("from_date"):
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		values["to_date"] = filters["to_date"]
	if filters.get("warehouse"):
		values["warehouse"] = filters["warehouse"]
	if filters.get("repair_type"):
		values["repair_type"] = filters["repair_type"]
	if filters.get("status"):
		values["status"] = filters["status"]
	if filters.get("item_type"):
		values["item_type"] = filters["item_type"]
	return values
