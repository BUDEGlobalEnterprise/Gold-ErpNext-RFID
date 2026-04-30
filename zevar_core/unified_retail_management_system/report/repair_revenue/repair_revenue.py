# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "period",
			"label": _("Period"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "repair_count",
			"label": _("Repair Count"),
			"fieldtype": "Int",
			"width": 110,
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
			"fieldname": "total_deposit",
			"label": _("Total Deposits"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "pending_balance",
			"label": _("Pending Balance"),
			"fieldtype": "Currency",
			"width": 130,
		},
	]


def get_data(filters):
	period_type = filters.get("period_type", "Monthly")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
	if not to_date:
		to_date = datetime.now().strftime("%Y-%m-%d")

	warehouse = filters.get("warehouse")
	repair_type = filters.get("repair_type")

	# Build conditions
	conditions = ["ro.docstatus = 1"]
	conditions.append("ro.received_date >= %(from_date)s")
	conditions.append("ro.received_date <= %(to_date)s")

	if warehouse:
		conditions.append("ro.warehouse = %(warehouse)s")
	if repair_type:
		conditions.append("ro.repair_type = %(repair_type)s")

	values = {
		"from_date": from_date,
		"to_date": to_date,
	}

	if warehouse:
		values["warehouse"] = warehouse
	if repair_type:
		values["repair_type"] = repair_type

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	sql = f"""
		SELECT
			ro.received_date,
			ro.repair_type,
			ro.warehouse,
			ro.total_cost,
			ro.deposit_amount,
			ro.balance_due,
			ro.payment_status
		FROM `tabRepair Order` ro
		WHERE {" AND ".join(conditions)}
		ORDER BY ro.received_date
	"""

	rows = frappe.db.sql(sql, values=values, as_dict=True)

	# Group by period
	period_data = {}

	for row in rows:
		period = get_period(row.received_date, period_type)

		if period not in period_data:
			period_data[period] = {
				"repair_count": 0,
				"total_revenue": 0,
				"total_deposit": 0,
				"pending_balance": 0,
			}

		period_data[period]["repair_count"] += 1
		period_data[period]["total_revenue"] += flt(row.total_cost)
		period_data[period]["total_deposit"] += flt(row.deposit_amount)
		period_data[period]["pending_balance"] += flt(row.balance_due)

	# Build result
	data = []
	for period in sorted(period_data.keys()):
		pd = period_data[period]
		data.append(
			{
				"period": period,
				"repair_count": pd["repair_count"],
				"total_revenue": flt(pd["total_revenue"], 2),
				"avg_revenue": flt(pd["total_revenue"] / pd["repair_count"], 2) if pd["repair_count"] else 0,
				"total_deposit": flt(pd["total_deposit"], 2),
				"pending_balance": flt(pd["pending_balance"], 2),
			}
		)

	return data


def get_period(date, period_type):
	"""Format date into period string based on period_type"""
	dt = getdate(date)

	if period_type == "Daily":
		return dt.strftime("%Y-%m-%d")
	elif period_type == "Weekly":
		week_start = dt - timedelta(days=dt.weekday())
		week_end = week_start + timedelta(days=6)
		return f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
	elif period_type == "Monthly":
		return dt.strftime("%Y-%m")
	elif period_type == "Quarterly":
		quarter = (dt.month - 1) // 3 + 1
		return f"{dt.year} Q{quarter}"
	else:  # Yearly
		return str(dt.year)


def get_chart_data(data, filters):
	if not data:
		return None

	labels = [row["period"] for row in data]
	revenue_values = [row["total_revenue"] for row in data]
	deposit_values = [row["total_deposit"] for row in data]
	[row["repair_count"] for row in data]

	return {
		"labels": labels,
		"datasets": [
			{
				"name": "Total Revenue",
				"values": revenue_values,
				"chartType": "bar",
			},
			{
				"name": "Deposits Collected",
				"values": deposit_values,
				"chartType": "line",
			},
		],
		"axisData": [
			{
				"title": "Revenue ($)",
				"index": 0,
			},
		],
		"type": "bar",
	}
