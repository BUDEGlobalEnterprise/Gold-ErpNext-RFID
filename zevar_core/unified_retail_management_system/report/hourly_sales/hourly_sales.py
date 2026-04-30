# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0


import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""
	Execute the Hourly Sales Report.

	Returns sales breakdown by hour of day for traffic analysis.
	"""
	columns = [
		{
			"fieldname": "hour",
			"label": _("Hour"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "transaction_count",
			"label": _("Transactions"),
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"fieldname": "total_sales",
			"label": _("Total Sales"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "avg_transaction",
			"label": _("Avg Transaction"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "peak_indicator",
			"label": _("Peak Hour"),
			"fieldtype": "Data",
			"width": 80,
		},
	]

	data = []

	filters = filters or {}

	# Date range filter
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = frappe.utils.today()
	if not to_date:
		to_date = frappe.utils.today()

	# Get hourly sales data
	hourly_data = frappe.db.sql(
		"""
		SELECT
			HOUR(si.posting_time) as hour,
			COUNT(*) as transaction_count,
			SUM(si.grand_total) as total_sales,
			AVG(si.grand_total) as avg_transaction
		FROM `tabSales Invoice` si
		WHERE si.is_pos = 1
			AND si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY HOUR(si.posting_time)
		ORDER BY hour
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	# Find peak hour
	max_sales = max((row.get("total_sales", 0) or 0) for row in hourly_data) if hourly_data else 0

	for row in hourly_data:
		hour = row.get("hour", 0)
		row["hour"] = f"{hour:02d}:00 - {hour + 1:02d}:00"
		row["total_sales"] = flt(row.get("total_sales", 0))
		row["avg_transaction"] = flt(row.get("avg_transaction", 0))
		row["peak_indicator"] = "★ PEAK" if row["total_sales"] == max_sales else ""
		data.append(row)

	return columns, data


def get_chart_data(filters=None):
	"""Return chart data for visualization."""
	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = frappe.utils.today()
	if not to_date:
		to_date = frappe.utils.today()

	chart_data = frappe.db.sql(
		"""
		SELECT
			HOUR(posting_time) as hour,
			SUM(grand_total) as value
		FROM `tabSales Invoice`
		WHERE is_pos = 1
			AND docstatus = 1
			AND posting_date BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY HOUR(posting_time)
		ORDER BY hour
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	hours = [f"{i:02d}:00" for i in range(24)]

	return {
		"labels": hours,
		"datasets": [
			{"name": "Sales by Hour", "values": [flt(chart_data.get(hour, 0)) for hour in range(24)]}
		],
	}
