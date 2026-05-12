# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

"""Quarterly Review Summary report for the Performance-Based Compensation system.

Reads from the Quarterly Performance Review DocType and presents each employee's
overall score, performance tier, recommendation, quarterly revenue, and
attendance rate for the selected review period and year.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    """Entry point for the Script Report.

    Args:
        filters: Dictionary with required ``review_period`` (Q1/Q2/Q3/Q4) and
            ``review_year`` (Int) keys.

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
        {
            "fieldname": "recommendation",
            "label": _("Recommendation"),
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "quarterly_revenue",
            "label": _("Quarterly Revenue"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "attendance_rate",
            "label": _("Attendance Rate"),
            "fieldtype": "Percent",
            "width": 120,
        },
    ]


def get_data(filters):
    """Fetch quarterly performance review records.

    Queries ``tabQuarterly Performance Review`` filtered by the selected
    review period and year.  Results are ordered by overall score descending.

    Args:
        filters: Report filter dictionary with ``review_period`` and
            ``review_year``.

    Returns:
        List of dictionaries representing report rows.
    """
    conditions, values = build_conditions(filters)

    # nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
    data = frappe.db.sql(  # nosemgrep
        f"""
        SELECT
            qpr.employee,
            qpr.employee_name,
            qpr.overall_score,
            qpr.performance_tier,
            qpr.recommendation,
            qpr.quarterly_revenue,
            qpr.attendance_rate
        FROM `tabQuarterly Performance Review` qpr
        WHERE qpr.docstatus = 1
            {conditions}
        ORDER BY qpr.overall_score DESC
        """,
        values=values,
        as_dict=True,
    )

    for row in data:
        row["overall_score"] = flt(row.get("overall_score"), 2)
        row["attendance_rate"] = flt(row.get("attendance_rate"), 2)

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

    if filters.get("review_period"):
        conditions += " AND qpr.review_period = %(review_period)s"
        values["review_period"] = filters["review_period"]

    if filters.get("review_year"):
        conditions += " AND qpr.review_year = %(review_year)s"
        values["review_year"] = filters["review_year"]

    return conditions, values
