# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

"""Team Performance Ranking report for the Performance-Based Compensation system.

Ranks employees by total revenue generated from Performance Log entries within a
given period, optionally filtered by store location.  Each row includes a numeric
rank, the overall score (derived from the most recent Compensation Calculation),
and the performance tier (sourced from the latest Quarterly Performance Review).
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""Entry point for the Script Report.

	Args:
	    filters: Dictionary with optional ``store_location`` and required
	        ``from_date`` / ``to_date`` keys.

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
			"fieldname": "rank",
			"label": _("Rank"),
			"fieldtype": "Int",
			"width": 70,
		},
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
			"fieldname": "overall_score",
			"label": _("Overall Score"),
			"fieldtype": "Percent",
			"width": 110,
		},
		{
			"fieldname": "performance_tier",
			"label": _("Performance Tier"),
			"fieldtype": "Data",
			"width": 140,
		},
	]


def get_data(filters):
	"""Fetch ranked employee performance data.

	Aggregates revenue from ``tabPerformance Log`` grouped by employee, then
	enriches each row with the most recent overall score and performance tier
	from Compensation Calculation and Quarterly Performance Review respectively.

	Args:
	    filters: Report filter dictionary.

	Returns:
	    List of dictionaries representing ranked report rows.
	"""
	conditions, values = build_conditions(filters)

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(  # nosemgrep
		f"""
        SELECT
            pl.employee,
            pl.employee_name,
            SUM(pl.revenue_amount) AS total_revenue
        FROM `tabPerformance Log` pl
        WHERE 1=1
            {conditions}
        GROUP BY pl.employee, pl.employee_name
        ORDER BY total_revenue DESC
        """,
		values=values,
		as_dict=True,
	)

	data = []
	for idx, row in enumerate(rows, start=1):
		row["rank"] = idx

		# Fetch the most recent overall score from Compensation Calculation
		row["overall_score"] = flt(
			frappe.db.get_value(
				"Compensation Calculation",
				{"employee": row["employee"], "docstatus": ["!=", 2]},
				"overall_performance_score",
				order_by="creation DESC",
			)
			or 0,
			2,
		)

		# Fetch the most recent performance tier from Quarterly Performance Review
		row["performance_tier"] = frappe.db.get_value(
			"Quarterly Performance Review",
			{"employee": row["employee"], "docstatus": ["!=", 2]},
			"performance_tier",
			order_by="creation DESC",
		) or _("N/A")

		data.append(row)

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

	if filters.get("store_location"):
		conditions += " AND pl.store_location = %(store_location)s"
		values["store_location"] = filters["store_location"]

	if filters.get("from_date"):
		conditions += " AND pl.event_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions += " AND pl.event_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	return conditions, values
