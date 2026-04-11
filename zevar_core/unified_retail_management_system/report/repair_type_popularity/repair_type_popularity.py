# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "repair_type",
			"label": _("Repair Type"),
			"fieldtype": "Link",
			"options": "Repair Type",
			"width": 180,
		},
		{
			"fieldname": "category",
			"label": _("Category"),
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"fieldname": "count",
			"label": _("Count"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "percentage",
			"label": _("% of Total"),
			"fieldtype": "Percent",
			"width": 100,
		},
		{
			"fieldname": "total_revenue",
			"label": _("Total Revenue"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "avg_revenue",
			"label": _("Avg Revenue"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "avg_turnaround",
			"label": _("Avg Turnaround (Days)"),
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"fieldname": "by_store",
			"label": _("By Store"),
			"fieldtype": "Data",
			"width": 200,
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)
	values = get_values(filters)

	# Get repair type counts and revenue
	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(
		f"""
		SELECT
			ro.repair_type,
			rt.category,
			COUNT(*) as count,
			SUM(ro.total_cost) as total_revenue,
			AVG(ro.total_cost) as avg_revenue
		FROM `tabRepair Order` ro
		LEFT JOIN `tabRepair Type` rt ON ro.repair_type = rt.name
		WHERE ro.docstatus = 1
			{conditions}
		GROUP BY ro.repair_type, rt.category
		ORDER BY count DESC
		""",
		values=values,
		as_dict=True,
	)

	# Get total count for percentage calculation
	total_count = sum(row.count for row in rows) if rows else 0

	data = []
	for row in rows:
		row.percentage = flt(row.count / total_count * 100) if total_count else 0

		# Calculate average turnaround for this repair type
		row.avg_turnaround = get_avg_turnaround(row.repair_type, filters)

		# Get breakdown by store
		row.by_store = get_store_breakdown(row.repair_type, filters)

		data.append(row)

	return data


def get_avg_turnaround(repair_type, filters):
	"""Calculate average turnaround days for a repair type"""
	conditions = "AND ro.repair_type = %(repair_type)s"
	values = {"repair_type": repair_type}

	if filters.get("from_date"):
		conditions += " AND ro.received_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions += " AND ro.received_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]
	if filters.get("warehouse"):
		conditions += " AND ro.warehouse = %(warehouse)s"
		values["warehouse"] = filters["warehouse"]

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	result = frappe.db.sql(
		f"""
		SELECT
			AVG(TIMESTAMPDIFF(HOUR, ro.received_date, ro.delivered_date) / 24) as avg_days
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			AND ro.status = 'Delivered'
			AND ro.delivered_date IS NOT NULL
			{conditions}
		""",
		values=values,
		as_dict=True,
	)

	return flt(result[0].avg_days, 1) if result and result[0].avg_days else 0


def get_store_breakdown(repair_type, filters):
	"""Get repair count by store for this repair type"""
	conditions = "AND ro.repair_type = %(repair_type)s"
	values = {"repair_type": repair_type}

	if filters.get("from_date"):
		conditions += " AND ro.received_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions += " AND ro.received_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	result = frappe.db.sql(
		f"""
		SELECT
			ro.warehouse,
			COUNT(*) as count
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			{conditions}
		GROUP BY ro.warehouse
		ORDER BY count DESC
		LIMIT 3
		""",
		values=values,
		as_dict=True,
	)

	if not result:
		return ""

	parts = []
	for row in result:
		parts.append(f"{row.warehouse}: {row.count}")

	return ", ".join(parts)


def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " AND ro.received_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND ro.received_date <= %(to_date)s"

	if filters.get("warehouse"):
		conditions += " AND ro.warehouse = %(warehouse)s"

	if filters.get("category"):
		conditions += " AND rt.category = %(category)s"

	return conditions


def get_values(filters):
	values = {}
	if filters.get("from_date"):
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		values["to_date"] = filters["to_date"]
	if filters.get("warehouse"):
		values["warehouse"] = filters["warehouse"]
	if filters.get("category"):
		values["category"] = filters["category"]
	return values


def get_chart_data(data):
	if not data:
		return None

	# Top 10 repair types by count
	top_data = data[:10]

	labels = [row.get("repair_type", "") for row in top_data]
	count_values = [row.get("count", 0) for row in top_data]
	revenue_values = [flt(row.get("total_revenue", 0)) for row in top_data]

	return {
		"labels": labels,
		"datasets": [
			{
				"name": "Repair Count",
				"values": count_values,
				"chartType": "bar",
			},
			{
				"name": "Revenue",
				"values": revenue_values,
				"chartType": "line",
			},
		],
		"type": "bar",
	}
