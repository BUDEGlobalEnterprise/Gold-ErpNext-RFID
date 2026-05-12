# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

"""Attendance Performance Correlation report for the Performance-Based Compensation system.

Correlates hours worked (sourced from ``Shift Complete`` events in Performance
Log) with revenue performance metrics to help identify the relationship between
attendance and output.  For each employee the report shows total hours worked,
revenue, transaction count, revenue per hour, and attendance percentage (hours
worked relative to scheduled hours from Compensation Calculation records).
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    """Entry point for the Script Report.

    Args:
        filters: Dictionary with required ``from_date`` and ``to_date`` keys.

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
            "width": 140,
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "fieldname": "hours_worked",
            "label": _("Hours Worked"),
            "fieldtype": "Float",
            "width": 110,
        },
        {
            "fieldname": "revenue",
            "label": _("Revenue"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "transactions",
            "label": _("Transactions"),
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "fieldname": "revenue_per_hour",
            "label": _("Revenue Per Hour"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "attendance_pct",
            "label": _("Attendance %"),
            "fieldtype": "Percent",
            "width": 110,
        },
    ]


def get_data(filters):
    """Fetch attendance-performance correlation data.

    Aggregates hours from ``Shift Complete`` events and revenue from all
    revenue-generating events in ``tabPerformance Log``.  Attendance
    percentage is computed by comparing actual hours against scheduled hours
    from the most recent Compensation Calculation.

    Args:
        filters: Report filter dictionary.

    Returns:
        List of dictionaries representing report rows.
    """
    conditions, values = build_conditions(filters)

    # nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
    rows = frappe.db.sql(  # nosemgrep
        f"""
        SELECT
            pl.employee,
            pl.employee_name,
            SUM(CASE WHEN pl.event_type = 'Shift Complete' THEN pl.hours_worked ELSE 0 END) AS hours_worked,
            SUM(pl.revenue_amount) AS revenue,
            COUNT(CASE WHEN pl.event_type IN ('Sale Completed', 'Layaway Completed', 'Upsell Recorded') THEN 1 END) AS transactions
        FROM `tabPerformance Log` pl
        WHERE 1=1
            {conditions}
        GROUP BY pl.employee, pl.employee_name
        ORDER BY revenue DESC
        """,
        values=values,
        as_dict=True,
    )

    data = []
    for row in rows:
        hours = flt(row.get("hours_worked"), 2)
        revenue = flt(row.get("revenue"), 2)
        transactions = row.get("transactions") or 0

        revenue_per_hour = flt((revenue / hours) if hours > 0 else 0, 2)

        # Fetch scheduled hours from the most recent Compensation Calculation
        scheduled = flt(
            frappe.db.get_value(
                "Compensation Calculation",
                {"employee": row["employee"], "docstatus": 1},
                "scheduled_hours",
                order_by="creation DESC",
            )
            or 0,
            2,
        )

        attendance_pct = flt((hours / scheduled * 100) if scheduled > 0 else 0, 2)

        data.append(
            {
                "employee": row["employee"],
                "employee_name": row["employee_name"],
                "hours_worked": hours,
                "revenue": revenue,
                "transactions": transactions,
                "revenue_per_hour": revenue_per_hour,
                "attendance_pct": attendance_pct,
            }
        )

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

    if filters.get("from_date"):
        conditions += " AND pl.event_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND pl.event_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    return conditions, values
