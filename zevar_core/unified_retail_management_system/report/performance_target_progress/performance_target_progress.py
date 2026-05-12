# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

"""Performance Target Progress report for the Performance-Based Compensation system.

Reads active Performance Targets and correlates them with aggregated revenue from
Performance Log entries to show progress towards each target.  The report
displays the revenue target, revenue achieved so far, the percentage achieved,
and a computed status (On Track / Behind / Exceeded / At Risk).
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    """Entry point for the Script Report.

    Args:
        filters: Dictionary with optional ``employee`` and ``store_location``
            keys.

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
            "fieldname": "period_type",
            "label": _("Period Type"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "period",
            "label": _("Period"),
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "revenue_target",
            "label": _("Revenue Target"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "revenue_achieved",
            "label": _("Revenue Achieved"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "revenue_pct",
            "label": _("Revenue %"),
            "fieldtype": "Percent",
            "width": 100,
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 110,
        },
    ]


def get_data(filters):
    """Fetch active performance targets with aggregated revenue progress.

    Queries ``tabPerformance Target`` for active records, then aggregates
    revenue from ``tabPerformance Log`` within each target's period to
    compute progress.

    Args:
        filters: Report filter dictionary.

    Returns:
        List of dictionaries representing report rows.
    """
    conditions, values = build_conditions(filters)

    # nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
    targets = frappe.db.sql(  # nosemgrep
        f"""
        SELECT
            pt.name,
            pt.employee,
            pt.employee_name,
            pt.period_type,
            pt.period_start,
            pt.period_end,
            pt.revenue_target,
            pt.store_location
        FROM `tabPerformance Target` pt
        WHERE pt.status = 'Active'
            AND pt.docstatus = 1
            {conditions}
        ORDER BY pt.employee, pt.period_start DESC
        """,
        values=values,
        as_dict=True,
    )

    data = []
    for target in targets:
        period_label = "{} to {}".format(
            getdate(target["period_start"]).strftime("%Y-%m-%d"),
            getdate(target["period_end"]).strftime("%Y-%m-%d"),
        )

        # Aggregate revenue from Performance Log within the target period
        achieved = flt(
            frappe.db.sql(
                """
                SELECT SUM(pl.revenue_amount)
                FROM `tabPerformance Log` pl
                WHERE pl.employee = %s
                    AND pl.event_date >= %s
                    AND pl.event_date <= %s
                """,
                (target["employee"], target["period_start"], target["period_end"]),
            )[0][0]
            or 0,
            2,
        )

        revenue_target = flt(target.get("revenue_target"), 2)
        revenue_pct = flt((achieved / revenue_target * 100) if revenue_target > 0 else 0, 2)
        status = compute_status(revenue_pct, target["period_start"], target["period_end"])

        data.append(
            {
                "employee": target["employee"],
                "employee_name": target["employee_name"],
                "period_type": target["period_type"],
                "period": period_label,
                "revenue_target": revenue_target,
                "revenue_achieved": achieved,
                "revenue_pct": revenue_pct,
                "status": status,
            }
        )

    return data


def compute_status(revenue_pct, period_start, period_end):
    """Determine the target progress status.

    Compares the revenue percentage against the elapsed portion of the target
    period to decide whether the employee is on track, behind, has exceeded
    the target, or is at risk.

    Args:
        revenue_pct: Revenue achievement percentage.
        period_start: Target period start date string.
        period_end: Target period end date string.

    Returns:
        Status string label.
    """
    if revenue_pct >= 100:
        return _("Exceeded")

    today = getdate()
    start = getdate(period_start)
    end = getdate(period_end)

    total_days = max((end - start).days, 1)
    elapsed_days = max((min(today, end) - start).days, 0)
    time_pct = flt((elapsed_days / total_days) * 100, 2)

    if revenue_pct >= time_pct:
        return _("On Track")
    elif revenue_pct >= time_pct * 0.75:
        return _("At Risk")
    else:
        return _("Behind")


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
        conditions += " AND pt.employee = %(employee)s"
        values["employee"] = filters["employee"]

    if filters.get("store_location"):
        conditions += " AND pt.store_location = %(store_location)s"
        values["store_location"] = filters["store_location"]

    return conditions, values
