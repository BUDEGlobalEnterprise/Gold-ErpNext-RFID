# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

"""Compensation Breakdown report for the Performance-Based Compensation system.

Reads from the Compensation Calculation DocType and presents a detailed breakdown
of each employee's pay including guaranteed pay, bonus, commission, deductions,
and the final calculated pay alongside hours worked and revenue metrics.
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
            "width": 140,
        },
        {
            "fieldname": "period",
            "label": _("Period"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "total_hours_worked",
            "label": _("Hours Worked"),
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "fieldname": "revenue_achieved",
            "label": _("Revenue Achieved"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "revenue_achievement_pct",
            "label": _("Revenue Target %"),
            "fieldtype": "Percent",
            "width": 110,
        },
        {
            "fieldname": "overall_performance_score",
            "label": _("Overall Score"),
            "fieldtype": "Percent",
            "width": 110,
        },
        {
            "fieldname": "guaranteed_pay",
            "label": _("Guaranteed Pay"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "performance_bonus",
            "label": _("Bonus"),
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "fieldname": "commission_earned",
            "label": _("Commission"),
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "fieldname": "final_calculated_pay",
            "label": _("Final Pay"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "effective_hourly_rate",
            "label": _("Effective Hourly Rate"),
            "fieldtype": "Currency",
            "width": 140,
        },
    ]


def get_data(filters):
    """Fetch compensation calculation records.

    Queries ``tabCompensation Calculation`` with date-range and optional
    employee filters.  The period column is composed from period_start and
    period_end for readability.

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
            cc.employee,
            CONCAT(DATE_FORMAT(cc.period_start, '%Y-%m-%d'), ' to ', DATE_FORMAT(cc.period_end, '%Y-%m-%d')) AS period,
            cc.total_hours_worked,
            cc.revenue_achieved,
            cc.revenue_achievement_pct,
            cc.overall_performance_score,
            cc.guaranteed_pay,
            cc.performance_bonus,
            cc.commission_earned,
            cc.final_calculated_pay,
            cc.effective_hourly_rate
        FROM `tabCompensation Calculation` cc
        WHERE cc.docstatus = 1
            {conditions}
        ORDER BY cc.employee, cc.period_start DESC
        """,
        values=values,
        as_dict=True,
    )

    for row in data:
        row["total_hours_worked"] = flt(row.get("total_hours_worked"), 2)

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
        conditions += " AND cc.employee = %(employee)s"
        values["employee"] = filters["employee"]

    if filters.get("from_date"):
        conditions += " AND cc.period_start >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND cc.period_end <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    return conditions, values
