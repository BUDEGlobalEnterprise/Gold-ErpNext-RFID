# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

"""Employee Performance Summary report for the Performance-Based Compensation system.

Aggregates Performance Log entries by employee within a given date range,
producing metrics such as total revenue, transaction count, average transaction
value, items sold, layaways created, repairs completed, commission earned, and
hours worked.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""Entry point for the Script Report.

	Args:
	    filters: Dictionary with optional ``employee`` and required ``from_date``,
	        ``to_date`` keys.

	Returns:
	    Tuple of (columns, data).
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Return column definitions for the report."""
	return [
		{
			"fieldname": "employee",
			"label": _("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 160,
		},
		{
			"fieldname": "employee_name",
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"fieldname": "total_revenue",
			"label": _("Total Revenue"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "total_transactions",
			"label": _("Total Transactions"),
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"fieldname": "avg_transaction_value",
			"label": _("Avg Transaction Value"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "items_sold",
			"label": _("Items Sold"),
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"fieldname": "layaways_created",
			"label": _("Layaways Created"),
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"fieldname": "repairs_completed",
			"label": _("Repairs Completed"),
			"fieldtype": "Int",
			"width": 130,
		},
		{
			"fieldname": "commission_earned",
			"label": _("Commission Earned"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "hours_worked",
			"label": _("Hours Worked"),
			"fieldtype": "Float",
			"width": 110,
		},
	]


def get_data(filters):
	"""Fetch aggregated performance data from Performance Log.

	Builds conditional SQL based on the supplied *filters* and groups results
	by employee.

	Args:
	    filters: Report filter dictionary.

	Returns:
	    List of dictionaries representing report rows.
	"""
	conditions, values = build_conditions(filters)

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	data = frappe.db.sql(  # nosemgrep
		f"""
        SELECT
            pl.employee,
            pl.employee_name,
            SUM(pl.revenue_amount) AS total_revenue,
            COUNT(CASE WHEN pl.event_type IN ('Sale Completed', 'Layaway Completed', 'Upsell Recorded') THEN 1 END) AS total_transactions,
            AVG(CASE WHEN pl.event_type = 'Sale Completed' THEN pl.revenue_amount END) AS avg_transaction_value,
            SUM(pl.item_count) AS items_sold,
            COUNT(CASE WHEN pl.event_type = 'Layaway Created' THEN 1 END) AS layaways_created,
            COUNT(CASE WHEN pl.event_type = 'Repair Completed' THEN 1 END) AS repairs_completed,
            SUM(pl.commission_amount) AS commission_earned,
            SUM(CASE WHEN pl.event_type = 'Shift Complete' THEN pl.hours_worked ELSE 0 END) AS hours_worked
        FROM `tabPerformance Log` pl
        WHERE 1=1
            {conditions}
        GROUP BY pl.employee, pl.employee_name
        ORDER BY total_revenue DESC
        """,
		values=values,
		as_dict=True,
	)

	# Round computed values for display
	for row in data:
		row["avg_transaction_value"] = flt(row.get("avg_transaction_value"), 2)
		row["hours_worked"] = flt(row.get("hours_worked"), 2)

	return data


def build_conditions(filters):
	"""Build SQL WHERE clause fragments and parameter values from *filters*.

	Args:
	    filters: Report filter dictionary.

	Returns:
	    Tuple of (conditions_string, values_dict).
	"""
	conditions = ""
	values = {}

	if filters.get("employee"):
		conditions += " AND pl.employee = %(employee)s"
		values["employee"] = filters["employee"]

	if filters.get("from_date"):
		conditions += " AND pl.event_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions += " AND pl.event_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	return conditions, values
