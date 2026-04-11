# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, get_datetime, time_diff_in_hours
from frappe import _

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
			"fieldtype": "Datetime",
			"width": 140,
		},
		{
			"fieldname": "delivered_date",
			"label": _("Delivered Date"),
			"fieldtype": "Datetime",
			"width": 140,
		},
		{
			"fieldname": "promised_date",
			"label": _("Promised Date"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "turnaround_hours",
			"label": _("Turnaround (Hours)"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "turnaround_days",
			"label": _("Turnaround (Days)"),
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"fieldname": "vs_promised",
			"label": _("Vs Promised"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "repair_type",
			"label": _("Repair Type"),
			"fieldtype": "Link",
			"options": "Repair Type",
			"width": 140,
		},
		{
			"fieldname": "assigned_to",
			"label": _("Technician"),
			"fieldtype": "Link",
			"options": "User",
			"width": 130,
		},
		{
			"fieldname": "warehouse",
			"label": _("Store/Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 110,
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
			ro.received_date,
			ro.delivered_date,
			ro.promised_date,
			ro.repair_type,
			ro.assigned_to,
			ro.warehouse,
			ro.status
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			{conditions}
		ORDER BY ro.received_date DESC
		""",
		values=values,
		as_dict=True,
	)

	data = []
	total_hours = 0
	on_time_count = 0
	late_count = 0
	processed_count = 0

	for row in rows:
		if row.received_date and row.delivered_date:
			received = get_datetime(row.received_date)
			delivered = get_datetime(row.delivered_date)
			hours = time_diff_in_hours(delivered, received)
			days = flt(hours) / 24

			row.turnaround_hours = flt(hours, 2)
			row.turnaround_days = flt(days, 2)
			total_hours += flt(hours)
			processed_count += 1

			# Compare with promised date
			if row.promised_date:
				promised = frappe.utils.getdate(row.promised_date)
				actual = frappe.utils.getdate(row.delivered_date)
				if actual <= promised:
					row.vs_promised = '<span class="text-success">On Time</span>'
					on_time_count += 1
				else:
					days_late = (actual - promised).days
					row.vs_promised = f'<span class="text-danger">{days_late}d Late</span>'
					late_count += 1
			else:
				row.vs_promised = "No Promise"

			data.append(row)

	# Add summary row at the end if data exists
	if data and filters.get("include_summary"):
		avg_days = flt(total_hours / processed_count / 24) if processed_count else 0
		summary = {
			"repair_order": '<b>SUMMARY</b>',
			"turnaround_days": f'<b>Avg: {avg_days:.1f}d</b>',
			"vs_promised": f'<b>On Time: {on_time_count} | Late: {late_count}</b>',
		}
		data.append(summary)

	return data


def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " AND ro.received_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND ro.received_date <= %(to_date)s"

	if filters.get("warehouse"):
		conditions += " AND ro.warehouse = %(warehouse)s"

	if filters.get("repair_type"):
		conditions += " AND ro.repair_type = %(repair_type)s"

	if filters.get("assigned_to"):
		conditions += " AND ro.assigned_to = %(assigned_to)s"

	if filters.get("status"):
		conditions += " AND ro.status = %(status)s"

	if filters.get("customer"):
		conditions += " AND ro.customer = %(customer)s"

	# Only delivered repairs for turnaround calculation
	if filters.get("delivered_only"):
		conditions += " AND ro.status = 'Delivered' AND ro.delivered_date IS NOT NULL"

	return conditions


def get_values(filters):
	values = {}
	if filters.get("from_date"):
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		values["to_date"] = filters["to_date"]
	if filters.get("warehouse"):
		values["warehouse"] = filters["warehouse"]
	if filters.get("repair_type"):
		values["repair_type"] = filters["repair_type"]
	if filters.get("assigned_to"):
		values["assigned_to"] = filters["assigned_to"]
	if filters.get("status"):
		values["status"] = filters["status"]
	if filters.get("customer"):
		values["customer"] = filters["customer"]
	return values
