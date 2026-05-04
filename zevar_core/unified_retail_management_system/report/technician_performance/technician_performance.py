# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, time_diff_in_hours


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "technician",
			"label": _("Technician"),
			"fieldtype": "Link",
			"options": "User",
			"width": 160,
		},
		{
			"fieldname": "total_assigned",
			"label": _("Total Assigned"),
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"fieldname": "in_progress",
			"label": _("In Progress"),
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"fieldname": "completed",
			"label": _("Completed"),
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"fieldname": "completion_rate",
			"label": _("Completion Rate"),
			"fieldtype": "Percent",
			"width": 110,
		},
		{
			"fieldname": "total_hours",
			"label": _("Total Hours"),
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"fieldname": "avg_hours_per_repair",
			"label": _("Avg Hours/Repair"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "on_time_count",
			"label": _("On Time"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "late_count",
			"label": _("Late"),
			"fieldtype": "Int",
			"width": 80,
		},
		{
			"fieldname": "on_time_rate",
			"label": _("On-Time Rate"),
			"fieldtype": "Percent",
			"width": 100,
		},
		{
			"fieldname": "total_revenue",
			"label": _("Total Revenue"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "avg_revenue",
			"label": _("Avg Revenue"),
			"fieldtype": "Currency",
			"width": 120,
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)
	values = get_values(filters)

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			ro.assigned_to as technician,
			COUNT(*) as total_assigned,
			SUM(CASE WHEN ro.status IN ('Received', 'Estimated', 'Approved', 'In Progress', 'Waiting for Parts', 'Quality Check') THEN 1 ELSE 0 END) as in_progress,
			SUM(CASE WHEN ro.status = 'Delivered' THEN 1 ELSE 0 END) as completed,
			ro.received_date,
			ro.delivered_date,
			ro.promised_date,
			ro.total_cost
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			AND ro.assigned_to IS NOT NULL
			{conditions}
		GROUP BY ro.assigned_to
		ORDER BY completed DESC, total_assigned DESC
		""",
		values=values,
		as_dict=True,
	)

	data = []
	for row in rows:
		# Get detailed metrics for this technician
		technician_data = get_technician_metrics(row.technician, filters)

		row.update(technician_data)
		data.append(row)

	return data


def get_technician_metrics(technician, filters):
	"""Get detailed metrics for a specific technician"""
	conditions = get_conditions(filters)
	values = get_values(filters)
	values["technician"] = technician

	# Get completed repairs with dates
	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	completed_repairs = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			ro.received_date,
			ro.delivered_date,
			ro.promised_date,
			ro.total_cost
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			AND ro.assigned_to = %(technician)s
			AND ro.status = 'Delivered'
			AND ro.delivered_date IS NOT NULL
			{conditions}
		""",
		values=values,
		as_dict=True,
	)

	total_hours = 0
	on_time_count = 0
	late_count = 0
	total_revenue = 0

	for repair in completed_repairs:
		if repair.received_date and repair.delivered_date:
			hours = time_diff_in_hours(
				get_datetime(repair.delivered_date), get_datetime(repair.received_date)
			)
			total_hours += flt(hours)

		# Check if on time
		if repair.promised_date:
			promised = frappe.utils.getdate(repair.promised_date)
			actual = frappe.utils.getdate(repair.delivered_date)
			if actual <= promised:
				on_time_count += 1
			else:
				late_count += 1

		total_revenue += flt(repair.total_cost)

	completed_count = len(completed_repairs)
	avg_hours = flt(total_hours / completed_count) if completed_count else 0
	on_time_rate = flt(on_time_count / completed_count * 100) if completed_count else 0
	avg_revenue = flt(total_revenue / completed_count) if completed_count else 0

	return {
		"total_hours": flt(total_hours, 2),
		"avg_hours_per_repair": flt(avg_hours, 2),
		"on_time_count": on_time_count,
		"late_count": late_count,
		"on_time_rate": flt(on_time_rate, 2),
		"total_revenue": flt(total_revenue, 2),
		"avg_revenue": flt(avg_revenue, 2),
	}


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
	return values


def get_chart_data(data):
	if not data:
		return None

	labels = [row.get("technician", "") for row in data]
	completed_values = [row.get("completed", 0) for row in data]
	on_time_values = [row.get("on_time_count", 0) for row in data]
	late_values = [row.get("late_count", 0) for row in data]

	return {
		"labels": labels,
		"datasets": [
			{
				"name": "Completed",
				"values": completed_values,
				"chartType": "bar",
			},
			{
				"name": "On Time",
				"values": on_time_values,
				"chartType": "bar",
			},
			{
				"name": "Late",
				"values": late_values,
				"chartType": "bar",
			},
		],
		"type": "bar",
	}
